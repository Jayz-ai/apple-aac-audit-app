#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Finderでダブルクリックしてセットアップするための起動ファイル
exec python3 -c 'from app.installer import launch_installer; launch_installer()'
