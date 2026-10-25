"""Shared pytest fixtures.

The test suite runs against a dedicated ``japantogo_test`` database on the
same native PostgreSQL server used for development.
"""

from __future__ import annotations

import io
import os
import tempfile
from collections.abc import AsyncIterator

# The environment must be configured *before* the application modules import
# ``app.core.config`` (the settings object is cached on first import).
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://isamumatsuyama@localhost:5432/japantogo_test",
)
os.environ.setdefault("JWT_SECRET", "test-secret-key-0123456789abcdef")
os.environ.setdefault(
    "UPLOADS_DIR", os.path.join(tempfile.gettempdir(), "japantogo-test-uploads")
)
os.environ.setdefault("ENVIRONMENT", "test")
# Rate limits are disabled by default so the suite is not throttled; the
# dedicated rate limit test enables them explicitly.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import asyncpg  # noqa: E402
import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

import app.models  # noqa: E402,F401  (registers the tables)
from app.core.database import Base, get_db  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import UserRole  # noqa: E402
from app.models.user import User  # noqa: E402

TEST_DB_NAME = "japantogo_test"


def _base_url() -> str:
    url = os.environ["DATABASE_URL"]
    return url.rsplit("/", 1)[0]


def _test_url() -> str:
    return f"{_base_url()}/{TEST_DB_NAME}"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


def pytest_collection_modifyitems(items: list) -> None:
    """Run every async test on the shared session event loop.

    The engine, the sessions and the tests must all use the same loop,
    otherwise asyncpg connections end up bound to a loop that is already
    closed when the session is finalised.
    """
    for item in items:
        if item.get_closest_marker("asyncio") is None:
            continue
        item.own_markers = [
            marker for marker in item.own_markers if marker.name != "asyncio"
        ]
        item.add_marker(pytest.mark.asyncio(loop_scope="session"))


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncIterator:
    """Create the test database (if needed) and the schema."""
    admin_url = _base_url().replace("postgresql+asyncpg://", "postgresql://")
    connection = await asyncpg.connect(admin_url)
    try:
        exists = await connection.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
        )
        if not exists:
            await connection.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await connection.close()

    test_engine = create_async_engine(_test_url(), poolclass=NullPool)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def clean_database(engine) -> AsyncIterator[None]:
    """Truncate every table after each test so the suite stays isolated."""
    yield

    async with engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE users, legal_terms_acceptance, pre_order_items, "
                "pre_orders, inspection_photos, suite_items, shipments "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest_asyncio.fixture(loop_scope="session")
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(session_factory) -> AsyncIterator[AsyncSession]:
    """Provide a session bound to the test database."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def client(session_factory) -> AsyncIterator[AsyncClient]:
    """HTTP client wired to the test database."""

    async def _override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http:
        yield http
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="session")
async def admin_user(db_session: AsyncSession) -> User:
    """An administrator account."""
    admin = User(
        email="admin@test.japantogo",
        hashed_password=hash_password("admin-password1"),
        full_name="Admin Test",
        phone="+81-6-0000-0000",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(loop_scope="session")
async def client_user(db_session: AsyncSession) -> User:
    """A client account with an allocated suite code."""
    user = User(
        email="client@test.japantogo",
        hashed_password=hash_password("client-password1"),
        full_name="Client Test",
        phone="+55-11-99999-0000",
        role=UserRole.client,
        is_active=True,
        suite_code="JTG-9001",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Deprecated: sessions are carried by HttpOnly cookies, not headers."""

    def _build(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _build


async def login(
    client: AsyncClient, email: str, password: str
) -> AsyncClient:
    """Authenticate and keep the HttpOnly session cookies on the client."""
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, response.text
    return client


def make_upload(
    filename: str, content: bytes, content_type: str = "image/png"
):
    """Build a FastAPI ``UploadFile`` with the given content type."""
    from fastapi import UploadFile
    from starlette.datastructures import Headers

    return UploadFile(
        file=io.BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )
