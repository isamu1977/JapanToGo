"""User model and the PostgreSQL sequence backing ``suite_code``."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Sequence, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.models.base import Base, TimestampMixin, UserRole, sa_enum, uuid_pk

#: Native PostgreSQL sequence used to allocate immutable suite codes.
#: The first allocated value is ``1001`` which renders as ``JTG-1001``.
suite_code_sequence = Sequence(
    "suite_code_seq",
    metadata=Base.metadata,
    start=1001,
    increment=1,
)

SUITE_CODE_PREFIX = "JTG-"


class User(Base, TimestampMixin):
    """Application account.

    Clients receive an immutable ``suite_code`` (``JTG-XXXX``) used as the
    warehouse identifier; administrators do not get one.
    """

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_role_is_active", "role", "is_active"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    cpf_tax_id: Mapped[str | None] = mapped_column(String(14), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        sa_enum(UserRole, "user_role"),
        nullable=False,
        default=UserRole.client,
        index=True,
    )
    suite_code: Mapped[str | None] = mapped_column(
        String(16), unique=True, nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    pre_orders = relationship(
        "PreOrder", back_populates="user", cascade="all, delete-orphan"
    )
    suite_items = relationship(
        "SuiteItem", back_populates="user", cascade="all, delete-orphan"
    )
    shipments = relationship(
        "Shipment", back_populates="user", cascade="all, delete-orphan"
    )
    legal_acceptances = relationship(
        "LegalTermsAcceptance", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.email} role={self.role} suite={self.suite_code}>"


class LegalTermsAcceptance(Base):
    """Audit trail of legal documents accepted by a user."""

    __tablename__ = "legal_terms_acceptance"
    __table_args__ = (
        Index("ix_legal_terms_acceptance_user_term", "user_id", "term_type"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    term_type: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="legal_acceptances")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<LegalTermsAcceptance {self.term_type} v{self.version}>"
