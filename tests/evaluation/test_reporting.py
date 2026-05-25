from __future__ import annotations

import pytest

from poker_ai.agents import TDAgent
from poker_ai.engine import Action
from poker_ai.evaluation import (
    DEFAULT_ENSEMBLE_WEIGHTS,
    WITH_TD_ENSEMBLE_WEIGHTS,
    config_from_env,
    render_spanish_conclusions,
    run_report_experiment,
)


def test_config_from_env_supports_academic_overrides() -> None:
    config = config_from_env({"POKER_REPORT_HANDS": "12", "POKER_REPORT_SEEDS": "1,2,3"})

    assert config.hands_per_seed == 12
    assert config.seeds == (1, 2, 3)
    assert config.total_hands_per_agent == 36


def test_run_report_experiment_aggregates_multiple_seeds(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("POKER_REPORT_FRESH_TD", "0")
    config = config_from_env({"POKER_REPORT_HANDS": "2", "POKER_REPORT_SEEDS": "42,43"})

    with pytest.warns(RuntimeWarning, match="untrained TDLearning fallback"):
        rows = run_report_experiment(config)

    assert {row.agent_name for row in rows} == {
        "Random",
        "Minimax",
        "Bayesian",
        "Markov",
        "TDLearning (untrained)",
        "EnsembleNoTD",
        "EnsembleWithTD (untrained)",
    }
    assert all(row.seeds == 2 for row in rows)
    assert all(row.hands_per_seed == 2 for row in rows)
    assert all(row.total_hands == 4 for row in rows)


def test_run_report_experiment_exposes_distinct_ensemble_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("POKER_REPORT_FRESH_TD", "0")
    config = config_from_env({"POKER_REPORT_HANDS": "2", "POKER_REPORT_SEEDS": "42"})

    with pytest.warns(RuntimeWarning, match="untrained TDLearning fallback"):
        rows = run_report_experiment(config)
    no_td = next(row for row in rows if row.agent_name == "EnsembleNoTD")
    with_td = next(row for row in rows if row.agent_name == "EnsembleWithTD (untrained)")

    assert no_td.composition == ("minimax", "bayesian", "markov")
    assert no_td.weights == tuple(DEFAULT_ENSEMBLE_WEIGHTS.values())
    assert no_td.as_dict()["composition"] == ("minimax", "bayesian", "markov")
    assert no_td.as_dict()["weights"] == tuple(DEFAULT_ENSEMBLE_WEIGHTS.values())
    assert with_td.composition == ("minimax", "bayesian", "markov", "td")
    assert with_td.weights == tuple(WITH_TD_ENSEMBLE_WEIGHTS.values())
    assert with_td.as_dict()["composition"] == ("minimax", "bayesian", "markov", "td")
    assert with_td.as_dict()["weights"] == tuple(WITH_TD_ENSEMBLE_WEIGHTS.values())


def test_render_spanish_conclusions_mentions_ensemble_weights_and_roi(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("POKER_REPORT_FRESH_TD", "0")
    config = config_from_env({"POKER_REPORT_HANDS": "2", "POKER_REPORT_SEEDS": "42"})
    with pytest.warns(RuntimeWarning, match="untrained TDLearning fallback"):
        rows = run_report_experiment(config)

    conclusions = render_spanish_conclusions(rows)

    assert "EnsembleNoTD" in conclusions
    assert "EnsembleWithTD" in conclusions
    assert "baseline principal" in conclusions
    assert "minimax" in conclusions
    assert "bayesian" in conclusions
    assert "markov" in conclusions
    assert "pesos" in conclusions
    assert "ROI" in conclusions
    assert "Caveat" in conclusions
    assert "TDLearning" in conclusions
    assert "α=0.1" in conclusions
    assert "td_meets_gate" in conclusions


def test_run_report_experiment_loads_td_snapshot_when_available(tmp_path, monkeypatch) -> None:
    path = tmp_path / "td_qtable.json"
    TDAgent(q_values={("preflop", 5, 0, "premium"): {Action.CALL: 2.0}}).save(path, episodes=1, seed=7)
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(path))
    monkeypatch.setenv("POKER_REPORT_FRESH_TD", "0")
    config = config_from_env({"POKER_REPORT_HANDS": "1", "POKER_REPORT_SEEDS": "42"})

    rows = run_report_experiment(config)

    assert "TDLearning" in {row.agent_name for row in rows}
    assert "TDLearning (untrained)" not in {row.agent_name for row in rows}
    assert "EnsembleWithTD" in {row.agent_name for row in rows}


def test_run_report_experiment_warns_and_labels_td_when_snapshot_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(tmp_path / "missing.json"))
    monkeypatch.setenv("POKER_REPORT_FRESH_TD", "0")
    config = config_from_env({"POKER_REPORT_HANDS": "1", "POKER_REPORT_SEEDS": "42"})

    with pytest.warns(RuntimeWarning, match="untrained TDLearning fallback"):
        rows = run_report_experiment(config)

    assert "TDLearning (untrained)" in {row.agent_name for row in rows}
    assert "EnsembleWithTD (untrained)" in {row.agent_name for row in rows}


def test_run_report_experiment_uses_fresh_td_by_default(tmp_path, monkeypatch) -> None:
    stale = tmp_path / "stale.json"
    TDAgent(q_values={("preflop", 5, 0, "weak"): {Action.FOLD: 99.0}}).save(stale, episodes=1, seed=7)
    monkeypatch.setenv("POKER_TD_QTABLE_PATH", str(stale))
    monkeypatch.delenv("POKER_REPORT_FRESH_TD", raising=False)
    config = config_from_env({"POKER_REPORT_HANDS": "1", "POKER_REPORT_SEEDS": "42"})

    rows = run_report_experiment(config)
    td_row = next(row for row in rows if row.agent_name.startswith("TDLearning"))

    assert td_row.agent_name == "TDLearning (fresh)"
    assert isinstance(td_row.td_meets_gate, bool)
    assert td_row.as_dict()["td_meets_gate"] is td_row.td_meets_gate
    assert "EnsembleWithTD (fresh)" in {row.agent_name for row in rows}
