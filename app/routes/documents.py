from fastapi import APIRouter, Depends, Request

from app.models.user import User
from app.routes.deps import get_current_user
from app.templates.jinja import templates
from uuid import UUID

from sqlmodel import select


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


@documents_router.get("/to_form")
async def upload_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "current_user": current_user,
            "container_class": "card card-lg",
        },
    )


@documents_router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    pages: str = Form(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        return templates.TemplateResponse(
            "documents/upload.html",
            {
                "request": request,
                "current_user": current_user,
                "container_class": "card card-lg",
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
    document = session.exec(
        select(Document).where(Document.id == document_id)
    ).first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден.",
        )

    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к документу.",
        )

    return templates.TemplateResponse(
        "documents/document.html",
        {
            "request": request,
            "document": document,
            "container_class": "card card-md",
        },
    )