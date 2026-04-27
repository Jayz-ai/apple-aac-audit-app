from __future__ import annotations

import json
import math
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class ClipStats:
    on_sample: int
    inter_sample: int
    raw_text: str


@dataclass
class DiffStats:
    rms: float
    verdict: str


def check_tool_exists(name: str) -> bool:
    return shutil.which(name) is not None


def ensure_tools() -> None:
    missing = [tool for tool in ("afconvert", "afclip") if not check_tool_exists(tool)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"必要なApple公式ツールが見つかりません: {joined}")


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
    )


def convert_to_aac(source_wav: Path, encoded_m4a: Path) -> str:
    result = run_command(
        [
            "afconvert",
            "-f",
            "m4af",
            "-d",
            "aac",
            "-b",
            "256000",
            str(source_wav),
            str(encoded_m4a),
        ]
    )
    return (result.stdout or "") + (result.stderr or "")


def decode_aac_to_wav(encoded_m4a: Path, decoded_wav: Path, sample_rate: int) -> str:
    result = run_command(
        [
            "afconvert",
            "-f",
            "WAVE",
            "-d",
            "LEI24",
            "-r",
            str(sample_rate),
            str(encoded_m4a),
            str(decoded_wav),
        ]
    )
    return (result.stdout or "") + (result.stderr or "")


def run_afclip(target: Path) -> ClipStats:
    result = run_command(["afclip", str(target)])
    out = (result.stdout or "") + (result.stderr or "")
    on_sample = 0
    inter_sample = 0
    for line in out.splitlines():
        low = line.lower()
        if "on-sample" in low:
            on_sample = _extract_last_int(line)
        if "inter-sample" in low:
            inter_sample = _extract_last_int(line)
    return ClipStats(on_sample=on_sample, inter_sample=inter_sample, raw_text=out)


def _extract_last_int(line: str) -> int:
    ints = []
    current = ""
    for c in line:
        if c.isdigit():
            current += c
        elif current:
            ints.append(int(current))
            current = ""
    if current:
        ints.append(int(current))
    return ints[-1] if ints else 0


def calculate_diff_rms(source_wav: Path, decoded_wav: Path) -> float:
    with wave.open(str(source_wav), "rb") as s, wave.open(str(decoded_wav), "rb") as d:
        frames = min(s.getnframes(), d.getnframes())
        s_data = s.readframes(frames)
        d_data = d.readframes(frames)
    if not s_data or not d_data:
        return 0.0
    n = min(len(s_data), len(d_data))
    squared_sum = 0.0
    for i in range(n):
        diff = s_data[i] - d_data[i]
        squared_sum += diff * diff
    return math.sqrt(squared_sum / n)


def diff_verdict(rms: float) -> str:
    if rms < 2.0:
        return "合格"
    if rms < 6.0:
        return "要確認"
    return "不合格"


def attenuate_wav(source_wav: Path, out_wav: Path, db: float) -> None:
    factor = 10 ** (db / 20.0)
    with wave.open(str(source_wav), "rb") as src:
        params = src.getparams()
        raw = src.readframes(src.getnframes())

    width = params.sampwidth
    if width != 3:
        raise RuntimeError("24bit WAVのみ対応しています")

    converted = bytearray()
    for i in range(0, len(raw), 3):
        sample = int.from_bytes(raw[i : i + 3], "little", signed=True)
        out = int(sample * factor)
        out = max(min(out, 8388607), -8388608)
        converted.extend(int(out).to_bytes(3, "little", signed=True))

    with wave.open(str(out_wav), "wb") as dst:
        dst.setparams(params)
        dst.writeframes(bytes(converted))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def join_logs(*chunks: Iterable[str]) -> str:
    out: list[str] = []
    for c in chunks:
        for item in c:
            if item:
                out.append(item)
    return "\n".join(out)
