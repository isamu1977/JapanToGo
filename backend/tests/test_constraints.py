"""Database constraint tests (PostgreSQL integrity rules)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import PreOrderStatus, PreOrderType, SuiteItemStatus, UserRole
from app.models.pre_order import PreOrder
from app.models.suite_item import SuiteItem
from app.models.user import User


async def _make_user(
    db: AsyncSession, *, email: str, suite_code: str | None = None
) -> User:
    user = User(
        email=email,
        hashed_password="hashed",
        full_name="Constraint User",
        phone="+55-11-90000-0000",
        role=UserRole.client,
        is_active=True,
        suite_code=suite_code,
    )
    db.add(user)
    await db.commit()
    return user


class TestUserConstraints:
    async def test_email_must_be_unique(self, db_session: AsyncSession) -> None:
        await _make_user(db_session, email="dup@example.com")

        db_session.add(
            User(
                email="dup@example.com",
                hashed_password="hashed",
                full_name="Another",
                phone="+55-11-90000-0001",
                role=UserRole.client,
                is_active=True,
            )
        )
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_suite_code_must_be_unique(
        self, db_session: AsyncSession
    ) -> None:
        await _make_user(db_session, email="a@example.com", suite_code="JTG-7001")

        db_session.add(
            User(
                email="b@example.com",
                hashed_password="hashed",
                full_name="Another",
                phone="+55-11-90000-0001",
                role=UserRole.client,
                is_active=True,
                suite_code="JTG-7001",
            )
        )
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_email_is_required(self, db_session: AsyncSession) -> None:
        db_session.add(
            User(
                email=None,  # type: ignore[arg-type]
                hashed_password="hashed",
                full_name="No email",
                phone="+55-11-90000-0001",
                role=UserRole.client,
                is_active=True,
            )
        )
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()


class TestSuiteCodeSequence:
    async def test_sequence_allocates_incrementing_codes(
        self, db_session: AsyncSession
    ) -> None:
        first = await db_session.execute(
            text("SELECT 'JTG-' || lpad(nextval('suite_code_seq')::text, 4, '0')")
        )
        first_value = first.scalar_one()
        second = await db_session.execute(
            text("SELECT 'JTG-' || lpad(nextval('suite_code_seq')::text, 4, '0')")
        )
        second_value = second.scalar_one()

        assert first_value.startswith("JTG-")
        assert int(second_value[4:]) == int(first_value[4:]) + 1


class TestForeignKeys:
    async def test_pre_order_requires_an_existing_user(
        self, db_session: AsyncSession
    ) -> None:
        db_session.add(
            PreOrder(
                user_id=uuid.uuid4(),
                type=PreOrderType.assisted_purchase,
                status=PreOrderStatus.submitted,
                total_items_price_jpy=Decimal("1000.00"),
                service_fee_jpy=Decimal("2000.00"),
                total_jpy=Decimal("3000.00"),
            )
        )
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_suite_item_requires_an_existing_user(
        self, db_session: AsyncSession
    ) -> None:
        db_session.add(
            SuiteItem(
                user_id=uuid.uuid4(),
                description="Orphan item",
                weight_grams=100,
                status=SuiteItemStatus.in_storage,
            )
        )
        with pytest.raises(IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_deleting_a_user_cascades(
        self, db_session: AsyncSession
    ) -> None:
        user = await _make_user(db_session, email="cascade@example.com")
        db_session.add(
            PreOrder(
                user_id=user.id,
                type=PreOrderType.assisted_purchase,
                status=PreOrderStatus.submitted,
                total_items_price_jpy=Decimal("1000.00"),
                service_fee_jpy=Decimal("2000.00"),
                total_jpy=Decimal("3000.00"),
            )
        )
        await db_session.commit()

        await db_session.delete(user)
        await db_session.commit()

        remaining = await db_session.execute(select(PreOrder))
        assert remaining.scalars().all() == []
