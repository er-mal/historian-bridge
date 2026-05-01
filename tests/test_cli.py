"""CLI smoke tests \u2014 verify spec parsing and the in-memory query path."""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from datetime import datetime, timezone

import pytest

from historian_bridge.cli import main, parse_query_spec


def test_parse_spec_last():
    now = datetime(2026, 4, 29, 13, 0, 0, tzinfo=timezone.utc)
    q = parse_query_spec("tag:a,b last 1h agg=avg interval=10m", now=now)
    assert q.tags == ["a", "b"]
    assert q.from_ == "2026-04-29T12:00:00+00:00"
    assert q.to == "2026-04-29T13:00:00+00:00"
    assert q.agg == "avg"
    assert q.interval == "10m"


def test_parse_spec_explicit_range():
    q = parse_query_spec("tag:T from=2026-04-29T12:00:00+00:00 to=2026-04-29T13:00:00+00:00")
    assert q.tags == ["T"]
    assert q.from_.startswith("2026-04-29T12")


def test_parse_spec_rejects_missing_range():
    with pytest.raises(ValueError):
        parse_query_spec("tag:T")


def test_parse_spec_rejects_missing_tag():
    with pytest.raises(ValueError):
        parse_query_spec("last 1h")


def test_cli_query_against_seeded_memory(monkeypatch):
    monkeypatch.setenv("HISTORIAN_BRIDGE_BACKEND", "memory")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main([
            "--seed-demo",
            "query",
            "tag:site.line1.station_a.temperature last 2h",
        ])
    assert rc == 0
    rows = json.loads(buf.getvalue())
    # Seed produces 60 minute-resolution points anchored at now; last 2h covers them all.
    assert len(rows) == 60
    assert all(r["tag"] == "site.line1.station_a.temperature" for r in rows)


def test_cli_tags_against_seeded_memory(monkeypatch):
    monkeypatch.setenv("HISTORIAN_BRIDGE_BACKEND", "memory")
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(["--seed-demo", "tags", "--prefix", "site.line1.station_a"])
    assert rc == 0
    names = {t["name"] for t in json.loads(buf.getvalue())}
    assert names == {
        "site.line1.station_a.temperature",
        "site.line1.station_a.pressure",
    }
