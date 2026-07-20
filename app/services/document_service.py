from pathlib import Path
from shutil import copyfileobj
from uuid import UUID, uuid4
import shutil
import fitz
from fastapi import UploadFile
from sqlmodel import Session

from app.models.document import Document, DocumentStatus

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
        )

        self.session.add(document)

        self.session.commit()

        self.session.refresh(document)

        workspace = self.create_workspace(document.id)

        pdf_path = self.save_pdf(
            workspace,
            file,
        )

        temp_path.unlink()

        return document, pdf_path

    def remove_workspace(
    self,
    document_id: UUID,
    ):

        workspace = self.processing_dir / str(document_id)

        if workspace.exists():

            shutil.rmtree(workspace)


    