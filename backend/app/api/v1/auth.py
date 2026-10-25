"""Authentication endpoints: register, login, refresh, profile, logout."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import (
    clear_session_cookies,
    get_current_user,
    read_refresh_cookie,
    set_access_cookie,
    set_refresh_cookie,
)
from app.core.errors import AuthenticationError, ConflictError, ValidationError
from app.core.security import (
    access_token_ttl_seconds,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.rate_limit import rate_limit
from app.models.base import UserRole
from app.models.user import LegalTermsAcceptance, User
from app.schemas.auth import TokenResponse, UserLogin, UserProfile, UserRegister
from app.services.suite_service import generate_suite_code

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


def _client_ip(request: Request) -> str | None:
    """Best effort client IP, honouring the reverse proxy header."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _issue_session(response: Response, user: User) -> TokenResponse:
    """Issue both tokens as HttpOnly cookies and return the public profile."""
    set_access_cookie(response, create_access_token(
        str(user.id), email=user.email, role=user.role.value
    ))
    set_refresh_cookie(response, create_refresh_token(str(user.id)))

    return TokenResponse(
        token_type="cookie",
        expires_in=access_token_ttl_seconds(),
        user=UserProfile.model_validate(user),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new client account",
)
@rate_limit(lambda: settings.rate_limit_register)
async def register(
    request: Request,
    payload: UserRegister,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    """Create a client account, allocate its suite code and open a session."""
    if not payload.accept_terms or not payload.accept_privacy:
        raise ValidationError(
            "Both the Terms of Use and the Privacy Policy must be accepted.",
            details={
                "accept_terms": payload.accept_terms,
                "accept_privacy": payload.accept_privacy,
            },
        )

    email = payload.email.lower().strip()
    existing = await db.execute(select(User.id).where(User.email == email))
    if existing.scalar_one_or_none() is not None:
        raise ConflictError("An account with this email address already exists.")

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        phone=payload.phone,
        cpf_tax_id=payload.cpf_tax_id,
        role=UserRole.client,
        is_active=True,
        suite_code=await generate_suite_code(db),
    )
    db.add(user)

    ip_address = _client_ip(request)
    db.add_all(
        [
            LegalTermsAcceptance(
                user=user,
                term_type="terms_of_service",
                version=settings.terms_version,
                ip_address=ip_address,
            ),
            LegalTermsAcceptance(
                user=user,
                term_type="privacy_policy",
                version=settings.privacy_version,
                ip_address=ip_address,
            ),
        ]
    )

    await db.commit()
    await db.refresh(user)

    return _issue_session(response, user)


@router.post("/login", response_model=TokenResponse, summary="Authenticate")
@rate_limit(lambda: settings.rate_limit_login)
async def login(
    request: Request,
    payload: UserLogin,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    """Exchange email + password for a session cookie."""
    email = payload.email.lower().strip()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Invalid email or password.")
    if not user.is_active:
        raise AuthenticationError("User account is disabled.")

    return _issue_session(response, user)


@router.post("/refresh", response_model=TokenResponse, summary="Rotate session")
async def refresh(request: Request, response: Response, db: DbSession) -> TokenResponse:
    """Rotate both cookies using the ``refresh_token`` cookie."""
    token = read_refresh_cookie(request)
    if not token:
        raise AuthenticationError("Refresh token cookie is missing.")

    try:
        payload = decode_token(token, expected_type="refresh")
    except ValueError as exc:
        raise AuthenticationError(str(exc)) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid refresh token.") from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise AuthenticationError("User account is not available.")

    return _issue_session(response, user)


@router.get("/me", response_model=UserProfile, summary="Current user profile")
async def read_profile(
    user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """Return the profile of the authenticated user."""
    return UserProfile.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log out")
async def logout(response: Response) -> Response:
    """Clear both session cookies."""
    clear_session_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
