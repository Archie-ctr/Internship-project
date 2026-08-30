"""Password and token primitives used by authentication routes.

This module deliberately contains no HTTP concerns. Keeping cryptographic
operations in one small, testable place helps prevent inconsistent token claims
or accidental plaintext-password handling in route handlers.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

# bcrypt is intentionally selected as required by the training project.
# We call the bcrypt library directly instead of through passlib because
# passlib's bcrypt backend has a known compatibility issue with Python 3.13
# and bcrypt >= 4.x that raises ValueError on its internal self-test.
_BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    """Return a bcrypt hash string; callers must never persist the plaintext."""
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=_BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Use bcrypt's constant-time checkpw to prevent timing attacks."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


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
