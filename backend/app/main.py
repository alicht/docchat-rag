from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging

from app.routes import documents, chat
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DocChat RAG API", version="1.0.0")

# Initialize services
vector_store = VectorStoreService()
llm_service = LLMService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "DocChat RAG API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: list = []

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Answer questions using RAG (Retrieval-Augmented Generation)
    """
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Search for relevant document chunks
        relevant_chunks = await vector_store.search(
            query=request.question,
            top_k=5
        )
        
        if not relevant_chunks:
            logger.warning("No documents found in ChromaDB")
            return AskResponse(
                answer="No documents found. Please upload some documents first to ask questions about them.",
                sources=[]
            )
        
        # Log retrieved chunks for debugging
        logger.info(f"Retrieved {len(relevant_chunks)} chunks:")
        for i, chunk in enumerate(relevant_chunks):
            metadata = chunk.get("metadata", {})
            logger.info(f"  Chunk {i+1}: {metadata.get('filename', 'Unknown')} "
                       f"(chunk {metadata.get('chunk_index', 'N/A')}) "
                       f"- distance: {chunk.get('distance', 'N/A')}")
        
        # Construct context from chunks
        context_parts = []
        sources = []
        
        for chunk in relevant_chunks:
            context_parts.append(chunk["text"])
            metadata = chunk.get("metadata", {})
            sources.append({
                "filename": metadata.get("filename", "Unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "distance": chunk.get("distance")
            })
        
        context = "\n\n".join(context_parts)
        
        # Generate response using LLM
        answer = await llm_service.generate_response(
            query=request.question,
            context=context
        )
        
        logger.info(f"Generated answer of length: {len(answer)}")
        
        return AskResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error processing your question. Please try again."
        )

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunks_stored: int

@app.post("/upload-doc", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document for processing
    """
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not supported. Please upload PDF or TXT files."
            )
        
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Process document with vector store
        doc_id, chunk_count = await vector_store.add_document(
            content=content,
            filename=file.filename or "unknown",
            content_type=file.content_type
        )
        
        logger.info(f"Successfully processed document {file.filename}: {chunk_count} chunks stored")
        
        return UploadResponse(
            message="Document uploaded and processed successfully",
            document_id=doc_id,
            filename=file.filename or "unknown",
            chunks_stored=chunk_count
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise  # Re-raise HTTP exceptions without modification
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while processing document")