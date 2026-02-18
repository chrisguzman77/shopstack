from __future__ import annotations

import time
from dataclasses import dataclass

import redis.asyncio as redis


@dataclass(frozen=True)
class RateLimitResults:
    allowed: bool
    remaining: int
    reset_epoch: int


class RedisRateLimiter:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def hit(self, *, key: str, limit: int, windows_seconds: int) -> RateLimitResults:
        now = int(time.time())
        window_key = f"{key}:{now // windows_seconds}"
        count = await self.client.incr(window_key)
        if count == 1:
            await self.client.expire(window_key, windows_seconds)

        ttl = await self.client.ttl(window_key)
        reset = now + max(ttl, 0)
        remaining = max(limit - int(count), 0)
        allowed = int(count) <= limit
        return RateLimitResults(allowed=allowed, remaining=remaining, reset_epoch=reset)
    