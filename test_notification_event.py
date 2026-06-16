import asyncio
import uuid
import json
from datetime import datetime
from backend.shared.messaging.rabbitmq import publish_event, init_rabbitmq
from backend.shared.events.envelope import EventEnvelope

async def test_event():
    await init_rabbitmq()
    await asyncio.sleep(2)
    
    # We'll use dispatch.driver.selected
    envelope = EventEnvelope(
        event_name="dispatch.driver.selected",
        event_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow().isoformat(),
        version="1.0",
        source="pricing-engine",
        producer="test_script",
        payload={
            "booking_id": str(uuid.uuid4()),
            "driver_id": str(uuid.uuid4()),
            "passenger_id": "5f795795-13c3-4a14-abc2-4490b6ee4747",  # Operator
        }
    )

    await publish_event("dispatch.driver.selected", envelope.model_dump())
    print("Event published!")

if __name__ == "__main__":
    asyncio.run(test_event())
