"""Export shipment data in the Japan Post "International Mail My Page" format.

The Japan Post web portal is filled in manually, so the service produces a
structured payload plus a plain-text block that can be copied into the portal
(or downloaded as a text/CSV file).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable

#: ISO 3166-1 alpha-2 country code of the destination.
DEFAULT_COUNTRY_CODE = "BR"

#: Fields expected by the International Mail My Page shipment form.
JAPAN_POST_FIELDS = (
    "recipient_name",
    "country_code",
    "postal_code",
    "state_city",
    "address_line_1",
    "address_line_2",
    "recipient_phone",
    "contents",
)


@dataclass
class CustomsLine:
    """A single customs declaration line."""

    description: str
    quantity: int
    declared_value_jpy: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "quantity": self.quantity,
            "declared_value_jpy": self.declared_value_jpy,
        }


@dataclass
class JapanPostExport:
    """Structured export payload for one shipment."""

    recipient_name: str
    country_code: str
    postal_code: str
    state_city: str
    address_line_1: str
    address_line_2: str
    recipient_phone: str
    contents: list[CustomsLine] = field(default_factory=list)
    total_declared_value_jpy: float = 0.0
    total_quantity: int = 0
    shipping_method: str = ""
    total_weight_grams: int = 0
    international_tracking_code: str | None = None
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipient_name": self.recipient_name,
            "country_code": self.country_code,
            "postal_code": self.postal_code,
            "state_city": self.state_city,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "recipient_phone": self.recipient_phone,
            "contents": [line.to_dict() for line in self.contents],
            "total_declared_value_jpy": self.total_declared_value_jpy,
            "total_quantity": self.total_quantity,
            "shipping_method": self.shipping_method,
            "total_weight_grams": self.total_weight_grams,
            "international_tracking_code": self.international_tracking_code,
            "generated_at": self.generated_at,
        }

    def to_text(self) -> str:
        """Render the payload as a copy-paste friendly text block."""
        lines = [
            "===== Japan Post International Mail My Page =====",
            f"Recipient Name     : {self.recipient_name}",
            f"Country Code       : {self.country_code}",
            f"Postal Code        : {self.postal_code}",
            f"State / City       : {self.state_city}",
            f"Address Line 1     : {self.address_line_1}",
            f"Address Line 2     : {self.address_line_2 or '-'}",
            f"Recipient Phone    : {self.recipient_phone}",
            "",
            "--- Customs Contents (EN) ---",
        ]

        if self.contents:
            for index, line in enumerate(self.contents, start=1):
                lines.append(
                    f"{index}. {line.description} | Qty: {line.quantity} | "
                    f"Declared Value: JPY {line.declared_value_jpy:,.0f}"
                )
        else:
            lines.append("(no customs lines)")

        lines.extend(
            [
                "",
                f"Total Quantity         : {self.total_quantity}",
                f"Total Declared Value   : JPY {self.total_declared_value_jpy:,.0f}",
                f"Shipping Method        : {self.shipping_method}",
                f"Total Weight (grams)   : {self.total_weight_grams}",
                "===============================================",
            ]
        )
        return "\n".join(lines)

    def to_csv(self) -> str:
        """Render the customs lines as CSV (one row per line item)."""
        header = (
            "recipient_name,country_code,postal_code,state_city,address_line_1,"
            "address_line_2,recipient_phone,item_name,quantity,declared_value_jpy"
        )
        rows = []
        for line in self.contents:
            rows.append(
                ",".join(
                    _csv_cell(value)
                    for value in (
                        self.recipient_name,
                        self.country_code,
                        self.postal_code,
                        self.state_city,
                        self.address_line_1,
                        self.address_line_2,
                        self.recipient_phone,
                        line.description,
                        line.quantity,
                        f"{line.declared_value_jpy:.2f}",
                    )
                )
            )
        return "\n".join([header, *rows])


def _csv_cell(value: Any) -> str:
    text = str(value if value is not None else "")
    if any(char in text for char in [",", '"', "\n"]):
        escaped = text.replace('"', '""')
        return f'"{escaped}"'
    return text


def _split_address(address: str) -> tuple[str, str]:
    """Split a free-form address into two lines for the Japan Post form."""
    parts = [part.strip() for part in (address or "").split("\n") if part.strip()]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def build_export(
    shipment: Any,
    *,
    customs_lines: Iterable[CustomsLine] | None = None,
    default_country_code: str = DEFAULT_COUNTRY_CODE,
) -> JapanPostExport:
    """Build the Japan Post export payload from a ``Shipment`` record.

    ``customs_lines`` may be supplied to override the declaration stored on
    the shipment (e.g. when the operator edits the declaration before
    dispatch).
    """
    address_line_1, address_line_2 = _split_address(
        getattr(shipment, "recipient_address", "") or ""
    )

    if customs_lines is None:
        declaration = getattr(shipment, "customs_declaration", None) or {}
        raw_items = declaration.get("items", []) if isinstance(declaration, dict) else []
        customs_lines = [
            CustomsLine(
                description=str(item.get("description", "")),
                quantity=int(item.get("quantity", 1) or 1),
                declared_value_jpy=float(item.get("declared_value_jpy", 0) or 0),
            )
            for item in raw_items
        ]

    lines = list(customs_lines)
    state_city = " / ".join(
        part
        for part in (
            getattr(shipment, "recipient_state", None),
            getattr(shipment, "recipient_city", None),
        )
        if part
    )

    return JapanPostExport(
        recipient_name=getattr(shipment, "recipient_name", "") or "",
        country_code=default_country_code,
        postal_code=getattr(shipment, "recipient_postal_code", "") or "",
        state_city=state_city,
        address_line_1=address_line_1,
        address_line_2=address_line_2,
        recipient_phone=getattr(shipment, "recipient_phone", "") or "",
        contents=lines,
        total_declared_value_jpy=sum(line.declared_value_jpy for line in lines),
        total_quantity=sum(line.quantity for line in lines),
        shipping_method=_method_value(getattr(shipment, "shipping_method", "")),
        total_weight_grams=int(getattr(shipment, "total_weight_grams", 0) or 0),
        international_tracking_code=getattr(
            shipment, "international_tracking_code", None
        ),
        generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
    )


def _method_value(method: Any) -> str:
    return getattr(method, "value", method) or ""
