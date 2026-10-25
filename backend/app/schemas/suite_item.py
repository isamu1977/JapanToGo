"""Schemas for suite inventory and the warehouse address."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.base import SuiteItemStatus


class InspectionPhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    photo_url: str
    display_order: int
    created_at: datetime


class SuiteItemOut(BaseModel):
    """A single item held in the client's warehouse suite."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pre_order_id: uuid.UUID | None
    shipment_id: uuid.UUID | None
    description: str
    weight_grams: int
    status: SuiteItemStatus
    tracking_domestic: str | None
    received_at: datetime | None
    created_at: datetime
    photos: list[InspectionPhotoOut] = Field(default_factory=list)


class SuiteSummaryOut(BaseModel):
    """Aggregate view of the client's suite."""

    suite_code: str | None
    item_count: int
    total_weight_grams: int
    items: list[SuiteItemOut] = Field(default_factory=list)


class WarehouseAddressOut(BaseModel):
    """Warehouse address rendered in Japanese and in the Latin alphabet."""

    suite_code: str | None
    ja: dict[str, Any]
    romaji: dict[str, Any]
