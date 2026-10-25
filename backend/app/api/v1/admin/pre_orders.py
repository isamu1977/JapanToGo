"""Admin pre-order queue and purchase completion."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.errors import NotFoundError
from app.models.base import PreOrderStatus, PreOrderType
from app.models.pre_order import PreOrder
from app.models.user import User
from app.schemas.pre_order import AdminPurchaseUpdate, PreOrderOut

router = APIRouter(prefix="/admin/pre-orders", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Admin = Annotated[User, Depends(require_admin)]


@router.get("", response_model=list[PreOrderOut], summary="Pre-order queue")
async def list_admin_pre_orders(
    db: DbSession,
    _: Admin,
    order_type: PreOrderType | None = None,
    status_filter: PreOrderStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[PreOrderOut]:
    """List pre-orders with optional filters, newest first."""
    query = (
        select(PreOrder)
        .options(selectinload(PreOrder.items))
        .order_by(PreOrder.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if order_type is not None:
        query = query.where(PreOrder.type == order_type)
    if status_filter is not None:
        query = query.where(PreOrder.status == status_filter)

    result = await db.execute(query)
    return [PreOrderOut.model_validate(row) for row in result.scalars().all()]


@router.put(
    "/{pre_order_id}/purchase",
    response_model=PreOrderOut,
    summary="Mark an assisted purchase as purchased",
)
async def update_purchase(
    pre_order_id: uuid.UUID, payload: AdminPurchaseUpdate, db: DbSession, _: Admin
) -> PreOrderOut:
    """Update the status of a pre-order and store the domestic tracking code."""
    result = await db.execute(
        select(PreOrder)
        .options(selectinload(PreOrder.items))
        .where(PreOrder.id == pre_order_id)
    )
    pre_order = result.scalar_one_or_none()
    if pre_order is None:
        raise NotFoundError("Pre-order not found.")

    pre_order.status = payload.status
    if payload.domestic_tracking_code:
        pre_order.domestic_tracking_code = payload.domestic_tracking_code
    if payload.admin_notes is not None:
        pre_order.admin_notes = payload.admin_notes

    await db.commit()
    await db.refresh(pre_order)
    return PreOrderOut.model_validate(pre_order)
