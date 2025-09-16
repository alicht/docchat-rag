import chromadb
from chromadb.config import Settings
import uuid
from typing import List, Dict, Any, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import logging
import re
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
        Add a document to the vector store with fine-grained parsing
        Returns: (document_id, number_of_chunks)
        """
        doc_id = str(uuid.uuid4())
        
        # Check if this document needs fine-grained parsing
        use_fine_grained = self._should_use_fine_grained_parsing(filename, content_type)
        
        if use_fine_grained:
            # Use fine-grained parsing for documents with Topic patterns
            if content_type == "application/pdf":
                chunks, metadatas = self._extract_pdf_fine_grained(content, filename, doc_id)
            else:  # text/plain
                chunks, metadatas = self._extract_text_fine_grained(content, filename, doc_id)
        else:
            # Use standard extraction for other documents
            if content_type == "application/pdf":
                text = self._extract_pdf_text(content)
            else:  # text/plain or other text formats
                text = content.decode('utf-8', errors='ignore')
            
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(text)
            
            if not text_chunks:
                raise ValueError("No text content could be extracted from the document")
            
            chunks = text_chunks
            metadatas = [{
                "doc_id": doc_id,
                "chunk_index": i,
                "filename": filename,
                "content_type": content_type,
                "total_chunks": len(chunks)
            } for i in range(len(chunks))]
        
        if not chunks:
            raise ValueError("No text content could be extracted from the document")
        
        # Generate embeddings
        embeddings = await self.embedding_service.get_embeddings(chunks)
        
        # Prepare IDs for ChromaDB
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        
        # Store in ChromaDB
        self.collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Stored {len(chunks)} chunks for document {filename} (ID: {doc_id})")
        
        return doc_id, len(chunks)
    
    def _should_use_fine_grained_parsing(self, filename: str, content_type: str) -> bool:
        """Determine if fine-grained parsing should be used for this file"""
        # Use fine-grained parsing for Encyclopedia or similar structured docs
        fine_grained_patterns = [
            "encyclopedia", "testing", "topics", "index", "reference"
        ]
        filename_lower = filename.lower()
        # Enable for PDFs and text files with matching patterns
        if any(pattern in filename_lower for pattern in fine_grained_patterns):
            return content_type in ["application/pdf", "text/plain"]
        return False
    
    def _extract_pdf_fine_grained(self, content: bytes, filename: str, doc_id: str) -> Tuple[List[str], List[Dict]]:
        """
        Extract PDF with fine-grained parsing, detecting Topic X-Y patterns
        Returns: (chunks, metadatas)
        """
        import io
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        
        chunks = []
        metadatas = []
        chunk_index = 0
        
        # Regex pattern to detect "Topic X-Y" format
        topic_pattern = re.compile(r'Topic\s+(\d+)-(\d+)[:\s]*(.*)', re.IGNORECASE)
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if not text:
                continue
            
            # Split by lines for fine-grained processing
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines, start=1):
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line contains a Topic marker
                topic_match = topic_pattern.search(line)
                
                if topic_match:
                    # This is a topic line - create its own chunk
                    topic_page = topic_match.group(1)
                    topic_line = topic_match.group(2)
                    topic_text = topic_match.group(3)
                    topic_label = f"Topic {topic_page}-{topic_line}"
                    
                    # Create chunk with the full line
                    chunks.append(line)
                    metadatas.append({
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "filename": filename,
                        "content_type": "application/pdf",
                        "page": page_num,
                        "line": line_num,
                        "topic": topic_label,
                        "is_topic": True
                    })
                    chunk_index += 1
                elif len(line) > 50:  # Only create chunks for substantial lines
                    # Regular line - check if it's meaningful content
                    chunks.append(line)
                    metadatas.append({
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "filename": filename,
                        "content_type": "application/pdf",
                        "page": page_num,
                        "line": line_num,
                        "topic": "",  # Use empty string instead of None
                        "is_topic": False
                    })
                    chunk_index += 1
        
        # If no fine-grained chunks were created, fall back to paragraph chunking
        if not chunks:
            return self._fallback_pdf_extraction(content, filename, doc_id)
        
        # Update total_chunks in metadata
        for metadata in metadatas:
            metadata["total_chunks"] = len(chunks)
        
        logger.info(f"Fine-grained parsing extracted {len(chunks)} chunks from {filename}")
        return chunks, metadatas
    
    def _extract_text_fine_grained(self, content: bytes, filename: str, doc_id: str) -> Tuple[List[str], List[Dict]]:
        """
        Extract text file with fine-grained parsing, detecting Topic X-Y patterns
        Returns: (chunks, metadatas)
        """
        text = content.decode('utf-8', errors='ignore')
        
        chunks = []
        metadatas = []
        chunk_index = 0
        
        # Regex pattern to detect "Topic X-Y" format
        topic_pattern = re.compile(r'Topic\s+(\d+)-(\d+)[:\s]*(.*)', re.IGNORECASE)
        
        # Split by lines for fine-grained processing
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line contains a Topic marker
            topic_match = topic_pattern.search(line)
            
            if topic_match:
                # This is a topic line - create its own chunk
                topic_page = topic_match.group(1)
                topic_line = topic_match.group(2)
                topic_text = topic_match.group(3)
                topic_label = f"Topic {topic_page}-{topic_line}"
                
                # Create chunk with the full line
                chunks.append(line)
                metadatas.append({
                    "doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "filename": filename,
                    "content_type": "text/plain",
                    "page": int(topic_page),
                    "line": int(topic_line),
                    "topic": topic_label,
                    "is_topic": True
                })
                chunk_index += 1
            elif len(line) > 30:  # Only create chunks for substantial lines
                # Regular line
                chunks.append(line)
                metadatas.append({
                    "doc_id": doc_id,
                    "chunk_index": chunk_index,
                    "filename": filename,
                    "content_type": "text/plain",
                    "page": 0,  # Use 0 instead of None for ChromaDB compatibility
                    "line": line_num,
                    "topic": "",  # Use empty string instead of None
                    "is_topic": False
                })
                chunk_index += 1
        
        # Update total_chunks in metadata
        for metadata in metadatas:
            metadata["total_chunks"] = len(chunks)
        
        logger.info(f"Fine-grained parsing extracted {len(chunks)} chunks from {filename}")
        return chunks, metadatas
    
    def _fallback_pdf_extraction(self, content: bytes, filename: str, doc_id: str) -> Tuple[List[str], List[Dict]]:
        """Fallback to standard paragraph-based extraction"""
        text = self._extract_pdf_text(content)
        chunks = self.text_splitter.split_text(text)
        
        metadatas = [{
            "doc_id": doc_id,
            "chunk_index": i,
            "filename": filename,
            "content_type": "application/pdf",
            "total_chunks": len(chunks)
        } for i in range(len(chunks))]
        
        return chunks, metadatas
    
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