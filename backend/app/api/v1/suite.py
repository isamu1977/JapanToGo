"""Client suite endpoints: inventory overview, photos and warehouse address."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import fetch_owned, require_client
from app.core.errors import NotFoundError
from app.models.base import SuiteItemStatus
from app.models.suite_item import InspectionPhoto, SuiteItem
from app.models.user import User
from app.schemas.suite_item import (
    InspectionPhotoOut,
    SuiteItemOut,
    SuiteSummaryOut,
    WarehouseAddressOut,
)
from app.services.file_storage import storage
from app.services.suite_service import build_warehouse_address

router = APIRouter(prefix="/suite", tags=["suite"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Client = Annotated[User, Depends(require_client)]


@router.get("/me", response_model=SuiteSummaryOut, summary="My suite inventory")
async def my_suite(db: DbSession, user: Client) -> SuiteSummaryOut:
    """Return the items currently held in the client's warehouse suite."""
    result = await db.execute(
        select(SuiteItem)
        .options(selectinload(SuiteItem.photos))
        .where(SuiteItem.user_id == user.id)
        .order_by(SuiteItem.received_at.desc().nullslast(), SuiteItem.created_at.desc())
    )
    items = list(result.scalars().all())

    return SuiteSummaryOut(
        suite_code=user.suite_code,
        item_count=len(items),
        total_weight_grams=sum(item.weight_grams for item in items),
        items=[SuiteItemOut.model_validate(item) for item in items],
    )


@router.get(
    "/me/address",
    response_model=WarehouseAddressOut,
    summary="Warehouse address with my suite code",
)
async def my_suite_address(user: Client) -> WarehouseAddressOut:
    """Return the JapanToGo warehouse address with the suite code injected."""
    address = build_warehouse_address(user.suite_code)
    return WarehouseAddressOut(
        suite_code=user.suite_code, ja=address["ja"], romaji=address["romaji"]
    )


@router.get(
    "/me/items/{item_id}", response_model=SuiteItemOut, summary="Suite item detail"
)
async def my_suite_item(
    item_id: uuid.UUID, db: DbSession, user: Client
) -> SuiteItemOut:
    """Return a single suite item owned by the authenticated client.

    Accessing an item that belongs to another client is rejected with HTTP 403
    Forbidden (IDOR prevention).
    """
    item = await fetch_owned(
        db,
        SuiteItem,
        item_id,
        user.id,
        options=[selectinload(SuiteItem.photos)],
        not_found_message="Suite item not found.",
    )
    return SuiteItemOut.model_validate(item)


@router.get(
    "/me/photos/{photo_id}",
    summary="Inspection photo (ownership verified)",
    response_class=FileResponse,
)
async def my_inspection_photo(
    photo_id: uuid.UUID, db: DbSession, user: Client
) -> FileResponse:
    """Return an inspection photo owned by the authenticated client.

    The photo is only served when the related suite item belongs to the
    requesting user.
    """
    result = await db.execute(
        select(InspectionPhoto)
        .join(SuiteItem, SuiteItem.id == InspectionPhoto.suite_item_id)
        .where(
            InspectionPhoto.id == photo_id,
            SuiteItem.user_id == user.id,
        )
    )
    photo = result.scalar_one_or_none()
    if photo is None:
        raise NotFoundError("Inspection photo not found.")

    stored_path = storage.base_dir / photo.photo_url.removeprefix("/uploads/")
    if not stored_path.is_file():
        raise NotFoundError("Inspection photo file is missing.")

    return FileResponse(
        stored_path,
        media_type="image/webp",
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.get(
    "/me/stats", summary="Suite counters used by the client dashboard"
)
async def my_suite_stats(db: DbSession, user: Client) -> dict[str, int]:
    """Return aggregated counters for the client dashboard."""
    result = await db.execute(
        select(SuiteItem.status, func.count(SuiteItem.id))
        .where(SuiteItem.user_id == user.id)
        .group_by(SuiteItem.status)
    )
    counts = {status.value: 0 for status in SuiteItemStatus}
    for status, count in result.all():
        counts[status.value] = int(count)

    total_weight = await db.execute(
        select(func.coalesce(func.sum(SuiteItem.weight_grams), 0)).where(
            SuiteItem.user_id == user.id
        )
    )
    return {
        "total": sum(counts.values()),
        "total_weight_grams": int(total_weight.scalar_one()),
        **{f"status_{key}": value for key, value in counts.items()},
    }
