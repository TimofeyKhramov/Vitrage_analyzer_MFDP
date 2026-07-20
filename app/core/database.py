from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.drawing import Drawing
from app.models.analysis_result import AnalysisResult


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session


def init_db(recreate: bool = False) -> None:
    """
    Создание схемы базы данных.

    Args:
        recreate: удалить существующие таблицы перед созданием.
    """
    if recreate:
        SQLModel.metadata.drop_all(engine)

    SQLModel.metadata.create_all(engine)