#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# macOSのFinderからダブルクリック起動する想定
# CLI引数は受け取らず、常にGUIを起動する
exec python3 -c 'from app.gui import launch; launch()'
