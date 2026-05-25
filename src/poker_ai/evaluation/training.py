"""Lightweight training helpers for extracted agents."""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from poker_ai.agents import (
    DEFAULT_ENSEMBLE_WEIGHTS,
    CallAgent,
    MarkovAgent,
    RandomAgent,
    TDAgent,
    build_default_ensemble,
)
from poker_ai.engine import play_hand

from .metrics import calculate_roi, evaluate_agent


CALIBRATION_SEEDS = (101, 202, 303)
CALIBRATION_HANDS = 40
CALIBRATION_PANEL = ("call", "random", "markov")
DEFAULT_TD_QTABLE_PATH = Path("artifacts/td_qtable.json")
DEFAULT_TD_ALPHA = 0.1
DEFAULT_TD_TRAIN_HANDS = 200
DEFAULT_TD_TRAIN_SEED = 17
CALIBRATION_WEIGHT_GRID: tuple[dict[str, float], ...] = (
    {"minimax": 0.5, "bayesian": 0.3, "markov": 0.2},
    {"minimax": 0.4, "bayesian": 0.4, "markov": 0.2},
    {"minimax": 0.4, "bayesian": 0.3, "markov": 0.3},
    {"minimax": 0.6, "bayesian": 0.2, "markov": 0.2},
    {"minimax": 0.2, "bayesian": 0.5, "markov": 0.3},
    {"minimax": 0.2, "bayesian": 0.3, "markov": 0.5},
    {"minimax": 1 / 3, "bayesian": 1 / 3, "markov": 1 / 3},
)


def train_td_agent(
    agent: TDAgent | None = None,
    opponent=None,
    *,
    n_hands: int = DEFAULT_TD_TRAIN_HANDS,
    rng: random.Random | None = None,
    master_seed: int | None = DEFAULT_TD_TRAIN_SEED,
    starting_stack: int = 1_000,
    save_path: str | Path | None = None,
    seed: int | None = None,
) -> TDAgent:
    """Train the extracted TD agent through repeated engine hands."""

    if n_hands <= 0:
        raise ValueError("n_hands must be positive.")
    resolved_seed = _resolve_master_seed(master_seed=master_seed, seed=seed, rng=rng)
    deck_rng, explore_rng, opponent_rng = _td_training_streams(resolved_seed, rng=rng)
    trained = agent or TDAgent(epsilon=0.1, alpha=DEFAULT_TD_ALPHA, rng=explore_rng)
    if agent is not None and getattr(agent, "rng", None) is None:
        agent.rng = explore_rng
    baseline = opponent or RandomAgent(opponent_rng)
    for _ in range(n_hands):
        result = play_hand(trained, baseline, deck_rng, starting_stack=starting_stack)
        trained.observe_reward(result.profit[0])
    if save_path is not None:
        trained.save(save_path, episodes=n_hands, seed=resolved_seed)
    return trained


def _resolve_master_seed(
    *, master_seed: int | None, seed: int | None, rng: random.Random | None
) -> int | None:
    if seed is not None:
        return seed
    if rng is not None:
        return None
    return master_seed


def _td_training_streams(
    master_seed: int | None = DEFAULT_TD_TRAIN_SEED,
    *,
    rng: random.Random | None = None,
) -> tuple[random.Random, random.Random, random.Random]:
    """Build independent deck, exploration, and opponent RNG streams."""

    master = rng or random.Random(master_seed)
    seeds = [master.randrange(0, 2**63) for _ in range(3)]
    return tuple(random.Random(stream_seed) for stream_seed in seeds)  # type: ignore[return-value]


def estimate_transition_probabilities(histories: Iterable[Iterable[dict]]) -> dict[tuple[str, str], dict[str, float]]:
    """Estimate next-action probabilities from engine action histories."""

    counts: dict[tuple[str, str], defaultdict[str, int]] = {}
    for history in histories:
        entries = list(history)
        for current, following in zip(entries, entries[1:]):
            key = (str(current.get("phase", "unknown")), str(current.get("action", "unknown")))
            counts.setdefault(key, defaultdict(int))[str(following.get("action", "unknown"))] += 1
    return {
        key: {action: count / sum(next_counts.values()) for action, count in next_counts.items()}
        for key, next_counts in counts.items()
    }


def calibrate_ensemble_weights(
    *,
    seeds: tuple[int, ...] = CALIBRATION_SEEDS,
    hands_per_seed: int = CALIBRATION_HANDS,
    panel: tuple[str, ...] = CALIBRATION_PANEL,
) -> dict[str, float]:
    """Run a bounded deterministic grid search and return the committed default weights."""

    if hands_per_seed <= 0:
        raise ValueError("hands_per_seed must be positive.")
    if not seeds:
        raise ValueError("At least one calibration seed is required.")

    ranked = [
        (_score_weights(weights, seeds=seeds, hands_per_seed=hands_per_seed, panel=panel), weights)
        for weights in CALIBRATION_WEIGHT_GRID
    ]
    best_weights = max(ranked, key=lambda item: item[0])[1]
    return {name: round(float(best_weights[name]), 6) for name in DEFAULT_ENSEMBLE_WEIGHTS}


def _score_weights(
    weights: dict[str, float],
    *,
    seeds: tuple[int, ...],
    hands_per_seed: int,
    panel: tuple[str, ...],
) -> tuple[float, float, float]:
    total_profit = 0
    total_invested = 0
    total_wins = 0
    total_hands = 0
    for seed in seeds:
        for panel_index, opponent_name in enumerate(panel):
            ensemble = build_default_ensemble(seed + panel_index)
            ensemble.weights = dict(weights)
            result = evaluate_agent(
                ensemble,
                _build_calibration_opponent(opponent_name, seed + panel_index * 10_000),
                n_hands=hands_per_seed,
                rng=random.Random(seed + panel_index * 100_000),
            )
            total_profit += result.total_profit
            total_invested += result.total_invested
            total_wins += result.wins
            total_hands += result.hands
    return (
        calculate_roi(total_profit, total_invested),
        total_wins / total_hands if total_hands else 0.0,
        total_profit,
    )


def _build_calibration_opponent(name: str, seed: int):
    if name == "call":
        return CallAgent()
    if name == "random":
        return RandomAgent(random.Random(seed))
    if name == "markov":
        return MarkovAgent()
    raise ValueError(f"Unknown calibration opponent: {name}")
