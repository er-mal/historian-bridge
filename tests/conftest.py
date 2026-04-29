"""Shared fixtures."""
from __future__ import annotations

import pytest
from axon_historian import InMemoryHistorian

from historian_bridge import GatewayConfig, build_app
from historian_bridge.demo import seed_inmemory


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def seeded_client() -> InMemoryHistorian:
    hist = InMemoryHistorian()
    seed_inmemory(hist)
    return hist


@pytest.fixture
def app(seeded_client: InMemoryHistorian):
    cfg = GatewayConfig(write_enabled=True)
    return build_app(client=seeded_client, cfg=cfg)
