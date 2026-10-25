"""Core package: settings, database, security and error handling."""

from app.core.config import get_settings, settings
from app.core.database import Base, AsyncSessionLocal, engine, get_db
from app.core.errors import (
    AppError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    StorageError,
    ValidationError,
    register_exception_handlers,
)

__all__ = [
    "AppError",
    "AsyncSessionLocal",
    "AuthenticationError",
    "Base",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "StorageError",
    "ValidationError",
    "engine",
    "get_db",
    "get_settings",
    "register_exception_handlers",
    "settings",
]
