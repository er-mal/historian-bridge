# HistorianBridge

> Vendor-agnostic gateway in front of historian backends. One typed API,
> swappable drivers. Read-only v1.

## Status

**App #1 — ship first.** See [docs/validation.md](docs/validation.md).

## v1 surface (locked)

- **CLI:** `historianbridge {serve,tags,query,tail}` — the wedge demo.
- **HTTP:** `/healthz`, `/tags`, `/current`, `/query`. Loopback by default.
- **Backends:** `memory` (built-in) and `influx` (extra: `pip install .[influx]`).
- **Read-only.** No `/write` route. No write env flags.
- **Auth:** local config / env. No SSO, no Vault.
- **Deploy:** Python wheel + `historianbridge` script. Docker is in
  [examples/docker/](examples/docker/) for CI / buyers who insist.

PI Web API support is **not in v1** — gated on AVEVA EULA review (see
`docs/validation.md` §11). OPC UA, writes, multi-tenant cloud, web UI,
Kafka/CDC, and inbound network ports are explicit non-goals.

## Wedge demo

```bash
# 1. List demo tags from the in-memory backend
historianbridge --seed-demo tags --prefix site.line1

# 2. One-shot query, JSON to stdout
historianbridge --seed-demo query \
    "tag:site.line1.station_a.temperature last 1h"

# 3. Same shape against Influx
HISTORIAN_BRIDGE_BACKEND=influx INFLUX_URL=... INFLUX_TOKEN=... \
INFLUX_ORG=axon INFLUX_BUCKET=historian \
    historianbridge query "tag:T-101.temp last 1h"

# 4. Live tail
historianbridge --seed-demo tail --tag site.line1.station_a.temperature

# 5. Local HTTP gateway for Grafana (binds 127.0.0.1:8080)
historianbridge serve
```
