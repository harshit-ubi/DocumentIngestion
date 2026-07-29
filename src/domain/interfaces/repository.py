from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.document import DocumentMetadata, IngestionStatus


class DocumentRepositoryInterface(ABC):
    """Abstract Port Interface for Relational Document Metadata Repository."""

    @abstractmethod
    async def create_document(self, document: DocumentMetadata) -> DocumentMetadata:
        """Saves a new document metadata record."""
        pass

    @abstractmethod
    async def get_document_by_id(self, document_id: str) -> Optional[DocumentMetadata]:
        """Retrieves document metadata by ID."""
        pass

    @abstractmethod
    async def update_status(
        self,
        document_id: str,
        status: IngestionStatus,
        number_of_chunks: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        """Updates document processing status, chunk count, or error message."""
        pass

    @abstractmethod
    async def list_documents(
        self,
        status: Optional[IngestionStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[DocumentMetadata]:
        """Lists documents with optional status filtering and pagination."""
        pass

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Deletes document metadata by ID."""
        pass
