from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import create_access_token
from app.templates.jinja import templates
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

auth_route = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_route.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
            "container_class": "card card-register"
        },
    )

@auth_route.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    service = AuthService(session)

    data = RegisterRequest(
        username=username,
        email=email,
        password=password,
    )

    try:
        user = service.register_user(data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    token = create_access_token(user.id)

    response = RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,      # позже True
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return response

@auth_route.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
        },
    )

@auth_route.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    service = AuthService(session)

    user = service.authenticate_user(
        username=username,
        password=password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.id)

    response = RedirectResponse(
        url="/documents/to_form",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )

    return response

@auth_route.get("/logout")
async def logout():

    response = RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )

    response.delete_cookie("access_token")

    return response