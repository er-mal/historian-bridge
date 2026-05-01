# HistorianBridge

> Vendor-agnostic gateway in front of any historian backend. One typed API,
> swappable drivers, no TrendMiner license. Read-only v1.

## Status

Clean-room build. Sequencing: this is **app #1** in the Axon Suite portfolio.
Validation plan: [docs/validation.md](docs/validation.md). Master plan:
[../../docs/validation-plans-2026.md](../../docs/validation-plans-2026.md).

## v1 surface (locked)

- **CLI:** `historianbridge {serve,tags,query,tail}` — the wedge demo.
- **HTTP:** `/healthz`, `/tags`, `/current`, `/query`. Loopback by default.
- **Backends:** `memory` (built-in) and `influx` (extra: `pip install .[influx]`).
- **Read-only.** No `/write` route. No write env flags.
- **Auth:** local config / env. No SSO, no Vault.
- **Deploy:** Python wheel + `historianbridge` script. Docker is demoted
  to [examples/docker/](examples/docker/) for CI / buyers who insist.

PI Web API support is **not in v1** — gated on AVEVA EULA review (see
`docs/validation.md` §11). OPC UA, writes, multi-tenant cloud, web UI,
Kafka/CDC, and inbound network ports are explicit non-goals (§5).

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

## Knowledge base

The shared 48 GB Confluence corpus is read-only context, not a code source.
Three idioms:

1. **Offline slice** — `kb/sources.jsonl`. See [kb/INDEX.md](kb/INDEX.md).
2. **Live MCP** — the `confkb` server is registered in `.vscode/mcp.json`.
3. **Raw bytes on demand** — `confluence_extract_attachment` via MCP.

## License & IP hygiene

See `LICENSE` and `CLEANROOM.md`. Patterns are referenced; verbatim Confluence
content is never redistributed.
