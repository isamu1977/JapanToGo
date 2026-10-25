"""Business rule tests: service fee floor and landed cost simulation."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.models.base import ShippingMethod
from app.services.fee_calculator import (
    calculate_landed_cost,
    calculate_service_fee,
    estimate_freight_jpy,
)


class TestServiceFee:
    def test_floor_applied_below_threshold(self) -> None:
        fee = calculate_service_fee(Decimal("6000"))

        assert fee.fee_jpy == Decimal("2000.00")
        assert fee.floor_applied is True
        assert fee.total_jpy == Decimal("8000.00")

    def test_proportional_fee_at_or_above_threshold(self) -> None:
        fee = calculate_service_fee(Decimal("25000"))

        assert fee.fee_jpy == Decimal("5000.00")
        assert fee.floor_applied is False
        assert fee.total_jpy == Decimal("30000.00")

    def test_threshold_is_exclusive(self) -> None:
        """Exactly ¥ 10.000 uses the proportional fee (20% = ¥ 2.000)."""
        fee = calculate_service_fee(Decimal("10000"))

        assert fee.fee_jpy == Decimal("2000.00")
        assert fee.floor_applied is False

    def test_just_below_threshold_uses_floor(self) -> None:
        fee = calculate_service_fee(Decimal("9999"))

        assert fee.proportional_fee_jpy == Decimal("1999.80")
        assert fee.fee_jpy == Decimal("2000.00")
        assert fee.floor_applied is True

    def test_proportional_fee_is_smaller_than_floor(self) -> None:
        fee = calculate_service_fee(Decimal("1000"))

        assert fee.proportional_fee_jpy == Decimal("200.00")
        assert fee.fee_jpy == Decimal("2000.00")
        assert fee.floor_applied is True


class TestFreightEstimation:
    def test_ems_base_band(self) -> None:
        assert estimate_freight_jpy(ShippingMethod.ems, 500) == 3000

    def test_ems_adds_one_band_per_extra_500g(self) -> None:
        assert estimate_freight_jpy(ShippingMethod.ems, 1000) == 3600
        assert estimate_freight_jpy(ShippingMethod.ems, 1500) == 4200

    def test_small_packet_is_cheaper_than_ems(self) -> None:
        assert estimate_freight_jpy(ShippingMethod.small_packet, 1000) < (
            estimate_freight_jpy(ShippingMethod.ems, 1000)
        )

    def test_small_packet_rejects_oversized_parcels(self) -> None:
        with pytest.raises(ValueError):
            estimate_freight_jpy(ShippingMethod.small_packet, 2500)


class TestLandedCost:
    def test_assisted_purchase_includes_service_fee_and_taxes(self) -> None:
        result = calculate_landed_cost(
            item_price_jpy=Decimal("8000"),
            weight_grams=1000,
            order_type="assisted_purchase",
            shipping_method="ems",
        )

        # 20% of 8.000 is 1.600 but the ¥ 2.000 floor applies.
        assert result.service_fee_jpy == Decimal("2000.00")
        assert result.service_fee_floor_applied is True
        assert result.freight_jpy == Decimal("3600")
        assert result.total_jpy == Decimal("13600.00")

        # RTS 60% + ICMS charged por dentro (over the customs value + RTS).
        assert float(result.rts_brl) == pytest.approx(
            float(result.customs_value_brl * Decimal("0.60")), abs=0.01
        )
        assert float(result.icms_brl) == pytest.approx(
            float(
                (result.customs_value_brl + result.rts_brl) * Decimal("0.18")
            ),
            abs=0.01,
        )
        assert float(result.total_brl) == pytest.approx(
            float(
                result.customs_value_brl
                + result.rts_brl
                + result.icms_brl
                + result.service_fee_brl
                + result.freight_brl
            ),
            abs=0.01,
        )

    def test_forwarding_excludes_the_service_fee(self) -> None:
        result = calculate_landed_cost(
            item_price_jpy=Decimal("15000"),
            weight_grams=500,
            order_type="forwarding",
            shipping_method="small_packet",
        )

        assert result.service_fee_jpy == Decimal("0.00")
        assert result.service_fee_floor_applied is False
        assert result.freight_jpy == Decimal("1500")
        assert result.total_jpy == Decimal("16500.00")

    def test_exchange_rate_includes_the_safety_spread(self) -> None:
        result = calculate_landed_cost(
            item_price_jpy=Decimal("10000"),
            weight_grams=500,
            order_type="forwarding",
        )

        assert result.exchange_rate_brl > 0.038
        assert result.exchange_rate_spread == Decimal("0.02")

    def test_breakdown_covers_every_component(self) -> None:
        result = calculate_landed_cost(
            item_price_jpy=Decimal("10000"),
            weight_grams=1000,
        )

        labels = [line.label for line in result.breakdown]
        assert len(labels) == 5
        assert result.disclaimer
