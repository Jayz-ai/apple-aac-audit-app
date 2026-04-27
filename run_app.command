#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 互換ランチャー（Finderでダブルクリック可能）
exec python3 -c 'from app.gui import launch; launch()'
python3 -m app
