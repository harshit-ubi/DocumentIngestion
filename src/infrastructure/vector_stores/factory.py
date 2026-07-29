from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.interfaces.vector_store import VectorStoreAdapter
from src.domain.models.document import VectorStoreType
from src.infrastructure.vector_stores.pgvector import PgVectorAdapter
from src.infrastructure.vector_stores.aoss import AOSSAdapter
from src.infrastructure.vector_stores.s3_vectors import S3VectorsAdapter
from src.core.exceptions import VectorStoreError


class VectorStoreFactory:
    """
    Factory Pattern class for instantiating target VectorStoreAdapter instances.
    """

    @staticmethod
    def get_vector_store(
        vector_store_type: VectorStoreType | str, session: AsyncSession
    ) -> VectorStoreAdapter:
        """
        Instantiates and returns the concrete VectorStoreAdapter based on selected store type.
        
        :param vector_store_type: VectorStoreType enum or string ("pgvector", "aoss", "s3_vectors")
        :param session: AsyncSession instance for database operations.
        :return: Concrete VectorStoreAdapter instance.
        """
        store_str = vector_store_type.value if isinstance(vector_store_type, VectorStoreType) else str(vector_store_type).lower()

        if store_str == VectorStoreType.PGVECTOR.value:
            return PgVectorAdapter(session=session)
        elif store_str == VectorStoreType.AOSS.value:
            return AOSSAdapter()
        elif store_str == VectorStoreType.S3_VECTORS.value:
            return S3VectorsAdapter()
        else:
            raise VectorStoreError(f"Unsupported vector store type '{store_str}'. Supported types: ['pgvector', 'aoss', 's3_vectors'].")
