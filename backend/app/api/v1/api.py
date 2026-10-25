"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, calculator, contact, pre_orders, shipments, suite
from app.api.v1.admin import dashboard as admin_dashboard
from app.api.v1.admin import pre_orders as admin_pre_orders
from app.api.v1.admin import shipments as admin_shipments
from app.api.v1.admin import warehouse as admin_warehouse

api_router = APIRouter()

# --- Public -----------------------------------------------------------------
api_router.include_router(auth.router)
api_router.include_router(calculator.router)
api_router.include_router(contact.router)


# --- Client -----------------------------------------------------------------
api_router.include_router(pre_orders.router)
api_router.include_router(suite.router)
api_router.include_router(shipments.router)

# --- Admin ------------------------------------------------------------------
api_router.include_router(admin_dashboard.router)
api_router.include_router(admin_pre_orders.router)
api_router.include_router(admin_warehouse.router)
api_router.include_router(admin_shipments.router)
