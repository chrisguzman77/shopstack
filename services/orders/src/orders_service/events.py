import json
from typing import Any

import redis.asyncio as redis
from shopstack_shared.contracts.events import EventEnvelope

STREAM_NAME = "orders.events"


async def publish_event(r: redis.Redis, *, event_type: str, data: dict[str, Any]) -> str:
    envelope = EventEnvelope(event_type=event_type, data=data)
    payload = envelope.model_dump(mode="json")
    msg_id = await r.xadd(STREAM_NAME, {"payload": json.dumps(payload)})
    return msg_id
