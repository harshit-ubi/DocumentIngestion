"""change_embedding_dimension_to_1024

Revision ID: 74132c3e8e19
Revises: '81dc768eedb4'
Create Date: 2026-07-30 07:38:05.643638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74132c3e8e19'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_document_embeddings_hnsw;")
    op.execute("TRUNCATE TABLE document_embeddings;")
    op.execute("ALTER TABLE document_embeddings ALTER COLUMN embedding TYPE vector(1024) USING embedding::vector(1024);")
    op.execute("""
        CREATE INDEX idx_document_embeddings_hnsw 
        ON document_embeddings 
        USING hnsw (embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 64);
    """)

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_document_embeddings_hnsw;")
    op.execute("ALTER TABLE document_embeddings ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536);")
    op.execute("""
        CREATE INDEX idx_document_embeddings_hnsw 
        ON document_embeddings 
        USING hnsw (embedding vector_cosine_ops) 
        WITH (m = 16, ef_construction = 64);
    """)
