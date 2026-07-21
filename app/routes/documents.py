from pathlib import Path
from app.services.page_range_parser import PageRangeParser
from fastapi import APIRouter, Depends, File, Form, Request, HTTPException, status, UploadFile
from fastapi.responses import RedirectResponse
from app.models.user import User
from app.routes.deps import get_current_user
from app.templates.jinja import templates
from app.services.document_service import DocumentService
from app.core.database import get_session
from app.models.document import Document
from uuid import UUID
from sqlmodel import select, Session
import logging

logger = logging.getLogger(__name__)
documents_router = APIRouter(prefix="/documents")

@documents_router.get("/upload")
async def upload_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "current_user": current_user,
            "container_class": "card card-upload"
        },
    )

documents_router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@documents_router.get("/form")
async def upload_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "current_user": current_user,
            "container_class": "card card-upload",
        },
    )


@documents_router.post("/form")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    pages: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    print(0)
    if file.content_type != "application/pdf":
        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "current_user": current_user,
                "container_class": "card card-upload",
                "error": "Можно загрузить только PDF-файл.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    print(1)
    service = DocumentService(session)
    print(2)
    document, pdf_path = service.create_document(
        user_id=current_user.id,
        file=file,
        requested_pages=pages,
    )
    logger.info(3)
    try:
        selected_pages = PageRangeParser.parse(
            pages=pages,
            max_page=document.pages,
        )
    except ValueError as e:

        service.delete_document(document)

        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "current_user": current_user,
                "container_class": "card card-upload",
                "error": str(e),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    print(4)
    return RedirectResponse(
        url=f"/documents/{document.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )

@documents_router.get("/{document_id}")
async def document_page(
    document_id: UUID,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(session)

    document = service.get_document(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return templates.TemplateResponse(
        "documents/document.html",
        {
            "request": request,
            "document": document,
            "container_class": "card card-upload",
        },
    )