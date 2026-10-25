"""Password hashing and JWT token helpers."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# passlib 1.7.4 probes ``bcrypt.__about__.__version__`` which was removed in
# bcrypt 4.1. The probe failure is harmless (the backend still loads), but it
# spams stderr on every process start, so the warning is muted.
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

#: Password hashing is delegated to Passlib with the bcrypt scheme. The
#: scheme is pinned so hashes can never silently degrade to a weaker
#: algorithm; ``argon2id`` can be added to the list later while keeping the
#: existing bcrypt hashes verifiable.
PASSWORD_SCHEMES = ["bcrypt"]

pwd_context = CryptContext(schemes=PASSWORD_SCHEMES, deprecated="auto")

TokenType = Literal["access", "refresh"]


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plain text password with Passlib (bcrypt)."""
    return pwd_context.hash(password)


def password_hash_scheme(hashed_password: str) -> str:
    """Return the Passlib scheme used by a stored hash."""
    return pwd_context.identify(hashed_password) or "unknown"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its Passlib hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        # Malformed hash - treat as a failed verification instead of a 500.
        return False


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
def _build_token(
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(
    subject: str,
    *,
    email: str | None = None,
    role: str | None = None,
    expires_minutes: int | None = None,
) -> str:
    """Create a short-lived access token."""
    minutes = expires_minutes or settings.access_token_expire_minutes
    claims: dict[str, Any] = {}
    if email:
        claims["email"] = email
    if role:
        claims["role"] = role
    return _build_token(subject, "access", timedelta(minutes=minutes), claims)


def create_refresh_token(subject: str, *, expires_days: int | None = None) -> str:
    """Create a long-lived refresh token."""
    days = expires_days or settings.refresh_token_expire_days
    return _build_token(subject, "refresh", timedelta(days=days))


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode and validate a JWT.

    Raises ``ValueError`` when the token is invalid, expired, or of an
    unexpected type.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:  # pragma: no cover - message varies by jose version
        raise ValueError(f"Invalid token: {exc}") from exc

    if expected_type is not None and payload.get("type") != expected_type:
        raise ValueError(f"Expected a {expected_type} token.")

    if not payload.get("sub"):
        raise ValueError("Token is missing the subject claim.")

    return payload


def access_token_ttl_seconds() -> int:
    """Lifetime of an access token in seconds."""
    return settings.access_token_expire_minutes * 60
