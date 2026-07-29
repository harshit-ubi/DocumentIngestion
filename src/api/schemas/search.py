from pydantic import BaseModel, Field
from typing import List
from src.api.schemas.ingestion import VectorStoreEnum


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query.")
    vector_stores: List[VectorStoreEnum] = Field(
        default=[VectorStoreEnum.PGVECTOR],
        description="Vector store(s) to search across.",
    )
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of results to return.")


class SearchResultResponse(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    chunk_text: str
    similarity_score: float
    vector_store: VectorStoreEnum


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultResponse]