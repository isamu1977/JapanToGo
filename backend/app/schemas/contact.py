"""Pydantic schemas for public contact inquiry messages."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ContactMessageCreate(BaseModel):
    """Payload for ``POST /api/v1/contact``."""

    name: str = Field(..., min_length=2, max_length=120, description="Full name of the sender")
    email: EmailStr = Field(..., description="Valid email address for reply")
    subject: str = Field(..., min_length=3, max_length=120, description="Subject of the inquiry")
    suite_code: str | None = Field(default=None, max_length=32, description="Optional customer suite code (e.g. JTG-8821)")
    message: str = Field(..., min_length=10, max_length=5000, description="Detailed inquiry message")


class ContactMessageResponse(BaseModel):
    """Response payload for successful contact submission."""

    success: bool = True
    message: str = "Mensagem recebida com sucesso! Nossa equipe responderá em breve."
