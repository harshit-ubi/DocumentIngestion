class BaseAppException(Exception):
    """Base exception class for Document Ingestion platform."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UnsupportedFileTypeError(BaseAppException):
    """Raised when an unsupported file type is uploaded."""
    pass


class ExtractionError(BaseAppException):
    """Raised when text extraction fails for a document."""
    pass


class EmbeddingGenerationError(BaseAppException):
    """Raised when vector embedding generation fails."""
    pass


class VectorStoreError(BaseAppException):
    """Raised when an operation on a vector store fails."""
    pass


class DocumentNotFoundError(BaseAppException):
    """Raised when a requested document ID does not exist."""
    pass
