from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, status, Query
from typing import Optional, List
import uuid

from src.api.schemas.ingestion import IngestionResponse, VectorStoreEnum, IngestionStatusEnum, DocumentMetadataResponse
from src.domain.models.document import DocumentMetadata, IngestionStatus, VectorStoreType
from src.infrastructure.database.connection import db_manager
from src.infrastructure.database.repository import SQLAlchemyDocumentRepository
from src.services.ingestion_service import IngestionPipelineService
from src.infrastructure.vector_stores.factory import VectorStoreFactory
from src.core.exceptions import UnsupportedFileTypeError
from src.core.logging import logger

router = APIRouter()
ingestion_pipeline = IngestionPipelineService()


@router.post(
    "/documents/ingest",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Document",
)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    vector_store: VectorStoreEnum = Form(VectorStoreEnum.PGVECTOR),
):
    """
    Accepts a document file (.pdf, .docx, .xlsx) and a target vector store.
    Enqueues processing as an asynchronous background task and returns HTTP 202.
    """
    filename = file.filename or "uploaded_document"
    extension = filename.split(".")[-1].lower() if "." in filename else ""

    if extension not in ["pdf", "docx", "xlsx"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file format '.{extension}'. Only .pdf, .docx, and .xlsx files are supported.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    document_id = str(uuid.uuid4())
    vector_store_domain = VectorStoreType(vector_store.value)

    # Save initial metadata record in PostgreSQL DB
    async with db_manager.session() as session:
        repo = SQLAlchemyDocumentRepository(session)
        metadata = DocumentMetadata(
            id=document_id,
            file_name=filename,
            file_type=extension,
            file_size=len(file_bytes),
            vector_store=vector_store_domain,
            status=IngestionStatus.PROCESSING,
        )
        await repo.create_document(metadata)

    # Dispatch asynchronous background task
    background_tasks.add_task(
        ingestion_pipeline.execute_ingestion,
        document_id=document_id,
        file_content=file_bytes,
        file_name=filename,
        vector_store_type=vector_store_domain,
    )

    logger.info(f"Dispatched background task for doc '{filename}' (ID: {document_id}).")

    return IngestionResponse(
        document_id=document_id,
        status=IngestionStatusEnum.PROCESSING,
        message=f"Document '{filename}' accepted for processing in vector store '{vector_store.value}'.",
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentMetadataResponse,
    summary="Get Document Ingestion Status",
)
async def get_document_status(document_id: str):
    """Retrieves document ingestion status and metadata by ID."""
    async with db_manager.session() as session:
        repo = SQLAlchemyDocumentRepository(session)
        doc = await repo.get_document_by_id(document_id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' was not found.",
        )

    return DocumentMetadataResponse(
        document_id=doc.id,
        file_name=doc.file_name,
        file_type=doc.file_type,
        file_size=doc.file_size,
        vector_store=VectorStoreEnum(doc.vector_store.value),
        embedding_model=doc.embedding_model,
        number_of_chunks=doc.number_of_chunks,
        status=IngestionStatusEnum(doc.status.value),
        error_message=doc.error_message,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get(
    "/documents",
    summary="List Ingested Documents",
)
async def list_documents(
    status_filter: Optional[IngestionStatusEnum] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Lists ingested documents with optional status filtering and pagination."""
    status_domain = IngestionStatus(status_filter.value) if status_filter else None

    async with db_manager.session() as session:
        repo = SQLAlchemyDocumentRepository(session)
        docs = await repo.list_documents(status=status_domain, limit=limit, offset=offset)

    return {
        "total": len(docs),
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "document_id": d.id,
                "file_name": d.file_name,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "vector_store": d.vector_store.value,
                "embedding_model": d.embedding_model,
                "number_of_chunks": d.number_of_chunks,
                "status": d.status.value,
                "error_message": d.error_message,
                "created_at": d.created_at,
                "updated_at": d.updated_at,
            }
            for d in docs
        ],
    }


@router.delete(
    "/documents/{document_id}",
    summary="Delete Document",
)
async def delete_document(document_id: str):
    """Deletes document metadata and all associated vector store chunks."""
    async with db_manager.session() as session:
        repo = SQLAlchemyDocumentRepository(session)
        doc = await repo.get_document_by_id(document_id)

        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' was not found.",
            )

        # Delete vector chunks from vector store
        vector_store = VectorStoreFactory.get_vector_store(doc.vector_store, session)
        await vector_store.delete_document_chunks(document_id)

        # Delete document record from SQL metadata repo
        await repo.delete_document(document_id)

    return {
        "document_id": document_id,
        "message": f"Document '{doc.file_name}' and all associated vector chunks deleted successfully.",
    }
