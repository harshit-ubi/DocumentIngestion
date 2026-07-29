from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from src.domain.interfaces.repository import DocumentRepositoryInterface
from src.domain.models.document import DocumentMetadata, IngestionStatus, VectorStoreType
from src.infrastructure.database.models import DocumentModel


class SQLAlchemyDocumentRepository(DocumentRepositoryInterface):
    """SQLAlchemy implementation of DocumentRepositoryInterface."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, document: DocumentMetadata) -> DocumentMetadata:
        model = DocumentModel(
            id=document.id,
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            vector_store=document.vector_store.value if isinstance(document.vector_store, VectorStoreType) else str(document.vector_store),
            embedding_model=document.embedding_model,
            number_of_chunks=document.number_of_chunks,
            status=document.status.value if isinstance(document.status, IngestionStatus) else str(document.status),
            error_message=document.error_message,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def get_document_by_id(self, document_id: str) -> Optional[DocumentMetadata]:
        stmt = select(DocumentModel).where(DocumentModel.id == document_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_status(
        self,
        document_id: str,
        status: IngestionStatus,
        number_of_chunks: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        stmt = (
            update(DocumentModel)
            .where(DocumentModel.id == document_id)
            .values(
                status=status.value if isinstance(status, IngestionStatus) else str(status),
                number_of_chunks=number_of_chunks,
                error_message=error_message,
                updated_at=func.now(),
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def list_documents(
        self,
        status: Optional[IngestionStatus] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[DocumentMetadata]:
        stmt = select(DocumentModel)
        if status:
            stmt = stmt.where(DocumentModel.status == (status.value if isinstance(status, IngestionStatus) else str(status)))
        stmt = stmt.order_by(DocumentModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def delete_document(self, document_id: str) -> bool:
        stmt = delete(DocumentModel).where(DocumentModel.id == document_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    def _to_domain(self, model: DocumentModel) -> DocumentMetadata:
        return DocumentMetadata(
            id=model.id,
            file_name=model.file_name,
            file_type=model.file_type,
            file_size=model.file_size,
            vector_store=VectorStoreType(model.vector_store),
            embedding_model=model.embedding_model,
            number_of_chunks=model.number_of_chunks,
            status=IngestionStatus(model.status),
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
