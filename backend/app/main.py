from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import logging

from app.routes import documents, chat
from app.services.vector_store import VectorStoreService

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DocChat RAG API", version="1.0.0")

# Initialize services
vector_store = VectorStoreService()

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

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    return AskResponse(answer="Hello from backend")

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