"""In-memory historian — useful for tests, demos, and the HistorianBridge dev loop."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from typing import AsyncIterator, Iterable, Optional
from axon_core import HistorianPoint, HistorianTag, TagQuery
from .base import HistorianClient


class InMemoryHistorian(HistorianClient):
    def __init__(self) -> None:
        self._tags: dict[str, HistorianTag] = {}
        self._points: dict[str, list[HistorianPoint]] = defaultdict(list)
        self._connected = False

    async def connect(self) -> None:
        self._connected = True

    async def close(self) -> None:
        self._connected = False

    def upsert_tag(self, tag: HistorianTag) -> None:
        self._tags[tag.name] = tag

    async def list_tags(self, prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]:
        items = list(self._tags.values())
        if prefix:
            items = [t for t in items if t.name.startswith(prefix)]
        return items[:limit]

    async def get_current(self, tags: Iterable[str]) -> list[HistorianPoint]:
        out: list[HistorianPoint] = []
        for name in tags:
            pts = self._points.get(name, [])
            if pts:
                out.append(pts[-1])
        return out

    async def query(self, q: TagQuery) -> AsyncIterator[HistorianPoint]:
        for name in q.tags:
            for p in self._points.get(name, []):
                if q.from_ <= p.ts <= q.to:
                    yield p

    async def write(self, points: Iterable[HistorianPoint]) -> None:
        for p in points:
            self._points[p.tag].append(p)
            self._tags.setdefault(p.tag, HistorianTag(name=p.tag))

    # convenience for tests
    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()
