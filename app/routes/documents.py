from fastapi import APIRouter, Depends, Request

from app.models.user import User
from app.routes.deps import get_current_user
from app.core.templates import templates

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
        },
    )