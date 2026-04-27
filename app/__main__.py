from __future__ import annotations

import sys

from .cli import run_cli
from .gui import launch


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raise SystemExit(run_cli(sys.argv[1:]))
    launch()
