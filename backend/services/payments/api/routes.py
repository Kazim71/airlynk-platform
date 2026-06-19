"""
AirLynk — Payment API Routes.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from backend.shared.database.session import get_db_session
from backend.services.payments.schemas.payment import CreateIntentRequest, PaymentIntentResponse, WebhookRequest
from backend.services.payments.service.payment_service import PaymentService
from backend.shared.middleware.rbac import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_intent(
    req: CreateIntentRequest,
    user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Create a new payment intent."""
    service = PaymentService(session)
    return await service.create_intent(uuid.UUID(user["sub"]), req)

@router.post("/webhook/mock")
async def mock_webhook(
    req: WebhookRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """Process a mock payment gateway webhook."""
    service = PaymentService(session)
    return await service.process_webhook(req)
