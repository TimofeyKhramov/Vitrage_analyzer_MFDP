from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.analysis_result import AnalysisResult


class Drawing(SQLModel, table=True):

    __tablename__ = "drawings"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            "drawing_number",
            name="uq_document_page_drawing",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    document_id: UUID = Field(foreign_key="documents.id", ondelete="CASCADE")

    page_number: int

    drawing_number: int

    document: "Document" = Relationship(back_populates="drawings")

    analysis_results: list["AnalysisResult"] = Relationship(
        back_populates="drawing", cascade_delete=True
    )