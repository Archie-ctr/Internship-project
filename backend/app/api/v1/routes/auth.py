"""Registration, OAuth2 password-flow login, token refresh, and identity routes."""

from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import credentials_exception, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import CurrentUserResponse, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth")


def issue_token_pair(user: User) -> TokenResponse:
    """Use one source of truth for the claims and expirations of both tokens."""
    role_name = user.role.name
    return TokenResponse(
        access_token=create_access_token(str(user.id), role_name),
        refresh_token=create_refresh_token(str(user.id), role_name),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Create a citizen account and immediately issue a normal login token pair."""
    normalized_email = str(payload.email).lower()
    if db.scalar(select(User.id).where(User.email == normalized_email)) is not None:
        # Deliberately generic enough not to reveal any account details.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email")

    citizen_role = db.scalar(select(Role).where(Role.name == "citizen"))
    if citizen_role is None:
        # This indicates deployment/migration failure, not bad client input.
        raise HTTPException(status_code=500, detail="Required citizen role is not configured")

    user = User(
        email=normalized_email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role=citizen_role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # The unique constraint is the final defence against two simultaneous
        # registrations using the same address.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email")
    db.refresh(user)
    return issue_token_pair(user)


@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenResponse:
    """OAuth2 password-flow login; `username` contains the user's email."""
    normalized_email = form_data.username.lower()
    user = db.scalar(
        select(User).options(joinedload(User.role)).where(User.email == normalized_email)
    )
    if user is None or not user.is_active or not verify_password(form_data.password, user.password_hash):
        # One response for all failures avoids account-enumeration clues.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return issue_token_pair(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Exchange only a valid refresh token for a new access/refresh pair.

    Phase 3 uses stateless refresh tokens for clarity. A production system would
    add token-family IDs and server-side revocation to detect token reuse.
    """
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            raise credentials_exception
        user_id = UUID(token_data["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credentials_exception

    user = db.scalar(select(User).options(joinedload(User.role)).where(User.id == user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return issue_token_pair(user)


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    """Return only safe identity fields for the currently authenticated account."""
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name,
        is_active=current_user.is_active,
    )
