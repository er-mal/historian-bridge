"""Gateway configuration loaded from environment or constructed in-process."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal, Optional

Backend = Literal["memory", "influx"]


@dataclass
class GatewayConfig:
    backend: Backend = "memory"
    cors_allow_origins: list[str] = field(default_factory=lambda: ["*"])
    write_enabled: bool = False
    # Influx
    influx_url: Optional[str] = None
    influx_token: Optional[str] = None
    influx_org: Optional[str] = None
    influx_bucket: Optional[str] = None
    # HTTP
    host: str = "0.0.0.0"
    port: int = 8080


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _truthy(value: Optional[str]) -> bool:
    return (value or "").lower() in {"1", "true", "yes", "on"}


def load_from_env(env: Optional[dict[str, str]] = None) -> GatewayConfig:
    """Build a GatewayConfig from os.environ-style dict."""
    e = env if env is not None else os.environ
    backend = (e.get("HISTORIAN_BRIDGE_BACKEND") or "memory").lower()
    if backend not in ("memory", "influx"):
        raise ValueError(f"Unknown backend: {backend!r}")
    origins = _split_csv(e.get("HISTORIAN_BRIDGE_CORS", "*"))
    return GatewayConfig(
        backend=backend,  # type: ignore[arg-type]
        cors_allow_origins=origins or ["*"],
        write_enabled=_truthy(e.get("HISTORIAN_BRIDGE_WRITE")),
        influx_url=e.get("INFLUX_URL"),
        influx_token=e.get("INFLUX_TOKEN"),
        influx_org=e.get("INFLUX_ORG"),
        influx_bucket=e.get("INFLUX_BUCKET"),
        host=e.get("HISTORIAN_BRIDGE_HOST", "0.0.0.0"),
        port=int(e.get("HISTORIAN_BRIDGE_PORT", "8080")),
    )
