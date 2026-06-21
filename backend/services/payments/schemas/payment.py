"""
AirLynk — Payment Schemas.
"""

import uuid

from pydantic import BaseModel, ConfigDict

from backend.services.payments.models.payment import PaymentStatus


class CreateIntentRequest(BaseModel):
    booking_id: uuid.UUID
    amount: float


class PaymentIntentResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    amount: float
    currency: str
    status: PaymentStatus

    model_config = ConfigDict(from_attributes=True)


class WebhookRequest(BaseModel):
    intent_id: uuid.UUID
    status: str
