from sqlmodel import Session

from app.core.config import settings
from app.models.document import Document
from app.services.detectors.detector import DrawingDetector, DrawingAnalyzer
from app.services.pdf.splitter import PDFSplitter
from app.services.storage_service import StorageService
from app.services.extractors.pdf_extractor import PdfExtractor

class AnalysisService:

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def process_page(
        self,
        document: Document,
        page_number: int,
    ):

        pdf_path = StorageService.get_pdf_path(
            document
        )

        tiles_dir = StorageService.get_tiles_directory(
            document,
            page_number,
        )

        tiles = PDFSplitter.split(
            pdf_path=pdf_path,
            page_number=page_number,
            output_dir=tiles_dir,
        )

        nodes = DrawingDetector(
            model_drawing_path=settings.drawings_model_path,
            conf_drawings=settings.conf_drawings,
            imgsz=settings.imgsz,
        ).detect(
            tiles
        )

        detection_dict = DrawingAnalyzer().graph(nodes)

        extractor = PdfExtractor(
            model_doors_path=settings.doors_model_path,
            document=document,
            page_number=page_number,
        )

        try:
            result_dict = extractor.extract_params(detection_dict)
        finally:
            extractor.close()

        return result_dict