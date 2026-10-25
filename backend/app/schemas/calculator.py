"""Schemas for the public landed cost calculator."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


class LandedCostRequest(BaseModel):
    """Body of ``POST /api/v1/calculator/simulate``."""

    item_price_jpy: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    weight_grams: int = Field(gt=0, le=100_000)
    order_type: Literal["assisted_purchase", "forwarding"] = "assisted_purchase"
    shipping_method: Literal["ems", "small_packet"] = "ems"


class LandedCostLine(BaseModel):
    label: str
    label_ja: str
    amount_jpy: float
    amount_brl: float


class LandedCostResponse(BaseModel):
    """Result of a landed cost simulation."""

    order_type: str
    shipping_method: str
    item_price_jpy: float
    weight_grams: int
    exchange_rate_brl: float
    exchange_rate_spread: float
    item_price_brl: float
    service_fee_jpy: float
    service_fee_brl: float
    service_fee_floor_applied: bool
    freight_jpy: float
    freight_brl: float
    customs_value_brl: float
    rts_brl: float
    icms_brl: float
    total_jpy: float
    total_brl: float
    breakdown: list[LandedCostLine]
    disclaimer: str


class ServiceFeeResponse(BaseModel):
    """Result of an assisted purchase fee calculation."""

    items_total_jpy: float
    fee_rate: float
    proportional_fee_jpy: float
    fee_jpy: float
    floor_applied: bool
    minimum_fee_jpy: float
    total_jpy: float


class JapanPostExportResponse(BaseModel):
    """Japan Post International Mail My Page export payload."""

    payload: dict[str, Any]
    text: str
    csv: str
