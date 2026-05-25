from __future__ import annotations

import time
import random

from poker_ai.agents import TDAgent
from poker_ai.engine import Action
from poker_ai.evaluation import DEFAULT_ENSEMBLE_WEIGHTS, calibrate_ensemble_weights
from poker_ai.evaluation.training import train_td_agent


def test_calibrate_ensemble_weights_is_deterministic_and_committed() -> None:
    first = calibrate_ensemble_weights(seeds=(101,), hands_per_seed=4)
    second = calibrate_ensemble_weights(seeds=(101,), hands_per_seed=4)

    assert first == second
    assert first == DEFAULT_ENSEMBLE_WEIGHTS


def test_calibrate_ensemble_weights_returns_bounded_default_keys_quickly() -> None:
    started = time.perf_counter()

    weights = calibrate_ensemble_weights(seeds=(101,), hands_per_seed=2, panel=("call", "random", "markov"))

    elapsed = time.perf_counter() - started
    assert elapsed < 60
    assert tuple(weights) == ("minimax", "bayesian", "markov")
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(0.0 <= weight <= 1.0 for weight in weights.values())


def test_train_td_agent_writes_non_empty_qtable_snapshot(tmp_path) -> None:
    path = tmp_path / "td_qtable.json"

    agent = train_td_agent(n_hands=10, master_seed=17, save_path=path)

    assert path.exists()
    assert any(actions for actions in agent.q_values.values())
    loaded = TDAgent.load(path)
    assert dict(loaded.q_values) == dict(agent.q_values)


def test_td_qtable_roundtrip_preserves_values(tmp_path) -> None:
    path = tmp_path / "roundtrip.json"
    q_values = {("preflop", 10, 0, "premium"): {Action.CALL: 1.5, Action.FOLD: -0.2}}
    agent = TDAgent(alpha=0.2, q_values=q_values)

    agent.save(path, episodes=3, seed=99)
    loaded = TDAgent.load(path)

    assert loaded.alpha == 0.2
    assert dict(loaded.q_values) == q_values


def test_train_td_agent_is_reproducible_for_same_master_seed() -> None:
    first = train_td_agent(n_hands=12, master_seed=123)
    second = train_td_agent(n_hands=12, master_seed=123)

    assert dict(first.q_values) == dict(second.q_values)


def test_train_td_agent_master_seed_changes_trajectory() -> None:
    first = train_td_agent(n_hands=12, master_seed=123)
    second = train_td_agent(n_hands=12, master_seed=124)

    assert dict(first.q_values) != dict(second.q_values)
