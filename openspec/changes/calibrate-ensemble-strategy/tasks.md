# Tasks: Calibrate Ensemble Strategy

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 260-380 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | Single PR: code + tests + notebook/report refresh |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Calibrated ensemble defaults and deterministic calibration | PR 1 | Foundation; tests included with code. |
| 2 | Reporting/notebook exposure and Spanish conclusions | PR 1 | Depends on Unit 1; keep notebook diff minimal. |

## Phase 1: Ensemble Foundation

- [x] 1.1 Update `src/poker_ai/agents/ensemble.py` with `DEFAULT_ENSEMBLE_WEIGHTS` and `build_default_ensemble(seed)` using Minimax, Bayesian, Markov.
- [x] 1.2 Preserve explicit `EnsembleAgent(agents, weights)` behavior; ensure default path excludes Random, Call, and TD.
- [x] 1.3 Export default ensemble helpers from `src/poker_ai/agents/__init__.py` if needed by reporting/tests.

## Phase 2: Calibration Utility

- [x] 2.1 Add `CALIBRATION_SEEDS`, `CALIBRATION_HANDS`, weight grid, and `calibrate_ensemble_weights()` to `src/poker_ai/evaluation/training.py`.
- [x] 2.2 Use fixed RNGs and panel `("call", "random", "markov")`; return a deterministic dict matching committed `DEFAULT_ENSEMBLE_WEIGHTS`.
- [x] 2.3 Export `calibrate_ensemble_weights` from `src/poker_ai/evaluation/__init__.py`.

## Phase 3: Reporting and Notebook

- [x] 3.1 Extend `ReportRow` in `src/poker_ai/evaluation/reporting.py` with `composition` and `weights`; include both in `as_dict()`.
- [x] 3.2 Replace report ensemble construction with `build_default_ensemble(seed)` and attach composition/weights when aggregating rows.
- [x] 3.3 Add `render_spanish_conclusions(rows)` with professional Spanish text mentioning composition, weights, ROI, and calibration caveats.
- [x] 3.4 Update `poker_ia_comparativa_final.ipynb` and refreshed result outputs to render `composition`, `weights`, and generated Spanish conclusions only.

## Phase 4: Tests and Guards

- [x] 4.1 Extend `tests/agents/test_model_agents.py` to assert default ensemble constituents/weights and forbid Random, Call, TD.
- [x] 4.2 Create `tests/evaluation/test_training.py` for deterministic calibration and bounded key/weight output.
- [x] 4.3 Extend `tests/evaluation/test_reporting.py` to assert Ensemble row metadata and Spanish conclusion content.
- [x] 4.4 Run verification: `uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_reporting.py tests/evaluation/test_training.py -q`.
- [x] 4.5 Run calibration/report smoke: `uv run python -c "from poker_ai.evaluation import calibrate_ensemble_weights; print(calibrate_ensemble_weights())"` and `POKER_REPORT_HANDS=20 POKER_REPORT_SEEDS=42,43 uv run python -c "from poker_ai.evaluation import config_from_env, run_report_experiment, render_spanish_conclusions; rows=run_report_experiment(config_from_env()); print(render_spanish_conclusions(rows))"`.
