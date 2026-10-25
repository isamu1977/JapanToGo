"""Pydantic schemas for authentication and user profiles."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.config import settings


class UserRegister(BaseModel):
    """Payload for ``POST /api/v1/auth/register``."""

    email: EmailStr
    password: str
    full_name: str = Field(min_length=2, max_length=255)
    phone: str = Field(min_length=6, max_length=32)
    cpf_tax_id: str | None = Field(default=None, max_length=14)
    accept_terms: bool = False
    accept_privacy: bool = False

    @field_validator("full_name", "phone")
    @classmethod
    def _strip(cls, value: str) -> str:
        return value.strip()

    @field_validator("cpf_tax_id")
    @classmethod
    def _strip_cpf(cls, value: str | None) -> str | None:
        return value.strip() if value else None

    @field_validator("password")
    @classmethod
    def _check_password_complexity(cls, value: str) -> str:
        """Enforce the password policy (length + character classes)."""
        if len(value) < settings.password_min_length:
            raise ValueError(
                f"The password must have at least {settings.password_min_length} characters."
            )
        if len(value) > settings.password_max_length:
            raise ValueError(
                f"The password must have at most {settings.password_max_length} characters."
            )
        if not re.search(r"[A-Za-z]", value):
            raise ValueError("The password must contain at least one letter.")
        if not re.search(r"\d", value):
            raise ValueError("The password must contain at least one digit.")
        return value


class UserLogin(BaseModel):
    """Payload for ``POST /api/v1/auth/login``."""

    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Public representation of a user account."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    phone: str
    cpf_tax_id: str | None = None
    role: str
    suite_code: str | None = None
    is_active: bool
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    """Session response.

    The access and refresh tokens are **never** included in the payload:
    they are delivered exclusively through HttpOnly cookies so that no
    client-side script can read them.
    """

    token_type: str = "cookie"
    expires_in: int
    user: UserProfile
