# Apple AAC Audit App (macOS)

Apple Music / iTunes配信用 96kHz 24bit WAV の事前監査をGUI/CLIで実行するツールです。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## GUI起動

```bash
./launch_app.command
```

または:

```bash
python3 -m app
```

## CLI実行

```bash
python3 -m app run input.wav --target-sr 48000 --reports-root ./reports --auto-remediate
```

## 主な仕様

- WAV選択 / レポート保存先選択
- target sample rate 44.1/48 kHz
- 自動補正ON/OFF
- afconvert で AAC 256kbps 変換
- afclip で source/encoded/decoded を検査
- source vs decode 差分RMS評価
- クリップ時に -1.1 〜 -2.1dB 自動補正試行
- report.md/report.json と autofix_report.md/autofix_report.json を日本語出力

## 注意

- `afconvert` / `afclip` が必要です（Xcode Command Line Tools等を含む環境）。
- 24bit WAV向けです。


## クリック起動（推奨）

Finderで `launch_app.command` をダブルクリックして起動してください。
初回のみ、macOSのセキュリティ設定により実行許可が必要な場合があります。
