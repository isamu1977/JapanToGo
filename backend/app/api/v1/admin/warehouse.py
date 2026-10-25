"""Warehouse check-in: client search, parcel registration and inspection photos."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import require_admin
from app.core.errors import NotFoundError, ValidationError
from app.models.base import PreOrderStatus, PreOrderType, SuiteItemStatus, UserRole
from app.models.pre_order import PreOrder
from app.models.suite_item import InspectionPhoto, SuiteItem
from app.models.user import User
from app.schemas.suite_item import SuiteItemOut
from app.services.file_storage import storage

router = APIRouter(prefix="/admin/warehouse", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Admin = Annotated[User, Depends(require_admin)]


@router.get("/search", summary="Find a client by suite code or name")
async def search_clients(
    db: DbSession,
    _: Admin,
    q: str = Query(min_length=1, max_length=255),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[dict]:
    """Search clients by ``suite_code`` or full name and list pending pre-orders."""
    term = f"%{q.strip().lower()}%"
    result = await db.execute(
        select(User)
        .where(
            User.role == UserRole.client,
            or_(
                func.lower(User.suite_code) == q.strip().lower(),
                func.lower(User.full_name).like(term),
                func.lower(User.email).like(term),
            ),
        )
        .limit(limit)
    )
    users = list(result.scalars().all())

    payload: list[dict] = []
    for user in users:
        pending = await db.execute(
            select(PreOrder)
            .options(selectinload(PreOrder.items))
            .where(
                PreOrder.user_id == user.id,
                PreOrder.status.in_(
                    [PreOrderStatus.submitted, PreOrderStatus.purchased]
                ),
            )
            .order_by(PreOrder.created_at.desc())
        )
        payload.append(
            {
                "id": str(user.id),
                "suite_code": user.suite_code,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "pending_pre_orders": [
                    {
                        "id": str(order.id),
                        "type": order.type.value,
                        "status": order.status.value,
                        "store_name": order.store_name,
                        "expected_domestic_tracking": order.expected_domestic_tracking,
                        "domestic_tracking_code": order.domestic_tracking_code,
                        "total_jpy": float(order.total_jpy),
                        "item_count": len(order.items),
                        "created_at": order.created_at.isoformat(),
                    }
                    for order in pending.scalars().all()
                ],
            }
        )
    return payload


@router.post(
    "/checkin",
    response_model=SuiteItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a received parcel in the client's suite",
)
async def checkin(
    db: DbSession,
    _: Admin,
    suite_code: Annotated[str, Form(min_length=4, max_length=16)],
    description: Annotated[str, Form(min_length=1, max_length=512)],
    weight_grams: Annotated[int, Form(ge=1, le=2_000_000)],
    tracking_domestic: Annotated[str | None, Form(max_length=64)] = None,
    pre_order_id: Annotated[str | None, Form()] = None,
    photos: Annotated[list[UploadFile] | None, File()] = None,
) -> SuiteItemOut:
    """Create a ``suite_items`` record and attach the inspection photos."""
    normalized = suite_code.strip().upper()
    result = await db.execute(
        select(User).where(User.suite_code == normalized)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError(
            f"No client found with suite code '{normalized}'.",
            details={"suite_code": normalized},
        )

    linked_pre_order: uuid.UUID | None = None
    if pre_order_id:
        try:
            linked_pre_order = uuid.UUID(pre_order_id)
        except ValueError as exc:
            raise ValidationError("pre_order_id must be a valid UUID.") from exc

        owned = await db.execute(
            select(PreOrder.id).where(
                PreOrder.id == linked_pre_order, PreOrder.user_id == user.id
            )
        )
        if owned.scalar_one_or_none() is None:
            raise NotFoundError("Pre-order not found for this client.")

    # Photos are optional at check-in time (they can be added later), but
    # never more than the configured maximum.
    photos = list(photos or [])
    if len(photos) > settings.max_inspection_photos:
        raise ValidationError(
            f"A maximum of {settings.max_inspection_photos} inspection photos is "
            f"allowed per item (received {len(photos)})."
        )
    stored_photos = [
        await storage.save_image(photo, subdir="inspections") for photo in photos
    ]

    item = SuiteItem(
        user_id=user.id,
        pre_order_id=linked_pre_order,
        description=description,
        weight_grams=weight_grams,
        status=SuiteItemStatus.in_storage,
        tracking_domestic=tracking_domestic,
        received_at=datetime.now(timezone.utc),
    )
    db.add(item)
    await db.flush()

    for order, stored in enumerate(stored_photos):
        db.add(
            InspectionPhoto(
                suite_item_id=item.id,
                photo_url=stored.url,
                display_order=order,
            )
        )

    await db.commit()

    result = await db.execute(
        select(SuiteItem)
        .options(selectinload(SuiteItem.photos))
        .where(SuiteItem.id == item.id)
    )
    return SuiteItemOut.model_validate(result.scalar_one())
