import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import logging
from app.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

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
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
    
    async def add_document(self, content: bytes, filename: str, content_type: str) -> Tuple[str, int]:
        """
        Add a document to the vector store
        Returns: (document_id, number_of_chunks)
        """
        doc_id = str(uuid.uuid4())
        
        # Extract text based on content type
        if content_type == "application/pdf":
            text = self._extract_pdf_text(content)
        else:  # text/plain or other text formats
            text = content.decode('utf-8', errors='ignore')
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            raise ValueError("No text content could be extracted from the document")
        
        # Generate embeddings
        embeddings = await self.embedding_service.get_embeddings(chunks)
        
        # Prepare data for ChromaDB
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [{
            "doc_id": doc_id,
            "chunk_index": i,
            "filename": filename,
            "content_type": content_type,
            "total_chunks": len(chunks)
        } for i in range(len(chunks))]
        
        # Store in ChromaDB
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Stored {len(chunks)} chunks for document {filename} (ID: {doc_id})")
        
        return doc_id, len(chunks)
    
    def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF bytes"""
        import io
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
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
                    "filename": metadata.get('filename', 'Unknown'),
                    "content_type": metadata.get('content_type', 'Unknown'),
                    "total_chunks": metadata.get('total_chunks', 0)
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
            logger.info(f"Deleted {len(ids_to_delete)} chunks for document {document_id}")