from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token
from app.db.session import get_db
from app.models import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserRead
from app.services.user_service import DuplicateEmailError, UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _authenticate_and_create_token(
    *,
    email: str,
    password: str,
    db: Session,
) -> TokenResponse:
    user = UserService(db).authenticate(email=email, password=password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(user.id))


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: UserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        return UserService(db).create_user(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
    except DuplicateEmailError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post("/login", response_model=TokenResponse)
def login_user(
    request: UserLogin,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return _authenticate_and_create_token(
        email=request.email,
        password=request.password,
        db=db,
    )


@router.post("/token", response_model=TokenResponse)
def oauth2_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return _authenticate_and_create_token(
        email=form_data.username,
        password=form_data.password,
        db=db,
    )


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
