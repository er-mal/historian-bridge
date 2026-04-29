# HistorianBridge — Architecture

## Target market
TBD — fill in based on `kb/INDEX.md` evidence.

## Public-standard inputs (no IP risk)
- IEC 62660 (cell perf / safety)
- UNECE R100 / R136 (EV battery type approval)
- ISO 6469 (EV electrical safety)
- UN 38.3 (transport)
- GB 38031 (CN safety)
- Vendor public docs (Siemens TIA, Beckhoff TwinCAT, OSIsoft PI, etc.)

## Components
TBD.

## Data dependencies on confkb-hub
- Read-only: FTS search via MCP
- On-demand: raw attachment extraction via MCP `confluence_extract_attachment`
- Bake-time: `kb/sources.jsonl` slice (do not commit if size > 5 MB)

## Interfaces with sibling products
TBD.
