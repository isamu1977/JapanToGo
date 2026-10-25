"""Pre-order models: assisted purchases and pure redirections."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.models.base import (
    Base,
    PreOrderStatus,
    PreOrderType,
    TimestampMixin,
    sa_enum,
    uuid_pk,
)


class PreOrder(Base, TimestampMixin):
    """A client request placed either as *assisted purchase* or *redirection*."""

    __tablename__ = "pre_orders"
    __table_args__ = (
        Index("ix_pre_orders_user_status", "user_id", "status"),
        Index("ix_pre_orders_user_type", "user_id", "type"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[PreOrderType] = mapped_column(
        sa_enum(PreOrderType, "pre_order_type"), nullable=False, index=True
    )
    status: Mapped[PreOrderStatus] = mapped_column(
        sa_enum(PreOrderStatus, "pre_order_status"),
        nullable=False,
        default=PreOrderStatus.submitted,
        index=True,
    )

    # -- Financials (assisted purchase) ---------------------------------
    total_items_price_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    service_fee_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    total_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )

    # -- Redirection details --------------------------------------------
    receipt_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    receipt_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    store_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expected_domestic_tracking: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )

    # -- Operations ------------------------------------------------------
    domestic_tracking_code: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="pre_orders")
    items = relationship(
        "PreOrderItem",
        back_populates="pre_order",
        cascade="all, delete-orphan",
        order_by="PreOrderItem.id",
    )
    suite_items = relationship("SuiteItem", back_populates="pre_order")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<PreOrder {self.id} {self.type} {self.status}>"


class PreOrderItem(Base):
    """A single product line inside a pre-order."""

    __tablename__ = "pre_order_items"

    id: Mapped[uuid.UUID] = uuid_pk()
    pre_order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("pre_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    product_name: Mapped[str] = mapped_column(String(512), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    options_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    line_total_jpy: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )

    pre_order = relationship("PreOrder", back_populates="items")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<PreOrderItem {self.product_name} x{self.quantity}>"
