from src.domain.interfaces.extractor import DocumentExtractorInterface
from src.infrastructure.extractors.pdf_extractor import PdfExtractor
from src.infrastructure.extractors.docx_extractor import DocxExtractor
from src.infrastructure.extractors.xlsx_extractor import XlsxExtractor
from src.core.exceptions import UnsupportedFileTypeError


class ExtractorFactory:
    """
    Factory Pattern class for resolving concrete DocumentExtractorInterface implementations
    based on document file extensions.
    """

    _extractors = {
        "pdf": PdfExtractor(),
        "docx": DocxExtractor(),
        "xlsx": XlsxExtractor(),
    }

    @classmethod
    def get_extractor(cls, filename: str) -> DocumentExtractorInterface:
        """
        Returns the appropriate extractor based on the file extension.
        
        :param filename: Filename string (e.g. 'report.pdf')
        :return: Concrete DocumentExtractorInterface implementation.
        """
        extension = filename.split(".")[-1].lower() if "." in filename else ""
        if extension not in cls._extractors:
            raise UnsupportedFileTypeError(
                f"Unsupported file extension '.{extension}'. Supported formats are: {list(cls._extractors.keys())}"
            )
        return cls._extractors[extension]
