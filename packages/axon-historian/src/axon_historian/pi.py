"""OSIsoft PI Web API historian driver.

Uses HTTP only (no DCOM, no PI OLEDB — those stay on customer Windows boxes).
Customer provides the PI Web API base URL + bearer token / Kerberos delegation.
"""
from __future__ import annotations
from typing import AsyncIterator, Iterable, Optional
from axon_core import HistorianPoint, HistorianTag, TagQuery
from .base import ConnectionInfo, HistorianClient


class PiWebApiHistorian(HistorianClient):
    def __init__(self, info: ConnectionInfo) -> None:
        if info.kind != "pi":
            raise ValueError(f"PiWebApiHistorian got kind={info.kind}")
        self.info = info
        self._client = None  # lazy httpx.AsyncClient

    async def connect(self) -> None:
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise ImportError("PiWebApiHistorian requires `httpx`. Install axon-historian[pi].") from e
        headers = {}
        if self.info.token:
            headers["Authorization"] = f"Bearer {self.info.token}"
        self._client = httpx.AsyncClient(base_url=self.info.url or "", headers=headers, timeout=30)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def list_tags(self, prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]:
        assert self._client is not None
        params = {"query": (prefix or "*"), "maxCount": limit}
        r = await self._client.get("/points", params=params)
        r.raise_for_status()
        items = r.json().get("Items", [])
        return [HistorianTag(name=i["Name"], description=i.get("Descriptor"), unit=i.get("EngineeringUnits")) for i in items]

    async def get_current(self, tags: Iterable[str]) -> list[HistorianPoint]:
        assert self._client is not None
        out: list[HistorianPoint] = []
        for name in tags:
            r = await self._client.get(f"/streams/{name}/value")
            if r.status_code == 200:
                v = r.json()
                out.append(HistorianPoint(tag=name, ts=v["Timestamp"], value=float(v["Value"]), quality=("good" if v.get("Good") else "bad")))
        return out

    async def query(self, q: TagQuery) -> AsyncIterator[HistorianPoint]:
        assert self._client is not None
        for tag in q.tags:
            params = {"startTime": q.from_, "endTime": q.to}
            r = await self._client.get(f"/streams/{tag}/recorded", params=params)
            r.raise_for_status()
            for item in r.json().get("Items", []):
                yield HistorianPoint(
                    tag=tag,
                    ts=item["Timestamp"],
                    value=float(item["Value"]),
                    quality=("good" if item.get("Good") else "bad"),
                )

    async def write(self, points: Iterable[HistorianPoint]) -> None:
        raise NotImplementedError("PI Web API driver is read-only by default; enable writes via customer config.")
