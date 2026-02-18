from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EventEnvelope(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    occurred_at: datetime = Field(default_factory=utc_now)
    data: dict[str, Any]


class OrderCreatedEvent(BaseModel):
    order_id: UUID
    user_id: UUID
    total_amount: int
    currency: str


class OrderPaidEvent(BaseModel):
    order_id: UUID
    user_id: UUID
    payment_id: UUID


class OrderPaymentFailedEvent(BaseModel):
    order_id: UUID
    user_id: UUID
    reason: Literal["DECLINED", "TIMEOUT", "UNKNOWN"] = "DECLINED"
