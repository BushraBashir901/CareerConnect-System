"""RAG (Retrieval-Augmented Generation) schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class RetrievalRequest(BaseModel):
    """Request for document retrieval."""
    query: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    max_results: Optional[int] = 5
    min_score: Optional[float] = 0.7


class RetrievedDocument(BaseModel):
    """A single retrieved document."""
    content: str
    source: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class RetrievalResponse(BaseModel):
    """Response from document retrieval."""
    context_text: str
    retrieved_documents: List[RetrievedDocument]
    total_results: int
    query_time: Optional[float] = None
