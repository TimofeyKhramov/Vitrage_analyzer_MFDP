from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.drawing import Drawing

class AnalysisResult(SQLModel, table=True):

    __tablename__ = "analysis_results"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str

    quantity: int

    width: float

    height: float

    doors_count: int

    drawing_id: UUID = Field(foreign_key="drawings.id", ondelete="CASCADE")

    drawing: "Drawing" = Relationship(
        back_populates="analysis_results"
    )