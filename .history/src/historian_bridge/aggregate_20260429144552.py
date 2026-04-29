"""Gateway-side aggregation over raw HistorianPoint streams.

Backends that already aggregate server-side (Influx with `aggregateWindow`)
should bypass this module. For backends returning raw points (InMemory, PI
read-raw), this gives uniform `agg=avg|min|max|stddev|count|first|last` and
optional `interval` bucketing across any source.
"""
from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from axon_core import HistorianPoint


_UNITS = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0}


def parse_interval(interval: str) -> timedelta:
    """Parse "10s", "1m", "500ms", "2h" → timedelta. Raises ValueError."""
    s = interval.strip().lower()
    for suf in ("ms", "s", "m", "h", "d"):
        if s.endswith(suf):
            num = s[: -len(suf)]
            try:
                value = float(num)
            except ValueError as e:
                raise ValueError(f"Bad interval number: {interval!r}") from e
            return timedelta(seconds=value * _UNITS[suf])
    raise ValueError(f"Bad interval suffix: {interval!r}")


def _parse_ts(ts: str) -> datetime:
    # tolerate trailing Z
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _reduce(values: list[float], agg: str) -> Optional[float]:
    if not values:
        return None
    if agg == "avg":
        return sum(values) / len(values)
    if agg == "min":
        return min(values)
    if agg == "max":
        return max(values)
    if agg == "count":
        return float(len(values))
    if agg == "first":
        return values[0]
    if agg == "last":
        return values[-1]
    if agg == "stddev":
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(var)
    raise ValueError(f"Unknown agg: {agg!r}")


def aggregate(
    points: Iterable[HistorianPoint],
    agg: str = "raw",
    interval: Optional[str] = None,
) -> list[HistorianPoint]:
    """Aggregate raw points. With `agg="raw"` returns input unchanged."""
    pts = list(points)
    if agg == "raw":
        return pts
    if interval is None:
        # collapse the whole window per tag
        return _aggregate_whole(pts, agg)
    delta = parse_interval(interval)
    return _aggregate_buckets(pts, agg, delta)


def _aggregate_whole(pts: list[HistorianPoint], agg: str) -> list[HistorianPoint]:
    by_tag: dict[str, list[HistorianPoint]] = defaultdict(list)
    for p in pts:
        by_tag[p.tag].append(p)
    out: list[HistorianPoint] = []
    for tag, items in by_tag.items():
        items.sort(key=lambda p: p.ts)
        v = _reduce([p.value for p in items], agg)
        if v is None:
            continue
        out.append(HistorianPoint(tag=tag, ts=items[-1].ts, value=v))
    return out


def _aggregate_buckets(
    pts: list[HistorianPoint], agg: str, delta: timedelta
) -> list[HistorianPoint]:
    by_tag: dict[str, list[HistorianPoint]] = defaultdict(list)
    for p in pts:
        by_tag[p.tag].append(p)
    out: list[HistorianPoint] = []
    for tag, items in by_tag.items():
        items.sort(key=lambda p: p.ts)
        bucket: dict[datetime, list[float]] = defaultdict(list)
        for p in items:
            t = _parse_ts(p.ts)
            epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
            n = int((t - epoch).total_seconds() // delta.total_seconds())
            key = epoch + timedelta(seconds=n * delta.total_seconds())
            bucket[key].append(p.value)
        for key in sorted(bucket):
            v = _reduce(bucket[key], agg)
            if v is None:
                continue
            out.append(HistorianPoint(tag=tag, ts=key.isoformat(), value=v))
    return out
