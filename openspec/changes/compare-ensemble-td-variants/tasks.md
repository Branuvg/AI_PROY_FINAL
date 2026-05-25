# Tasks: compare-ensemble-td-variants

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 300–500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 builders/exports → PR 2 reporting rows/metadata/conclusions → PR 3 docs/notebook/verification |
| Delivery strategy | auto; chained_pr_strategy=ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Add explicit ensemble variant builders and exports | PR 1 | Tests for composition, weights, and backward compatibility included. |
| 2 | Report both variants with distinct metadata and Spanish conclusions | PR 2 | Depends on PR 1; reporting tests included. |
| 3 | Refresh notebook-facing docs and run verification commands | PR 3 | Depends on PR 2; docs/notebook and execution proof included. |

## Phase 1: Builders and Exports

- [x] 1.1 Update `src/poker_ai/agents/ensemble.py` with `WITH_TD_ENSEMBLE_WEIGHTS`, `build_ensemble_no_td(seed)`, and `build_ensemble_with_td(td_agent, seed)`.
- [x] 1.2 Keep `build_default_ensemble()` backward compatible by delegating to no-TD while preserving legacy `name="Ensemble"`.
- [x] 1.3 Export new builders and weights from `src/poker_ai/agents/__init__.py`; update `src/poker_ai/evaluation/__init__.py` only if consumers require it.

## Phase 2: Reporting Integration

- [x] 2.1 Update `src/poker_ai/evaluation/reporting.py` `_build_report_agents(seed)` to include `EnsembleNoTD` and `EnsembleWithTD[ (fresh|untrained)]` rows.
- [x] 2.2 Extend report metadata so each ensemble row exposes distinct composition and weights without aggregation key collisions.
- [x] 2.3 Update Spanish conclusion rendering to mention both variants and recommend the no-TD baseline from observed metrics.

## Phase 3: Tests and Guards

- [x] 3.1 Add `tests/agents/test_model_agents.py` coverage for no-TD composition, with-TD inclusion, excluded Random/Call agents, and weight sums.
- [x] 3.2 Add `tests/evaluation/test_reporting.py` assertions for both ensemble rows, fallback TD labels, metadata separation, and Spanish conclusion text.
- [x] 3.3 Update `tests/test_notebook_contract.py` only if current expected-name guards reject `EnsembleNoTD` or `EnsembleWithTD`.

## Phase 4: Docs, Notebook, Verification

- [x] 4.1 Update `docs/notebook_backend_report.md` to replace deferred-TD wording with the side-by-side comparison narrative.
- [x] 4.2 Update markdown cells in `poker_ia_comparativa_final.ipynb`; avoid unrelated executable notebook changes.
- [x] 4.3 Verify with `uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_reporting.py`, `uv run pytest`, report experiment, and nbconvert execution.
