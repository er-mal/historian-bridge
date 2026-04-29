"""OPC UA historian driver via `asyncua` (optional dep).

For greenfield plants where the historian is just an OPC UA server (Siemens
WinCC, Kepware, Ignition, …). Supports current-value reads and HistoryRead.
Install with: `pip install axon-historian[opcua]`.
"""
from __future__ import annotations
from typing import AsyncIterator, Iterable, Optional
from axon_core import HistorianPoint, HistorianTag, TagQuery
from .base import ConnectionInfo, HistorianClient


class OpcUaHistorian(HistorianClient):
    def __init__(self, info: ConnectionInfo) -> None:
        if info.kind != "opcua":
            raise ValueError(f"OpcUaHistorian got kind={info.kind}")
        self.info = info
        self._client = None

    async def connect(self) -> None:
        try:
            from asyncua import Client
        except ImportError as e:  # pragma: no cover
            raise ImportError("OpcUaHistorian requires `asyncua`. Install axon-historian[opcua].") from e
        self._client = Client(url=self.info.url or "")
        if self.info.username:
            self._client.set_user(self.info.username)
            self._client.set_password(self.info.password or "")
        await self._client.connect()

    async def close(self) -> None:
        if self._client is not None:
            await self._client.disconnect()
            self._client = None

    async def list_tags(self, prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]:
        # OPC UA Browse is recursive; for v0 we only browse Objects/Server root.
        assert self._client is not None
        root = self._client.nodes.objects
        children = await root.get_children()
        out: list[HistorianTag] = []
        for ch in children[:limit]:
            name = (await ch.read_browse_name()).Name
            if prefix and not name.startswith(prefix):
                continue
            out.append(HistorianTag(name=name))
        return out

    async def get_current(self, tags: Iterable[str]) -> list[HistorianPoint]:
        assert self._client is not None
        out: list[HistorianPoint] = []
        for tag in tags:
            node = self._client.get_node(tag) if tag.startswith("ns=") else await _resolve(self._client, tag)
            dv = await node.read_data_value()
            out.append(HistorianPoint(
                tag=tag,
                ts=dv.SourceTimestamp.isoformat() if dv.SourceTimestamp else dv.ServerTimestamp.isoformat(),
                value=float(dv.Value.Value),
                quality="good" if dv.StatusCode.is_good() else "bad",
            ))
        return out

    async def query(self, q: TagQuery) -> AsyncIterator[HistorianPoint]:
        assert self._client is not None
        from datetime import datetime
        t0 = datetime.fromisoformat(q.from_)
        t1 = datetime.fromisoformat(q.to)
        for tag in q.tags:
            node = self._client.get_node(tag) if tag.startswith("ns=") else await _resolve(self._client, tag)
            history = await node.read_raw_history(t0, t1)
            for dv in history:
                yield HistorianPoint(
                    tag=tag,
                    ts=(dv.SourceTimestamp or dv.ServerTimestamp).isoformat(),
                    value=float(dv.Value.Value),
                    quality="good" if dv.StatusCode.is_good() else "bad",
                )

    async def write(self, points: Iterable[HistorianPoint]) -> None:
        raise NotImplementedError("OPC UA driver is read-only by default.")


async def _resolve(client, tag: str):
    """Resolve a path-like tag (e.g. 'Plant/LineA/Stage3/Temperature') under Objects."""
    node = client.nodes.objects
    for part in tag.strip("/").split("/"):
        children = await node.get_children()
        match = None
        for ch in children:
            bn = await ch.read_browse_name()
            if bn.Name == part:
                match = ch
                break
        if match is None:
            raise KeyError(f"OPC UA path not found: {tag}")
        node = match
    return node
