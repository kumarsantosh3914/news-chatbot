from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Distance, VectorParams

from app.core.config import settings
from app.schemas.message import SearchResult


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def store(self, texts: List[str], embeddings: List[np.ndarray], 
              metas: Optional[List[Dict]] = None) -> List[str]:
        """Store text chunks and their embeddings.
        
        Args:
            texts: List of text chunks to store.
            embeddings: List of embedding vectors.
            metas: Optional list of meta dicts.
            
        Returns:
            List of IDs for the stored items.
        """
        pass
        
    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Find most similar documents to query.
        
        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.
            
        Returns:
            List of search results.
        """
        pass


class QdrantStore(VectorStore):
    """Vector store implementation using Qdrant."""
    
    def __init__(self):
        """Initialize Qdrant store."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists, create if it doesn't."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
    
    def store(self, texts: List[str], embeddings: List[np.ndarray], 
              metas: Optional[List[Dict]] = None) -> List[str]:
        """Store text chunks and embeddings in Qdrant."""
        if not texts or not embeddings:
            return []
        
        if len(texts) != len(embeddings):
            raise ValueError("Number of texts and embeddings must match")
        
        if metas and len(metas) != len(texts):
            raise ValueError("Number of meta items must match texts")
        
        # Generate IDs for the points
        import uuid
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Prepare points for insertion
        points = []
        for i, (text_id, text, embedding) in enumerate(zip(ids, texts, embeddings)):
            point = qmodels.PointStruct(
                id=text_id,
                vector=embedding.tolist(),
                payload={
                    "text": text,
                    **(metas[i] if metas else {})
                }
            )
            points.append(point)
        
        # Insert points in batches
        batch_size = 100  # Adjust based on your Qdrant setup
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        return ids
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """Search for similar documents in Qdrant."""
        if query_embedding is None:
            return []
        
        try:
            # Search for similar vectors
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k
            )
            
            # Convert to SearchResult objects
            search_results = []
            for res in results:
                # Extract text and meta from payload
                payload = res.payload or {}
                text = payload.pop("text", "")
                
                search_results.append(SearchResult(
                    id=res.id,
                    text=text,
                    score=res.score,
                    meta=payload
                ))
            
            return search_results
        
        except Exception as e:
            return []


# Singleton instance
vector_store = QdrantStore()

def search_similar_articles(query: str, top_k: int = 3) -> List[dict]:
    """Search for articles similar to the query."""
    # Get query embedding from the embedding service
    from app.rag.embeddings import embedding_service
    query_vectors = embedding_service.generate_embeddings([query], mode="query")
    if not query_vectors:
        return []
    query_vector = query_vectors[0]
    
    # Search for similar articles
    return vector_store.search(query_vector, top_k=top_k)