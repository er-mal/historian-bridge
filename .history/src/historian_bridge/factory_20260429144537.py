"""Pick a HistorianClient implementation from a GatewayConfig."""
from __future__ import annotations

from axon_historian import ConnectionInfo, HistorianClient, InMemoryHistorian

from .config import GatewayConfig


def build_client(cfg: GatewayConfig) -> HistorianClient:
    """Return a concrete HistorianClient. Lazy-imports optional drivers."""
    if cfg.backend == "memory":
        return InMemoryHistorian()
    if cfg.backend == "influx":
        if not (cfg.influx_url and cfg.influx_token and cfg.influx_org and cfg.influx_bucket):
            raise ValueError(
                "Influx backend requires INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET"
            )
        from axon_historian.influx import InfluxHistorian

        info = ConnectionInfo(kind="influx", url=cfg.influx_url, token=cfg.influx_token)
        return InfluxHistorian(info=info, bucket=cfg.influx_bucket, org=cfg.influx_org)
    raise ValueError(f"Unknown backend: {cfg.backend!r}")
