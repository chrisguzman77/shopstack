import random
import uuid
from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shopstack_shared.clients.auth_client import AuthClient
from shopstack_shared.observability.logging import configure_logging
from shopstack_shared.observability.request_id import RequestIdMiddleware

from .config import settings
from .db import SessionLocal
from .events import publish_event
from .models import Order, OrderItem

app = FastAPI(title="Orders Service", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
configure_logging(settings.log_level)
router = APIRouter()


def error(code: str, message: str, status: int) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": {"code": code, "message": message}})


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def get_redis() -> redis.Redis:
    client = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


async def require_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise error("MISSING_TOKEN", "Missing bearer token", 401)
    token = authorization.split(" ", 1)[1].strip()
    client = AuthClient(settings.auth_service_url)
    try:
        principal = await client.verify(token)
    except Exception:
        raise error("INVALID_TOKEN", "Token invalid or expired", 401)
    if not principal.get("valid"):
        raise error("INVALID_TOKEN", "Token invalid or expired", 401)
    return principal


class ItemIn(BaseModel):
    sku: str
    name: str
    qty: int = Field(ge=1)
    unit_price: int = Field(ge=1)


class CreateOrderIn(BaseModel):
    currency: str = "USD"
    items: list[ItemIn]


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/orders")
async def create_order(
    payload: CreateOrderIn,
    idem_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
    principal: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    if not idem_key:
        raise error("MISSING_IDEMPOTENCY_KEY", "Idempotency-Key header required", 400)

    user_id = uuid.UUID(principal["user_id"])
    total = sum(i.qty * i.unit_price for i in payload.items)

    # if exists, return existing
    q = await db.execute(select(Order).where(Order.user_id == user_id, Order.idempotency_key == idem_key))
    existing = q.scalar_one_or_none()
    if existing:
        return {"id": str(existing.id), "status": existing.status, "total_amount": existing.total_amount}

    order = Order(user_id=user_id, total_amount=total, currency=payload.currency, idempotency_key=idem_key)
    for i in payload.items:
        order.items.append(OrderItem(sku=i.sku, name=i.name, qty=i.qty, unit_price=i.unit_price))

    db.add(order)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # race condition fallback: re-fetch
        q2 = await db.execute(select(Order).where(Order.user_id == user_id, Order.idempotency_key == idem_key))
        o2 = q2.scalar_one()
        return {"id": str(o2.id), "status": o2.status, "total_amount": o2.total_amount}

    await db.refresh(order)
    return {"id": str(order.id), "status": order.status, "total_amount": order.total_amount}


@router.get("/orders")
async def list_orders(
    db: AsyncSession = Depends(get_db),
    principal: dict[str, Any] = Depends(require_user),
) -> list[dict[str, Any]]:
    user_id = uuid.UUID(principal["user_id"])
    q = await db.execute(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()))
    orders = q.scalars().all()
    return [{"id": str(o.id), "status": o.status, "total_amount": o.total_amount, "currency": o.currency} for o in orders]


@router.get("/orders/{order_id}")
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    principal: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    user_id = uuid.UUID(principal["user_id"])
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise error("NOT_FOUND", "Order not found", 404)
    if order.user_id != user_id:
        raise error("FORBIDDEN", "Not your order", 403)
    return {
        "id": str(order.id),
        "status": order.status,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "items": [{"sku": it.sku, "name": it.name, "qty": it.qty, "unit_price": it.unit_price} for it in order.items],
    }


@router.post("/orders/{order_id}/pay")
async def pay_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
    principal: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    user_id = uuid.UUID(principal["user_id"])
    q = await db.execute(select(Order).where(Order.id == order_id))
    order = q.scalar_one_or_none()
    if not order:
        raise error("NOT_FOUND", "Order not found", 404)
    if order.user_id != user_id:
        raise error("FORBIDDEN", "Not your order", 403)

    # simulate payment: 90% success
    success = random.random() < 0.9
    if success:
        order.status = "PAID"
        payment_id = uuid.uuid4()
        await db.commit()
        await publish_event(
            r,
            event_type="order.paid",
            data={"order_id": str(order.id), "user_id": str(order.user_id), "payment_id": str(payment_id)},
        )
        return {"id": str(order.id), "status": order.status, "payment_id": str(payment_id)}
    else:
        order.status = "FAILED"
        await db.commit()
        await publish_event(
            r,
            event_type="order.payment_failed",
            data={"order_id": str(order.id), "user_id": str(order.user_id), "reason": "DECLINED"},
        )
        return {"id": str(order.id), "status": order.status}


app.include_router(router)