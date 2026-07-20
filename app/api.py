from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.home import home_route
from app.core.config import settings
from sqlalchemy import text

from app.core.database import engine

app = FastAPI(
    title="Vitrage Analyzer",
    version="1.0.0",
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