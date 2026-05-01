"""Demo seed used both by tests and by examples/seed_demo.py."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

from axon_core import HistorianPoint, HistorianTag
from axon_historian import InMemoryHistorian

DEMO_TAGS: tuple[str, ...] = (
    "site.line1.station_a.temperature",
    "site.line1.station_a.pressure",
    "site.line1.station_b.flow",
)
DEMO_UNITS: tuple[str, ...] = ("C", "kPa", "lpm")
# Fixed anchor for deterministic tests. Production CLI seeds relative to now.
DEMO_BASE = datetime(2026, 4, 29, 12, 0, 0, tzinfo=timezone.utc)


def make_demo_points(
    n: int = 60, anchor: Optional[datetime] = None
) -> list[HistorianPoint]:
    """Build n synthetic minute-resolution points per tag, ending at `anchor`.

    `anchor` defaults to DEMO_BASE + (n-1) minutes (i.e. tests get the same
    timestamps as before). The CLI passes `anchor=datetime.now(...)` so the
    wedge demo's `last 1h` window actually contains data.
    """
    if anchor is None:
        end = DEMO_BASE + timedelta(minutes=n - 1)
    else:
        end = anchor
    start = end - timedelta(minutes=n - 1)
    out: list[HistorianPoint] = []
    for i, name in enumerate(DEMO_TAGS):
        for k in range(n):
            ts = (start + timedelta(minutes=k)).isoformat()
            value = math.sin(k / 5.0 + i) * 10 + (50 + i * 5)
            quality = "questionable" if k == 7 else "good"
            out.append(HistorianPoint(tag=name, ts=ts, value=value, quality=quality))
    return out


def seed_inmemory(
    hist: InMemoryHistorian, n: int = 60, anchor: Optional[datetime] = None
) -> None:
    for i, name in enumerate(DEMO_TAGS):
        hist.upsert_tag(HistorianTag(name=name, unit=DEMO_UNITS[i]))
    for p in make_demo_points(n, anchor=anchor):
        hist._points[p.tag].append(p)  # noqa: SLF001 — fixture seed
