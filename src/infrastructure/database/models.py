from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class DocumentModel(Base):
    """SQLAlchemy ORM model for storing document metadata."""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    vector_store = Column(String(50), nullable=False, default="pgvector")
    embedding_model = Column(String(100), nullable=False, default="amazon.titan-embed-text-v1")
    number_of_chunks = Column(Integer, nullable=False, default=0)
    status = Column(String(30), nullable=False, default="PROCESSING")
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to document vector chunks
    chunks = relationship(
        "DocumentChunkModel",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunkModel(Base):
    """SQLAlchemy ORM model for storing text chunks and pgvector embeddings."""

    __tablename__ = "document_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1024), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship to document metadata
    document = relationship("DocumentModel", back_populates="chunks")

    __table_args__ = (
        # HNSW Index on embedding vector column for fast cosine similarity search
        Index(
            "idx_document_embeddings_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
