from pathlib import Path
from shutil import copyfileobj
from uuid import UUID, uuid4
import shutil
import fitz
from fastapi import UploadFile
from sqlmodel import Session
from shutil import copy2
from app.core.config import settings
from urllib.parse import quote
from app.models.document import Document, DocumentStatus
from app.models.analysis_result import AnalysisResult
from app.models.drawing import Drawing

from app.core.rabbitmq import RabbitMQClient

from app.services.pdf.splitter import PDFSplitter

from app.services.storage_service import StorageService

from collections import defaultdict

from sqlmodel import select

from fastapi.responses import StreamingResponse

from app.services.excel_exporter import ExcelExporter


class DocumentService:

    def __init__(
        self,
        session: Session,
        processing_dir: str | Path | None = None,
    ):
        self.session = session

        self.processing_dir = (
            Path(processing_dir)
            if processing_dir is not None
            else settings.storage_dir
        )

        self.processing_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def get_pages_count(pdf_path: Path) -> int:
        """
        Возвращает количество страниц PDF.
        """

        with fitz.open(pdf_path) as pdf:
            return pdf.page_count
    
    def create_workspace(
    self,
    document_id: UUID,
    ) -> Path:

        workspace = settings.storage_dir / str(document_id)

        workspace.mkdir(
            parents=True,
            exist_ok=True,
        )

        return workspace

    def save_pdf(
    self,
    workspace: Path,
    file: UploadFile,
    ) -> Path:

        pdf_path = workspace / "original.pdf"

        with pdf_path.open("wb") as buffer:

            copyfileobj(
                file.file,
                buffer,
            )

        return pdf_path
    
    def get_document(
    self,
    document_id: UUID,
        ) -> Document | None:
        return self.session.get(
        Document,
        document_id,
        )
    
    def create_document(
    self,
    user_id: UUID,
    file: UploadFile,
    requested_pages: str,
        ) -> Document:

        temp_path = self.processing_dir / f"{uuid4()}.pdf"

        with temp_path.open("wb") as buffer:
            copyfileobj(file.file, buffer)

        pages = self.get_pages_count(temp_path)

        document = Document(
            source_filename=file.filename,
            pages=pages,
            status=DocumentStatus.uploaded,
            user_id=user_id,
            requested_pages=requested_pages,
        )

        self.session.add(document)
        self.session.commit()
        self.session.refresh(document)

        workspace = StorageService.get_workspace(document)

        pdf_path = StorageService.get_pdf_path(document)

        copy2(
            temp_path,
            pdf_path,
        )

        temp_path.unlink()

        return document, pdf_path
    
    def delete_document(
            self,
            document: Document,
        ) -> None:

            self.remove_workspace(document.id)

            self.session.delete(document)

            self.session.commit()

    def remove_workspace(
    self,
    document_id: UUID,
    ):

        workspace = self.processing_dir / str(document_id)

        if workspace.exists():

            shutil.rmtree(workspace)

    def queue_document(
        self,
        document: Document,
        selected_pages: list[int],
    ) -> None:

        document.status = DocumentStatus.queued

        self.session.add(document)
        self.session.commit()

        client = RabbitMQClient()

        try:
            client.publish_document(
                document_id=document.id,
                selected_pages=selected_pages,
            )
        finally:
            client.close()


    def get_document_results(
        self,
        document_id: UUID,
    ) -> list[dict]:

        statement = (
            select(
                Drawing,
                AnalysisResult,
            )
            .join(
                AnalysisResult,
            )
            .where(
                Drawing.document_id == document_id,
            )
            .order_by(
                Drawing.page_number,
                Drawing.drawing_number,
            )
        )

        rows = self.session.exec(statement).all()

        pages = defaultdict(list)

        for drawing, result in rows:

            pages[drawing.page_number].append(
                {
                    "drawing_number": drawing.drawing_number,
                    "name": result.name,
                    "amount": result.quantity,
                    "width": result.width,
                    "height": result.height,
                    "doors_count": result.doors_count,
                }
            )

        return [
            {
                "page": page,
                "drawings": drawings,
            }
            for page, drawings in pages.items()
        ]


    def get_user_documents(
    self,
    user_id: UUID,
    ):

        statement = (
            select(Document)
            .where(
                Document.user_id == user_id,
            )
            .order_by(
                Document.uploaded_at.desc(),
            )
        )

        return self.session.exec(statement).all()
    
    def download_excel(
    self,
    document_id: UUID,
):

        document = self.get_document(
            document_id,
        )

        if document is None:

            raise ValueError(
                "Document not found",
            )

        excel = ExcelExporter(
            self.session,
        ).export(
            document,
        )

        filename = (
            document.source_filename.removesuffix(".pdf")
            + ".xlsx"
        )

        headers = {
            "Content-Disposition":
                f"attachment; filename*=UTF-8''{quote(filename)}"
        }

        return StreamingResponse(
                excel,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers=headers,
            )