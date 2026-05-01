"""PyInstaller entry point shim.

PyInstaller wants a real Python file as the script; we cannot point it at
the `historianbridge` console_script. This file is the smallest possible
trampoline into `historian_bridge.cli:main`.
"""
from __future__ import annotations

import sys

from historian_bridge.cli import main


if __name__ == "__main__":
    sys.exit(main())
