"""Evaluation helpers for poker agents."""

from poker_ai.agents import DEFAULT_ENSEMBLE_WEIGHTS, WITH_TD_ENSEMBLE_WEIGHTS

from .metrics import EvaluationResult, calculate_roi, evaluate_agent, summarize_results
from .reporting import (
    ExperimentConfig,
    ReportRow,
    config_from_env,
    evaluate_td_metric_gate,
    render_spanish_conclusions,
    run_report_experiment,
)
from .training import (
    DEFAULT_TD_ALPHA,
    DEFAULT_TD_QTABLE_PATH,
    DEFAULT_TD_TRAIN_HANDS,
    DEFAULT_TD_TRAIN_SEED,
    calibrate_ensemble_weights,
    estimate_transition_probabilities,
    train_td_agent,
)

__all__ = [
    "EvaluationResult",
    "ExperimentConfig",
    "DEFAULT_ENSEMBLE_WEIGHTS",
    "DEFAULT_TD_ALPHA",
    "DEFAULT_TD_QTABLE_PATH",
    "DEFAULT_TD_TRAIN_HANDS",
    "DEFAULT_TD_TRAIN_SEED",
    "WITH_TD_ENSEMBLE_WEIGHTS",
    "ReportRow",
    "calculate_roi",
    "calibrate_ensemble_weights",
    "config_from_env",
    "evaluate_agent",
    "evaluate_td_metric_gate",
    "estimate_transition_probabilities",
    "render_spanish_conclusions",
    "run_report_experiment",
    "summarize_results",
    "train_td_agent",
]
