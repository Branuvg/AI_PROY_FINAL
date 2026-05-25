# Design: compare-ensemble-td-variants

## Technical Approach

Keep `EnsembleAgent` and add two builders in `agents/ensemble.py`:

- `build_ensemble_no_td(seed)` — calibrated baseline (Minimax/Bayesian/Markov, 0.5/0.3/0.2), name `EnsembleNoTD`.
- `build_ensemble_with_td(td_agent, seed)` — same trio plus TD with small committed weight, name `EnsembleWithTD`.

`reporting.py` evaluates both side-by-side. Each row carries its own composition/weights so aggregation keys do not collide. Spanish conclusions render a comparison and recommend the no-TD baseline based on observed ROI. `build_default_ensemble` delegates to `build_ensemble_no_td` so existing tests, calibration code, and the legacy `Ensemble` label stay intact for unchanged consumers; only the report runner switches to the explicit variant names.

## Architecture Decisions

| Decision | Choice | Alternative | Rationale |
|---|---|---|---|
| Variant API | Two builders returning `EnsembleAgent` with distinct `name` | Subclasses per variant | Keeps weighted-vote logic in one class; matches existing `build_default_ensemble` pattern. |
| Report labels | Set `EnsembleNoTD`/`EnsembleWithTD` via `EnsembleAgent.name` | Tag rows in `reporting.py` only | Label travels with the agent, prevents grouping collisions in `grouped[result.agent_name]`. |
| With-TD weights | Minimax 0.45 / Bayesian 0.27 / Markov 0.18 / TD 0.10 | Equal 0.25 each | Preserves trio dominance (0.90 sum) so TD cannot capture votes alone; trio internal ratios kept at 0.5/0.3/0.2 × 0.9; sums to 1.0. Committed as `WITH_TD_ENSEMBLE_WEIGHTS` for determinism. |
| TD construction | Inject `td_agent` from `_load_report_td_agent(seed)` | Build TD inside builder | Keeps fresh/snapshot/untrained policy in one place; builder stays pure and seedable. |
| Backward compat | `build_default_ensemble` delegates to `build_ensemble_no_td`; legacy `name="Ensemble"` kept on that path | Rename existing tests | Tests/calibration asserting `agent_name == "Ensemble"` still pass; only the report runner uses variant names. |
| TD label propagation | Append fallback suffix into with-TD label (e.g. `EnsembleWithTD (fresh)`) | Hide TD status | Mirrors existing `TDLearning (fresh)` convention; report explains fallback behaviour. |

## Data Flow

    config_from_env ─► run_report_experiment
        │
        ├─► _build_report_agents(seed)
        │       ├─ Random, Minimax, Bayesian, Markov
        │       ├─ td_agent = _load_report_td_agent(seed)
        │       ├─ build_ensemble_no_td(seed)           → name "EnsembleNoTD"
        │       └─ build_ensemble_with_td(td_agent)     → name "EnsembleWithTD[ (fresh|untrained)]"
        │
        ├─► evaluate_agent(...) per agent
        ├─► _report_agent_metadata(seed) emits composition+weights for both ensembles
        └─► _aggregate_results → ReportRow per agent
                                    │
                                    └─► render_spanish_conclusions(rows)
                                            mentions both variants, recommends no-TD

## File Changes

| File | Action | Description |
|---|---|---|
| `src/poker_ai/agents/ensemble.py` | Modify | Add `WITH_TD_ENSEMBLE_WEIGHTS`, `build_ensemble_no_td`, `build_ensemble_with_td`; `build_default_ensemble` delegates to no-TD. |
| `src/poker_ai/agents/__init__.py` | Modify | Export new builders and `WITH_TD_ENSEMBLE_WEIGHTS`. |
| `src/poker_ai/evaluation/reporting.py` | Modify | Swap legacy `Ensemble` row for the two variants; extend `_report_agent_metadata` to return both; update Spanish conclusions to compare them and recommend no-TD. |
| `src/poker_ai/evaluation/__init__.py` | Modify | Re-export `WITH_TD_ENSEMBLE_WEIGHTS` if reporting consumers need it. |
| `tests/agents/test_model_agents.py` | Modify | Tests for both builders: composition, weights sum, TD inclusion/exclusion, no Random/Call. |
| `tests/evaluation/test_reporting.py` | Modify | Assert rows contain `EnsembleNoTD` and `EnsembleWithTD` with distinct metadata; conclusions string mentions both and recommends no-TD. |
| `docs/notebook_backend_report.md` | Modify | Replace deferred-TD narrative with side-by-side comparison paragraph. |
| `poker_ia_comparativa_final.ipynb` | Modify | Update markdown cells; do not change executable code beyond what the runner already produces. |
| `tests/test_notebook_contract.py` | Modify (only if needed) | Add `EnsembleNoTD`/`EnsembleWithTD` to expected-name set if the contract pins agent names. |

## Interfaces / Contracts

```python
WITH_TD_ENSEMBLE_WEIGHTS: dict[str, float] = {
    "minimax": 0.45, "bayesian": 0.27, "markov": 0.18, "td": 0.10,
}

def build_ensemble_no_td(seed: int | None = None) -> EnsembleAgent: ...
def build_ensemble_with_td(td_agent: TDAgent, seed: int | None = None) -> EnsembleAgent: ...
```

`EnsembleAgent.name` is set to `EnsembleNoTD` / `EnsembleWithTD[ (fresh|untrained)]` by the builder so downstream grouping by `result.agent_name` produces two distinct rows.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit | Both builders return correct composition, weights sum to 1.0, exclusions hold | `pytest` introspection in `tests/agents/test_model_agents.py`. |
| Integration | `run_report_experiment` yields rows for both variants with distinct composition/weights metadata | Existing fixtures in `tests/evaluation/test_reporting.py` with `POKER_REPORT_FRESH_TD=0` and missing snapshot path. |
| Narrative | Spanish conclusions mention both variants and recommend no-TD | Substring assertions in `test_render_spanish_conclusions_*`. |
| Regression | `build_default_ensemble` still returns the no-TD baseline used by calibration | Existing `test_default_ensemble_uses_calibrated_strong_constituents_only` unchanged. |

## Verification Commands

```bash
uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_reporting.py
uv run pytest
POKER_REPORT_HANDS=2 POKER_REPORT_SEEDS=42 POKER_REPORT_FRESH_TD=0 \
  uv run python -m poker_ai.evaluation.report_experiment
```

## Migration / Rollout

No data migration. The `build_default_ensemble` symbol and its `name="Ensemble"` are preserved for external/legacy callers; only `reporting.py` switches to the explicit variant names. Notebook re-execution is needed once to refresh narrative cells.

## Open Questions

- [ ] Confirm with-TD weights `0.45/0.27/0.18/0.10` before locking — tasks phase can run a one-shot ROI check vs Call and adjust the TD weight in the 0.05–0.15 band if needed.
- [ ] Should `EnsembleWithTD` use `_load_report_td_agent` directly (current plan) or accept any TD provider for future calibration experiments?
