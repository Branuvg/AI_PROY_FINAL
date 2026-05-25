"""Small evaluation CLI used by verification commands."""

from __future__ import annotations

import argparse

from .reporting import config_from_env, render_spanish_conclusions, run_report_experiment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Poker AI evaluation helpers.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("report", help="Run the reproducible report experiment.")
    args = parser.parse_args(argv)

    if args.command == "report":
        rows = sorted(run_report_experiment(config_from_env()), key=lambda row: (row.roi, row.avg_profit), reverse=True)
        for row in rows:
            print(row)
        print()
        print(render_spanish_conclusions(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
