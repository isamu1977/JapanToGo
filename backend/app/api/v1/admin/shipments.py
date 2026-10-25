"""Admin dispatch queue, international tracking and Japan Post export."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.errors import NotFoundError, ValidationError
from app.models.base import ShipmentStatus, SuiteItemStatus
from app.models.shipment import Shipment
from app.models.suite_item import SuiteItem
from app.models.user import User
from app.schemas.calculator import JapanPostExportResponse
from app.schemas.shipment import AdminDispatchUpdate, ShipmentOut
from app.services.japan_post_export import build_export

router = APIRouter(prefix="/admin/shipments", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Admin = Annotated[User, Depends(require_admin)]


@router.get("", response_model=list[ShipmentOut], summary="Dispatch queue")
async def list_admin_shipments(
    db: DbSession,
    _: Admin,
    status_filter: ShipmentStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[ShipmentOut]:
    """List shipments awaiting dispatch, newest first."""
    query = (
        select(Shipment)
        .order_by(Shipment.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status_filter is not None:
        query = query.where(Shipment.status == status_filter)

    result = await db.execute(query)
    return [ShipmentOut.model_validate(row) for row in result.scalars().all()]


@router.get(
    "/{shipment_id}", response_model=ShipmentOut, summary="Shipment detail"
)
async def get_admin_shipment(
    shipment_id: uuid.UUID, db: DbSession, _: Admin
) -> ShipmentOut:
    """Return a shipment with the operator details."""
    result = await db.execute(
        select(Shipment)
        .options(selectinload(Shipment.suite_items))
        .where(Shipment.id == shipment_id)
    )
    shipment = result.scalar_one_or_none()
    if shipment is None:
        raise NotFoundError("Shipment not found.")
    return ShipmentOut.model_validate(shipment)


@router.put(
    "/{shipment_id}/dispatch",
    response_model=ShipmentOut,
    summary="Register the international dispatch",
)
async def dispatch_shipment(
    shipment_id: uuid.UUID, payload: AdminDispatchUpdate, db: DbSession, _: Admin
) -> ShipmentOut:
    """Transition a shipment to ``dispatched`` and ship its suite items."""
    result = await db.execute(
        select(Shipment).where(Shipment.id == shipment_id)
    )
    shipment = result.scalar_one_or_none()
    if shipment is None:
        raise NotFoundError("Shipment not found.")

    if (
        payload.status is ShipmentStatus.dispatched
        and not payload.international_tracking_code
    ):
        raise ValidationError(
            "The international tracking code is required to dispatch a shipment.",
            details={"field": "international_tracking_code"},
        )

    shipment.status = payload.status
    if payload.total_weight_grams:
        shipment.total_weight_grams = payload.total_weight_grams
    if payload.shipping_fee_jpy is not None:
        shipment.shipping_fee_jpy = Decimal(str(payload.shipping_fee_jpy))
    if payload.international_tracking_code:
        shipment.international_tracking_code = payload.international_tracking_code

    if payload.status is ShipmentStatus.dispatched:
        shipment.dispatched_at = datetime.now(timezone.utc)

        items = await db.execute(
            select(SuiteItem).where(SuiteItem.shipment_id == shipment.id)
        )
        for item in items.scalars().all():
            item.status = SuiteItemStatus.shipped

    await db.commit()
    await db.refresh(shipment)
    return ShipmentOut.model_validate(shipment)


@router.get(
    "/{shipment_id}/export-japan-post",
    response_model=JapanPostExportResponse,
    summary="Export the shipment for Japan Post",
)
async def export_japan_post(
    shipment_id: uuid.UUID, db: DbSession, _: Admin
) -> JapanPostExportResponse:
    """Format the shipment for the Japan Post International Mail My Page."""
    result = await db.execute(
        select(Shipment)
        .options(selectinload(Shipment.suite_items))
        .where(Shipment.id == shipment_id)
    )
    shipment = result.scalar_one_or_none()
    if shipment is None:
        raise NotFoundError("Shipment not found.")

    export = build_export(shipment)
    return JapanPostExportResponse(
        payload=export.to_dict(), text=export.to_text(), csv=export.to_csv()
    )
