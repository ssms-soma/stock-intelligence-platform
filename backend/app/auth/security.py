from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings


password_hasher = PasswordHash.recommended()


class AuthConfigurationError(RuntimeError):
    pass


class InvalidAccessTokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password, password_hash)
    except (TypeError, ValueError):
        return False


def _get_jwt_secret() -> str:
    if not settings.jwt_secret_key:
        raise AuthConfigurationError(
            "JWT_SECRET_KEY is required to create or validate access tokens."
        )
    return settings.jwt_secret_key


def create_access_token(
    user_id: int,
    *,
    now: datetime | None = None,
) -> str:
    issued_at = now or datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        _get_jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, TypeError, ValueError) as error:
        raise InvalidAccessTokenError("Invalid access token.") from error

    if user_id <= 0:
        raise InvalidAccessTokenError("Invalid access token subject.")
    return user_id
