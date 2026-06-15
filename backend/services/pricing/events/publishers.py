"""
AirLynk — Pricing Domain Event Publishers.
"""

from __future__ import annotations

import uuid

from backend.services.pricing.schemas.pricing import FareEstimateResponse
from backend.shared.events.envelope import EventEnvelope
from backend.shared.messaging.rabbitmq import publish_event


async def publish_pricing_estimate_generated(estimate: FareEstimateResponse) -> None:
    payload = estimate.model_dump(mode="json")
    event = EventEnvelope(
        event_name="pricing.estimate.generated",
        producer="pricing-service",
        payload=payload,
    )
    await publish_event("pricing.estimate.generated", event.model_dump(mode="json"))


async def publish_pricing_rule_updated(rule_id: uuid.UUID, action: str) -> None:
    event = EventEnvelope(
        event_name="pricing.rule.updated",
        producer="pricing-service",
        payload={"rule_id": str(rule_id), "action": action},
    )
    await publish_event("pricing.rule.updated", event.model_dump(mode="json"))


async def publish_pricing_surge_changed(city: str, new_multiplier: float) -> None:
    event = EventEnvelope(
        event_name="pricing.surge.changed",
        producer="pricing-service",
        payload={"city": city, "new_multiplier": new_multiplier},
    )
    await publish_event("pricing.surge.changed", event.model_dump(mode="json"))
