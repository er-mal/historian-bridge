"""Push the demo seed corpus into a running gateway via /write."""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
import json

from historian_bridge.demo import make_demo_points


def main() -> int:
    base = os.environ.get("HISTORIAN_BRIDGE_URL", "http://localhost:8080").rstrip("/")
    points = [p.model_dump() for p in make_demo_points()]
    body = json.dumps(points).encode()
    req = urllib.request.Request(
        f"{base}/write", data=body, method="POST",
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"error: {e.code} {e.read().decode()}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
