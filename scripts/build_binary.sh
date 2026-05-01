#!/usr/bin/env bash
# Build the single-file `historianbridge` binary for the current platform.
#
# Output: dist/historianbridge[.exe]
# Honest expected size on macOS arm64 / Linux x86_64: ~45–55 MB.
#
# Usage (from the app dir):
#   ./scripts/build_binary.sh
#
# Run from the monorepo root if uv complains about workspace context.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$APP_DIR/../.." && pwd)"

cd "$ROOT_DIR"

echo "==> uv sync (build + influx + dev extras)"
uv sync --package historian_bridge --extra build --extra influx --extra dev

echo "==> PyInstaller"
uv run --package historian_bridge --extra build --extra influx \
    pyinstaller \
        --clean \
        --noconfirm \
        --workpath "$APP_DIR/build" \
        --distpath "$APP_DIR/dist" \
        "$APP_DIR/scripts/historianbridge.spec"

BIN="$APP_DIR/dist/historianbridge"
if [[ ! -x "$BIN" ]]; then
    echo "build failed: $BIN not produced" >&2
    exit 1
fi

SIZE_BYTES=$(wc -c < "$BIN" | tr -d ' ')
SIZE_MB=$(( SIZE_BYTES / 1024 / 1024 ))
echo "==> built: $BIN  (${SIZE_MB} MB)"

echo "==> smoke: --help"
"$BIN" --help >/dev/null

echo "==> smoke: tags --seed-demo"
"$BIN" --seed-demo tags --prefix site.line1 >/dev/null

echo "==> smoke: query --seed-demo"
"$BIN" --seed-demo query \
    "tag:site.line1.station_a.temperature last 1h" >/dev/null

echo "==> ok"
