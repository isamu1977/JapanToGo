"""JapanToGo FastAPI application entrypoint."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.types import Scope

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import dispose_engine
from app.core.errors import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.rate_limit import limiter


class SecureStaticFiles(StaticFiles):
    """Static files served with hardening headers.

    ``X-Content-Type-Options: nosniff`` stops the browser from guessing a
    different content type, which prevents an uploaded file from being
    interpreted as an executable script.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'; img-src 'self'; style-src 'unsafe-inline'"
        return response


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepare the uploads directory and dispose the engine on shutdown."""
    configure_logging("DEBUG" if settings.debug else "INFO")
    os.makedirs(settings.uploads_dir, exist_ok=True)
    yield
    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    summary="JapanToGo - assisted purchase and forwarding API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# The rate limiter runs inside the CORS middleware so that preflight requests
# are answered by CORS and never consume the caller's quota.
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    # Only the explicitly configured origins are accepted: the official
    # production domain plus localhost for development.
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "Retry-After"],
    max_age=600,
)

register_exception_handlers(app)

app.state.limiter = limiter

app.include_router(api_router, prefix=settings.api_prefix)
app.include_router(api_router, prefix="/api")

os.makedirs(settings.uploads_dir, exist_ok=True)
app.mount(
    "/uploads",
    SecureStaticFiles(directory=settings.uploads_dir, check_dir=False),
    name="uploads",
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Return a JSON envelope when a route limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": (
                    "Too many requests. Please slow down and try again shortly."
                ),
                "details": {"limit": str(exc.detail)},
            }
        },
        headers=getattr(exc, "headers", None),
    )


@app.get("/health", tags=["system"], summary="Liveness probe")
async def health() -> dict[str, str]:
    """Simple liveness probe used by Docker / Coolify healthchecks."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Service banner."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api": settings.api_prefix,
    }
