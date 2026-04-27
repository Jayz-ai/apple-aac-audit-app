from pathlib import Path


def test_readme_mentions_installer_file_and_link() -> None:
    text = Path('README.md').read_text(encoding='utf-8')
    assert 'install_app.command' in text
    assert '[`install_app.command`](./install_app.command)' in text
    assert 'Code → Download ZIP' in text
