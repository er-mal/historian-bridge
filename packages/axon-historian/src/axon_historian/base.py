from __future__ import annotations
from typing import AsyncIterator, Iterable, Optional, Protocol, runtime_checkable
from pydantic import BaseModel
from axon_core import HistorianPoint, HistorianTag, TagQuery


class ConnectionInfo(BaseModel):
    """Generic connection descriptor; concrete drivers map relevant fields."""
    kind: str  # "influx" | "pi" | "opcua" | "memory" | ...
    url: Optional[str] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    extra: dict = {}


@runtime_checkable
class HistorianClient(Protocol):
    """Minimal contract a historian backend must satisfy.

    Implementations should be safe to share across coroutines but may keep an
    internal connection pool. Implementations MUST honor the `quality` field
    if the backend exposes it.
    """

    async def connect(self) -> None: ...
    async def close(self) -> None: ...

    async def list_tags(self, prefix: Optional[str] = None, limit: int = 1000) -> list[HistorianTag]: ...

    async def get_current(self, tags: Iterable[str]) -> list[HistorianPoint]: ...

    async def query(self, q: TagQuery) -> AsyncIterator[HistorianPoint]: ...

    async def write(self, points: Iterable[HistorianPoint]) -> None:
        """Optional. Backends that are read-only should raise NotImplementedError."""
        ...
