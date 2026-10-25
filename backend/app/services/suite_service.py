"""Warehouse suite services: suite code allocation and address rendering."""

from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import SUITE_CODE_PREFIX

#: JapanToGo warehouse address in Japanese (kanji / kana).
WAREHOUSE_ADDRESS_JA: dict[str, str] = {
    "company": "株式会社ジャパン・トゥ・ゴー",
    "postal_code": "〒540-0027",
    "prefecture": "大阪府大阪市天王寺区",
    "city": "大阪市天王寺区",
    "street": "茶屋町1丁目15番",
    "building": "リバーシティ 4F",
    "telephone": "+81-6-0000-0000",
}

#: The same address transliterated into the Latin alphabet.
WAREHOUSE_ADDRESS_ROMAJI: dict[str, str] = {
    "company": "JapanToGo Co., Ltd.",
    "postal_code": "540-0027",
    "prefecture": "Osaka-fu, Osaka-shi",
    "city": "Tennaishi-ku, Osaka-shi",
    "street": "1-15 Chayamachi",
    "building": "Rivercity Bldg 4F",
    "telephone": "+81-6-0000-0000",
}


async def generate_suite_code(db: AsyncSession) -> str:
    """Allocate the next immutable suite code (``JTG-XXXX``).

    The value comes from the native PostgreSQL sequence ``suite_code_seq`` so
    concurrent registrations can never collide.
    """
    result = await db.execute(
        text("SELECT 'JTG-' || lpad(nextval('suite_code_seq')::text, 4, '0')")
    )
    suite_code = result.scalar_one()
    return str(suite_code)


def build_warehouse_address(suite_code: str | None) -> dict[str, Any]:
    """Return the warehouse address with the suite code injected.

    The complement line carries the suite code (``#JTG-XXXX``) which Japanese
    carriers require when forwarding a parcel.
    """
    complement_ja = f"＃{suite_code}" if suite_code else "（部屋番号必須）"
    complement_romaji = f"Suite {suite_code}" if suite_code else "(Suite number required)"

    return {
        "ja": {
            "company": WAREHOUSE_ADDRESS_JA["company"],
            "postal_code": WAREHOUSE_ADDRESS_JA["postal_code"],
            "prefecture": WAREHOUSE_ADDRESS_JA["prefecture"],
            "city": WAREHOUSE_ADDRESS_JA["city"],
            "street": WAREHOUSE_ADDRESS_JA["street"],
            "building": WAREHOUSE_ADDRESS_JA["building"],
            "complement": complement_ja,
            "telephone": WAREHOUSE_ADDRESS_JA["telephone"],
            "full": _compose_address_ja(suite_code),
        },
        "romaji": {
            "company": WAREHOUSE_ADDRESS_ROMAJI["company"],
            "postal_code": WAREHOUSE_ADDRESS_ROMAJI["postal_code"],
            "prefecture": WAREHOUSE_ADDRESS_ROMAJI["prefecture"],
            "city": WAREHOUSE_ADDRESS_ROMAJI["city"],
            "street": WAREHOUSE_ADDRESS_ROMAJI["street"],
            "building": WAREHOUSE_ADDRESS_ROMAJI["building"],
            "complement": complement_romaji,
            "telephone": WAREHOUSE_ADDRESS_ROMAJI["telephone"],
            "full": _compose_address_romaji(suite_code),
        },
    }


def _compose_address_ja(suite_code: str | None) -> str:
    complement = f" {suite_code}" if suite_code else ""
    return (
        f"{WAREHOUSE_ADDRESS_JA['postal_code']} "
        f"{WAREHOUSE_ADDRESS_JA['prefecture']}"
        f"{WAREHOUSE_ADDRESS_JA['street']} "
        f"{WAREHOUSE_ADDRESS_JA['building']}{complement}"
    )


def _compose_address_romaji(suite_code: str | None) -> str:
    complement = f", Suite {suite_code}" if suite_code else ""
    return (
        f"{WAREHOUSE_ADDRESS_ROMAJI['company']}\n"
        f"{WAREHOUSE_ADDRESS_ROMAJI['building']}, "
        f"{WAREHOUSE_ADDRESS_ROMAJI['street']}\n"
        f"{WAREHOUSE_ADDRESS_ROMAJI['city']} "
        f"{WAREHOUSE_ADDRESS_ROMAJI['postal_code']}, JAPAN{complement}\n"
        f"TEL: {WAREHOUSE_ADDRESS_ROMAJI['telephone']}"
    )


def suite_code_prefix() -> str:
    """The prefix used by every suite code (``JTG-``)."""
    return SUITE_CODE_PREFIX
