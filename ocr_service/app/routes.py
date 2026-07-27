from fastapi import APIRouter, Request
from app.schemas import OcrRequest


router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "ok",
    }


@router.post("/drawing")
def drawing(
    request: Request,
    body: OcrRequest,
):

    service = request.app.state.ocr_service

    return service.extract_drawing(
        body.image,
    )


@router.post("/name")
def name(
    request: Request,
    body: OcrRequest,
):

    service = request.app.state.ocr_service

    return service.extract_name(
        body.image,
    )


@router.post("/amount")
def amount(
    request: Request,
    body: OcrRequest,
):

    service = request.app.state.ocr_service

    return service.extract_amount(
        body.image,
    )
