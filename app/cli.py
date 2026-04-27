from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import RunConfig, execute


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apple AAC監査ツール")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="監査を実行")
    run.add_argument("input_wav", type=Path)
    run.add_argument("--target-sr", type=int, choices=[44100, 48000], default=48000)
    run.add_argument("--reports-root", type=Path, required=True)
    run.add_argument("--auto-remediate", action="store_true")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        cfg = RunConfig(
            input_wav=args.input_wav,
            reports_root=args.reports_root,
            target_sr=args.target_sr,
            auto_remediate=args.auto_remediate,
        )

        def log(msg: str) -> None:
            if msg.strip():
                print(msg.strip())

        def progress(pct: int, step: str) -> None:
            print(f"[{pct:3d}%] {step}")

        result = execute(cfg, log, progress)
        print(f"report.md: {result.report_md}")
        print(f"report.json: {result.report_json}")
        if result.autofix_md:
            print(f"autofix_report.md: {result.autofix_md}")
            print(f"autofix_report.json: {result.autofix_json}")
    return 0
