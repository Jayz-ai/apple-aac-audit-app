from app.reporting import build_autofix_markdown


def test_autofix_markdown_has_required_fields() -> None:
    data = {
        "source": "src.wav",
        "target_sr": 48000,
        "chosen_try": "-1.1 dB",
        "chosen_db": -1.1,
        "decision": "採用",
        "trials": [{"name": "trial.wav", "aac_clip": "合格", "on": 0, "inter": 0}],
        "final_on": 0,
        "final_inter": 0,
        "summary": "AAC後クリップが解消",
        "encoded_path": "enc.m4a",
        "decoded_path": "dec.wav",
        "diff_rms": 1.2,
        "comment": "OK",
    }
    md = build_autofix_markdown(data)
    for required in [
        "元ファイル",
        "変換先サンプルレート",
        "採用された試行",
        "採用された減衰量",
        "採用判定",
        "試行一覧",
        "各試行のAACクリップ判定",
        "On-sample数",
        "Inter-sample数",
        "採用結果の概要",
        "Encoded AACパス",
        "Decoded WAVパス",
        "元音源に対する差分RMS",
        "補足コメント",
    ]:
        assert required in md
