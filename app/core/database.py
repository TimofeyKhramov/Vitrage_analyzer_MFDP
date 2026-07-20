from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session


def create_database():
    SQLModel.metadata.create_all(engine)