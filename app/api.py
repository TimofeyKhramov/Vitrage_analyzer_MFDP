from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routes.home import home_route
from app.core.config import settings
from sqlalchemy import text
from app.core.database import engine, init_db
from app.templates.jinja import templates
import logging


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing database...")

    init_db()

    logger.info("Database initialized successfully.")

    yield

    logger.info("Application stopped.")

app = FastAPI(
    title="Vitrage Analyzer",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(home_route)

@app.get("/db-health")
async def db_health():

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"database": "connected"}

@app.get("/health")
async def health():
    return {"status": "ok"}