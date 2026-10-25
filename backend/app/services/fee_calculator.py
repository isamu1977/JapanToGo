"""Business rules: assisted purchase service fee and landed cost simulation."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Literal

from app.core.config import settings
from app.models.base import PreOrderType, ShippingMethod

OrderType = Literal["assisted_purchase", "forwarding"]

_CENT = Decimal("0.01")


def _money(value: Decimal | int | float) -> Decimal:
    """Round a monetary amount to 2 decimal places."""
    return Decimal(str(value)).quantize(_CENT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Assisted purchase service fee
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ServiceFee:
    """Result of the assisted purchase fee calculation."""

    items_total_jpy: Decimal
    fee_rate: Decimal
    proportional_fee_jpy: Decimal
    fee_jpy: Decimal
    floor_applied: bool
    minimum_fee_jpy: Decimal
    total_jpy: Decimal

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: float(value) if isinstance(value, Decimal) else value
                for key, value in data.items()}


def calculate_service_fee(
    items_total_jpy: Decimal | int | float,
    *,
    rate: Decimal | None = None,
    minimum_fee_jpy: Decimal | int | None = None,
    floor_threshold_jpy: Decimal | int | None = None,
) -> ServiceFee:
    """Apply the 20% service fee with the ¥ 2.000 minimum floor rule.

    The floor only applies when the total item price is **strictly below**
    ¥ 10.000. For example:

    * ¥ 6.000 in items  -> fee ¥ 2.000 (floor) -> total ¥ 8.000
    * ¥ 25.000 in items -> fee ¥ 5.000 (20%)   -> total ¥ 30.000
    """
    items_total = _money(items_total_jpy)
    rate_dec = rate if rate is not None else Decimal(str(settings.service_fee_rate))
    minimum = (
        _money(minimum_fee_jpy)
        if minimum_fee_jpy is not None
        else Decimal(settings.service_fee_min_jpy)
    )
    threshold = (
        Decimal(str(floor_threshold_jpy))
        if floor_threshold_jpy is not None
        else Decimal(settings.service_fee_floor_threshold_jpy)
    )

    proportional = _money(items_total * rate_dec)
    floor_applied = items_total < threshold and proportional < minimum
    fee = minimum if floor_applied else proportional
    total = _money(items_total + fee)

    return ServiceFee(
        items_total_jpy=items_total,
        fee_rate=rate_dec,
        proportional_fee_jpy=proportional,
        fee_jpy=fee,
        floor_applied=floor_applied,
        minimum_fee_jpy=minimum,
        total_jpy=total,
    )


# ---------------------------------------------------------------------------
# Freight estimation
# ---------------------------------------------------------------------------
def estimate_freight_jpy(
    shipping_method: ShippingMethod | str,
    weight_grams: int,
) -> int:
    """Estimate the international shipping cost in JPY.

    The tariff is a base price covering the first 500 g plus a fixed amount
    for every additional 500 g band.
    """
    method = ShippingMethod(shipping_method)
    grams = max(1, int(weight_grams or 1))

    if method is ShippingMethod.ems:
        base, per_band = settings.ems_base_jpy, settings.ems_per_500g_jpy
    else:
        if grams > settings.small_packet_max_grams:
            raise ValueError(
                "Small Packet cannot exceed "
                f"{settings.small_packet_max_grams} g (received {grams} g)."
            )
        base, per_band = (
            settings.small_packet_base_jpy,
            settings.small_packet_per_500g_jpy,
        )

    extra_bands = max(0, math.ceil(grams / 500) - 1)
    return int(base + extra_bands * per_band)


# ---------------------------------------------------------------------------
# Landed cost
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LandedCostBreakdown:
    """A single line of the landed cost breakdown."""

    label: str
    label_ja: str
    amount_jpy: Decimal
    amount_brl: Decimal


@dataclass(frozen=True)
class LandedCost:
    """Full landed cost simulation for the client facing simulator."""

    order_type: OrderType
    shipping_method: str
    item_price_jpy: Decimal
    weight_grams: int
    exchange_rate_brl: Decimal
    exchange_rate_spread: Decimal
    item_price_brl: Decimal
    service_fee_jpy: Decimal
    service_fee_brl: Decimal
    service_fee_floor_applied: bool
    freight_jpy: Decimal
    freight_brl: Decimal
    customs_value_brl: Decimal
    rts_brl: Decimal
    icms_brl: Decimal
    total_jpy: Decimal
    total_brl: Decimal
    breakdown: list[LandedCostBreakdown] = field(default_factory=list)
    disclaimer: str = (
        "Estimativa baseada na cotação de referência e na alíquota fiscal "
        "estimada. O valor final pode variar conforme a cotação do dia, o "
        "regime tributário e a taxa aplicada pela transportadora."
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["breakdown"] = [
            {
                "label": line.label,
                "label_ja": line.label_ja,
                "amount_jpy": float(line.amount_jpy),
                "amount_brl": float(line.amount_brl),
            }
            for line in self.breakdown
        ]
        for key, value in list(data.items()):
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data


def effective_exchange_rate(
    rate: float | None = None, spread: float | None = None
) -> Decimal:
    """Reference JPY -> BRL rate including the safety spread."""
    base = Decimal(str(rate if rate is not None else settings.jpy_to_brl_rate))
    margin = Decimal(str(spread if spread is not None else settings.exchange_rate_spread))
    return (base * (Decimal("1") + margin)).quantize(
        Decimal("0.00000001"), rounding=ROUND_HALF_UP
    )


def calculate_landed_cost(
    *,
    item_price_jpy: Decimal | int | float,
    weight_grams: int,
    order_type: OrderType | PreOrderType = PreOrderType.assisted_purchase,
    shipping_method: ShippingMethod | str = ShippingMethod.ems,
    exchange_rate: float | None = None,
    spread: float | None = None,
) -> LandedCost:
    """Simulate the total landed cost of a purchase or a redirection.

    * the 20% assisted purchase fee is only charged for ``assisted_purchase``
    * freight is estimated from the parcel weight
    * Brazilian import taxes are projected as RTS 60% + ICMS charged
      "por dentro" (i.e. over the customs value + RTS)
    """
    kind = order_type.value if isinstance(order_type, PreOrderType) else order_type
    if kind not in {"assisted_purchase", "forwarding"}:
        raise ValueError(f"Unsupported order type: {order_type}")

    rate = effective_exchange_rate(exchange_rate, spread)
    margin = Decimal(
        str(spread if spread is not None else settings.exchange_rate_spread)
    )

    item_price = _money(item_price_jpy)
    item_price_brl = _money(item_price * rate)

    if kind == "assisted_purchase":
        fee = calculate_service_fee(item_price)
        service_fee_jpy = fee.fee_jpy
        floor_applied = fee.floor_applied
    else:
        service_fee_jpy = Decimal("0.00")
        floor_applied = False

    service_fee_brl = _money(service_fee_jpy * rate)

    freight_jpy = Decimal(str(estimate_freight_jpy(shipping_method, weight_grams)))
    freight_brl = _money(freight_jpy * rate)

    customs_value_brl = item_price_brl
    rts_brl = _money(customs_value_brl * Decimal(str(settings.rts_rate)))
    icms_base = customs_value_brl + rts_brl
    icms_brl = _money(icms_base * Decimal(str(settings.icms_rate)))

    total_brl = _money(
        customs_value_brl + rts_brl + icms_brl + service_fee_brl + freight_brl
    )
    total_jpy = _money(item_price + service_fee_jpy + freight_jpy)

    breakdown = [
        LandedCostBreakdown(
            "Item value", "商品の代金", item_price, item_price_brl
        ),
        LandedCostBreakdown(
            "JapanToGo service fee (20%)",
            "サービス手数料 (20%)",
            service_fee_jpy,
            service_fee_brl,
        ),
        LandedCostBreakdown(
            "Estimated international freight",
            "国際送料の見積り",
            freight_jpy,
            freight_brl,
        ),
        LandedCostBreakdown(
            "Brazilian import tax (RTS 60%)",
            "輸入税 (RTS 60%)",
            Decimal("0.00"),
            rts_brl,
        ),
        LandedCostBreakdown(
            "ICMS (calculated por dentro)",
            "ICMS (内税計算)",
            Decimal("0.00"),
            icms_brl,
        ),
    ]

    return LandedCost(
        order_type=kind,  # type: ignore[arg-type]
        shipping_method=ShippingMethod(shipping_method).value,
        item_price_jpy=item_price,
        weight_grams=int(weight_grams),
        exchange_rate_brl=rate,
        exchange_rate_spread=margin,
        item_price_brl=item_price_brl,
        service_fee_jpy=service_fee_jpy,
        service_fee_brl=service_fee_brl,
        service_fee_floor_applied=floor_applied,
        freight_jpy=freight_jpy,
        freight_brl=freight_brl,
        customs_value_brl=customs_value_brl,
        rts_brl=rts_brl,
        icms_brl=icms_brl,
        total_jpy=total_jpy,
        total_brl=total_brl,
        breakdown=breakdown,
    )
