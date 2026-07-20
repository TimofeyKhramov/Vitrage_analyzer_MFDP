from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

class LoginRequest(BaseModel):

    username: str

    password: str

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

class TokenPayload(BaseModel):

    sub: str

    exp: int

from uuid import UUID


class UserResponse(BaseModel):

    id: UUID

    username: str

    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True,
    )
