from pathlib import Path
from unittest.mock import patch

from app.audio_tools import convert_to_aac


def test_subprocess_uses_list_args_with_japanese_path() -> None:
    src = Path("/tmp/日本語 ファイル(テスト).wav")
    out = Path("/tmp/出力 (確認).m4a")
    with patch("app.audio_tools.subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        convert_to_aac(src, out)
        args, kwargs = mock_run.call_args
        assert isinstance(args[0], list)
        assert str(src) in args[0]
        assert str(out) in args[0]
        assert kwargs["check"] is True
