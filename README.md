# Apple AAC Audit App (macOS)

Apple Music / iTunes配信用 96kHz 24bit WAV の事前監査をGUI/CLIで実行するツールです。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## かんたんインストール（CLI不要）

インストーラーファイルは **`install_app.command`** です。  
Finderで `install_app.command` をダブルクリックすると、インストーラーが起動します（Tk GUIは使わず、Terminal上でセットアップを実行）。  
`.venv` 作成と依存関係インストールが自動で実行され、完了時にダイアログを表示します。

### GitHubからのダウンロード手順（推奨）

**推奨: リポジトリ画面の `Code → Download ZIP` で一式をダウンロード**し、展開後に `install_app.command` を実行してください。

> READMEのリンクから `install_app.command` 単体を保存した場合、実行権限が外れることがあります。

### 単体ダウンロードしてしまった場合の対処（ターミナル不要）

1. `install_app.command` をFinderで選択
2. `ファイル > 情報を見る` を開く
3. `名前と拡張子` で拡張子が `.command` になっていることを確認
4. `共有とアクセス権` で自分の権限を `読み/書き` に変更
5. 右クリックから `開く` を選択して実行（Gatekeeper確認を許可）

必要に応じてターミナルで実行権限付与も可能です: `chmod +x install_app.command`

> 補足: 一部環境（Apple提供Python 3.9 + Tk 8.5）で Tk 初期化クラッシュが起きるため、
> インストーラーは Tk を使わない実装にしています。

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
