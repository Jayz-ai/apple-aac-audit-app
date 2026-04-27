from __future__ import annotations

from pathlib import Path


def write_markdown(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def build_audit_markdown(data: dict) -> str:
    return f"""# 通常監査レポート

- 元ファイル: {data['source']}
- 変換先サンプルレート: {data['target_sr']}
- Encoded AAC: {data['encoded']}
- Decoded WAV: {data['decoded']}
- Encoded AACクリップ: on={data['encoded_clip_on']} / inter={data['encoded_clip_inter']}
- 差分RMS: {data['diff_rms']:.4f}
- 判定: {data['verdict']}
"""


def build_autofix_markdown(data: dict) -> str:
    lines = [
        "# 自動補正レポート",
        "",
        f"- 元ファイル: {data['source']}",
        f"- 変換先サンプルレート: {data['target_sr']}",
        f"- 採用された試行: {data['chosen_try']}",
        f"- 採用された減衰量: {data['chosen_db']}",
        f"- 採用判定: {data['decision']}",
        "- 試行一覧:",
        "- 各試行のAACクリップ判定:",
    ]
    for trial in data["trials"]:
        lines.append(
            f"  - {trial['name']}: AACクリップ判定={trial['aac_clip']} On-sample={trial['on']} Inter-sample={trial['inter']}"
        )
    lines.extend(
        [
            f"- On-sample数: {data['final_on']}",
            f"- Inter-sample数: {data['final_inter']}",
            f"- 採用結果の概要: {data['summary']}",
            f"- Encoded AACパス: {data['encoded_path']}",
            f"- Decoded WAVパス: {data['decoded_path']}",
            f"- 元音源に対する差分RMS: {data['diff_rms']:.4f}",
            f"- 補足コメント: {data['comment']}",
            "",
        ]
    )
    return "\n".join(lines)
