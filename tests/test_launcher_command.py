from pathlib import Path


def test_launch_command_starts_gui_directly() -> None:
    text = Path("launch_app.command").read_text(encoding="utf-8")
    assert "from app.gui import launch; launch()" in text
    assert "python3 -m app" not in text
