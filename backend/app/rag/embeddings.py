import os
from typing import List
import numpy as np
import requests

from app.core.config import settings

JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v2-base-en"
JINA_DIMENSIONS = 768

class JinaEmbeddingService:
    """Service for generating embeddings using Jina AI HTTP API."""
    def __init__(self):
        self.api_key = settings.JINA_API_KEY
        self.model = JINA_MODEL
        self.dimensions = JINA_DIMENSIONS

    def generate_embeddings(self, texts: List[str], mode: str = "passage") -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        Args:
            texts: List of text strings to embed.
            mode: 'passage' for indexing, 'query' for searching
        Returns:
            List of embedding vectors as numpy arrays.
        """
        if not texts:
            return []
        
        batch_size = 20
        all_embeddings = []
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                # Format the request according to Jina API docs
                data = {
                    "model": self.model,
                    "input": batch,
                    "task": f"retrieval.{mode}"
                }
                
                response = requests.post(JINA_API_URL, headers=headers, json=data)
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                if "data" not in result:
                    raise Exception(f"Unexpected API response format: {result}")
                
                # Extract embeddings
                batch_embeddings = []
                for item in result["data"]:
                    if "embedding" not in item:
                        raise Exception(f"Missing embedding in response: {item}")
                    batch_embeddings.append(np.array(item["embedding"]))
                
                all_embeddings.extend(batch_embeddings)
                
            except Exception as e:
                # Add zero vectors as placeholders
                all_embeddings.extend([np.zeros(self.dimensions) for _ in range(len(batch))])
        
        return all_embeddings

# Singleton instance
embedding_service = JinaEmbeddingService()