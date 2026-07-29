from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from src.domain.interfaces.vector_store import VectorStoreAdapter
from src.domain.models.document import DocumentChunk
from src.domain.models.search import SearchResult
from src.infrastructure.database.models import DocumentChunkModel, DocumentModel
from src.core.exceptions import VectorStoreError
from src.core.logging import logger


class PgVectorAdapter(VectorStoreAdapter):
    """
    PostgreSQL + pgvector VectorStoreAdapter implementation (Adapter Pattern).
    Stores document chunks and vector embeddings directly in PostgreSQL using pgvector.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def initialize(self) -> None:
        """Pgvector tables and indexes are managed via Alembic migrations."""
        pass

    async def insert_chunks(self, chunks: List[DocumentChunk]) -> bool:
        if not chunks:
            return True

        try:
            models = [
                DocumentChunkModel(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    embedding=chunk.embedding,
                )
                for chunk in chunks
            ]
            self.session.add_all(models)
            await self.session.flush()
            logger.info(f"Successfully inserted {len(chunks)} chunks into pgvector store for document ID '{chunks[0].document_id}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to insert chunks into pgvector: {str(e)}")
            raise VectorStoreError(f"Failed to insert chunks into pgvector store: {str(e)}")

    async def delete_document_chunks(self, document_id: str) -> bool:
        try:
            stmt = delete(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)
            result = await self.session.execute(stmt)
            logger.info(f"Deleted {result.rowcount} vector chunks from pgvector for document ID '{document_id}'.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chunks from pgvector for doc '{document_id}': {str(e)}")
            raise VectorStoreError(f"Failed to delete chunks from pgvector: {str(e)}")

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        try:
            distance = DocumentChunkModel.embedding.cosine_distance(query_embedding)
            stmt = (
                select(
                    DocumentChunkModel.id,
                    DocumentChunkModel.document_id,
                    DocumentChunkModel.chunk_text,
                    DocumentModel.file_name,
                    distance.label("distance"),
                )
                .join(DocumentModel, DocumentModel.id == DocumentChunkModel.document_id)
                .order_by(distance)
                .limit(top_k)
            )
            result = await self.session.execute(stmt)
            rows = result.all()

            return [
                SearchResult(
                    chunk_id=row.id,
                    document_id=row.document_id,
                    file_name=row.file_name,
                    chunk_text=row.chunk_text,
                    similarity_score=round(1 - row.distance, 6),
                    vector_store="pgvector",
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to search pgvector store: {str(e)}")
            raise VectorStoreError(f"Failed to search pgvector store: {str(e)}")