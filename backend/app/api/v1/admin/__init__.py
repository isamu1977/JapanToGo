"""Admin API package."""

from app.api.v1.admin import dashboard, pre_orders, shipments, warehouse

__all__ = ["dashboard", "pre_orders", "shipments", "warehouse"]
