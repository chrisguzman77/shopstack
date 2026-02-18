from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class AuthClient:
    base_url: str #e.g. http://auth:8001

    async def verify(self, token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{self.base_url}/auth/verify",
                headers={"Authorization": f"Bearer {token}"},
            )
            r.raise_for_status()
            return r.json()
        
