"""Public contact form endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request, Response, status

from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.schemas.contact import ContactMessageCreate, ContactMessageResponse

logger = logging.getLogger("app.api.contact")

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a customer inquiry or support request",
)
@rate_limit(lambda: settings.rate_limit_calculator)
async def submit_contact(
    request: Request,
    response: Response,
    payload: ContactMessageCreate,
) -> ContactMessageResponse:
    """Receive a customer support or general inquiry message.

    Logs the incoming inquiry for team follow-up, logs an automated
    acknowledgment dispatch, and returns a confirmation to the user.
    """
    logger.info(
        "Received contact inquiry from %s <%s> regarding '%s' (Suite: %s)",
        payload.name,
        payload.email,
        payload.subject,
        payload.suite_code or "None",
    )

    # In production, this can trigger an async Celery task / email dispatch via SES or Resend
    # For now, we simulate dispatch and log the audit trail
    logger.info("Notification dispatched to support team: contato@japantogo.com")
    logger.info("Confirmation autoresponder queued for client: %s", payload.email)

    return ContactMessageResponse(
        success=True,
        message="Sua mensagem foi enviada com sucesso! Em breve nossa equipe entrará em contato.",
    )
