from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os
import logging
import re

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
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
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

class Source(BaseModel):
    filename: str
    chunk_id: int
    score: float
    preview: str
    page: Optional[int] = None
    line: Optional[int] = None
    topic: Optional[str] = None
    doc_url: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    sources: List[Source] = []

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Answer questions using RAG (Retrieval-Augmented Generation)
    """
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Get MAX_RESULTS from environment, default to 1
        max_results = int(os.getenv("MAX_RESULTS", "1"))
        
        # Check if query matches Topic X-Y pattern
        topic_pattern = re.compile(r'Topic\s+(\d+)-(\d+)', re.IGNORECASE)
        topic_match = topic_pattern.search(request.question)
        
        # Log retrieval configuration
        if topic_match:
            topic_label = f"Topic {topic_match.group(1)}-{topic_match.group(2)}"
            logger.info(f"Retrieval config: k={max_results}, regex matched topic={topic_label}")
        else:
            logger.info(f"Retrieval config: k={max_results}, no topic regex match")
        
        # Search for relevant document chunks with configured k
        relevant_chunks = await vector_store.search(
            query=request.question,
            top_k=max_results if not topic_match else 10  # Get more results for filtering if topic match
        )
        
        # Filter chunks if topic pattern was matched
        if topic_match:
            topic_label = f"Topic {topic_match.group(1)}-{topic_match.group(2)}"
            # Filter to only chunks with matching topic
            filtered_chunks = []
            for chunk in relevant_chunks:
                metadata = chunk.get("metadata", {})
                if metadata.get("topic") == topic_label:
                    filtered_chunks.append(chunk)
            
            # If we found matching topic chunks, use them; otherwise fall back to top result
            if filtered_chunks:
                relevant_chunks = filtered_chunks[:max_results]
                logger.info(f"Filtered to {len(relevant_chunks)} chunks matching topic={topic_label}")
            else:
                # No exact topic match found, use top result anyway
                relevant_chunks = relevant_chunks[:max_results]
                logger.info(f"No exact topic match for {topic_label}, using top {max_results} result(s)")
        else:
            # No topic pattern, just limit to max_results
            relevant_chunks = relevant_chunks[:max_results]
        
        if not relevant_chunks:
            logger.warning("No documents found in ChromaDB")
            return AskResponse(
                answer="No documents found. Please upload some documents first to ask questions about them.",
                sources=[]
            )
        
        # Log retrieved chunks for debugging
        logger.info(f"Retrieved {len(relevant_chunks)} final chunks:")
        for i, chunk in enumerate(relevant_chunks):
            metadata = chunk.get("metadata", {})
            logger.info(f"  Chunk {i+1}: {metadata.get('filename', 'Unknown')} "
                       f"(chunk {metadata.get('chunk_index', 'N/A')}) "
                       f"topic={metadata.get('topic', 'None')} "
                       f"- distance: {chunk.get('distance', 'N/A')}")
        
        # Construct context from chunks
        context_parts = []
        sources = []
        
        for chunk in relevant_chunks:
            chunk_text = chunk["text"]
            context_parts.append(chunk_text)
            metadata = chunk.get("metadata", {})
            
            # Convert distance to similarity score (0-100)
            distance = chunk.get("distance", 1.0)
            similarity_score = max(0, (1 - distance) * 100)
            
            # Create preview (first ~200 characters)
            preview = chunk_text[:200].strip()
            if len(chunk_text) > 200:
                preview += "..."
            
            sources.append(Source(
                filename=metadata.get("filename", "Unknown"),
                chunk_id=metadata.get("chunk_index", 0),
                score=round(similarity_score, 1),
                preview=preview,
                page=metadata.get("page"),
                line=metadata.get("line"),
                topic=metadata.get("topic"),
                doc_url=metadata.get("doc_url")  # Will be None if not set
            ))
        
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