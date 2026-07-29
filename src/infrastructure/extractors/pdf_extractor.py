import io
from pypdf import PdfReader
from src.domain.interfaces.extractor import DocumentExtractorInterface
from src.core.exceptions import ExtractionError
from src.core.logging import logger


class PdfExtractor(DocumentExtractorInterface):
    """PDF Document Extractor using PyPDF."""

    def extract_text(self, file_content: bytes, filename: str) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)
            extracted_pages = []

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    extracted_pages.append(f"--- Page {i + 1} ---\n{page_text.strip()}")

            if not extracted_pages:
                raise ExtractionError(f"No extractable text content found in PDF '{filename}'.")

            logger.info(f"Successfully extracted {len(extracted_pages)} pages from PDF '{filename}'.")
            return "\n\n".join(extracted_pages)
        except Exception as e:
            logger.error(f"Failed to extract text from PDF '{filename}': {str(e)}")
            raise ExtractionError(f"Failed to extract text from PDF '{filename}': {str(e)}")
