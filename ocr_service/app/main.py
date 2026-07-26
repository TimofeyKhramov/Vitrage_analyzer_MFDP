from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes import router
from app.ocr_service import OcrService


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.ocr_service = OcrService()

    yield


app = FastAPI(
    lifespan=lifespan,
)

app.include_router(router)