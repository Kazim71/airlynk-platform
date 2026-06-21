"""
AirLynk — Payment API Routes.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.payments.schemas.payment import (
    CreateIntentRequest,
    PaymentIntentResponse,
    WebhookRequest,
)
from backend.services.payments.service.payment_service import PaymentService
from backend.shared.database.session import get_db_session
from backend.shared.middleware.rbac import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_intent(
    req: CreateIntentRequest,
    user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """Create a new payment intent."""
    service = PaymentService(session)
    return await service.create_intent(uuid.UUID(user["sub"]), req)


@router.post("/webhook/mock")
async def mock_webhook(
    req: WebhookRequest,
    user: dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """Process a mock payment gateway webhook."""
    service = PaymentService(session)
    return await service.process_webhook(req)
