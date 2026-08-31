from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models import User
from app.schemas.auth import normalize_email


class DuplicateEmailError(ValueError):
    pass


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        normalized_email = normalize_email(email)
        return self.db.scalar(
            select(User).where(User.email == normalized_email)
        )

    def create_user(
        self,
        *,
        email: str,
        password: str,
        display_name: str | None = None,
    ) -> User:
        normalized_email = normalize_email(email)
        if self.get_by_email(normalized_email) is not None:
            raise DuplicateEmailError("An account with this email already exists.")

        normalized_display_name = (
            display_name.strip() if display_name and display_name.strip() else None
        )
        user = User(
            email=normalized_email,
            password_hash=hash_password(password),
            display_name=normalized_display_name,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            raise DuplicateEmailError(
                "An account with this email already exists."
            ) from error

        self.db.refresh(user)
        return user

    def authenticate(self, *, email: str, password: str) -> User | None:
        user = self.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return user
