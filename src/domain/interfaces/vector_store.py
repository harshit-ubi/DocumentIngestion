from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.models.document import DocumentChunk
from src.domain.models.search import SearchResult


class VectorStoreAdapter(ABC):
    """Abstract Port Interface for Vector Store Adapters (Adapter Pattern)."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initializes target vector store collection, index, or table if needed."""
        pass

    @abstractmethod
    async def insert_chunks(self, chunks: List[DocumentChunk]) -> bool:
        """
        Inserts document vector chunks into the vector store.
        
        :param chunks: List of DocumentChunk domain entities with embeddings.
        :return: True if insertion succeeded.
        """
        pass

    @abstractmethod
    async def delete_document_chunks(self, document_id: str) -> bool:
        """
        Deletes all vector chunks associated with a document_id.
        
        :param document_id: Target Document UUID string.
        :return: True if deletion succeeded.
        """
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """
        Searches the vector store for chunks most similar to the query embedding.

        :param query_embedding: Query vector (same dimension/model as stored embeddings).
        :param top_k: Maximum number of results to return.
        :return: List of SearchResult domain entities, ordered by similarity descending.
        """
        pass
