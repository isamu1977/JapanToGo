"""Schemas for pre-orders (assisted purchase and redirection)."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.base import PreOrderStatus, PreOrderType


class PreOrderItemInput(BaseModel):
    """A product line submitted by the client."""

    product_url: str = Field(min_length=4, max_length=1024)
    product_name: str = Field(min_length=1, max_length=512)
    quantity: int = Field(ge=1, le=999)
    unit_price_jpy: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    options_description: str | None = Field(default=None, max_length=2000)

    @field_validator("product_url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        value = value.strip()
        if not value.lower().startswith(("http://", "https://")):
            raise ValueError("product_url must start with http:// or https://")
        return value

    @property
    def line_total_jpy(self) -> Decimal:
        return (self.unit_price_jpy * self.quantity).quantize(Decimal("0.01"))


class AssistedPreOrderCreate(BaseModel):
    """Body of ``POST /api/v1/pre-orders/assisted``."""

    items: list[PreOrderItemInput] = Field(min_length=1)
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def _require_items(self) -> "AssistedPreOrderCreate":
        if not self.items:
            raise ValueError("At least one item is required.")
        return self


class ForwardingPreOrderFields(BaseModel):
    """Non-file fields of ``POST /api/v1/pre-orders/forwarding``.

    The endpoint is multipart, so these values arrive as form fields. The
    schema documents the contract and is reused by the frontend types.
    """

    store_name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    expected_domestic_tracking: str | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=2000)


class PreOrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_url: str
    product_name: str
    quantity: int
    unit_price_jpy: float
    options_description: str | None
    line_total_jpy: float

    @field_validator("unit_price_jpy", "line_total_jpy", mode="before")
    @classmethod
    def _decimal_to_float(cls, value: Decimal) -> float:
        return float(value)


class PreOrderOut(BaseModel):
    """Summary of a pre-order."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    type: PreOrderType
    status: PreOrderStatus
    total_items_price_jpy: float
    service_fee_jpy: float
    total_jpy: float
    receipt_url: str | None
    receipt_filename: str | None
    store_name: str | None
    expected_domestic_tracking: str | None
    domestic_tracking_code: str | None
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[PreOrderItemOut] = Field(default_factory=list)

    @field_validator(
        "service_fee_jpy", "total_items_price_jpy", "total_jpy", mode="before"
    )
    @classmethod
    def _decimal_to_float(cls, value: Decimal) -> float:
        return float(value)


class AdminPurchaseUpdate(BaseModel):
    """Body of ``PUT /api/v1/admin/pre-orders/{id}/purchase``."""

    status: PreOrderStatus = PreOrderStatus.purchased
    domestic_tracking_code: str | None = Field(default=None, max_length=64)
    admin_notes: str | None = Field(default=None, max_length=2000)
