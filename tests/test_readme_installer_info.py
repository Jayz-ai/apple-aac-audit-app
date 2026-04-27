from pathlib import Path


def test_readme_mentions_installer_download_and_permission_recovery() -> None:
    text = Path('README.md').read_text(encoding='utf-8')
    assert 'install_app.command' in text
    assert 'Code → Download ZIP' in text
    assert '単体ダウンロードしてしまった場合の対処（ターミナル不要）' in text
    assert '情報を見る' in text
    assert 'Tk を使わない実装' in text
def test_readme_mentions_installer_file_and_link() -> None:
    text = Path('README.md').read_text(encoding='utf-8')
    assert 'install_app.command' in text
    assert '[`install_app.command`](./install_app.command)' in text
    assert 'Code → Download ZIP' in text
