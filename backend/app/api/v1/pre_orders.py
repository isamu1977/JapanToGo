"""Client pre-order endpoints (assisted purchase and redirection)."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import fetch_owned, require_client
from app.core.errors import ValidationError
from app.models.base import PreOrderStatus, PreOrderType
from app.models.pre_order import PreOrder, PreOrderItem
from app.models.user import User
from app.schemas.pre_order import AssistedPreOrderCreate, PreOrderOut
from app.services.fee_calculator import calculate_service_fee
from app.services.file_storage import storage
from app.services.ssrf_validator import validate_url

router = APIRouter(prefix="/pre-orders", tags=["pre-orders"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Client = Annotated[User, Depends(require_client)]


@router.post(
    "/assisted",
    response_model=PreOrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create an assisted purchase pre-order",
)
async def create_assisted_purchase(
    payload: AssistedPreOrderCreate, db: DbSession, user: Client
) -> PreOrderOut:
    """Store an assisted purchase request and compute the service fee.

    Every product URL is validated against the SSRF policy before it is
    persisted, so a hostile link can never be fetched by the backend.
    """
    for item in payload.items:
        validate_url(item.product_url)

    items_total = sum(
        (item.line_total_jpy for item in payload.items), start=Decimal("0")
    )
    fee = calculate_service_fee(items_total)

    pre_order = PreOrder(
        user_id=user.id,
        type=PreOrderType.assisted_purchase,
        status=PreOrderStatus.submitted,
        total_items_price_jpy=fee.items_total_jpy,
        service_fee_jpy=fee.fee_jpy,
        total_jpy=fee.total_jpy,
        admin_notes=payload.notes,
    )
    db.add(pre_order)

    for item in payload.items:
        db.add(
            PreOrderItem(
                pre_order=pre_order,
                product_url=item.product_url,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price_jpy=item.unit_price_jpy,
                options_description=item.options_description,
                line_total_jpy=item.line_total_jpy,
            )
        )

    await db.commit()

    result = await db.execute(
        select(PreOrder)
        .options(selectinload(PreOrder.items))
        .where(PreOrder.id == pre_order.id)
    )
    return PreOrderOut.model_validate(result.scalar_one())


@router.post(
    "/forwarding",
    response_model=PreOrderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pure redirection pre-order",
)
async def create_forwarding(
    db: DbSession,
    user: Client,
    store_name: Annotated[str, Form(min_length=1, max_length=255)],
    description: Annotated[str, Form(min_length=1, max_length=2000)],
    receipt: Annotated[UploadFile | None, File()] = None,
    expected_domestic_tracking: Annotated[str | None, Form(max_length=64)] = None,
    notes: Annotated[str | None, Form(max_length=2000)] = None,
) -> PreOrderOut:
    """Store a redirection request. The purchase receipt is mandatory."""
    if receipt is None or not receipt.filename:
        raise ValidationError(
            "The purchase receipt (invoice image or PDF) is mandatory for a "
            "redirection pre-order.",
            details={"field": "receipt"},
        )

    stored = await storage.save_receipt(receipt)

    pre_order = PreOrder(
        user_id=user.id,
        type=PreOrderType.forwarding,
        status=PreOrderStatus.submitted,
        total_items_price_jpy=Decimal("0.00"),
        service_fee_jpy=Decimal("0.00"),
        total_jpy=Decimal("0.00"),
        receipt_url=stored.url,
        receipt_filename=stored.filename,
        store_name=store_name,
        expected_domestic_tracking=expected_domestic_tracking,
        admin_notes=notes,
    )
    db.add(pre_order)
    await db.commit()

    result = await db.execute(
        select(PreOrder)
        .options(selectinload(PreOrder.items))
        .where(PreOrder.id == pre_order.id)
    )
    return PreOrderOut.model_validate(result.scalar_one())


@router.get("", response_model=list[PreOrderOut], summary="My pre-orders")
async def list_pre_orders(
    db: DbSession,
    user: Client,
    order_type: PreOrderType | None = None,
) -> list[PreOrderOut]:
    """List every pre-order of the authenticated client, newest first."""
    query = (
        select(PreOrder)
        .options(selectinload(PreOrder.items))
        .where(PreOrder.user_id == user.id)
        .order_by(PreOrder.created_at.desc())
    )
    if order_type is not None:
        query = query.where(PreOrder.type == order_type)

    result = await db.execute(query)
    return [PreOrderOut.model_validate(row) for row in result.scalars().all()]


@router.get("/{pre_order_id}", response_model=PreOrderOut, summary="Pre-order detail")
async def get_pre_order(
    pre_order_id: uuid.UUID, db: DbSession, user: Client
) -> PreOrderOut:
    """Return a single pre-order owned by the authenticated client.

    Accessing a pre-order that belongs to another client is rejected with
    HTTP 403 Forbidden (IDOR prevention).
    """
    pre_order = await fetch_owned(
        db,
        PreOrder,
        pre_order_id,
        user.id,
        options=[selectinload(PreOrder.items)],
        not_found_message="Pre-order not found.",
    )
    return PreOrderOut.model_validate(pre_order)
