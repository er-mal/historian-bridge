"""Entry point: `python -m historian_bridge`."""
from __future__ import annotations

import uvicorn

from .config import load_from_env
from .gateway import build_app


def main() -> None:
    cfg = load_from_env()
    app = build_app(cfg=cfg)
    uvicorn.run(app, host=cfg.host, port=cfg.port, log_level="info")


if __name__ == "__main__":
    main()
