"""Gateway configuration loaded from environment or constructed in-process.

v1 is read-only and binds to loopback by default. CORS is locked down to
the Grafana default origin. See docs/validation.md §5.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal, Optional

Backend = Literal["memory", "influx"]


@dataclass
class GatewayConfig:
    backend: Backend = "memory"
    cors_allow_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    # Influx
    influx_url: Optional[str] = None
    influx_token: Optional[str] = None
    influx_org: Optional[str] = None
    influx_bucket: Optional[str] = None
    # HTTP — loopback only by default; opening to a network interface is a
    # conscious deployment decision (see docs/validation.md §5 last bullet).
    host: str = "127.0.0.1"
    port: int = 8080


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def load_from_env(env: Optional[dict[str, str]] = None) -> GatewayConfig:
    """Build a GatewayConfig from os.environ-style dict."""
    e = env if env is not None else os.environ
    backend = (e.get("HISTORIAN_BRIDGE_BACKEND") or "memory").lower()
    if backend not in ("memory", "influx"):
        raise ValueError(f"Unknown backend: {backend!r}")
    cors_env = e.get("HISTORIAN_BRIDGE_CORS")
    origins = _split_csv(cors_env) if cors_env is not None else ["http://localhost:3000"]
    return GatewayConfig(
        backend=backend,  # type: ignore[arg-type]
        cors_allow_origins=origins or ["http://localhost:3000"],
        influx_url=e.get("INFLUX_URL"),
        influx_token=e.get("INFLUX_TOKEN"),
        influx_org=e.get("INFLUX_ORG"),
        influx_bucket=e.get("INFLUX_BUCKET"),
        host=e.get("HISTORIAN_BRIDGE_HOST", "127.0.0.1"),
        port=int(e.get("HISTORIAN_BRIDGE_PORT", "8080")),
    )
