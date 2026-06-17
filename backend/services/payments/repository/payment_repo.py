"""
AirLynk — Payment Repository.
"""
import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.payments.models.payment import PaymentIntent, Transaction, PaymentStatus

class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_intent(self, intent: PaymentIntent) -> PaymentIntent:
        self.session.add(intent)
        await self.session.commit()
        await self.session.refresh(intent)
        return intent

    async def get_intent(self, intent_id: uuid.UUID) -> PaymentIntent | None:
        stmt = select(PaymentIntent).where(PaymentIntent.id == intent_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_intent_status(self, intent: PaymentIntent, status: PaymentStatus) -> PaymentIntent:
        intent.status = status
        self.session.add(intent)
        await self.session.commit()
        await self.session.refresh(intent)
        return intent

    async def create_transaction(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction
