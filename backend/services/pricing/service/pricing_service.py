"""
AirLynk — Pricing Service.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.pricing.events.publishers import (
    publish_pricing_estimate_generated,
    publish_pricing_rule_updated,
)
from backend.services.pricing.models.pricing import FareEstimate
from backend.services.pricing.repository.pricing_repository import PricingRepository
from backend.services.pricing.schemas.pricing import (
    FareEstimateRequest,
    FareEstimateResponse,
    PricingRuleCreate,
    PricingRuleUpdate,
)
from backend.shared.cache.redis_client import get_redis_client


class PricingService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PricingRepository(db)

    async def get_surge_multiplier(self, city: str) -> Decimal:
        """Fetch the current surge multiplier for a region/city from Redis."""
        redis = get_redis_client()
        key = f"pricing:surge:{city.lower()}"
        val = await redis.get(key)
        if val:
            try:
                return Decimal(val.decode("utf-8"))
            except Exception:
                pass
        return Decimal("1.00")

    async def calculate_fare(self, request: FareEstimateRequest) -> FareEstimateResponse:
        """Calculate fare based on active rules and current surge."""
        rule = await self.repo.get_active_rule_for_city_and_vehicle(
            city=request.city, vehicle_type=request.vehicle_type
        )
        if not rule:
            raise ValueError(
                f"No active pricing rule found for city '{request.city}' and vehicle '{request.vehicle_type}'"
            )

        surge = await self.get_surge_multiplier(request.city)
        effective_surge = max(rule.surge_multiplier, surge)

        base = rule.base_fare.quantize(Decimal("0.01"))
        distance_fare = (rule.per_km_rate * request.estimated_distance_km).quantize(
            Decimal("0.01")
        )
        time_fare = (rule.per_minute_rate * Decimal(request.estimated_duration_minutes)).quantize(
            Decimal("0.01")
        )
        airport_fee = (rule.airport_fee if request.is_airport else Decimal("0.00")).quantize(
            Decimal("0.01")
        )

        subtotal = (base + distance_fare + time_fare).quantize(Decimal("0.01"))
        if subtotal < rule.minimum_fare:
            subtotal = rule.minimum_fare.quantize(Decimal("0.01"))

        total_estimate = ((subtotal * effective_surge) + airport_fee).quantize(Decimal("0.01"))

        estimate = FareEstimate(
            booking_id=request.booking_id if request.booking_id else uuid.uuid4(),
            pricing_rule_id=rule.id,
            estimated_distance_km=request.estimated_distance_km,
            estimated_duration_minutes=request.estimated_duration_minutes,
            estimated_fare=total_estimate,
            surge_applied=effective_surge,
        )
        # We only save the estimate if there is a booking ID provided.
        if request.booking_id:
            estimate = await self.repo.create_fare_estimate(estimate)

        response = FareEstimateResponse(
            id=estimate.id,
            booking_id=estimate.booking_id if request.booking_id else None,
            pricing_rule_id=rule.id,
            estimated_distance_km=request.estimated_distance_km,
            estimated_duration_minutes=request.estimated_duration_minutes,
            base_fare=base,
            distance_fare=distance_fare,
            time_fare=time_fare,
            airport_fee=airport_fee,
            surge_applied=effective_surge,
            subtotal=subtotal,
            total_estimate=total_estimate,
            created_at=estimate.created_at,
        )

        if request.booking_id:
            await publish_pricing_estimate_generated(response)

        return response

    async def create_rule(self, payload: PricingRuleCreate) -> Any:
        rule = await self.repo.create_rule(payload)
        await publish_pricing_rule_updated(rule.id, "created")
        return rule

    async def update_rule(self, rule_id: uuid.UUID, payload: PricingRuleUpdate) -> Any:
        rule = await self.repo.update_rule(rule_id, payload)
        if not rule:
            raise ValueError("Pricing rule not found")
        await publish_pricing_rule_updated(rule.id, "updated")
        return rule
