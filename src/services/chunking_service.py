from typing import List
from src.domain.models.document import DocumentChunk
import uuid


class TextChunkerService:
    """
    Text Chunking Service splitting document text into overlapping chunks.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, document_id: str, text: str) -> List[DocumentChunk]:
        """
        Recursively splits text content into overlapping chunk domain objects.
        """
        if not text or not text.strip():
            return []

        chunks: List[DocumentChunk] = []
        start = 0
        text_length = len(text)
        chunk_index = 0

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at paragraph or space boundary if not at end of text
            if end < text_length:
                break_point = text.rfind("\n", start, end)
                if break_point == -1 or break_point <= start:
                    break_point = text.rfind(" ", start, end)
                if break_point > start:
                    end = break_point

            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append(
                    DocumentChunk(
                        id=str(uuid.uuid4()),
                        document_id=document_id,
                        chunk_index=chunk_index,
                        chunk_text=chunk_content,
                    )
                )
                chunk_index += 1

            if end >= text_length:
                break

            start = end - self.chunk_overlap if end - self.chunk_overlap > start else end

        return chunks
