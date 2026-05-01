#!/usr/bin/env bash
# Wedge demo (validation.md §2) — runs the five steps end-to-end.
#
# Steps 1, 2, 4, 5 use the InMemory backend so the script is offline-safe.
# Steps 2b/3 (Influx + Grafana) only run if HISTORIANBRIDGE_DEMO_INFLUX=1 and
# the demoted docker-compose stack at examples/docker is up.
#
# Usage:
#   ./examples/wedge_demo.sh                # in-memory only, no network
#   HISTORIANBRIDGE_DEMO_INFLUX=1 ./examples/wedge_demo.sh
#
# This script is the README's source of truth. If a step here breaks,
# the demo broke.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Prefer the binary if present, fall back to the dev entrypoint.
if [[ -x "dist/historianbridge" ]]; then
    HB=("dist/historianbridge")
else
    HB=(uv run --package historian_bridge --extra dev historianbridge)
fi

say() { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }

say "1. List demo tags (memory backend)"
"${HB[@]}" --seed-demo tags --prefix site.line1.station_a

say "2a. One-shot query against memory"
"${HB[@]}" --seed-demo query \
    "tag:site.line1.station_a.temperature last 1h agg=avg interval=10m"

if [[ "${HISTORIANBRIDGE_DEMO_INFLUX:-0}" == "1" ]]; then
    say "2b. Same query shape against Influx"
    : "${INFLUX_URL:?set INFLUX_URL for the influx demo step}"
    : "${INFLUX_TOKEN:?set INFLUX_TOKEN for the influx demo step}"
    : "${INFLUX_ORG:?set INFLUX_ORG for the influx demo step}"
    : "${INFLUX_BUCKET:?set INFLUX_BUCKET for the influx demo step}"
    HISTORIAN_BRIDGE_BACKEND=influx "${HB[@]}" tags --limit 5 || \
        echo "(influx tags returned empty — bucket may be unseeded)"
fi

say "4. Tail current value (3 polls, 1s apart)"
# `tail` runs forever; stop after 3 seconds.
( "${HB[@]}" --seed-demo tail \
    --tag site.line1.station_a.temperature \
    --interval 1 ) & TAIL_PID=$!
sleep 3
kill "$TAIL_PID" 2>/dev/null || true
wait "$TAIL_PID" 2>/dev/null || true

say "5. HTTP gateway smoke (start, hit /healthz, stop)"
HISTORIAN_BRIDGE_PORT=8088 "${HB[@]}" --seed-demo serve & SERVE_PID=$!
trap 'kill $SERVE_PID 2>/dev/null || true' EXIT
# Wait up to ~5s for /healthz.
for i in $(seq 1 20); do
    if curl -fsS "http://127.0.0.1:8088/healthz" >/dev/null 2>&1; then
        break
    fi
    sleep 0.25
done
curl -fsS "http://127.0.0.1:8088/healthz"; echo
curl -fsS "http://127.0.0.1:8088/tags?limit=3" | head -c 200; echo
kill "$SERVE_PID" 2>/dev/null || true
trap - EXIT

say "wedge demo: ok"
