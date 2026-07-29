from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class VectorStoreEnum(str, Enum):
    PGVECTOR = "pgvector"
    AOSS = "aoss"
    S3_VECTORS = "s3_vectors"


class IngestionStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IngestionResponse(BaseModel):
    document_id: str
    status: IngestionStatusEnum
    message: str


class DocumentMetadataResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    file_size: int
    vector_store: VectorStoreEnum
    embedding_model: str
    number_of_chunks: int = 0
    status: IngestionStatusEnum
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
