"""Static contract tests for the presentation notebook."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[1] / "poker_ia_comparativa_final.ipynb"

FORBIDDEN_DEFINITIONS = {
    "Action",
    "BaseAgent",
    "BayesianAgent",
    "CallAgent",
    "EnsembleAgent",
    "GameState",
    "HandResult",
    "MarkovAgent",
    "MinimaxAgent",
    "QLearningAgent",
    "RandomAgent",
    "TDAgent",
    "action_to_bet_size",
    "calculate_roi",
    "deal_hand",
    "evaluate_agent",
    "evaluate_hand",
    "get_legal_actions",
    "legal_actions",
    "play_hand",
    "summarize_results",
    "train_td_agent",
}

OLD_ROI_FORMULA = re.compile(r"\bn_hands\s*\*\s*BIG_BLIND\b|\bBIG_BLIND\s*\*\s*n_hands\b")


def _code_sources() -> list[str]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]


def _markdown_sources() -> list[str]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "markdown"
    ]


def test_notebook_imports_modular_backend() -> None:
    joined = "\n".join(_code_sources())

    assert "from poker_ai.evaluation import" in joined
    assert "ExperimentConfig" in joined
    assert "run_report_experiment(" in joined
    assert "hands_per_seed=40" in joined
    assert "seeds=(101, 202, 303)" in joined


def test_notebook_final_run_does_not_require_environment_variables() -> None:
    joined = "\n".join(_code_sources())

    assert "config_from_env" not in joined
    assert "os.environ" not in joined
    assert "POKER_REPORT_HANDS" not in joined
    assert "POKER_REPORT_SEEDS" not in joined


def test_notebook_does_not_define_core_logic() -> None:
    found: list[str] = []
    for source in _code_sources():
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in FORBIDDEN_DEFINITIONS:
                    found.append(node.name)

    assert not found, f"Notebook must import core logic from poker_ai, not define: {sorted(found)}"


def test_notebook_does_not_use_historical_roi_denominator() -> None:
    joined = "\n".join(_code_sources())

    assert OLD_ROI_FORMULA.search(joined) is None


def test_notebook_documents_td_preflop_gate() -> None:
    joined = "\n".join(_markdown_sources())

    assert "bucket preflop" in joined
    assert "leakage-safe" in joined
    assert "td_meets_gate" in joined
    assert "EnsembleNoTD" in joined
    assert "EnsembleWithTD" in joined
