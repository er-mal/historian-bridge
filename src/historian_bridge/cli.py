"""`historianbridge` CLI.

Subcommands share one `HistorianClient` factory with the HTTP layer
(`build_client(load_from_env())`). Every subcommand is the wedge demo
spelled out in docs/validation.md \u00a72.

    historianbridge serve            # start local HTTP gateway (loopback)
    historianbridge tags [--prefix]  # list known tags
    historianbridge query <spec>     # one-shot query, JSON to stdout
    historianbridge tail --tag NAME  # poll get_current and print deltas

Spec grammar for `query` is intentionally tiny:
    "tag:T-101.temp last 1h"
    "tag:a,b last 30m agg=avg interval=1m"
    "tag:T from=2026-04-29T12:00Z to=2026-04-29T13:00Z"
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional

from axon_core import HistorianPoint, TagQuery
from axon_historian import HistorianClient, InMemoryHistorian

from .config import GatewayConfig, load_from_env
from .factory import build_client


# ---------- spec parsing -------------------------------------------------

_LAST_RX = re.compile(r"^(\d+(?:\.\d+)?)(ms|s|m|h|d)$")
_LAST_UNITS = {"ms": 0.001, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0}


def _parse_last(value: str) -> timedelta:
    m = _LAST_RX.match(value.strip().lower())
    if not m:
        raise ValueError(f"bad last= duration: {value!r}")
    n, unit = float(m.group(1)), m.group(2)
    return timedelta(seconds=n * _LAST_UNITS[unit])


def parse_query_spec(spec: str, now: Optional[datetime] = None) -> TagQuery:
    """Parse the CLI mini-DSL into a kernel TagQuery."""
    now = now or datetime.now(timezone.utc)
    tokens = spec.split()
    tags: list[str] = []
    from_ts: Optional[str] = None
    to_ts: Optional[str] = None
    agg: str = "raw"
    interval: Optional[str] = None
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("tag:"):
            tags = [s for s in t[4:].split(",") if s]
        elif t == "last" and i + 1 < len(tokens):
            delta = _parse_last(tokens[i + 1])
            to_ts = now.isoformat()
            from_ts = (now - delta).isoformat()
            i += 1
        elif t.startswith("from="):
            from_ts = t[5:]
        elif t.startswith("to="):
            to_ts = t[3:]
        elif t.startswith("agg="):
            agg = t[4:]
        elif t.startswith("interval="):
            interval = t[9:]
        else:
            raise ValueError(f"unrecognized token: {t!r}")
        i += 1

    if not tags:
        raise ValueError("query spec needs `tag:NAME[,NAME2,...]`")
    if from_ts is None or to_ts is None:
        raise ValueError("query spec needs either `last <duration>` or `from=... to=...`")
    return TagQuery(tags=tags, from_=from_ts, to=to_ts, agg=agg, interval=interval)  # type: ignore[arg-type]


# ---------- subcommand impls --------------------------------------------

def _maybe_seed(client: HistorianClient, seed_demo: bool) -> None:
    if not seed_demo:
        return
    if not isinstance(client, InMemoryHistorian):
        return
    from datetime import datetime, timezone

    from .demo import seed_inmemory  # local import to avoid circular at module load

    # Anchor at "now" so `last 1h` style queries actually contain data.
    seed_inmemory(client, anchor=datetime.now(timezone.utc))


def _dump_points(points: list[HistorianPoint]) -> None:
    json.dump([p.model_dump() for p in points], sys.stdout, default=str)
    sys.stdout.write("\n")


async def _run_tags(cfg: GatewayConfig, prefix: Optional[str], limit: int, seed_demo: bool) -> int:
    client = build_client(cfg)
    await client.connect()
    try:
        _maybe_seed(client, seed_demo)
        tags = await client.list_tags(prefix=prefix, limit=limit)
        json.dump([t.model_dump() for t in tags], sys.stdout, default=str)
        sys.stdout.write("\n")
        return 0
    finally:
        await client.close()


async def _run_query(cfg: GatewayConfig, spec: str, seed_demo: bool) -> int:
    client = build_client(cfg)
    await client.connect()
    try:
        _maybe_seed(client, seed_demo)
        # Parse the spec AFTER seeding so a `last Nh` window includes the
        # freshly-seeded final point (the seed anchor is `now`).
        q = parse_query_spec(spec)
        from .aggregate import aggregate

        raw: list[HistorianPoint] = []
        async for p in client.query(q):
            raw.append(p)
        out = raw if (q.agg or "raw") == "raw" else aggregate(raw, agg=q.agg or "raw", interval=q.interval)
        _dump_points(out)
        return 0
    finally:
        await client.close()


async def _run_tail(cfg: GatewayConfig, tags: list[str], interval_s: float, seed_demo: bool) -> int:
    """Poll get_current at `interval_s`, print on change.

    InMemory and Influx don't have native streaming in v1. Polling is honest
    and works against any backend in the validation \u00a74 list.
    """
    client = build_client(cfg)
    await client.connect()
    try:
        _maybe_seed(client, seed_demo)
        last_ts: dict[str, str] = {}
        while True:
            current = await client.get_current(tags)
            for p in current:
                if last_ts.get(p.tag) != p.ts:
                    last_ts[p.tag] = p.ts
                    sys.stdout.write(json.dumps(p.model_dump(), default=str) + "\n")
                    sys.stdout.flush()
            await asyncio.sleep(interval_s)
    except KeyboardInterrupt:
        return 0
    finally:
        await client.close()


def _run_serve(cfg: GatewayConfig, seed_demo: bool) -> int:
    try:
        import uvicorn
    except ImportError as e:  # pragma: no cover
        raise SystemExit("uvicorn is required for `serve` (pip install uvicorn[standard])") from e
    from .gateway import build_app

    client = build_client(cfg)
    _maybe_seed(client, seed_demo)
    app = build_app(client=client, cfg=cfg)
    uvicorn.run(app, host=cfg.host, port=cfg.port, log_level="info")
    return 0


# ---------- argparse ----------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="historianbridge",
        description="Vendor-agnostic historian gateway. Read-only v1.",
    )
    p.add_argument(
        "--seed-demo",
        action="store_true",
        help="Seed the InMemory backend with demo points (no-op for other backends).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("serve", help="Start the local HTTP gateway (loopback by default).")

    pt = sub.add_parser("tags", help="List known tags from the configured backend.")
    pt.add_argument("--prefix", default=None)
    pt.add_argument("--limit", type=int, default=1000)

    pq = sub.add_parser("query", help='One-shot query, e.g. "tag:T-101.temp last 1h".')
    pq.add_argument("spec", nargs="+", help="Query spec tokens.")

    ptl = sub.add_parser("tail", help="Live-tail current values for one or more tags.")
    ptl.add_argument("--tag", action="append", required=True, help="Tag to follow (repeatable).")
    ptl.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds.")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    cfg = load_from_env()

    if args.cmd == "serve":
        return _run_serve(cfg, args.seed_demo)
    if args.cmd == "tags":
        return asyncio.run(_run_tags(cfg, args.prefix, args.limit, args.seed_demo))
    if args.cmd == "query":
        return asyncio.run(_run_query(cfg, " ".join(args.spec), args.seed_demo))
    if args.cmd == "tail":
        return asyncio.run(_run_tail(cfg, args.tag, args.interval, args.seed_demo))
    parser.error(f"unknown command: {args.cmd!r}")
    return 2  # unreachable


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
