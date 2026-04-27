from pathlib import Path


def test_gui_has_required_strings() -> None:
    text = Path("app/gui.py").read_text(encoding="utf-8")
    for s in [
        "参照確定ファイル名",
        "ファイルのフォルダパス",
        "参照確定フォルダパス",
        "現在の処理内容",
        "進行状況",
        "処理継続中です。停止ではありません。",
    ]:
        assert s in text
