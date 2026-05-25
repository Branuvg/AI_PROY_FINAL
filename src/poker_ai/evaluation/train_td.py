"""Command-line entry point for deterministic TD training."""

from __future__ import annotations

import argparse
from pathlib import Path

from .training import DEFAULT_TD_QTABLE_PATH, DEFAULT_TD_TRAIN_HANDS, DEFAULT_TD_TRAIN_SEED, train_td_agent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train and persist the TDLearning Q-table snapshot.")
    parser.add_argument("--hands", type=int, default=DEFAULT_TD_TRAIN_HANDS)
    parser.add_argument("--seed", type=int, default=DEFAULT_TD_TRAIN_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_TD_QTABLE_PATH)
    args = parser.parse_args(argv)

    agent = train_td_agent(n_hands=args.hands, master_seed=args.seed, save_path=args.output)
    states = sum(1 for actions in agent.q_values.values() if actions)
    print(f"Saved TD Q-table to {args.output} ({states} state(s), hands={args.hands}, seed={args.seed}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
