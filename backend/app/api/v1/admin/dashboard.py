"""Admin operational dashboard metrics."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.base import (
    PreOrderStatus,
    PreOrderType,
    ShipmentStatus,
    SuiteItemStatus,
    UserRole,
)
from app.models.pre_order import PreOrder
from app.models.shipment import Shipment
from app.models.suite_item import SuiteItem
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
Admin = Annotated[User, Depends(require_admin)]


async def _count(db: AsyncSession, model, *conditions) -> int:
    query = select(func.count(model.id))
    for condition in conditions:
        query = query.where(condition)
    result = await db.execute(query)
    return int(result.scalar_one())


@router.get("/dashboard", summary="Operational metrics")
async def dashboard(db: DbSession, _: Admin) -> dict:
    """Return the operational counters used by the admin dashboard."""
    clients = await _count(db, User, User.role == UserRole.client)

    pre_orders_by_status: dict[str, int] = {}
    result = await db.execute(
        select(PreOrder.status, func.count(PreOrder.id)).group_by(PreOrder.status)
    )
    for status, count in result.all():
        pre_orders_by_status[status.value] = int(count)

    assisted_pending = await _count(
        db,
        PreOrder,
        PreOrder.type == PreOrderType.assisted_purchase,
        PreOrder.status == PreOrderStatus.submitted,
    )

    items_by_status: dict[str, int] = {}
    result = await db.execute(
        select(SuiteItem.status, func.count(SuiteItem.id)).group_by(SuiteItem.status)
    )
    for status, count in result.all():
        items_by_status[status.value] = int(count)

    shipments_by_status: dict[str, int] = {}
    result = await db.execute(
        select(Shipment.status, func.count(Shipment.id)).group_by(Shipment.status)
    )
    for status, count in result.all():
        shipments_by_status[status.value] = int(count)

    result = await db.execute(
        select(func.coalesce(func.sum(SuiteItem.weight_grams), 0)).where(
            SuiteItem.status == SuiteItemStatus.in_storage
        )
    )
    stored_weight = int(result.scalar_one())

    return {
        "clients": clients,
        "pre_orders": {
            "total": sum(pre_orders_by_status.values()),
            "by_status": pre_orders_by_status,
            "assisted_pending_purchase": assisted_pending,
        },
        "suite_items": {
            "total": sum(items_by_status.values()),
            "by_status": items_by_status,
            "stored_weight_grams": stored_weight,
        },
        "shipments": {
            "total": sum(shipments_by_status.values()),
            "by_status": shipments_by_status,
        },
        "pending_actions": {
            "purchases_to_complete": assisted_pending,
            "packages_to_check_in": pre_orders_by_status.get("purchased", 0),
            "shipments_to_dispatch": shipments_by_status.get("packed", 0)
            + shipments_by_status.get("requested", 0),
        },
    }
