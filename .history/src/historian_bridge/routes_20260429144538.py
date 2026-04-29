"""HTTP routes for the HistorianBridge gateway."""
from __future__ import annotations

from typing import Any, Optional

from axon_core import HistorianPoint, HistorianTag, TagQuery
from axon_historian import HistorianClient
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from .aggregate import aggregate, parse_interval
from .errors import BadRequest, GatewayError


class TagQueryBody(BaseModel):
    """Wire-format TagQuery. Accepts both `from` and `from_`."""

    tags: list[str]
    from_: str = Field(alias="from")
    to: str
    agg: Optional[str] = "raw"
    interval: Optional[str] = None

    model_config = {"populate_by_name": True}

    def to_kernel(self) -> TagQuery:
        return TagQuery(
            tags=self.tags,
            from_=self.from_,
            to=self.to,
            agg=self.agg,  # type: ignore[arg-type]
            interval=self.interval,
        )


def _validate_query(body: TagQueryBody) -> None:
    if not body.tags:
        raise BadRequest("tags must be non-empty")
    if body.interval is not None:
        parse_interval(body.interval)  # raises ValueError → caught upstream


async def _collect(client: HistorianClient, q: TagQuery) -> list[HistorianPoint]:
    out: list[HistorianPoint] = []
    async for p in client.query(q):
        out.append(p)
    return out


def build_router(client: HistorianClient, write_enabled: bool) -> APIRouter:
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
    async def query(body: TagQueryBody) -> list[HistorianPoint]:
        try:
            _validate_query(body)
        except ValueError as e:
            raise BadRequest(str(e))
        kernel_q = body.to_kernel()
        raw = await _collect(client, kernel_q)
        agg = body.agg or "raw"
        if agg == "raw":
            return raw
        return aggregate(raw, agg=agg, interval=body.interval)

    if write_enabled:
        @router.post("/write")
        async def write(points: list[HistorianPoint]) -> dict[str, Any]:
            if not points:
                raise BadRequest("points must be non-empty")
            await client.write(points)
            return {"ok": True, "n": len(points)}

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
