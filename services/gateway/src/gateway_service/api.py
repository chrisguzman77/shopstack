from __future__ import annotations

from collections.abc import Iterable

import httpx
from fastapi import FastAPI, Request, Response
from shopstack_shared.observability.logging import configure_logging
from shopstack_shared.observability.request_id import RequestIdMiddleware
from starlette.responses import JSONResponse

AUTH_URL = "http://auth:8001"
ORDERS_URL = "http://orders:8002"

HOP_BY_HOP: set[str] = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

app = FastAPI(title="Gateway", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
configure_logging("INFO")


@app.get("/")
async def index() -> dict[str, str]:
    return {
        "auth_docs": "/auth/docs",
        "orders_docs": "/orders/docs",
        "gateway_docs": "/docs",
    }


def filtered_headers(headers: Iterable[tuple[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers:
        if k.lower() in HOP_BY_HOP:
            continue
        out[k] = v
    return out


async def proxy(request: Request, upstream: str, path: str) -> Response:
    url = f"{upstream}/{path}"
    body = await request.body()

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.request(
            method=request.method,
            url=url,
            params=dict(request.query_params),
            headers=filtered_headers(request.headers.items()),
            content=body,
        )

    return Response(
        content=r.content,
        status_code=r.status_code,
        headers=filtered_headers(r.headers.items()),
        media_type=r.headers.get("content-type"),
    )


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth(path: str, request: Request) -> Response:
    return await proxy(request, AUTH_URL, path)


@app.api_route("/orders/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_orders(path: str, request: Request) -> Response:
    return await proxy(request, ORDERS_URL, path)


@app.exception_handler(Exception)
async def any_error(_, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": {"code": "GATEWAY_ERROR", "message": str(exc)}})