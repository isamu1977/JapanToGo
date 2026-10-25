"""Client shipment endpoints: consolidation requests and shipment history."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import fetch_owned, require_client
from app.core.errors import NotFoundError, ValidationError
from app.models.base import ShipmentStatus, SuiteItemStatus
from app.models.shipment import Shipment
from app.models.suite_item import SuiteItem
from app.models.user import User
from app.schemas.shipment import ShipmentOut, ShipmentRequestCreate

router = APIRouter(prefix="/shipments", tags=["shipments"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Client = Annotated[User, Depends(require_client)]


@router.post(
    "/request",
    response_model=ShipmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Request a consolidated shipment",
)
async def request_shipment(
    payload: ShipmentRequestCreate, db: DbSession, user: Client
) -> ShipmentOut:
    """Consolidate stored suite items into an international shipment."""
    result = await db.execute(
        select(SuiteItem)
        .options(selectinload(SuiteItem.photos))
        .where(
            SuiteItem.user_id == user.id,
            SuiteItem.id.in_(payload.suite_item_ids),
        )
    )
    items = list(result.scalars().all())

    if len(items) != len(payload.suite_item_ids):
        missing = set(payload.suite_item_ids) - {item.id for item in items}
        raise NotFoundError(
            "One or more suite items were not found.",
            details={"missing": [str(item_id) for item_id in missing]},
        )

    unavailable = [
        item.id
        for item in items
        if item.status is not SuiteItemStatus.in_storage
    ]
    if unavailable:
        raise ValidationError(
            "Only items in storage can be consolidated into a shipment.",
            details={"unavailable": [str(item_id) for item_id in unavailable]},
        )

    total_weight = sum(item.weight_grams for item in items)
    declared_total = sum(
        (item.declared_value_jpy * item.quantity for item in payload.customs_declaration.items),
        Decimal("0"),
    )

    shipment = Shipment(
        user_id=user.id,
        shipping_method=payload.shipping_method,
        status=ShipmentStatus.requested,
        total_weight_grams=total_weight,
        shipping_fee_jpy=Decimal("0.00"),
        recipient_name=payload.recipient_name,
        recipient_cpf=payload.recipient_cpf,
        recipient_phone=payload.recipient_phone,
        recipient_postal_code=payload.recipient_postal_code,
        recipient_address=payload.recipient_address,
        recipient_state=payload.recipient_state,
        recipient_city=payload.recipient_city,
        customs_declaration=payload.customs_declaration.to_json(),
    )
    db.add(shipment)
    await db.flush()

    for item in items:
        item.status = SuiteItemStatus.consolidation_requested
        item.shipment_id = shipment.id

    await db.commit()
    await db.refresh(shipment)
    return ShipmentOut.model_validate(shipment)


@router.get("", response_model=list[ShipmentOut], summary="My shipments")
async def list_shipments(db: DbSession, user: Client) -> list[ShipmentOut]:
    """List the shipments of the authenticated client, newest first."""
    result = await db.execute(
        select(Shipment)
        .where(Shipment.user_id == user.id)
        .order_by(Shipment.created_at.desc())
    )
    return [ShipmentOut.model_validate(row) for row in result.scalars().all()]


@router.get(
    "/{shipment_id}", response_model=ShipmentOut, summary="Shipment detail"
)
async def get_shipment(
    shipment_id: uuid.UUID, db: DbSession, user: Client
) -> ShipmentOut:
    """Return a single shipment owned by the authenticated client.

    Accessing a shipment that belongs to another client is rejected with
    HTTP 403 Forbidden (IDOR prevention).
    """
    shipment = await fetch_owned(
        db,
        Shipment,
        shipment_id,
        user.id,
        not_found_message="Shipment not found.",
    )
    return ShipmentOut.model_validate(shipment)
