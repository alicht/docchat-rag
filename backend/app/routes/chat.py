from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.vector_store import VectorStoreService
from app.services.llm import LLMService

router = APIRouter()

vector_store = VectorStoreService()
llm_service = LLMService()

class ChatRequest(BaseModel):
    message: str
    context_limit: int = 3

class ChatResponse(BaseModel):
    response: str
    sources: list = []

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        relevant_docs = await vector_store.search(
            query=request.message,
            top_k=request.context_limit
        )
        
        context = "\n\n".join([doc["text"] for doc in relevant_docs])
        
        response = await llm_service.generate_response(
            query=request.message,
            context=context
        )
        
        sources = [{"filename": doc.get("metadata", {}).get("filename", "Unknown")} 
                  for doc in relevant_docs]
        
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))