from fastapi import APIRouter, Depends, Request

from app.models.user import User
from app.routes.deps import get_current_user
from app.templates.jinja import templates
from app.services.document_service import DocumentService
from app.core.database import get_session
from app.models.document import Document
from uuid import UUID
from sqlmodel import select, Session
from fastapi.responses import RedirectResponse

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

from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
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

    service = DocumentService(session)

    document, _ = service.create_document(
        user_id=current_user.id,
        file=file,
        requested_pages=pages,
    )

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