# PyInstaller spec for the `historianbridge` single-file binary.
#
# v1 deploy story is one binary the engineer downloads and runs (validation §4).
# We bundle uvicorn + httpx + influxdb-client so the optional Influx backend
# works without a second pip install.
#
# Build:
#   uv run --package historian_bridge --extra dev --extra influx --extra build \
#       pyinstaller --clean --noconfirm scripts/historianbridge.spec
#
# Output: dist/historianbridge (~50 MB on macOS arm64; Linux similar).
# See docs/validation.md §10 — the 50 MB number is the honest one.

# pyright: reportMissingImports=false
# ruff: noqa
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

HERE = os.path.abspath(os.path.dirname(SPEC))  # type: ignore[name-defined]
APP_ROOT = os.path.dirname(HERE)
SRC = os.path.join(APP_ROOT, "src")

# Collect everything the optional drivers might import lazily.
hidden = (
    collect_submodules("influxdb_client")
    + collect_submodules("uvicorn")
    + collect_submodules("axon_historian")
    + collect_submodules("axon_core")
    + ["historian_bridge.cli", "historian_bridge.routes", "historian_bridge.gateway"]
)

a = Analysis(
    [os.path.join(APP_ROOT, "scripts", "historianbridge_entry.py")],
    pathex=[SRC],
    binaries=[],
    datas=[],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # We don't ship a notebook stack.
        "tkinter",
        "matplotlib",
        "IPython",
        "jupyter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="historianbridge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
