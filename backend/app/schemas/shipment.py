"""Schemas for shipments (consolidation, customs declaration, dispatch)."""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.base import ShipmentStatus, ShippingMethod

_CPF_PATTERN = re.compile(r"^\d{11}$")


def _validate_cpf(value: str) -> str:
    """Validate a Brazilian CPF (11 digits + check digits)."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 11 or len(set(digits)) == 1:
        raise ValueError("CPF must contain 11 digits.")
    for position in (9, 10):
        check = 0
        for index in range(position):
            check += int(digits[index]) * (position + 1 - index)
        remainder = (check * 10) % 11
        expected = 0 if remainder == 10 else remainder
        if expected != int(digits[position]):
            raise ValueError("CPF check digits are invalid.")
    return digits


class CustomsItemInput(BaseModel):
    """A customs declaration line.

    ``declared_value_jpy`` is the **total** declared value of the line
    (all units combined), which is how the Japan Post form is filled in.
    """

    description: str = Field(min_length=1, max_length=255)
    quantity: int = Field(ge=1, le=999)
    declared_value_jpy: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class CustomsDeclarationInput(BaseModel):
    """The customs declaration attached to a shipment request."""

    items: list[CustomsItemInput] = Field(min_length=1)
    invoice_number: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def _require_items(self) -> "CustomsDeclarationInput":
        if not self.items:
            raise ValueError("The customs declaration must contain at least one item.")
        return self

    def to_json(self) -> dict[str, Any]:
        return {
            "invoice_number": self.invoice_number,
            "items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "declared_value_jpy": float(item.declared_value_jpy),
                }
                for item in self.items
            ],
            "total_declared_value_jpy": float(
                sum(
                    (item.declared_value_jpy for item in self.items),
                    Decimal("0"),
                )
            ),
        }


class ShipmentRequestCreate(BaseModel):
    """Body of ``POST /api/v1/shipments/request``."""

    suite_item_ids: list[uuid.UUID] = Field(min_length=1)
    shipping_method: ShippingMethod
    customs_declaration: CustomsDeclarationInput
    recipient_name: str = Field(min_length=2, max_length=255)
    recipient_cpf: str
    recipient_phone: str = Field(min_length=8, max_length=32)
    recipient_postal_code: str = Field(min_length=5, max_length=16)
    recipient_address: str = Field(min_length=5, max_length=2000)
    recipient_state: str | None = Field(default=None, max_length=64)
    recipient_city: str | None = Field(default=None, max_length=128)

    @field_validator("recipient_cpf")
    @classmethod
    def _check_cpf(cls, value: str) -> str:
        return _validate_cpf(value)

    @field_validator("suite_item_ids")
    @classmethod
    def _unique_ids(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(set(value)) != len(value):
            raise ValueError("The suite item list contains duplicates.")
        return value


class ShipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    shipping_method: ShippingMethod
    status: ShipmentStatus
    total_weight_grams: int
    shipping_fee_jpy: float
    international_tracking_code: str | None
    recipient_name: str
    recipient_cpf: str
    recipient_phone: str
    recipient_postal_code: str
    recipient_address: str
    recipient_state: str | None
    recipient_city: str | None
    customs_declaration: dict[str, Any] | None
    dispatched_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_validator("shipping_fee_jpy", mode="before")
    @classmethod
    def _decimal_to_float(cls, value: Decimal) -> float:
        return float(value)


class AdminDispatchUpdate(BaseModel):
    """Body of ``PUT /api/v1/admin/shipments/{id}/dispatch``."""

    status: ShipmentStatus = ShipmentStatus.dispatched
    total_weight_grams: int | None = Field(default=None, ge=1)
    shipping_fee_jpy: Decimal = Field(default=Decimal("0"), ge=0)
    international_tracking_code: str | None = Field(default=None, max_length=64)
    admin_notes: str | None = Field(default=None, max_length=2000)
