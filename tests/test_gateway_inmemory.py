"""End-to-end gateway tests using httpx ASGI transport against InMemoryHistorian."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from historian_bridge.demo import DEMO_TAGS

pytestmark = pytest.mark.anyio


async def _client(app):
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_healthz(app):
    async with await _client(app) as c:
        r = await c.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"ok": True}


async def test_list_tags(app):
    async with await _client(app) as c:
        r = await c.get("/tags")
        assert r.status_code == 200
        names = {t["name"] for t in r.json()}
        assert names == set(DEMO_TAGS)


async def test_list_tags_prefix(app):
    async with await _client(app) as c:
        r = await c.get("/tags", params={"prefix": "site.line1.station_a"})
        names = {t["name"] for t in r.json()}
        assert names == {DEMO_TAGS[0], DEMO_TAGS[1]}


async def test_current(app):
    async with await _client(app) as c:
        r = await c.get(
            "/current", params=[("tag", DEMO_TAGS[0]), ("tag", DEMO_TAGS[1])]
        )
        assert r.status_code == 200
        body = r.json()
        assert {p["tag"] for p in body} == {DEMO_TAGS[0], DEMO_TAGS[1]}


async def test_query_raw(app):
    async with await _client(app) as c:
        r = await c.post(
            "/query",
            json={
                "tags": [DEMO_TAGS[0]],
                "from": "2026-04-29T12:00:00+00:00",
                "to": "2026-04-29T13:00:00+00:00",
                "agg": "raw",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 60
        assert all(p["tag"] == DEMO_TAGS[0] for p in body)


async def test_query_avg_interval(app):
    async with await _client(app) as c:
        r = await c.post(
            "/query",
            json={
                "tags": [DEMO_TAGS[0]],
                "from": "2026-04-29T12:00:00+00:00",
                "to": "2026-04-29T13:00:00+00:00",
                "agg": "avg",
                "interval": "10m",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 6


async def test_query_validation(app):
    async with await _client(app) as c:
        r = await c.post(
            "/query",
            json={
                "tags": [],
                "from": "2026-04-29T12:00:00+00:00",
                "to": "2026-04-29T13:00:00+00:00",
            },
        )
        assert r.status_code == 400
        assert r.json()["title"] == "bad_request"


async def test_write_route_absent(app):
    """v1 is read-only — the /write route must not exist (validation §5)."""
    async with await _client(app) as c:
        r = await c.post(
            "/write",
            json=[
                {
                    "tag": "site.line2.station_c.temp",
                    "ts": "2026-04-29T12:30:00+00:00",
                    "value": 21.5,
                }
            ],
        )
        assert r.status_code in (404, 405)
