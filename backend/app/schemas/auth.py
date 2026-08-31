from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_email(email: str) -> str:
    return email.strip().lower()


class EmailSchema(BaseModel):
    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def normalize_email_field(cls, value: str) -> str:
        normalized = normalize_email(value)
        if not normalized:
            raise ValueError("Email must not be blank.")
        return normalized


class UserCreate(EmailSchema):
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class UserLogin(EmailSchema):
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    display_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
