from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from pydantic import ValidationError
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
            "container_class": "card card-register",
        },
    )


@auth_route.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    service = AuthService(session)

    try:
        data = RegisterRequest(
            username=username,
            email=email,
            password=password,
        )

        user = service.register_user(data)

    except ValidationError as e:

        error = e.errors()[0]["msg"]

        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "container_class": "card card-register",
                "error": error,
                "username": username,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except ValueError as e:

        return templates.TemplateResponse(
            "auth/register.html",
            {
                "request": request,
                "container_class": "card card-register",
                "error": str(e),
                "username": username,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
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
        secure=False,
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
    request: Request,
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
        return templates.TemplateResponse(
            name="/auth/login.html",
            request=request,
            context={
                "request": request,
                "error": "Неверное имя пользователя или пароль.",
            },
            status_code=401,
        )

    token = create_access_token(user.id)

    response = RedirectResponse(
        url="/documents",
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