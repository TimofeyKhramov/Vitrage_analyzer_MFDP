from pathlib import Path
from shutil import copyfileobj
from uuid import UUID, uuid4
import shutil
import fitz
from fastapi import UploadFile
from sqlmodel import Session

from app.models.document import Document, DocumentStatus

from app.core.rabbitmq import RabbitMQClient

class DocumentService:

    def __init__(
        self,
        session: Session,
        processing_dir: str = "storage/processing",
    ):
        self.session = session

        self.processing_dir = Path(processing_dir)

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

        workspace = self.processing_dir / str(document_id)

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
    requested_pages: str
    ) -> tuple[Document, Path]:

        temp_path = self.processing_dir / f"{uuid4()}.pdf"

        with temp_path.open("wb") as buffer:
            copyfileobj(file.file, buffer)

        pages = self.get_pages_count(temp_path)

        document = Document(
            source_filename=file.filename,
            pages=pages,
            status=DocumentStatus.uploaded,
            user_id=user_id,
            requested_pages=requested_pages
        )

    

        self.session.add(document)

        self.session.commit()

        self.session.refresh(document)

        workspace = self.create_workspace(document.id)
        file.file.seek(0)
        pdf_path = self.save_pdf(
            workspace,
            file,
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
        ) -> None:

        document.status = DocumentStatus.queued

        self.session.add(document)

        self.session.commit()

        client = RabbitMQClient()

        try:
            client.publish_document(document.id)
        finally:
            client.close()


    