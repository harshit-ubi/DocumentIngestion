from dataclasses import dataclass


@dataclass
class SearchResult:
    chunk_id: str
    document_id: str
    file_name: str
    chunk_text: str
    similarity_score: float
    vector_store: str