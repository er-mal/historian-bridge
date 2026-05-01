# HistorianBridge — landing copy (≈200 words)

> Audience: process / data engineers running PI on-prem and at least one
> cloud time-series store, currently writing glue scripts on Friday.
> Channel: GitHub README, Show HN, LinkedIn DM, r/PLC, r/dataengineering.
> Tone: dev tool, not enterprise. No marketing softeners.

---

## HistorianBridge

**One typed API in front of every historian. Read-only. Local binary. No login.**

If you're tired of writing the same PI-to-Grafana glue every quarter, this
is for you.

```bash
pip install historian-bridge[influx]
historianbridge --seed-demo query "tag:T-101.temp last 1h"
```

The same command works against InfluxDB 2.x and (once your AVEVA EULA
review clears) PI Web API. Switch backends with one env var. The result
shape is the same: a typed `HistorianPoint` with units and quality —
no string parsing.

Point Grafana at `http://127.0.0.1:8080` and you have a panel in five
minutes. No inbound network port. No IT ticket. No cloud.

![Grafana panel rendered from HistorianBridge demo seed](grafana-demo.png)

**v1 is read-only on purpose** — that's what kills the OT security review.
OPC UA, writes, web UI, and multi-tenant cloud are explicit non-goals.

Built by an engineer who shipped one too many SAP-MII migrations.

→ GitHub: github.com/er-mal/historian-bridge
→ Validation plan: `docs/validation.md` in the repo
