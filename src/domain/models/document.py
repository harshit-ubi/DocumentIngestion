from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import uuid


class IngestionStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VectorStoreType(str, Enum):
    PGVECTOR = "pgvector"
    AOSS = "aoss"
    S3_VECTORS = "s3_vectors"


@dataclass
class DocumentChunk:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = ""
    chunk_index: int = 0
    chunk_text: str = ""
    embedding: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DocumentMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_name: str = ""
    file_type: str = ""
    file_size: int = 0
    vector_store: VectorStoreType = VectorStoreType.PGVECTOR
    embedding_model: str = "amazon.titan-embed-text-v1"
    number_of_chunks: int = 0
    status: IngestionStatus = IngestionStatus.PROCESSING
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    chunks: List[DocumentChunk] = field(default_factory=list)
