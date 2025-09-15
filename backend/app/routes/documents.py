from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.services.vector_store import VectorStoreService
from app.services.embeddings import EmbeddingService

router = APIRouter()

vector_store = VectorStoreService()
embedding_service = EmbeddingService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        doc_id = await vector_store.add_document(
            text=text,
            metadata={"filename": file.filename}
        )
        
        return {"message": "Document uploaded successfully", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_documents():
    try:
        documents = await vector_store.list_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    try:
        await vector_store.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))