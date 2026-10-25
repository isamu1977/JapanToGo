"""Shipment model: consolidation, customs declaration and dispatch."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.models.base import (
    Base,
    ShipmentStatus,
    ShippingMethod,
    TimestampMixin,
    sa_enum,
    uuid_pk,
)


class Shipment(Base, TimestampMixin):
    """An international parcel consolidating one or more suite items."""

    __tablename__ = "shipments"
    __table_args__ = (
        Index("ix_shipments_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    shipping_method: Mapped[ShippingMethod] = mapped_column(
        sa_enum(ShippingMethod, "shipping_method"), nullable=False, index=True
    )
    status: Mapped[ShipmentStatus] = mapped_column(
        sa_enum(ShipmentStatus, "shipment_status"),
        nullable=False,
        default=ShipmentStatus.requested,
        index=True,
    )
    total_weight_grams: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    shipping_fee_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    international_tracking_code: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )

    # -- Recipient (Brazil) ------------------------------------------------
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_cpf: Mapped[str] = mapped_column(String(32), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    recipient_postal_code: Mapped[str] = mapped_column(String(16), nullable=False)
    recipient_address: Mapped[str] = mapped_column(Text, nullable=False)
    recipient_state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    recipient_city: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # -- Customs declaration ----------------------------------------------
    customs_declaration: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True
    )

    dispatched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="shipments")
    suite_items = relationship("SuiteItem", back_populates="shipment")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Shipment {self.id} {self.shipping_method} {self.status}>"
