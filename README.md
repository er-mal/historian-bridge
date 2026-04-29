# HistorianBridge

> TrendMiner-grade analytics gateway, no TrendMiner license.

## Status
Scaffolded auto. Clean-room build authorized by IP-board.

## What this folder is
A standalone product workspace. Open it in its own VS Code window.
It talks to the shared 48 GB Confluence knowledge base via three idioms:

1. **Offline slice** — `kb/sources.jsonl` (most relevant pages, full body).
   See [kb/INDEX.md](kb/INDEX.md).
2. **Live MCP** — Copilot Chat in this window has the `confkb` MCP server
   configured (`.vscode/mcp.json`). Try:
   > `@workspace use confluence_search to find references to ...`
3. **Raw bytes on demand** — call `confluence_extract_attachment`
   through MCP, or hit `http://127.0.0.1:8765` if the hub web app is up.

## Mining queries
See [kb/QUERIES.md](kb/QUERIES.md). Re-run the slicer from the hub:
```
cd "/Users/ermal/confluence tool"
.venv/bin/python -m scripts.scaffold_products --only 05-historian-bridge
```

## Build / run
See `ARCH.md` for the target architecture.

## License & IP hygiene
See `LICENSE` and `CLEANROOM.md`. Patterns are referenced; verbatim
Confluence content is not redistributed.
