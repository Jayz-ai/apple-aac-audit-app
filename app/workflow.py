from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .audio_tools import (
    ClipStats,
    attenuate_wav,
    calculate_diff_rms,
    convert_to_aac,
    decode_aac_to_wav,
    diff_verdict,
    ensure_tools,
    run_afclip,
    write_json,
)
from .reporting import build_audit_markdown, build_autofix_markdown, write_markdown


LogFn = Callable[[str], None]
ProgressFn = Callable[[int, str], None]


@dataclass
class RunConfig:
    input_wav: Path
    reports_root: Path
    target_sr: int
    auto_remediate: bool


@dataclass
class RunResult:
    report_md: Path
    report_json: Path
    autofix_md: Path | None
    autofix_json: Path | None
    result_folder: Path


def execute(config: RunConfig, log: LogFn, progress: ProgressFn) -> RunResult:
    ensure_tools()
    out_dir = config.reports_root / config.input_wav.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    encoded = out_dir / "encoded.m4a"
    decoded = out_dir / "decode.wav"

    progress(5, "AAC変換中")
    log(convert_to_aac(config.input_wav, encoded))

    progress(20, "decode生成中")
    log(decode_aac_to_wav(encoded, decoded, config.target_sr))

    progress(35, "afclip検査中")
    source_clip = run_afclip(config.input_wav)
    encoded_clip = run_afclip(encoded)
    decoded_clip = run_afclip(decoded)
    log(_clip_log("source", source_clip))
    log(_clip_log("encoded", encoded_clip))
    log(_clip_log("decoded", decoded_clip))

    progress(50, "差分解析中")
    rms = calculate_diff_rms(config.input_wav, decoded)
    verdict = _overall_verdict(encoded_clip, rms)

    audit = {
        "source": str(config.input_wav),
        "target_sr": config.target_sr,
        "encoded": str(encoded),
        "decoded": str(decoded),
        "encoded_clip_on": encoded_clip.on_sample,
        "encoded_clip_inter": encoded_clip.inter_sample,
        "diff_rms": rms,
        "verdict": verdict,
    }
    report_md = out_dir / "report.md"
    report_json = out_dir / "report.json"

    progress(70, "レポート生成中")
    write_markdown(report_md, build_audit_markdown(audit))
    write_json(report_json, audit)

    autofix_md = None
    autofix_json = None
    if config.auto_remediate and (encoded_clip.on_sample > 0 or encoded_clip.inter_sample > 0):
        progress(75, "補正版生成中")
        autofix_md, autofix_json = _run_autofix(config, out_dir, log)

    progress(100, "完了")
    return RunResult(
        report_md=report_md,
        report_json=report_json,
        autofix_md=autofix_md,
        autofix_json=autofix_json,
        result_folder=out_dir,
    )


def _run_autofix(config: RunConfig, out_dir: Path, log: LogFn) -> tuple[Path, Path]:
    attempts = [-1.1, -1.3, -1.5, -1.7, -1.9, -2.1]
    trials: list[dict] = []
    chosen = None
    chosen_clip = ClipStats(on_sample=999999, inter_sample=999999, raw_text="")
    chosen_encoded = out_dir / "autofix_encoded.m4a"
    chosen_decoded = out_dir / "autofix_decode.wav"

    for db in attempts:
        trial_wav = out_dir / f"trial_{db:.1f}dB.wav"
        trial_encoded = out_dir / f"trial_{db:.1f}dB.m4a"
        trial_decoded = out_dir / f"trial_{db:.1f}dB_decode.wav"
        attenuate_wav(config.input_wav, trial_wav, db)
        convert_to_aac(trial_wav, trial_encoded)
        decode_aac_to_wav(trial_encoded, trial_decoded, config.target_sr)
        clip = run_afclip(trial_encoded)
        passed = clip.on_sample == 0 and clip.inter_sample == 0
        trials.append(
            {
                "name": trial_wav.name,
                "db": db,
                "aac_clip": "合格" if passed else "不合格",
                "on": clip.on_sample,
                "inter": clip.inter_sample,
            }
        )
        log(f"autofix試行 {db:.1f} dB => on={clip.on_sample}, inter={clip.inter_sample}")
        if passed and chosen is None:
            chosen = db
            chosen_clip = clip
            chosen_encoded = trial_encoded
            chosen_decoded = trial_decoded
            break

    if chosen is None:
        chosen = attempts[-1]

    diff_rms = calculate_diff_rms(config.input_wav, chosen_decoded)
    decision = "採用" if chosen_clip.on_sample == 0 and chosen_clip.inter_sample == 0 else "条件付き採用"
    summary = "AAC後クリップが解消" if decision == "採用" else "候補内で完全解消できず"
    comment = "差分RMSは中程度です。要確認。" if diff_rms >= 2.0 else "差分は小さい範囲です。"

    payload = {
        "source": str(config.input_wav),
        "target_sr": config.target_sr,
        "chosen_try": f"{chosen:.1f} dB",
        "chosen_db": chosen,
        "decision": decision,
        "trials": trials,
        "final_on": chosen_clip.on_sample,
        "final_inter": chosen_clip.inter_sample,
        "summary": summary,
        "encoded_path": str(chosen_encoded),
        "decoded_path": str(chosen_decoded),
        "diff_rms": diff_rms,
        "comment": comment,
    }

    md = out_dir / "autofix_report.md"
    js = out_dir / "autofix_report.json"
    write_markdown(md, build_autofix_markdown(payload))
    write_json(js, payload)
    return md, js


def _clip_log(name: str, stats: ClipStats) -> str:
    return f"{name}: on-sample={stats.on_sample}, inter-sample={stats.inter_sample}"


def _overall_verdict(encoded_clip: ClipStats, rms: float) -> str:
    if encoded_clip.on_sample > 0 or encoded_clip.inter_sample > 0:
        return "不合格"
    return diff_verdict(rms)
