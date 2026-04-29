"""FastAPI application factory for the HistorianBridge gateway."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from axon_historian import HistorianClient

from .config import GatewayConfig
from .factory import build_client
from .routes import build_router, install_error_handlers


def build_app(client: Optional[HistorianClient] = None, cfg: Optional[GatewayConfig] = None):
    """Build a FastAPI app. FastAPI imported lazily so the package stays light."""
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "HistorianBridge gateway needs fastapi: `pip install fastapi uvicorn`"
        ) from e

    cfg = cfg or GatewayConfig()
    client = client or build_client(cfg)

    @asynccontextmanager
    async def lifespan(_app):
        await client.connect()
        try:
            yield
        finally:
            await client.close()

    app = FastAPI(title="HistorianBridge", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)
    app.include_router(build_router(client, write_enabled=cfg.write_enabled))
    app.state.client = client
    app.state.config = cfg
    return app
