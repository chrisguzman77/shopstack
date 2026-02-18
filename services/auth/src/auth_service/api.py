from __future__ import annotations

from typing import Any
from uuid import UUID

import redis.asyncio as redis
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from shopstack_shared.observability.logging import configure_logging
from shopstack_shared.observability.request_id import RequestIdMiddleware

from .config import settings
from .db import SessionLocal
from .models import User
from .rate_limit import RedisRateLimiter
from .security import create_access_token, hash_password, verify_access_token, verify_password

app = FastAPI(title="Auth Service", version="0.1.0")
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


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/auth/register")
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    user = User(email=str(payload.email).lower(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise error("EMAIL_TAKEN", "Email already registered", 409)
    await db.refresh(user)
    return {"id": str(user.id), "email": user.email}


@router.post("/auth/login")
async def login(
    request: Request,
    response: Response,
    payload: LoginIn,
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
    x_forwarded_for: str | None = Header(default=None),
) -> dict[str, Any]:
    ip = (x_forwarded_for or request.client.host or "unknown").split(",")[0].strip()
    limiter = RedisRateLimiter(r)

    # Rate limit: by IP and by email
    rl_ip = await limiter.hit(key=f"rl:auth:login:ip:{ip}", limit=20, window_seconds=60)
    rl_email = await limiter.hit(key=f"rl:auth:login:email:{payload.email}", limit=10, window_seconds=60)

    # set headers (nice touch)
    response.headers["X-RateLimit-Remaining-IP"] = str(rl_ip.remaining)
    response.headers["X-RateLimit-Reset-IP"] = str(rl_ip.reset_epoch)
    response.headers["X-RateLimit-Remaining-Email"] = str(rl_email.remaining)
    response.headers["X-RateLimit-Reset-Email"] = str(rl_email.reset_epoch)

    if not rl_ip.allowed or not rl_email.allowed:
        response.headers["Retry-After"] = "60"
        raise error("RATE_LIMITED", "Too many login attempts. Try again later.", 429)

    q = await db.execute(select(User).where(User.email == str(payload.email).lower()))
    user = q.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise error("INVALID_CREDENTIALS", "Invalid email or password", 401)

    token = create_access_token(sub=str(user.id), email=user.email, roles=[])
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/verify")
async def verify(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise error("MISSING_TOKEN", "Missing bearer token", 401)
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = verify_access_token(token)
        return {
            "valid": True,
            "user_id": claims.get("sub"),
            "email": claims.get("email"),
            "roles": claims.get("roles", []),
        }
    except ValueError:
        raise error("INVALID_TOKEN", "Token invalid or expired", 401)


app.include_router(router)
