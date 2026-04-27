from pathlib import Path

from app.installer import InstallerApp


def test_install_command_uses_gui_installer() -> None:
    text = Path("install_app.command").read_text(encoding="utf-8")
    assert "from app.installer import launch_installer; launch_installer()" in text


def test_installer_runs_venv_and_pip_install() -> None:
    text = Path("app/installer.py").read_text(encoding="utf-8")
    assert '"-m", "venv", ".venv"' in text
    assert '"-m", "pip", "install", "-r", "requirements.txt"' in text


def test_resolve_venv_python_prefers_python3(tmp_path: Path) -> None:
    app = InstallerApp.__new__(InstallerApp)
    app.target_dir = tmp_path
    bin_dir = tmp_path / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    py3 = bin_dir / "python3"
    py = bin_dir / "python"
    py3.write_text("", encoding="utf-8")
    py.write_text("", encoding="utf-8")

    resolved = app._resolve_venv_python()

    assert resolved == py3


def test_resolve_venv_python_fallbacks_to_python(tmp_path: Path) -> None:
    app = InstallerApp.__new__(InstallerApp)
    app.target_dir = tmp_path
    bin_dir = tmp_path / ".venv" / "bin"
    bin_dir.mkdir(parents=True)
    py = bin_dir / "python"
    py.write_text("", encoding="utf-8")

    resolved = app._resolve_venv_python()

    assert resolved == py
