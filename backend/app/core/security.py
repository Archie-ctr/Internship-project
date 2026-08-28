"""Password and token primitives used by authentication routes.

This module deliberately contains no HTTP concerns. Keeping cryptographic
operations in one small, testable place helps prevent inconsistent token claims
or accidental plaintext-password handling in route handlers.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt is intentionally selected as required by the training project. The
# context owns salting and cost handling; never implement either manually.
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a one-way bcrypt hash; callers must never persist the plaintext."""
    return password_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Use bcrypt's timing-safe verification instead of comparing hashes ourselves."""
    return password_context.verify(plain_password, password_hash)


def create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    """Create a signed, expiring JWT with only the claims this API needs.

    `sub` is the stable user UUID; the email is deliberately excluded to reduce
    personally identifiable data in a token that may travel through clients.
    The server still loads the user from the database for every protected call.
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, role: str) -> str:
    return create_token(
        subject, role, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: str, role: str) -> str:
    return create_token(
        subject, role, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> dict[str, Any]:
    """Verify a JWT signature and expiry; callers translate errors to HTTP 401."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
