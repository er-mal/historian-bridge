# Start here — first prompt for Copilot Chat

Open Copilot Chat in this window and paste the prompt below verbatim. Copilot
will read `.github/copilot-instructions.md` automatically and use it as
context.

---

## PROMPT TO PASTE

I'm working on **HistorianBridge** — Vendor-agnostic gateway in front of PI / OPC UA / Influx historians.

The repo is already scaffolded. Read `.github/copilot-instructions.md`,
`README.md`, `ARCH.md`, `bundle.json`, and the `kb/INDEX.md` for context.

**Sprint-1 goal:** FastAPI gateway (uvicorn) with InMemoryHistorian + InfluxHistorian working. /tags, /current, /query endpoints. Docker image. TS client SDK that mirrors the API. One Grafana datasource example.

Before writing any code:

1. List the files you plan to create or modify, with one-line purpose each.
2. Identify the kernel imports you will use (@axon/core from TS kernel; axon-core, axon-historian from Python kernel).
3. Identify the 3 highest-risk unknowns and propose how to resolve each
   (looking up in confkb via MCP, asking me, or making a clear assumption).
4. Propose the test fixture(s) we'll use to demo end-to-end.

Then wait for my "go" before generating files.

When I say "go", produce ALL sprint-1 code in one pass. Use small, named
modules. Write tests next to the code. Keep functions <40 lines. No
placeholder TODOs — every function fully implemented or removed.

Constraints:
- Industry-generic names only. No "battery", "cell", "EV", "ESS",
  "Northvolt", "valibrary", "VoltTrack", "CellLine", "Northcloud",
  "Gigafactory" anywhere in source code or public APIs.
- Clean-room: do NOT copy from `kb/sources.jsonl`. Use it only to derive
  requirements.
- Every dependency on the kernel must use `workspace:*` (TS) or
  `{ workspace = true }` (Python).

Begin with step 1.
