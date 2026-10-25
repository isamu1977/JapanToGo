"""Shared column helpers and enumerations used across the models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """Adds ``created_at`` / ``updated_at`` bookkeeping columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def uuid_pk() -> Mapped[uuid.UUID]:
    """Primary key column using a UUID v4 default."""
    return mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


def sa_enum(enum_cls: type[enum.Enum], name: str) -> SAEnum:
    """Build a native PostgreSQL enum that stores the *values* of ``enum_cls``."""
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        validate_strings=True,
        values_callable=lambda e: [member.value for member in e],
    )


class UserRole(str, enum.Enum):
    client = "client"
    admin = "admin"


class PreOrderType(str, enum.Enum):
    assisted_purchase = "assisted_purchase"
    forwarding = "forwarding"


class PreOrderStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    purchased = "purchased"
    received = "received"
    cancelled = "cancelled"


class SuiteItemStatus(str, enum.Enum):
    in_storage = "in_storage"
    consolidation_requested = "consolidation_requested"
    shipped = "shipped"
    discarded = "discarded"


class ShippingMethod(str, enum.Enum):
    ems = "ems"
    small_packet = "small_packet"


class ShipmentStatus(str, enum.Enum):
    requested = "requested"
    packed = "packed"
    paid = "paid"
    dispatched = "dispatched"
    delivered = "delivered"


class LegalTermType(str, enum.Enum):
    terms_of_service = "terms_of_service"
    privacy_policy = "privacy_policy"
    specified_commercial_transactions = "specified_commercial_transactions"


__all__ = [
    "Base",
    "LegalTermType",
    "PreOrderStatus",
    "PreOrderType",
    "ShipmentStatus",
    "ShippingMethod",
    "SuiteItemStatus",
    "TimestampMixin",
    "UserRole",
    "sa_enum",
    "uuid_pk",
]
