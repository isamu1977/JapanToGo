"""Warehouse inventory models: suite items and inspection photos."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.models.base import (
    Base,
    SuiteItemStatus,
    TimestampMixin,
    sa_enum,
    uuid_pk,
)


class SuiteItem(Base, TimestampMixin):
    """An item physically held in the client's warehouse suite."""

    __tablename__ = "suite_items"
    __table_args__ = (
        Index("ix_suite_items_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pre_order_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("pre_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipment_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("shipments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description: Mapped[str] = mapped_column(String(512), nullable=False)
    weight_grams: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[SuiteItemStatus] = mapped_column(
        sa_enum(SuiteItemStatus, "suite_item_status"),
        nullable=False,
        default=SuiteItemStatus.in_storage,
        index=True,
    )
    tracking_domestic: Mapped[str | None] = mapped_column(String(64), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User", back_populates="suite_items")
    pre_order = relationship("PreOrder", back_populates="suite_items")
    shipment = relationship("Shipment", back_populates="suite_items")
    photos = relationship(
        "InspectionPhoto",
        back_populates="suite_item",
        cascade="all, delete-orphan",
        order_by="InspectionPhoto.display_order",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<SuiteItem {self.id} {self.weight_grams}g {self.status}>"


class InspectionPhoto(Base):
    """A photo taken by the warehouse operator while checking a parcel in."""

    __tablename__ = "inspection_photos"

    id: Mapped[uuid.UUID] = uuid_pk()
    suite_item_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suite_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    photo_url: Mapped[str] = mapped_column(String(512), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    suite_item = relationship("SuiteItem", back_populates="photos")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<InspectionPhoto {self.photo_url}>"
