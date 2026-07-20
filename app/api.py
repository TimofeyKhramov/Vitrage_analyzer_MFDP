from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.home import home_route
from app.core.config import settings


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


@app.get("/health")
async def health():
    return {"status": "ok"}