from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.document import VectorStoreType
from src.domain.models.search import SearchResult
from src.infrastructure.embedders.bedrock_embedder import BedrockEmbeddingAdapter
from src.infrastructure.vector_stores.factory import VectorStoreFactory
from src.core.logging import logger


class SearchService:
    """
    Orchestrates semantic search: embeds the query once, fans out to each
    requested vector store adapter, merges and re-ranks results by similarity.
    """

    def __init__(self, embedder: BedrockEmbeddingAdapter | None = None):
        self.embedder = embedder or BedrockEmbeddingAdapter()

    async def search(
        self,
        query: str,
        vector_store_types: List[VectorStoreType],
        top_k: int,
        session: AsyncSession,
    ) -> List[SearchResult]:
        query_embedding = self.embedder.generate_embeddings([query])[0]

        all_results: List[SearchResult] = []
        for vs_type in vector_store_types:
            adapter = VectorStoreFactory.get_vector_store(vs_type, session)
            store_results = await adapter.search(query_embedding, top_k)
            all_results.extend(store_results)

        all_results.sort(key=lambda r: r.similarity_score, reverse=True)
        logger.info(
            f"Search for query '{query[:50]}...' returned {len(all_results)} "
            f"raw results across {len(vector_store_types)} store(s), truncating to top_k={top_k}."
        )
        return all_results[:top_k]