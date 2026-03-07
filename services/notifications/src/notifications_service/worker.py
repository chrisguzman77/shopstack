import asyncio
import json
import logging
import uuid

import redis.asyncio as redis
from shopstack_shared.observability.logging import configure_logging
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import SessionLocal
from .models import Notification

log = logging.getLogger("notifications.worker")


async def ensure_group(r: redis.Redis) -> None:
    try:
        await r.xgroup_create(settings.stream_name, settings.group_name, id="$", mkstream=True)
    except Exception as e:
        # BUSYGROUP means already exists (redis raises a generic error)
        if "BUSYGROUP" not in str(e):
            raise


def template_for(event_type: str) -> str:
    return {
        "order.paid": "order_paid",
        "order.payment_failed": "order_payment_failed",
        "order.created": "order_created",
    }.get(event_type, "unknown_event")


async def handle_message(db: AsyncSession, payload: dict) -> None:
    event_type = payload["event_type"]
    data = payload["data"]
    user_id = uuid.UUID(data["user_id"])
    n = Notification(
        user_id=user_id,
        channel="EMAIL",
        template=template_for(event_type),
        payload=payload,
        status="SENT",
    )
    db.add(n)
    await db.commit()


async def run_loop() -> None:
    configure_logging(settings.log_level)
    r = redis.from_url(settings.redis_url, decode_responses=True)
    await ensure_group(r)

    while True:
        resp = await r.xreadgroup(
            groupname=settings.group_name,
            consumername=settings.consumer_name,
            streams={settings.stream_name: ">"},
            count=10,
            block=5000,
        )
        if not resp:
            continue

        for _stream, messages in resp:
            for msg_id, fields in messages:
                raw = fields.get("payload")
                try:
                    payload = json.loads(raw)
                    async with SessionLocal() as db:
                        await handle_message(db, payload)
                    await r.xack(settings.stream_name, settings.group_name, msg_id)
                    log.info(f"processed msg {msg_id}")
                except Exception as e:
                    log.error(f"failed msg {msg_id}: {e}")
                    # basic dead-letter strategy
                    await r.xadd("orders.deadletter", {"payoad": raw or "{}"})
                    await r.xack(settings.stream_name, settings.group_name, msg_id)

        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(run_loop())
