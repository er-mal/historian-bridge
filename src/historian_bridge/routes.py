"""HTTP routes for the HistorianBridge gateway.

v1 is read-only (see docs/validation.md §5). The kernel `TagQuery` is the
wire body for /query — it already accepts both `from` and `from_`. No
app-local body type overlaps a kernel type.
"""
from __future__ import annotations

from typing import Any, Optional

from axon_core import HistorianPoint, HistorianTag, TagQuery
from axon_historian import HistorianClient
from fastapi import APIRouter, Query, Request

from .aggregate import aggregate, parse_interval
from .errors import BadRequest, GatewayError


def _validate_query(q: TagQuery) -> None:
    if not q.tags:
        raise BadRequest("tags must be non-empty")
    if q.interval is not None:
        parse_interval(q.interval)  # raises ValueError → caught upstream


async def _collect(client: HistorianClient, q: TagQuery) -> list[HistorianPoint]:
    out: list[HistorianPoint] = []
    async for p in client.query(q):
        out.append(p)
    return out


def build_router(client: HistorianClient) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    async def healthz() -> dict[str, Any]:
        return {"ok": True}

    @router.get("/tags", response_model=list[HistorianTag])
    async def list_tags(prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]:
        if limit <= 0 or limit > 100_000:
            raise BadRequest("limit must be between 1 and 100000")
        return await client.list_tags(prefix=prefix, limit=limit)

    @router.get("/current", response_model=list[HistorianPoint])
    async def current(tag: list[str] = Query(...)) -> list[HistorianPoint]:
        if not tag:
            raise BadRequest("at least one `tag` is required")
        return await client.get_current(tag)

    @router.post("/query", response_model=list[HistorianPoint])
    async def query(body: TagQuery) -> list[HistorianPoint]:
        try:
            _validate_query(body)
        except ValueError as e:
            raise BadRequest(str(e))
        raw = await _collect(client, body)
        agg = body.agg or "raw"
        if agg == "raw":
            return raw
        return aggregate(raw, agg=agg, interval=body.interval)

    return router


def install_error_handlers(app) -> None:
    from fastapi.responses import JSONResponse

    @app.exception_handler(GatewayError)
    async def _gateway_exc(_: Request, exc: GatewayError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_problem())

    @app.exception_handler(NotImplementedError)
    async def _notimpl(_: Request, exc: NotImplementedError):
        return JSONResponse(
            status_code=501,
            content={"type": "about:blank#not_implemented", "title": "not_implemented",
                     "status": 501, "detail": str(exc) or "backend does not support this operation"},
        )
