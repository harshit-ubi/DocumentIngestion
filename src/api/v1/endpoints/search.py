from fastapi import APIRouter
from src.api.schemas.search import SearchRequest, SearchResponse, SearchResultResponse
from src.api.schemas.ingestion import VectorStoreEnum
from src.domain.models.document import VectorStoreType
from src.infrastructure.database.connection import db_manager
from src.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic Search Across Vector Stores",
)
async def search_documents(request: SearchRequest):
    """
    Converts the query into an embedding and searches one or more vector stores
    for the most semantically similar document chunks.
    """
    vector_store_types = [VectorStoreType(vs.value) for vs in request.vector_stores]

    async with db_manager.session() as session:
        results = await search_service.search(
            query=request.query,
            vector_store_types=vector_store_types,
            top_k=request.top_k,
            session=session,
        )

    return SearchResponse(
        query=request.query,
        total_results=len(results),
        results=[
            SearchResultResponse(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                file_name=r.file_name,
                chunk_text=r.chunk_text,
                similarity_score=r.similarity_score,
                vector_store=VectorStoreEnum(r.vector_store),
            )
            for r in results
        ],
    )
