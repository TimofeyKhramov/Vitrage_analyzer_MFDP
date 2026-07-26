# from fastapi import APIRouter

# from app.schemas import OcrRequest
# from app.ocr_service import OcrService

# router = APIRouter()

# service = OcrService()


# @router.post("/drawing")
# def drawing(
#     request: OcrRequest,
# ):

#     return service.extract_drawing(
#         request.image,
#     )


# @router.post("/name")
# def name(
#     request: OcrRequest,
# ):

#     return service.extract_name(
#         request.image,
#     )


# @router.post("/amount")
# def amount(
#     request: OcrRequest,
# ):

#     return service.extract_amount(
#         request.image,
#     )

from fastapi import APIRouter, Request

from app.schemas import OcrRequest
import base64


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


@router.post("/drawing/file")
async def drawing_file(
    request: Request,
    file: UploadFile = File(...),
):
    service = request.app.state.ocr_service

    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    return service.extract_drawing(image_b64)


@router.post("/name/file")
async def name_file(
    request: Request,
    file: UploadFile = File(...),
):
    service = request.app.state.ocr_service

    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    return service.extract_name(image_b64)


@router.post("/amount/file")
async def amount_file(
    request: Request,
    file: UploadFile = File(...),
):
    service = request.app.state.ocr_service

    image_bytes = await file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    return service.extract_amount(image_b64)