"""Shared test fixtures: a seeded InMemoryHistorian + FastAPI app."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import pytest
from axon_core import HistorianPoint, HistorianTag
from axon_historian import InMemoryHistorian

from historian_bridge import GatewayConfig, build_app

# Three industry-generic tags exercised end-to-end.
DEMO_TAGS = (
    "site.line1.station_a.temperature",
    "site.line1.station_a.pressure",
    "site.line1.station_b.flow",
)


def seed_historian(hist: InMemoryHistorian, n: int = 60) -> None:
    """Generate `n` minutes of synthetic data, one point per minute, for each demo tag."""
    base = datetime(2026, 4, 29, 12, 0, 0, tzinfo=timezone.utc)
    for i, name in enumerate(DEMO_TAGS):
        hist.upsert_tag(HistorianTag(name=name, unit=("C", "kPa", "lpm")[i]))
        for k in range(n):
            ts = (base + timedelta(minutes=k)).isoformat()
            value = math.sin(k / 5.0 + i) * 10 + (50 + i * 5)
            quality = "questionable" if k == 7 else "good"
            hist.write_sync(HistorianPoint(tag=name, ts=ts, value=value, quality=quality))


# Monkey-patch a sync helper into InMemoryHistorian for fixture seeding (kernel keeps
# write() async). This avoids leaking a sync API into the kernel itself.
def _write_sync(self: InMemoryHistorian, p: HistorianPoint) -> None:
    self._points[p.tag].append(p)
    self._tags.setdefault(p.tag, HistorianTag(name=p.tag))


InMemoryHistorian.write_sync = _write_sync  # type: ignore[attr-defined]


@pytest.fixture
def seeded_client() -> InMemoryHistorian:
    hist = InMemoryHistorian()
    seed_historian(hist)
    return hist


@pytest.fixture
def app(seeded_client: InMemoryHistorian):
    cfg = GatewayConfig(write_enabled=True)
    return build_app(client=seeded_client, cfg=cfg)
