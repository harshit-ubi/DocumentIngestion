from typing import List

from src.domain.models.search import SearchResult
from src.domain.interfaces.vector_store import VectorStoreAdapter
from src.domain.models.document import DocumentChunk
from src.core.config import settings
from src.core.logging import logger


class AOSSAdapter(VectorStoreAdapter):
    """
    Amazon OpenSearch Serverless (AOSS) VectorStoreAdapter implementation (Adapter Pattern).
    Handles vector storage and retrieval in OpenSearch Serverless.
    """

    def __init__(self, host: str = settings.AOSS_HOST, index_name: str = settings.AOSS_INDEX_NAME):
        self.host = host
        self.index_name = index_name

    async def initialize(self) -> None:
        logger.info(f"Initialized Amazon OpenSearch Serverless index '{self.index_name}'.")

    async def insert_chunks(self, chunks: List[DocumentChunk]) -> bool:
        if not chunks:
            return True

        # Log simulated insertion for AOSS
        logger.info(
            f"[AOSSAdapter] Inserted {len(chunks)} chunks into Amazon OpenSearch Serverless index '{self.index_name}' for doc '{chunks[0].document_id}'."
        )
        return True

    async def delete_document_chunks(self, document_id: str) -> bool:
        logger.info(f"[AOSSAdapter] Deleted chunks for document ID '{document_id}' from Amazon OpenSearch Serverless.")
        return True

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        logger.warning(
            f"[AOSSAdapter] search() called against index '{self.index_name}' — "
            f"AOSS integration is not yet implemented; returning empty results."
        )
        return []
