from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Ingestion Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # PostgreSQL Relational Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/document_ingestion_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgrespassword@localhost:5432/document_ingestion_db"

    # AWS Credentials & Bedrock
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v1"

    # Default Vector Store Selection
    DEFAULT_VECTOR_STORE: str = "pgvector"

    # OpenSearch Serverless (AOSS) Config
    AOSS_HOST: Optional[str] = None
    AOSS_INDEX_NAME: str = "document-embeddings"

    # AWS S3 Vector Store Config
    S3_VECTOR_BUCKET: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
