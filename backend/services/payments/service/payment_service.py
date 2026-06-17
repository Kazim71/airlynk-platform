"""
AirLynk — Payment Service.
"""
import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.payments.repository.payment_repo import PaymentRepository
from backend.services.payments.models.payment import PaymentIntent, PaymentStatus, Transaction
from backend.services.payments.schemas.payment import CreateIntentRequest, WebhookRequest
from backend.shared.messaging.rabbitmq import publish_event

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.repo = PaymentRepository(session)

    async def create_intent(self, customer_id: uuid.UUID, req: CreateIntentRequest) -> PaymentIntent:
        intent = PaymentIntent(
            booking_id=req.booking_id,
            customer_id=customer_id,
            amount=req.amount,
            status=PaymentStatus.PENDING
        )
        return await self.repo.create_intent(intent)

    async def process_webhook(self, req: WebhookRequest) -> dict:
        intent = await self.repo.get_intent(req.intent_id)
        if not intent:
            raise HTTPException(status_code=404, detail="Payment Intent not found")

        # Map string status to enum
        try:
            new_status = PaymentStatus(req.status.lower())
        except ValueError:
            new_status = PaymentStatus.FAILED

        # Update intent
        await self.repo.update_intent_status(intent, new_status)

        # Log transaction
        tx = Transaction(
            payment_intent_id=intent.id,
            amount=intent.amount,
            status=new_status.value
        )
        await self.repo.create_transaction(tx)

        # Broadcast event
        await publish_event(
            routing_key="payment.status.updated",
            payload={
                "intent_id": str(intent.id),
                "booking_id": str(intent.booking_id),
                "status": new_status.value,
                "customer_id": str(intent.customer_id)
            }
        )
        return {"status": "processed"}
