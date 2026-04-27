#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

show_alert() {
  local msg="$1"
  /usr/bin/osascript -e "display alert \"Apple AAC Audit App インストーラー\" message \"${msg}\" as critical buttons {\"OK\"} default button \"OK\"" >/dev/null 2>&1 || true
}

if ! command -v python3 >/dev/null 2>&1; then
  show_alert "python3 が見つかりません。Xcode Command Line Tools をインストールして再実行してください。"
  exit 1
fi

echo "[1/3] .venv を作成しています..."
python3 -m venv .venv

VENV_PY=".venv/bin/python3"
if [ ! -x "$VENV_PY" ]; then
  VENV_PY=".venv/bin/python"
fi

if [ ! -x "$VENV_PY" ]; then
  show_alert "仮想環境の Python 実行ファイルが見つかりませんでした。"
  exit 1
fi

echo "[2/3] pip を更新しています..."
"$VENV_PY" -m pip install --upgrade pip

echo "[3/3] 依存関係をインストールしています..."
"$VENV_PY" -m pip install -r requirements.txt

echo "セットアップが完了しました。launch_app.command をダブルクリックして起動してください。"
/usr/bin/osascript -e 'display dialog "セットアップ完了。次は launch_app.command をダブルクリックしてください。" buttons {"OK"} default button "OK"' >/dev/null 2>&1 || true
# Finderでダブルクリックしてセットアップするための起動ファイル
exec python3 -c 'from app.installer import launch_installer; launch_installer()'
