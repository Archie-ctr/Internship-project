"""Reusable FastAPI dependencies for identity and role enforcement."""

from collections.abc import Callable
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# This tells Swagger UI and OAuth2 clients where the password-flow token route
# lives. It does not itself authenticate anyone.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Validate an access token, then reload the active user from PostgreSQL.

    The database lookup is important: a token alone must not keep working after
    an administrator disables an account or changes its role.
    """
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = db.scalar(select(User).options(joinedload(User.role)).where(User.id == user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed_roles: str) -> Callable[..., User]:
    """Return a dependency that denies access unless the database role matches.

    Example: `Depends(require_role("officer", "admin"))`. This is deliberately
    applied per protected route in later phases, never trusted to the UI alone.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
