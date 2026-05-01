# HistorianBridge — Validation Plan (May 2026)

> Status: **draft for red-pen.** Sequencing locked: this is **#1, ship first.** Master plan: [../../../docs/validation-plans-2026.md](../../../docs/validation-plans-2026.md)

**One-line:** vendor-agnostic gateway that lets engineers query PI, OPC UA, Influx, Timescale, ADX through one typed API.

## Why this is #1

- Cleanest demo (5 min, one binary, no login).
- No compliance friction (read-only, local).
- Establishes the typed kernel by being the thing every other Axon app calls into.
- Behaves like a dev tool, not enterprise software → engineer self-serve adoption.

## 1. Target buyer

**Named persona:** *Process / data engineer at a mid-size manufacturer (200–2000 employees) running PI on-prem and at least one cloud time-series store (Influx, Timescale, ADX, or Timestream) for newer lines.*

Not the plant manager. Not IT. The engineer who currently writes glue scripts on Friday afternoons because PI-to-Grafana is "almost working."

Industries (broad on purpose, narrow later): batteries, specialty chemicals, food & bev, pharma CDMOs, metals.

## 2. Wedge demo (5 min)

1. `historianbridge query "tag:T-101.temp last 1h"` → returns rows from PI (or InMemory in week 1, until PI EULA review passes — see §11).
2. Same command, `--backend influx` → returns rows from Influx, identical shape. Single binary, swap via env var or `--backend` flag.
3. Grafana panel pointing at HistorianBridge on `127.0.0.1:8080`, switching backends with one env var. (Loopback-only — not a remote gateway.)
4. Show the typed result (`HistorianPoint` with units + quality, owned by `axon-core`) — no string-parsing.
5. `historianbridge tail --tag T-101.temp` for live streaming.

That's it. No login. No cloud. Local binary (~50 MB; see §10).

## 3. First 10 logos — how, not just who

Reach order:

1. **2 from your network** (former colleagues, Nordic manufacturing contacts). Free, fast feedback, do not count toward validation.
2. **3 from PI System Users Group** (LinkedIn community, regional events). Cold DM engineers who post about "PI to cloud" pain. Offer to co-debug their setup live.
3. **3 from r/PLC, r/dataengineering, Hacker News Show HN.** OSS-led pull. The repo *is* the pitch.
4. **2 from one targeted integrator** (e.g., Atlas Copco MES partners, Cognite ecosystem) who'll run it in their next migration project.

Channel order: GitHub → LinkedIn DM → integrator referral. Not conferences, not paid ads.

## 4. v1 integrations (ruthless minimum)

- **Read-only.** No writes in v1. (Kills the OT security review.)
- **2 backends in week 1, 3rd gated:** InMemory + InfluxDB 2.x ship week 1. PI (PI Web API, basic auth) gated on AVEVA EULA review (§11).
- **1 frontend:** CLI (`query` / `tail` / `tags`) + Grafana datasource plugin. Local HTTP bound to `127.0.0.1:8080` only.
- **1 auth mode:** local config file with creds (`~/.historianbridge.toml`). No SSO, no Vault, no Entra.
- **1 deploy mode:** single PyInstaller binary (~50 MB). Docker compose demoted to `examples/docker/`.

## 5. Explicit non-goals (v1)

- ❌ Writes to historians.
- ❌ OPC UA (defer to v2; AF SDK + Influx covers 80% of the demos).
- ❌ Multi-tenant cloud version.
- ❌ Web UI beyond the Grafana plugin.
- ❌ Authentication beyond config file.
- ❌ Streaming/CDC into Kafka/Pulsar.
- ❌ Any feature that requires an inbound network port.

## 6. The 2-week-yes question
>
> *Will an engineer install a ~50MB binary, point it at their PI server (or Influx in week 1), and get a Grafana panel showing live data within an hour — without filing an IT ticket?*

If yes, they'll tell three colleagues. That's the GTM.

If no (because PI Web API access already requires IT approval at most plants), the wedge collapses to "self-host in OT DMZ" which is much slower. **Validate this before writing connector code.**

## 7. Kill criteria

- After 50 GitHub stars, fewer than 3 unsolicited issues from real users → product isn't sticky enough.
- 5 consecutive engineers say "I'd use it but security won't let me install random binaries" → repackage as a PI AF plugin instead, or kill.
- Cognite or HighByte ships an OSS equivalent before we hit 100 stars → reposition or kill.

## 8. Open risks the research did NOT resolve

- **OT security review variance.** Some plants install a signed binary same-day; others need 3-month review. Distribution is binary, not gradual.
- **PI licensing on read-only access.** AVEVA may consider HistorianBridge a "client" requiring a PI Interface license. Read the PI EULA carefully before promoting it publicly.
- **Cognite competitive response.** They have the budget to OSS a competitor in 6 months if they notice traction.

## 9. Kernel discipline

The kernel types `HistorianTag`, `HistorianPoint`, and `TagQuery` are owned
by `axon_core`. HistorianBridge is the **reference consumer** that proves
their shape. The app does not redefine kernel types; if a future app needs
a different shape, the kernel changes first and HistorianBridge follows.

## 10. Packaging note

PyInstaller produces a single-file `historianbridge` binary. Measured size:

- macOS arm64: **~22 MB** (May 2026 build, Python 3.14, FastAPI + uvicorn +
  influxdb-client + httpx all bundled).
- Linux x86_64: not yet measured — expect comparable, possibly +10–20%.

The earlier "≈50 MB" worst-case estimate was conservative and the earlier
"20 MB" aspiration turned out to be roughly accurate after all. Promote the
real number once Linux is measured. Build with `scripts/build_binary.sh`.

## 11. PI driver gating

The PI Web API driver is **not built in week 1.** Open question for review:
AVEVA may treat read-only PI Web API consumers as “clients” requiring a
PI Interface license, in which case shipping a public connector is a
legal hazard. Resolve the EULA review before writing the driver. Week 1
demo runs on InMemory + Influx + CLI + Grafana.

---

## Prompt for a new chat session in this window

> **Context refresh — May 1, 2026.** HistorianBridge is **#1, ship first** in the Axon Suite portfolio. Read `docs/validation.md` in this directory and the master at `../../docs/validation-plans-2026.md`.
>
> Wedge: vendor-agnostic, read-only, local binary, 5-min Grafana demo, no cloud, no inbound ports. The 2-week-yes test (§6) is the gating question.
>
> Kernel discipline: this app **defines** `HistorianTag` and `HistorianPoint` in the kernel. Every other app imports them. Do not let app-local variants slip in.
>
> Do not write code yet. Tell me:
>
> 1. Smallest v1 that hits the wedge demo in §2 (PI + Influx + CLI + Grafana plugin, read-only).
> 2. What in current scaffolding contradicts §5 non-goals and should be ripped out now.
> 3. Who specifically can we put in front of the 2-week-yes test in the next 14 days.
>
> Confirm scope, push back where evidence is thin, then we lock and start coding.
