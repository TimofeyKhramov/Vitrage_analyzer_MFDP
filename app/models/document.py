from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.drawing import Drawing
    from app.models.analysis_result import AnalysisResult


class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Document(SQLModel, table=True):

    __tablename__ = "documents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    filename: str

    filepath: str

    pages: int

    status: DocumentStatus = Field(default=DocumentStatus.uploaded)

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")

    user: Optional["User"] = Relationship(back_populates="documents")

    drawings: list["Drawing"] = Relationship(
    back_populates="document", cascade_delete=True
)
