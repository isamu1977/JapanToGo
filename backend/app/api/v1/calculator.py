"""Public landed cost calculator endpoint (no authentication required)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.schemas.calculator import LandedCostRequest, LandedCostResponse
from app.services.fee_calculator import calculate_landed_cost

router = APIRouter(prefix="/calculator", tags=["calculator"])


@router.post(
    "/simulate",
    response_model=LandedCostResponse,
    summary="Simulate the landed cost of a purchase or a redirection",
)
@rate_limit(lambda: settings.rate_limit_calculator)
async def simulate(
    request: Request,
    response: Response,
    payload: LandedCostRequest,
) -> LandedCostResponse:
    """Estimate the total landed cost in JPY and BRL.

    The projection includes the JapanToGo service fee (20% with the ¥ 2.000
    floor for assisted purchases only), an international freight estimate and
    the Brazilian import taxes (RTS 60% + ICMS calculated "por dentro").
    """
    result = calculate_landed_cost(
        item_price_jpy=payload.item_price_jpy,
        weight_grams=payload.weight_grams,
        order_type=payload.order_type,
        shipping_method=payload.shipping_method,
    )
    return LandedCostResponse(**result.to_dict())
