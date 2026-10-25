"""Authentication, session cookies and role based access control dependencies."""

from __future__ import annotations

from typing import Annotated, Any, Sequence, TypeVar

from fastapi import Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Load

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import (
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.security import decode_token
from app.models.base import UserRole
from app.models.user import User

DbSession = Annotated[AsyncSession, Depends(get_db)]

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Session cookies
# ---------------------------------------------------------------------------
def _set_cookie(response: Response, name: str, value: str, max_age: int) -> None:
    """Set an HttpOnly session cookie."""
    response.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )


def _delete_cookie(response: Response, name: str) -> None:
    response.delete_cookie(
        key=name,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        path="/",
    )


def set_access_cookie(response: Response, token: str) -> None:
    """Store the access token in an HttpOnly cookie."""
    _set_cookie(
        response,
        settings.access_token_cookie_name,
        token,
        settings.access_token_expire_minutes * 60,
    )


def set_refresh_cookie(response: Response, token: str) -> None:
    """Store the refresh token in an HttpOnly cookie."""
    _set_cookie(
        response,
        settings.refresh_token_cookie_name,
        token,
        settings.refresh_token_expire_days * 24 * 60 * 60,
    )


def clear_session_cookies(response: Response) -> None:
    """Remove both session cookies."""
    _delete_cookie(response, settings.access_token_cookie_name)
    _delete_cookie(response, settings.refresh_token_cookie_name)


def read_access_cookie(request: Request) -> str | None:
    """Read the access token from its HttpOnly cookie."""
    return request.cookies.get(settings.access_token_cookie_name)


def read_refresh_cookie(request: Request) -> str | None:
    """Read the refresh token from its HttpOnly cookie."""
    return request.cookies.get(settings.refresh_token_cookie_name)


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------
async def get_current_user(request: Request, db: DbSession) -> User:
    """Resolve the authenticated user from the ``access_token`` cookie.

    The token is never exposed to JavaScript: it lives exclusively in an
    HttpOnly cookie, so it cannot be exfiltrated by an XSS payload.
    """
    token = read_access_cookie(request)
    if not token:
        raise AuthenticationError("Authentication cookie is missing.")

    try:
        payload = decode_token(token, expected_type="access")
    except ValueError as exc:
        raise AuthenticationError(str(exc)) from exc

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User account no longer exists.")
    if not user.is_active:
        raise AuthenticationError("User account is disabled.")

    return user


async def require_client(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Allow only users with the ``client`` role."""
    if user.role != UserRole.client:
        raise PermissionDeniedError("This endpoint is restricted to clients.")
    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Allow only users with the ``admin`` role."""
    if user.role != UserRole.admin:
        raise PermissionDeniedError("This endpoint is restricted to administrators.")
    return user


# ---------------------------------------------------------------------------
# Ownership (IDOR prevention)
# ---------------------------------------------------------------------------
async def fetch_owned(
    db: AsyncSession,
    model: type[T],
    resource_id: Any,
    user_id: Any,
    *,
    options: Sequence[Load] | None = None,
    not_found_message: str = "Resource not found.",
) -> T:
    """Fetch a resource that must belong to ``user_id``.

    The query is always scoped with ``WHERE id = :id AND user_id = :user_id`` so
    a cross-user request can never load foreign rows. When the scoped lookup
    misses but the resource exists, the caller is told it is forbidden (HTTP
    403) instead of a plain 404, so the access attempt is explicit while
    unrelated identifiers still return "not found".
    """
    statement = select(model).where(model.id == resource_id, model.user_id == user_id)
    if options:
        statement = statement.options(*options)

    result = await db.execute(statement)
    resource = result.scalar_one_or_none()
    if resource is not None:
        return resource

    exists = await db.execute(select(model.id).where(model.id == resource_id))
    if exists.scalar_one_or_none() is not None:
        raise PermissionDeniedError("You do not have access to this resource.")

    raise NotFoundError(not_found_message)
