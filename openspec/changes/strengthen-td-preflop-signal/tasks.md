# Tasks: Strengthen TD Preflop Signal

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 380-520 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 bucket+TD schema → PR 2 RNG+fresh reporting → PR 3 Spanish docs/notebook+full verification |
| Delivery strategy | auto; chained_pr_strategy=ask-always |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Preflop bucket and TD schema v2 compatibility | PR 1 | Base main/tracker; includes agent tests. |
| 2 | Training RNG separation and fresh metric gate | PR 2 | Depends on PR 1 state behavior; includes evaluation tests. |
| 3 | Spanish report/notebook updates and end-to-end verification | PR 3 | Depends on PR 2 reporting fields. |

## Phase 1: Preflop Bucket Foundation

- [x] 1.1 Create `src/poker_ai/agents/preflop.py` with `PreflopBucket` and pure `preflop_bucket(hole_cards)` using only two private cards.
- [x] 1.2 Create `tests/agents/test_preflop.py` for AA→premium, strong/playable boundaries, 72o→weak, invalid input, and no community/opponent parameters.
- [x] 1.3 Export/import helper only where needed; avoid engine or reporting dependencies.

## Phase 2: TD State Key and Migration

- [x] 2.1 Modify `src/poker_ai/agents/td.py` `_state_key` so preflop keys include bucket and postflop keys preserve backward-compatible shape/`None` semantics.
- [x] 2.2 Bump Q-table schema to v2; update serializer/deserializer to read 3-field legacy keys and 4-field v2 keys.
- [x] 2.3 Extend `tests/agents/test_model_agents.py` for preflop bucket key, postflop unchanged behavior, and v1 artifact migration.

## Phase 3: Training and Reporting Pipeline

- [x] 3.1 Modify `src/poker_ai/evaluation/training.py` so `train_td_agent(master_seed=...)` derives independent deck, exploration, and opponent `random.Random` streams.
- [x] 3.2 Extend `tests/evaluation/test_training.py` for same-master reproducibility and stream independence without coupled RNG draws.
- [x] 3.3 Modify `src/poker_ai/evaluation/reporting.py` so `POKER_REPORT_FRESH_TD=1` retrains an ephemeral TD snapshot and computes `td_meets_gate` vs Random/Call seeds `(101,202,303)`.
- [x] 3.4 Extend `tests/evaluation/test_reporting.py` for fresh-snapshot usage, stale artifact avoidance, and Spanish `td_meets_gate` reporting.

## Phase 4: Spanish Docs, Notebook, Verification

- [x] 4.1 Update `docs/notebook_backend_report.md` in Spanish with preflop bucket, RNG separation, ROI gate, and deferred Ensemble reintegration.
- [x] 4.2 Update `poker_ia_comparativa_final.ipynb` Spanish markdown cells with the same explanation; add/adjust `tests/test_notebook_contract.py` substrings if needed.
- [x] 4.3 Verify with `uv run pytest tests/agents/test_preflop.py tests/agents/test_model_agents.py`.
- [x] 4.4 Verify with `uv run pytest tests/evaluation/test_training.py tests/evaluation/test_reporting.py`.
- [x] 4.5 Verify full suite and notebook: `uv run pytest` and `uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output _exec.ipynb`.
