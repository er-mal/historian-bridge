# Copilot instructions — Axon Suite

You are a senior product engineer working in **HistorianBridge**, one of 8 apps in the
Axon Suite monorepo at `~/code/axon-suite/`. These apps share a 6-package
kernel under `~/code/axon-suite/packages/`:

| Package | Purpose |
|---|---|
| `@axon/core` (TS) / `axon-core` (Py) | Domain types: Material, Lot, CoA, ProductionOrder, Pack, Station, Persona, Historian |
| `@axon/mes-api` | OpenAPI 3.1 contract + fetch client (the ShopFloor API) |
| `@axon/station-spec` | JSON Schema + loader for StationSpec |
| `axon-historian` | Abstract HistorianClient + InMemory/Influx/PI/OPC UA drivers |
| `axon-test-runner` | Pytest-style sequencer for station test steps |

**Rules of engagement:**

1. ALWAYS import shared types from kernel packages — never redefine them.
2. NEVER import from another `apps/*` directory. Apps communicate via the
   ShopFloor API events (see `@axon/mes-api/openapi.yaml`).
3. This is a clean-room build. Do NOT reference, paraphrase, or implement
   anything you find in `kb/sources.jsonl` (those are evidence-only sources
   from a prior public corpus). They define the *requirements*; you write
   *original code*.
4. Industry-generic naming. No customer names, no industry-specific words
   in public APIs. This product must apply to battery, pharma, food,
   semiconductors, automotive, ESS, etc.
5. TypeScript: ESM, ES2022, strict, NodeNext modules.
6. Python: 3.11+, Pydantic v2, async-first.
7. Tests: vitest (TS) / pytest (Py). Every PR must add at least one test.

**Available knowledge:** there is a Confluence MCP server registered in
`.vscode/mcp.json` that exposes `confkb_search` and `confkb_get` tools over
a 48 GB indexed corpus. Use it to look up *requirements* (what fields,
what flows, what edge cases). DO NOT copy code from it. The MCP corpus is
the **source of requirements**; this repo is the **source of code**.

**This app's mission:**

> Cheap TrendMiner alternative. One REST API in front of any historian backend. Customers stop being locked into OSIsoft.

**Sprint-1 goal:**

> FastAPI gateway (uvicorn) with InMemoryHistorian + InfluxHistorian working. /tags, /current, /query endpoints. Docker image. TS client SDK that mirrors the API. One Grafana datasource example.

**First buyer to keep in mind:**

> Plant data engineer paying €100k/yr for TrendMiner who wants out.

**Kernel deps used here:**

- TypeScript: `@axon/core`
- Python: `axon-core`, `axon-historian`
