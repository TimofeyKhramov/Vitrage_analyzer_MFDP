from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import AuthService

UNAUTHORIZED_REDIRECT = HTTPException(
    status_code=status.HTTP_303_SEE_OTHER,
    headers={"Location": "/auth/login"},
)

async def get_current_user(
    access_token: str | None = Cookie(default=None),
    session: Session = Depends(get_session),
) -> User:
    """
    Возвращает текущего авторизованного пользователя.

    JWT хранится в HttpOnly Cookie с именем `access_token`.
    """

    if access_token is None:
        raise UNAUTHORIZED_REDIRECT

    try:
        payload = decode_access_token(access_token)
        user_id = UUID(payload["sub"])

    except (JWTError, ValueError, KeyError):
        raise UNAUTHORIZED_REDIRECT

    service = AuthService(session)

    user = service.get_user_by_id(user_id)

    if user is None:
        raise UNAUTHORIZED_REDIRECT

    return user