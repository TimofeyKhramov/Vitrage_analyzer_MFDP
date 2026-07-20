from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.document import Document

    
class User(SQLModel, table=True):

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    username: str = Field(index=True, unique=True)

    email: str = Field(index=True, unique=True)

    password_hash: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    documents: list["Document"] = Relationship(back_populates="user")