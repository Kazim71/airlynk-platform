"""
AirLynk — Pricing Repository.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.pricing.models.pricing import FareEstimate, PricingRule
from backend.services.pricing.schemas.pricing import PricingRuleCreate, PricingRuleUpdate


class PricingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_rule(self, rule_id: uuid.UUID) -> PricingRule | None:
        result = await self.db.execute(select(PricingRule).where(PricingRule.id == rule_id))
        return result.scalars().first()

    async def get_active_rule_for_city_and_vehicle(
        self, city: str, vehicle_type: str
    ) -> PricingRule | None:
        result = await self.db.execute(
            select(PricingRule).where(
                PricingRule.city == city,
                PricingRule.vehicle_type == vehicle_type,
                PricingRule.active.is_(True),
            )
        )
        return result.scalars().first()

    async def get_all_rules(self, city: str | None = None) -> Sequence[PricingRule]:
        query = select(PricingRule)
        if city:
            query = query.where(PricingRule.city == city)
        result = await self.db.execute(query.order_by(PricingRule.created_at.desc()))
        return result.scalars().all()

    async def create_rule(self, payload: PricingRuleCreate) -> PricingRule:
        rule = PricingRule(**payload.model_dump())
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def update_rule(
        self, rule_id: uuid.UUID, payload: PricingRuleUpdate
    ) -> PricingRule | None:
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_rule(rule_id)

        stmt = (
            update(PricingRule)
            .where(PricingRule.id == rule_id)
            .values(**update_data)
            .returning(PricingRule)
        )
        result = await self.db.execute(stmt)
        rule = result.scalars().first()
        if rule:
            await self.db.commit()
        return rule

    async def create_fare_estimate(self, estimate: FareEstimate) -> FareEstimate:
        self.db.add(estimate)
        await self.db.commit()
        await self.db.refresh(estimate)
        return estimate
