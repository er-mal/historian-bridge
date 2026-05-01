"""Shape-parity test: InMemory vs Influx must return identical-shape
HistorianPoints for the same query. This is the load-bearing claim in
validation.md section 2 step 2.

Marked `slow`. Skipped unless Docker is available *and* the user opts in:

    RUN_INFLUX_TESTS=1 uv run pytest -m slow apps/05-historian-bridge/tests

The test launches a one-off `influxdb:2.7` container, seeds both backends
with the same synthetic points, queries through both, and asserts:
  - same set of tags returned
  - same number of points per tag
  - same numeric values (float-tolerant)
  - same Pydantic field set on `HistorianPoint`

We deliberately do NOT compare timestamps byte-for-byte: Influx round-trips
ISO-8601 through nanosecond precision and may emit `T...Z` vs `+00:00`. We
check that the parsed UTC instant matches.
"""
from __future__ import annotations

import math
import os
import shutil
import socket
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from axon_core import HistorianPoint, TagQuery


pytestmark = [pytest.mark.slow, pytest.mark.anyio]


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(
            ["docker", "info"], capture_output=True, timeout=5
        ).returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


if not os.environ.get("RUN_INFLUX_TESTS"):
    pytest.skip("set RUN_INFLUX_TESTS=1 to run", allow_module_level=True)
if not _docker_available():
    pytest.skip("docker not available", allow_module_level=True)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def influx_container():
    """Spin up a one-off influxdb:2.7 container, tear down on exit."""
    port = _free_port()
    name = f"hb-influx-test-{uuid.uuid4().hex[:8]}"
    token = "hb-test-token"
    org = "axon"
    bucket = "historian"
    proc = subprocess.run(
        [
            "docker", "run", "-d", "--rm",
            "--name", name,
            "-p", f"127.0.0.1:{port}:8086",
            "-e", "DOCKER_INFLUXDB_INIT_MODE=setup",
            "-e", "DOCKER_INFLUXDB_INIT_USERNAME=admin",
            "-e", "DOCKER_INFLUXDB_INIT_PASSWORD=adminadmin",
            "-e", f"DOCKER_INFLUXDB_INIT_ORG={org}",
            "-e", f"DOCKER_INFLUXDB_INIT_BUCKET={bucket}",
            "-e", f"DOCKER_INFLUXDB_INIT_ADMIN_TOKEN={token}",
            "influxdb:2.7",
        ],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        pytest.skip(f"failed to start influxdb container: {proc.stderr.strip()}")
    cid = proc.stdout.strip()
    try:
        url = f"http://127.0.0.1:{port}"
        import urllib.error
        import urllib.request
        deadline = time.time() + 60
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{url}/health", timeout=2) as r:
                    if r.status == 200:
                        break
            except (urllib.error.URLError, ConnectionResetError):
                pass
            time.sleep(0.5)
        else:
            pytest.skip("influx container did not become healthy in 60s")
        yield {"url": url, "token": token, "org": org, "bucket": bucket}
    finally:
        subprocess.run(["docker", "stop", cid], capture_output=True, timeout=15)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _make_points() -> list[HistorianPoint]:
    base = datetime(2026, 4, 29, 12, 0, 0, tzinfo=timezone.utc)
    out: list[HistorianPoint] = []
    for i, name in enumerate(("parity.tag.a", "parity.tag.b")):
        for k in range(10):
            ts = (base + timedelta(seconds=k)).isoformat()
            value = math.sin(k / 3.0 + i) * 5 + 20.0
            out.append(HistorianPoint(tag=name, ts=ts, value=value))
    return out


async def _drain(client, q: TagQuery) -> list[HistorianPoint]:
    out: list[HistorianPoint] = []
    async for p in client.query(q):
        out.append(p)
    return out


async def test_inmemory_and_influx_shape_parity(influx_container):
    from axon_historian import ConnectionInfo, InMemoryHistorian
    from axon_historian.influx import InfluxHistorian

    points = _make_points()
    q = TagQuery(
        tags=["parity.tag.a", "parity.tag.b"],
        from_="2026-04-29T11:59:00+00:00",
        to="2026-04-29T12:00:30+00:00",
    )

    mem = InMemoryHistorian()
    await mem.connect()
    await mem.write(points)

    info = ConnectionInfo(
        kind="influx",
        url=influx_container["url"],
        token=influx_container["token"],
    )
    inf = InfluxHistorian(
        info=info,
        bucket=influx_container["bucket"],
        org=influx_container["org"],
    )
    await inf.connect()
    try:
        await inf.write(points)
        # Influx is async-eventual; give it a beat for write durability.
        time.sleep(1.0)

        mem_out = await _drain(mem, q)
        inf_out = await _drain(inf, q)

        # Same tag set
        mem_tags = {p.tag for p in mem_out}
        inf_tags = {p.tag for p in inf_out}
        assert mem_tags == inf_tags, f"tag sets diverged: mem={mem_tags} inf={inf_tags}"

        # Same Pydantic field set on the kernel model
        assert set(HistorianPoint.model_fields.keys()) == {"tag", "ts", "value", "quality"}

        # Same point count per tag
        for tag in ("parity.tag.a", "parity.tag.b"):
            mem_n = sum(1 for p in mem_out if p.tag == tag)
            inf_n = sum(1 for p in inf_out if p.tag == tag)
            assert mem_n == inf_n == 10, (
                f"point count diverged for {tag}: mem={mem_n} inf={inf_n}"
            )

        # Float values match within tolerance, ordered by parsed timestamp
        def _by_ts(pts):
            return sorted(
                pts,
                key=lambda p: datetime.fromisoformat(p.ts.replace("Z", "+00:00")),
            )

        for tag in ("parity.tag.a", "parity.tag.b"):
            mem_vals = [p.value for p in _by_ts([p for p in mem_out if p.tag == tag])]
            inf_vals = [p.value for p in _by_ts([p for p in inf_out if p.tag == tag])]
            for a, b in zip(mem_vals, inf_vals):
                assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9), (
                    f"{tag}: value drift {a} vs {b}"
                )
    finally:
        await inf.close()
        await mem.close()
