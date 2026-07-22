from pathlib import Path

from app.core.config import settings
from app.models.document import Document


class StorageService:

    @staticmethod
    def get_workspace(
        document: Document,
    ) -> Path:

        workspace = (
            Path(settings.storage_dir)
            / str(document.id)
        )

        workspace.mkdir(
            parents=True,
            exist_ok=True,
        )

        return workspace

    @staticmethod
    def get_pdf_path(
        document: Document,
    ) -> Path:

        return (
            StorageService.get_workspace(document)
            / "original.pdf"
        )

    @staticmethod
    def get_page_directory(
        document: Document,
        page_number: int,
    ) -> Path:

        page_dir = (
            StorageService.get_workspace(document)
            / f"page_{page_number}"
        )

        page_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        return page_dir

    @staticmethod
    def get_tiles_directory(
        document: Document,
        page_number: int,
    ) -> Path:

        tiles_dir = (
            StorageService.get_page_directory(
                document,
                page_number,
            )
            / "tiles"
        )

        tiles_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        return tiles_dir

    @staticmethod
    def get_excel_path(
        document: Document,
    ) -> Path:

        return (
            StorageService.get_workspace(document)
            / f"{Path(document.filename).stem}.xlsx"
        )