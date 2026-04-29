"""Tests for the gateway-side aggregator."""
from __future__ import annotations

from axon_core import HistorianPoint

from historian_bridge.aggregate import aggregate, parse_interval


def _pts(tag: str, values: list[tuple[str, float]]) -> list[HistorianPoint]:
    return [HistorianPoint(tag=tag, ts=ts, value=v) for ts, v in values]


def test_parse_interval():
    assert parse_interval("10s").total_seconds() == 10
    assert parse_interval("2m").total_seconds() == 120
    assert parse_interval("1h").total_seconds() == 3600
    assert parse_interval("500ms").total_seconds() == 0.5


def test_aggregate_raw_passthrough():
    pts = _pts("a", [("2026-01-01T00:00:00+00:00", 1.0)])
    assert aggregate(pts, agg="raw") == pts


def test_aggregate_avg_whole():
    pts = _pts("a", [
        ("2026-01-01T00:00:00+00:00", 2.0),
        ("2026-01-01T00:00:30+00:00", 4.0),
    ])
    out = aggregate(pts, agg="avg")
    assert len(out) == 1
    assert out[0].value == 3.0


def test_aggregate_min_max_count():
    pts = _pts("a", [
        ("2026-01-01T00:00:00+00:00", 2.0),
        ("2026-01-01T00:00:30+00:00", 5.0),
        ("2026-01-01T00:01:00+00:00", 1.0),
    ])
    assert aggregate(pts, agg="min")[0].value == 1.0
    assert aggregate(pts, agg="max")[0].value == 5.0
    assert aggregate(pts, agg="count")[0].value == 3.0


def test_aggregate_buckets():
    pts = _pts("a", [
        ("2026-01-01T00:00:00+00:00", 1.0),
        ("2026-01-01T00:00:30+00:00", 3.0),
        ("2026-01-01T00:01:00+00:00", 5.0),
        ("2026-01-01T00:01:30+00:00", 7.0),
    ])
    out = aggregate(pts, agg="avg", interval="1m")
    assert len(out) == 2
    assert out[0].value == 2.0
    assert out[1].value == 6.0
