from typing import Optional
from src.domain.models.document import DocumentMetadata, IngestionStatus, VectorStoreType
from src.infrastructure.database.connection import db_manager
from src.infrastructure.database.repository import SQLAlchemyDocumentRepository
from src.infrastructure.extractors.factory import ExtractorFactory
from src.infrastructure.embedders.bedrock_embedder import BedrockEmbeddingAdapter
from src.infrastructure.vector_stores.factory import VectorStoreFactory
from src.services.chunking_service import TextChunkerService
from src.core.logging import logger


class IngestionPipelineService:
    """
    Orchestration Pipeline Service for Document Ingestion (Application Service).
    Executed asynchronously by FastAPI BackgroundTasks worker.
    """

    def __init__(
        self,
        embedder: Optional[BedrockEmbeddingAdapter] = None,
        chunker: Optional[TextChunkerService] = None,
    ):
        self.embedder = embedder or BedrockEmbeddingAdapter()
        self.chunker = chunker or TextChunkerService()

    async def execute_ingestion(
        self,
        document_id: str,
        file_content: bytes,
        file_name: str,
        vector_store_type: VectorStoreType,
    ) -> None:
        """
        Executes the full asynchronous document ingestion workflow:
        1. Text Extraction (PDF/DOCX/XLSX)
        2. Text Chunking
        3. Bedrock Vector Embedding Generation
        4. Vector Store Insertion (pgvector/AOSS/S3 Vectors)
        5. Update Document Status in PostgreSQL DB
        """
        logger.info(f"Starting background ingestion for document '{file_name}' (ID: {document_id}).")

        async with db_manager.session() as session:
            repository = SQLAlchemyDocumentRepository(session)

            try:
                # Step 1: Text Extraction
                extractor = ExtractorFactory.get_extractor(file_name)
                extracted_text = extractor.extract_text(file_content, file_name)

                # Step 2: Text Chunking
                chunks = self.chunker.chunk_text(document_id, extracted_text)
                if not chunks:
                    raise ValueError(f"No valid text chunks generated for document '{file_name}'.")

                logger.info(f"Generated {len(chunks)} text chunks for document ID '{document_id}'.")

                # Step 3: Bedrock Embedding Generation
                chunk_texts = [c.chunk_text for c in chunks]
                embeddings = self.embedder.generate_embeddings(chunk_texts)

                for chunk, embedding in zip(chunks, embeddings):
                    chunk.embedding = embedding

                # Step 4: Vector Store Insertion
                vector_store = VectorStoreFactory.get_vector_store(vector_store_type, session)
                await vector_store.initialize()
                await vector_store.insert_chunks(chunks)

                # Step 5: Update Document Metadata Status to COMPLETED
                await repository.update_status(
                    document_id=document_id,
                    status=IngestionStatus.COMPLETED,
                    number_of_chunks=len(chunks),
                )
                logger.info(f"Document ingestion COMPLETED successfully for ID '{document_id}'.")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Document ingestion FAILED for ID '{document_id}': {error_msg}")
                await repository.update_status(
                    document_id=document_id,
                    status=IngestionStatus.FAILED,
                    error_message=error_msg,
                )
