# Third-party license notes

HistorianBridge is Apache-2.0. This file tracks license interactions with
third-party historian backends.

## InfluxDB 2.x

- Driver: `influxdb-client` (MIT). No restrictions on redistribution.
- Customer brings their own InfluxDB instance and token.
- No AVEVA-style EULA path. Ship freely.

## OPC UA

- Driver: `asyncua` (LGPL-3.0). Stub only in v1; reactivate when an OPC UA
  user files an issue.
- LGPL allows redistribution alongside Apache-2.0 code as long as the
  consumer can swap the LGPL component. Document the dynamic-link path
  before shipping.

## AVEVA PI (PI Web API) — STATUS: not shipped, gated

`packages/axon-historian/src/axon_historian/pi.py` is a stub. Activating
it must follow path (a) below.

### Path (a) — pure HTTPS, NO SDK bundling (committed)

A client that:

1. Uses `httpx` / `aiohttp` to call a customer-provided PI Web API
   endpoint over HTTPS.
2. Authenticates with a bearer token, basic auth, or Kerberos — all
   provided by the customer at runtime.
3. Bundles **no** AVEVA-shipped binaries, headers, or generated code.
4. Does not reverse-engineer the wire protocol — it follows the public
   REST shape documented at `https://docs.aveva.com/`.

Under this path, HistorianBridge ships under Apache-2.0 with no AVEVA
encumbrance. The customer needs their own PI Server license; that's
their problem, not ours.

### Path (b) — bundling AF SDK / PI Python — REJECTED

Bundling `PIconnect`, AF SDK, or any AVEVA-distributed binary triggers
AVEVA's developer agreement and is incompatible with our redistribution
model. Do not take this path without:

1. A signed AVEVA developer agreement on file.
2. Counsel review of the redistribution clauses.
3. A separate optional install path so the core wheel stays SDK-free.

### TODO when first PI user files an issue

- [ ] Re-fetch current AVEVA PI Web API terms from `https://docs.aveva.com/`
      (URLs change yearly; both `aveva.com/en/legal-and-policies/software-end-user-license-agreement/`
      and `docs.aveva.com/bundle/pi-web-api` returned 404 as of 2026-05-01).
- [ ] Capture exact clause numbers governing third-party HTTPS clients
      against PI Web API.
- [ ] Confirm path (a) is still allowed.
- [ ] If clauses changed, re-evaluate before merging the PI driver PR.

## Grafana

- The Grafana panel screenshot in `docs/grafana-demo.png` was rendered
  with Grafana OSS 11.0.0 (AGPL-3.0). The image is a screenshot, not a
  redistribution of Grafana itself. No license interaction.
