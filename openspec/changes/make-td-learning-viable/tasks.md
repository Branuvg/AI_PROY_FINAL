# Tasks: Make TD Learning Viable

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500-750 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 TD learning+persistence → PR 2 training/reporting → PR 3 docs/notebook |
| Delivery strategy | ask-on-risk (preflight chained_pr_strategy: ask-always) |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Fix `TDAgent` policy/update/persistence with focused tests | PR 1 | Base main; enables all later loading/training |
| 2 | Add train CLI and reporting snapshot fallback | PR 2 | Depends on PR 1; includes integration tests |
| 3 | Update Spanish docs/notebook and final verification | PR 3 | Depends on PR 2; docs with command proof |

## Phase 1: TD Core and Persistence

- [x] 1.1 Modify `src/poker_ai/agents/td.py`: add `alpha`, `q_values`, per-hand trace, ordered legal-action fallback `CHECK→CALL→BET→RAISE→FOLD`.
- [x] 1.2 Implement `TDAgent.observe_reward()` terminal update `Q ← Q + α(R-Q)` for traced `(state, action)` pairs and clear trace.
- [x] 1.3 Add JSON save/load in `src/poker_ai/agents/td.py` using schema version, alpha metadata, and `phase|to_call|history_len` state keys.
- [x] 1.4 Add/adjust `.gitignore` and `artifacts/.gitkeep` so generated `artifacts/*.json` is ignored.

## Phase 2: Training and Reporting Integration

- [x] 2.1 Modify `src/poker_ai/evaluation/training.py`: add TD constants, `save_path`, deterministic seed defaults, and snapshot save after training.
- [x] 2.2 Create `src/poker_ai/evaluation/train_td.py` module CLI for `uv run python -m poker_ai.evaluation.train_td`.
- [x] 2.3 Modify `src/poker_ai/evaluation/reporting.py`: load `POKER_TD_QTABLE_PATH`/default snapshot; warn and label `TDLearning (untrained)` when absent.
- [x] 2.4 Update Spanish report conclusions to include snapshot path, α, episodes, seed, and simulator limitations.

## Phase 3: Tests

- [x] 3.1 Update `tests/agents/test_model_agents.py` for unseen non-FOLD, deterministic tie-break, and reward update direction.
- [x] 3.2 Update `tests/evaluation/test_training.py` for `train_td_agent(save_path=tmp)`, non-empty Q-table, and save/load round-trip.
- [x] 3.3 Update `tests/evaluation/test_reporting.py` for loaded snapshot behavior and untrained warning/name suffix fallback.

## Phase 4: Docs and Verification

- [x] 4.1 Update `README.md` and `poker_ia_comparativa_final.ipynb` Spanish explanation with retrain command and TD caveats.
- [x] 4.2 Run `uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_training.py tests/evaluation/test_reporting.py -q`.
- [x] 4.3 Run `uv run python -m poker_ai.evaluation.train_td` then `uv run python -m poker_ai.evaluation.cli report`.

## Dependencies / Expected Files

Dependencies: Phase 1 before Phases 2-3; reporting depends on persistence; docs follow verified commands.
Expected files: `src/poker_ai/agents/td.py`, `src/poker_ai/evaluation/training.py`, `src/poker_ai/evaluation/train_td.py`, `src/poker_ai/evaluation/reporting.py`, `tests/agents/test_model_agents.py`, `tests/evaluation/test_training.py`, `tests/evaluation/test_reporting.py`, `README.md`, `poker_ia_comparativa_final.ipynb`, `.gitignore`, `artifacts/.gitkeep`.
