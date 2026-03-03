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
        