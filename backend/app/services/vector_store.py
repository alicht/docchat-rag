import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any
from app.services.embeddings import EmbeddingService

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./data",
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_service = EmbeddingService()
    
    async def add_document(self, text: str, metadata: Dict[str, Any] = None) -> str:
        doc_id = str(uuid.uuid4())
        chunks = self._chunk_text(text)
        
        embeddings = await self.embedding_service.get_embeddings(chunks)
        
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": doc_id, "chunk_index": i, **(metadata or {})} 
                    for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        return doc_id
    
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_embedding = await self.embedding_service.get_embeddings([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        
        return documents
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        all_data = self.collection.get()
        
        doc_map = {}
        for i, metadata in enumerate(all_data['metadatas'] or []):
            doc_id = metadata.get('doc_id')
            if doc_id and doc_id not in doc_map:
                doc_map[doc_id] = {
                    "id": doc_id,
                    "filename": metadata.get('filename', 'Unknown')
                }
        
        return list(doc_map.values())
    
    async def delete_document(self, document_id: str):
        all_data = self.collection.get()
        
        ids_to_delete = []
        for i, metadata in enumerate(all_data['metadatas'] or []):
            if metadata.get('doc_id') == document_id:
                ids_to_delete.append(all_data['ids'][i])
        
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks if chunks else [text]