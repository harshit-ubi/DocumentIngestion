from abc import ABC, abstractmethod
from typing import List


class EmbeddingProviderInterface(ABC):
    """Abstract Port Interface for Vector Embedding Generators."""

    @abstractmethod
    def generate_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of text chunks.
        
        :param text_chunks: List of string text chunks.
        :return: List of vector embeddings (lists of floats).
        """
        pass
