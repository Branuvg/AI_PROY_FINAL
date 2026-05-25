## Verification Report

**Change**: calibrate-ensemble-strategy  
**Version**: N/A  
**Mode**: Standard

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 15 |
| Tasks complete | 15 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: ➖ Not separate from tests; Python package exercised through `uv run pytest` and notebook execution.

**Tests**: ✅ 30 passed / ❌ 0 failed / ⚠️ 0 skipped

```text
uv run pytest

collected 30 items
tests/agents/test_base_agents.py ...
tests/agents/test_model_agents.py ..........
tests/engine/test_rules.py ..
tests/engine/test_simulator.py ...
tests/evaluation/test_metrics.py ...
tests/evaluation/test_reporting.py ....
tests/evaluation/test_training.py ..
tests/test_notebook_contract.py ...

30 passed in 0.14s
```

**Coverage**: ➖ Not available; no coverage threshold configured for this verification.

### Experiment Evidence

**Calibration command**: ✅ Passed

```text
uv run python -c "from poker_ai.evaluation import calibrate_ensemble_weights; print(calibrate_ensemble_weights())"
{'minimax': 0.5, 'bayesian': 0.3, 'markov': 0.2}
```

Parameters: default calibration seeds `(101, 202, 303)`, `hands_per_seed=40`, panel `("call", "random", "markov")`, grid size `7`.

**Report experiment command**: ✅ Passed

```text
POKER_REPORT_HANDS=100 POKER_REPORT_SEEDS=42,43,44,45,46 uv run python -c "from poker_ai.evaluation import config_from_env, run_report_experiment, render_spanish_conclusions; rows=sorted(run_report_experiment(config_from_env()), key=lambda r: (r.roi, r.avg_profit), reverse=True); print('agent|win_rate|total_profit|total_invested|roi|avg_profit|composition|weights'); [print(f'{r.agent_name}|{r.win_rate:.3f}|{r.total_profit}|{r.total_invested}|{r.roi:.6f}|{r.avg_profit:.3f}|{','.join(r.composition)}|{','.join(str(w) for w in r.weights)}') for r in rows]; print(); print(render_spanish_conclusions(rows))"
```

| Agent | Win rate | Total profit | Total invested | ROI | Avg profit | Composition | Weights |
|---|---:|---:|---:|---:|---:|---|---|
| Ensemble | 0.506 | 300 | 5000 | 0.060000 | 0.600 | minimax,bayesian,markov | 0.5,0.3,0.2 |
| Bayesian | 0.486 | 30 | 5000 | 0.006000 | 0.060 |  |  |
| Minimax | 0.480 | 10 | 5000 | 0.002000 | 0.020 |  |  |
| Markov | 0.462 | -170 | 5000 | -0.034000 | -0.340 |  |  |
| Random | 0.278 | -1515 | 5945 | -0.254836 | -3.030 |  |  |
| TDLearning | 0.000 | -2500 | 2500 | -1.000000 | -5.000 |  |  |

Spanish conclusion evidence: generated text states the best ROI was Ensemble at `0.060000`, identifies the calibrated constituents as `minimax, bayesian, markov`, lists weights `0.5, 0.3, 0.2`, and includes the calibration caveat about small fixed-seed validation.

**Notebook execution**: ✅ Passed

```text
POKER_REPORT_HANDS=100 POKER_REPORT_SEEDS=42,43,44,45,46 uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --inplace
[NbConvertApp] Converting notebook poker_ia_comparativa_final.ipynb to notebook
[NbConvertApp] Writing 13180 bytes to poker_ia_comparativa_final.ipynb
```

Notebook output inspection confirmed the executed notebook includes `minimax, bayesian, markov`, weights `0.5, 0.3, 0.2`, and Spanish conclusions matching the 100-hands × 5-seeds run.

### Spec Compliance Matrix

| Requirement | Scenario | Test / Execution Evidence | Result |
|-------------|----------|---------------------------|--------|
| Default Ensemble Composition | Instantiating default ensemble uses Minimax, Bayesian, Markov and no Random/Call | `tests/agents/test_model_agents.py::test_default_ensemble_uses_calibrated_strong_constituents_only`; `tests/agents/test_model_agents.py::test_ensemble_without_explicit_agents_uses_same_calibrated_default`; passed in `uv run pytest` | ✅ COMPLIANT |
| Exclude TD Agent by Default | TD agent absent or zero-weight in default ensemble | `tests/agents/test_model_agents.py::test_default_ensemble_uses_calibrated_strong_constituents_only`; passed in `uv run pytest` | ✅ COMPLIANT |
| Reproducible Calibration Weights | Calibration run produces documented static weights applied during voting | `tests/evaluation/test_training.py::test_calibrate_ensemble_weights_is_deterministic_and_committed`; default calibration command returned `{'minimax': 0.5, 'bayesian': 0.3, 'markov': 0.2}` | ✅ COMPLIANT |
| Guard Against Regression | Test suite confirms default constituents and no old notebook code paths | `tests/agents/test_model_agents.py` guards plus `tests/test_notebook_contract.py`; grep found notebook render paths for composition/weights and no old Random+Call narrative in notebook outputs | ✅ COMPLIANT |
| Ensemble Evaluation Report | Report includes constituent agents, weights, and corrected ROI | `tests/evaluation/test_reporting.py::test_run_report_experiment_exposes_ensemble_metadata`; 100×5 report table exposes Ensemble composition/weights and ROI `0.060000` | ✅ COMPLIANT |
| Spanish Conclusions | Professional Spanish conclusions reflect post-calibration metrics and caveats | `tests/evaluation/test_reporting.py::test_render_spanish_conclusions_mentions_ensemble_weights_and_roi`; 100×5 report and executed notebook show generated Spanish conclusions with actual ROI/win-rate/weights/caveat | ✅ COMPLIANT |

**Compliance summary**: 6/6 scenarios compliant.

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Default/report ensemble strong composition | ✅ Implemented | `src/poker_ai/agents/ensemble.py` defaults to Minimax, Bayesian, Markov; `src/poker_ai/evaluation/reporting.py` uses `build_default_ensemble(seed)`. |
| No Random/Call/TD in default ensemble | ✅ Implemented | Default constructor and helper use only strong constituents; explicit custom ensembles remain supported by design. |
| Reproducible/documented weights | ✅ Implemented | `DEFAULT_ENSEMBLE_WEIGHTS = {minimax: 0.5, bayesian: 0.3, markov: 0.2}` and `calibrate_ensemble_weights()` regenerates the same vector with fixed seeds/panel/grid. |
| Composition exposed in report/notebook | ✅ Implemented | `ReportRow` includes `composition` and `weights`; notebook renders both from report rows. |
| Spanish conclusions reflect actual post-calibration results | ✅ Implemented | `render_spanish_conclusions(rows)` derives best agent, ROI, win-rate, average profit, ensemble weights, and caveat from actual report rows. |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Default constituents: Minimax + Bayesian + Markov | ✅ Yes | Verified in source, tests, report, and notebook. |
| Calibration: bounded curated grid over Call/Random/Markov panel | ✅ Yes | `CALIBRATION_WEIGHT_GRID` has 7 vectors and the panel is `("call", "random", "markov")`. |
| Seeds/budget: `(101, 202, 303)`, `40` hands | ✅ Yes | Defaults implemented and exercised by calibration command. |
| Weight provenance: committed constant, no import-time calibration | ✅ Yes | Constant lives in `ensemble.py`; calibration is explicit. |
| Reporting surface: `ReportRow.composition` and `ReportRow.weights` | ✅ Yes | Included in dataclass and `as_dict()`. |
| Templated Spanish conclusions | ✅ Yes | `render_spanish_conclusions(rows)` generates data-bound Spanish text. |

### Issues Found

**CRITICAL**: None  
**WARNING**: None  
**SUGGESTION**: Consider a later statistical validation run with more hands/opponents and confidence intervals; current caveat accurately documents the intentionally small calibration scope.

### Verdict

PASS

All SDD requirements and completed tasks are verified by passing runtime tests, calibration execution, a stronger 500-hands-per-agent report experiment, and executed notebook outputs.
