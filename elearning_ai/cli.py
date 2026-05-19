from __future__ import annotations

import argparse
import sys

from .config import load_config
from .runner import format_results, run_automation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a configurable browser automation flow for e-learning assignments."
    )
    parser.add_argument("config", help="Path to the JSON config file.")
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory used for relative screenshot output paths (default: outputs).",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Show the browser window instead of running headless.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    results = run_automation(config, output_dir=args.output_dir, headed_override=args.headed)
    if results:
        print(format_results(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
