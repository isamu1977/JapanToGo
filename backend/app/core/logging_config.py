"""Logging configuration with automatic masking of PII and credentials.

The filter is attached to the root logger so every record written to stdout
(the Docker / Coolify log stream) is sanitised before it leaves the process.
"""

from __future__ import annotations

import logging
import re
from typing import Any

#: The masked representation used for every CPF occurrence.
CPF_MASK = "***.***.***-**"

#: Patterns applied to the formatted log message.
#: The order matters: bearer tokens and JWTs are consumed first so the
#: credential-keyword rule cannot leave a partially masked value behind.
_MESSAGE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Bearer tokens.
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]+"), "Bearer ***"),
    # JSON Web Tokens (header.payload.signature).
    (
        re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{4,}\.[A-Za-z0-9_\-]*"),
        "***",
    ),
    # Formatted CPF: 123.456.789-09
    (re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}"), CPF_MASK),
    # Bare CPF: 11 consecutive digits.
    (re.compile(r"(?<!\d)\d{11}(?!\d)"), CPF_MASK),
    # JSON / keyword style credentials: "password": "secret"
    (
        re.compile(
            r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|authorization)"
            r"(\"?\s*[:=]\s*\"?)([^\"\s,}\]]+)"
        ),
        r"\1\2***",
    ),
)


class SensitiveDataMaskingFilter(logging.Filter):
    """Mask CPF numbers, passwords, API keys and authorization tokens."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover - broken format string
            return True

        masked = message
        for pattern, replacement in _MESSAGE_PATTERNS:
            masked = pattern.sub(replacement, masked)

        if masked != message:
            record.msg = masked
            record.args = ()

        # Structured payloads (e.g. ``extra={"body": {...}}``) are sanitised too.
        for key, value in list(record.__dict__.items()):
            if key in {"msg", "args"} or not isinstance(value, str):
                continue
            sanitized = value
            for pattern, replacement in _MESSAGE_PATTERNS:
                sanitized = pattern.sub(replacement, sanitized)
            if sanitized != value:
                record.__dict__[key] = sanitized

        return True


def mask_text(text: str) -> str:
    """Apply the masking rules to an arbitrary string."""
    masked = text
    for pattern, replacement in _MESSAGE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def configure_logging(level: int | str = logging.INFO) -> None:
    """Install the masking filter on the root logger and every handler."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    for handler in root.handlers:
        if not any(isinstance(f, SensitiveDataMaskingFilter) for f in handler.filters):
            handler.addFilter(SensitiveDataMaskingFilter())

    # Guarantee at least one sanitised handler exists.
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(SensitiveDataMaskingFilter())
        root.addHandler(handler)

    # Uvicorn keeps its own handlers; sanitise them as well.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine"):
        logger = logging.getLogger(name)
        for handler in logger.handlers:
            if not any(isinstance(f, SensitiveDataMaskingFilter) for f in handler.filters):
                handler.addFilter(SensitiveDataMaskingFilter())


def get_logger(name: str) -> logging.Logger:
    """Return a logger that is guaranteed to be sanitised."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, SensitiveDataMaskingFilter) for f in logger.filters):
        logger.addFilter(SensitiveDataMaskingFilter())
    return logger


__all__ = [
    "CPF_MASK",
    "SensitiveDataMaskingFilter",
    "configure_logging",
    "get_logger",
    "mask_text",
]
