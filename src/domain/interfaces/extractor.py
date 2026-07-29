from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, Any


class DocumentExtractorInterface(ABC):
    """Abstract Port Interface for Document Text Extractors."""

    @abstractmethod
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extracts raw text content from the document binary payload.
        
        :param file_content: Binary content of the document.
        :param filename: Original filename.
        :return: Cleaned extracted text string.
        """
        pass
