# Outreach — v1 validation gate

Goal: 3 unsolicited GitHub issues from people who are NOT in my personal
network. That's the gate to unfreeze ShopFloor API.

The 5 profiles below are fictional ICP sketches, not real people. Use them
to filter real candidates on LinkedIn / control.com forums / r/PLC /
r/industrialautomation / OPC Foundation member directory.

## Profiles

### 1. Controls engineer at mid-size pharma

- 40-200 OPC tags into OSIsoft PI / Aveva PI
- Knows Python at script level, not service level
- Pain: Grafana team keeps asking her for ad-hoc tag dumps
- HB pitch: `historianbridge tags` + `query`, zero infra

### 2. MES analyst at auto Tier-2 supplier

- Wonderware / AVEVA Historian
- Currently mid-vendor-evaluation (Cognite, Seeq, TrendMiner)
- Pain: needs a parity layer to compare candidates without writing glue
- HB pitch: same wire format across drivers — neutral evaluation harness

### 3. Plant data scientist, specialty chemicals

- Influx 2.x, post-2024 stack
- pandas-first workflow
- Pain: influxdb-client is too low-level for ad-hoc analysis
- HB pitch: `/query` returns rows shaped like a frame, parity-tested

### 4. Independent SI, Nordics, SMB food/bev

- OEE dashboards on customer hardware
- Reseller margin pressure
- Pain: <1h deploy, customer IT must sign off without a security review
- HB pitch: 22 MB single binary, 127.0.0.1 only, no Docker needed

### 5. Reliability engineer, cement plant

- AVEVA PI Web API
- Heritage PI-DataLink Excel users
- Pain: writing the migration story off Excel
- HB pitch: PI driver is gated on AVEVA EULA — honest about scope

## Channel hypothesis (ranked)

1. **r/PLC + r/industrialautomation** — Show HN-style post with the wedge
   demo gif. High signal-to-noise.
2. **control.com forums** — older crowd, owns the historian buying
   decision.
3. **LinkedIn DMs** to people whose title contains "historian", "process
   data", "MES analyst" — 30 cold, expect 3 replies.
4. **OPC Foundation Slack** — only after we have the OPC UA driver.
5. **HN Show HN** — last, only if 1-3 pull at all. HN is high-variance.

## Anti-targets (do NOT pitch)

- Anyone selling a competing historian
- Big-3 SI (Accenture, Deloitte, Cap) — they want a platform, not a wedge
- Cloud SaaS shops with no plant floor — wrong stack

## Done-when

- 3 unsolicited GitHub issues from accounts not in my network → unfreeze
  ShopFloor API.
