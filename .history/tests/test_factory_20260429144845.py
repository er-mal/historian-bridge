"""Tests for env → backend selection."""
from __future__ import annotations

import pytest
from axon_historian import InMemoryHistorian

from historian_bridge import build_client, load_from_env
from historian_bridge.config import GatewayConfig


def test_default_is_memory():
    cfg = load_from_env(env={})
    assert cfg.backend == "memory"
    assert isinstance(build_client(cfg), InMemoryHistorian)


def test_unknown_backend_rejected():
    with pytest.raises(ValueError):
        load_from_env(env={"HISTORIAN_BRIDGE_BACKEND": "wildberry"})


def test_influx_requires_creds():
    cfg = GatewayConfig(backend="influx")
    with pytest.raises(ValueError):
        build_client(cfg)


def test_cors_csv():
    cfg = load_from_env(env={"HISTORIAN_BRIDGE_CORS": "https://a.example, https://b.example"})
    assert cfg.cors_allow_origins == ["https://a.example", "https://b.example"]


def test_write_truthy():
    assert load_from_env(env={"HISTORIAN_BRIDGE_WRITE": "true"}).write_enabled is True
    assert load_from_env(env={"HISTORIAN_BRIDGE_WRITE": "0"}).write_enabled is False
