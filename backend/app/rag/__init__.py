from typing import AsyncGenerator, List

import numpy as np

from app.rag.embeddings import embedding_service
from app.rag.llm import llm_service
from app.rag.vector_store import vector_store


class RAGService:
    """Service for answering queries using RAG pipeline."""