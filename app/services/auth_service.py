from uuid import UUID

from sqlmodel import Session, select

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


class AuthService:

    def __init__(self, session: Session):
        self.session = session

    def get_user_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def register_user(self, data: RegisterRequest) -> User:

        if self.get_user_by_username(data.username):
            raise ValueError("Username already exists")

        if self.get_user_by_email(data.email):
            raise ValueError("Email already exists")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> User | None:

        user = self.get_user_by_username(username)

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user
    