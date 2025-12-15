"""
Knowledge Store (RAG) Adapter
Wrapper for ChromaDB and SentenceTransformers
"""

import logging
import os
from typing import List, Dict, Any, Optional
import chromadb  # pyright: ignore[reportMissingImports]
from chromadb.config import Settings  # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer  # pyright: ignore[reportMissingImports]

logger = logging.getLogger(__name__)

class KnowledgeStore:
    """
    Persistent Vector Store for Grounded Knowledge (RAG).
    
    Uses:
    - ChromaDB (Vector Database)
    - SentenceTransformers (Embedding Model)
    
    Structure:
    - Collection: "interview_knowledge"
    - Embeddings: all-MiniLM-L6-v2 (384d)
    """
    
    def __init__(self, persist_path: str = "./data/chroma_db"):
        self.persist_path = persist_path
        
        # Initialize Embedding Model (Lazy Loaded by Chroma if strictly needed, 
        # but we control it deeply here for reliability)
        self.embedding_fn = None 
        
        # Initialize Client
        try:
            self.client = chromadb.PersistentClient(path=persist_path)
            
            # Create or Get Collection
            # We use the default embedding function provided by Chroma for simplicity first,
            # or explicit sentence-transformer if customizable.
            # For stability, let's use the built-in default (SentenceTransformer) implicitly 
            # or define a custom one if needed. Chroma default is decent (all-MiniLM-L6-v2).
            self.collection = self.client.get_or_create_collection(
                name="interview_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"📚 KnowledgeStore initialized at {persist_path}")
            logger.info(f"   - Documents in store: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize KnowledgeStore: {e}")
            raise

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """
        Add texts to the vector store.
        """
        if not texts:
            return
            
        if ids is None:
            # Generate stable IDs based on content hash to avoid duplicates
            import hashlib
            ids = [hashlib.md5(t.encode()).hexdigest() for t in texts]
            
        try:
            # ChromaDB expects metadatas to be List[Dict[str, str | int | float | bool]] or None
            # Convert our Dict[str, Any] to the expected format
            chroma_metadatas = None
            if metadatas is not None:
                from typing import cast, List, Mapping, Union
                chroma_metadatas = cast(
                    List[Mapping[str, Union[str, int, float, bool]]],
                    [
                        {k: v for k, v in md.items() if isinstance(v, (str, int, float, bool))}
                        for md in metadatas
                    ]
                )
            self.collection.add(
                documents=texts,
                metadatas=chroma_metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(texts)} documents to KnowledgeStore")
        except Exception as e:
            logger.error(f"Failed to add texts: {e}")

    def search(self, query: str, k: int = 3, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where=filter_criteria
            )
            
            # Format results
            structured_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    structured_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0,
                        "id": results['ids'][0][i]
                    })
            
            return structured_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def clear(self):
        """Clear all data (Use with caution)"""
        try:
            self.client.delete_collection("interview_knowledge")
            self.collection = self.client.get_or_create_collection("interview_knowledge")
            logger.warning("⚠️ KnowledgeStore cleared")
        except Exception as e:
            logger.error(f"Failed to clear store: {e}")
