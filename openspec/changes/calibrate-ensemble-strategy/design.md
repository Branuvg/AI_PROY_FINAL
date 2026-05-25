# Design: Calibrate Ensemble Strategy

## Technical Approach

Replace the weak default `EnsembleAgent` composition (Random + Call) used by the report with a strong baseline (Minimax + Bayesian + Markov), derive its weights from a small reproducible grid validated against a diverse opponent panel under fixed seeds and a runtime budget, and expose composition/weights in `ReportRow` so both the Spanish report and notebook render accurate, calibrated conclusions. TD is excluded from the default to avoid dragging the ensemble down given its sparse Q-table (notebook reports 119 states learned). The hard-vote interface in `ensemble.py` is preserved; only defaults, construction helpers, and reporting plumbing change.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Default constituents | Minimax + Bayesian + Markov | Add TD; keep Random/Call | TD Q-table too sparse to add value; Random/Call inflate baseline noise — the proposal forbids them. |
| Calibration method | Small curated grid (≤9 weight triples) validated vs panel | Static curated only; full continuous optimizer | Grid is reproducible, bounded by runtime budget, and produces a documented best vector. Pure curated lacks evidence; continuous risks overfit. |
| Validation panel | `CallAgent` + `RandomAgent(seed)` + `MarkovAgent` | Only CallAgent | Diversifies opponents so weights don't overfit the passive Caller (proposal risk). |
| Seeds & budget | `CALIBRATION_SEEDS=(101,202,303)`, `CALIBRATION_HANDS=40`, soft cap ~30s | Reuse report seeds 42–46 | Disjoint from report seeds prevents leakage; small budget keeps `pytest` and notebook fast. |
| Weight provenance | Module-level `DEFAULT_ENSEMBLE_WEIGHTS` constant produced by calibration, committed | Compute live in tests/notebook | Determinism, transparency, and CI speed; calibration script regenerates it on demand. |
| Reporting surface | Extend `ReportRow` with `composition: tuple[str,...]` and `weights: tuple[float,...]` | Side-channel dict | Keeps `as_dict()` self-describing for notebook and Spanish report. |
| Conclusion text | Templated Spanish paragraph injected from `ReportRow` data | Hand-edited markdown | Avoids stale text; numbers and weights stay in sync with calibration output. |

## Data Flow

    calibrate_ensemble_weights(seeds, hands)
            │  (grid × panel × fixed RNG)
            ▼
    DEFAULT_ENSEMBLE_WEIGHTS  ──►  build_default_ensemble()
                                          │
                                          ▼
    run_report_experiment(config) ──► ReportRow{composition, weights, roi}
                                          │
                          ┌───────────────┴────────────────┐
                          ▼                                ▼
              render_spanish_conclusions()         notebook cell render
                          │                                │
                          └────────► Spanish report ◄──────┘

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/poker_ai/agents/ensemble.py` | Modify | Add `build_default_ensemble(seed)` and `DEFAULT_ENSEMBLE_WEIGHTS` constant; keep weighted-vote logic intact. |
| `src/poker_ai/evaluation/training.py` | Modify | Add `calibrate_ensemble_weights(seeds, hands, panel)` returning best weight triple; deterministic grid search with fixed RNG. |
| `src/poker_ai/evaluation/reporting.py` | Modify | Replace `EnsembleAgent({"random",..,"call",..})` with `build_default_ensemble(seed)`; add `composition`/`weights` to `ReportRow`; add `render_spanish_conclusions(rows)`. |
| `src/poker_ai/evaluation/__init__.py` | Modify | Export `calibrate_ensemble_weights`, `render_spanish_conclusions`, `DEFAULT_ENSEMBLE_WEIGHTS`. |
| `tests/agents/test_model_agents.py` | Modify | Add tests: default ensemble has Minimax/Bayesian/Markov, no Random/Call/TD; weights match `DEFAULT_ENSEMBLE_WEIGHTS`. |
| `tests/evaluation/test_reporting.py` | Modify | Assert Ensemble row exposes composition+weights; assert Spanish conclusions string mentions composition and ROI. |
| `tests/evaluation/test_training.py` | Create | Test `calibrate_ensemble_weights` is deterministic for fixed seeds and stays within runtime soft cap (assert ≤ 60s smoke). |
| `poker_ia_comparativa_final.ipynb` | Modify | Render `composition`/`weights`/`render_spanish_conclusions` from `ReportRow`; remove hand-written Random+Call narrative. |

## Interfaces / Contracts

```python
# src/poker_ai/agents/ensemble.py
DEFAULT_ENSEMBLE_WEIGHTS: dict[str, float]  # keys: "minimax","bayesian","markov"

def build_default_ensemble(seed: int | None = None) -> EnsembleAgent: ...

# src/poker_ai/evaluation/training.py
def calibrate_ensemble_weights(
    *,
    seeds: tuple[int, ...] = (101, 202, 303),
    hands_per_seed: int = 40,
    panel: tuple[str, ...] = ("call", "random", "markov"),
) -> dict[str, float]: ...

# src/poker_ai/evaluation/reporting.py
@dataclass(frozen=True, slots=True)
class ReportRow:
    ...  # existing fields
    composition: tuple[str, ...] = ()
    weights: tuple[float, ...] = ()

def render_spanish_conclusions(rows: list[ReportRow]) -> str: ...
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `build_default_ensemble` composition & weights; no Random/Call/TD | `pytest` direct introspection. |
| Unit | `calibrate_ensemble_weights` determinism + bounded keys | Run twice with same seeds, compare dicts. |
| Integration | `run_report_experiment` produces Ensemble row with composition/weights | Existing `test_reporting.py` extended. |
| Integration | `render_spanish_conclusions` includes composition, weights, ROI | Substring assertions in Spanish. |
| Guard | Regression guard for forbidden agents | Test fails if RandomAgent/CallAgent/TDAgent appear in default ensemble. |

## Migration / Rollout

No data migration. Weights constant ships in code; rollback restores prior `EnsembleAgent({"random","call"})` construction. Notebook re-execution required once to refresh narrative cells.

## Verification Commands

```bash
uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_reporting.py tests/evaluation/test_training.py -q
uv run python -c "from poker_ai.evaluation import calibrate_ensemble_weights; print(calibrate_ensemble_weights())"
POKER_REPORT_HANDS=20 POKER_REPORT_SEEDS=42,43 uv run python -c "from poker_ai.evaluation import config_from_env, run_report_experiment, render_spanish_conclusions; rows=run_report_experiment(config_from_env()); print(render_spanish_conclusions(rows))"
```

## Open Questions

- [ ] Should `DEFAULT_ENSEMBLE_WEIGHTS` be committed as floats or recomputed at import time? (Design assumes committed for determinism — confirm during tasks.)
