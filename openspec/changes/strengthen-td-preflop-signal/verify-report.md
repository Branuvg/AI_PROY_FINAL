# Verification Report

**Change**: strengthen-td-preflop-signal  
**Version**: N/A  
**Mode**: Standard (Strict TDD inactive)

## Executive Summary

Final verification passed. The implementation satisfies the OpenSpec requirements for leakage-safe TD preflop buckets, deterministic separated training RNG streams, fresh TD snapshot evaluation, fixed-seed baseline gate reporting, and Spanish documentation/notebook updates. The freshly trained TD snapshot clears the configured minimal gate (`ROI > -1.0` vs Random and Call), but TD should remain deferred from Ensemble reintegration because its fixed-report ROI against Call remains negative and weaker than Markov/Bayesian in the same run.

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 17 |
| Tasks complete | 17 |
| Tasks incomplete | 0 |
| Strict TDD | inactive |

## Build & Tests Execution

**Build**: ➖ Not applicable; no separate build command discovered for this Python project.

**Tests**: ✅ 54 passed / 0 failed / 0 skipped

```text
Command: uv run pytest
Result: 54 passed in 0.27s
Coverage: not requested / not reported
```

**Fresh TD snapshot training**: ✅ Passed

```text
Command: uv run python -m poker_ai.evaluation.train_td --hands 200 --seed 17 --output /tmp/opencode/td_verify_qtable.json
Result: Saved TD Q-table to /tmp/opencode/td_verify_qtable.json (8 state(s), hands=200, seed=17).
```

**Fixed-seed report experiment with fresh TD**: ✅ Passed

```text
Command: POKER_REPORT_HANDS=40 POKER_REPORT_SEEDS=101,202,303 POKER_REPORT_FRESH_TD=1 uv run python - <<'PY' ...
Result: report ran with 3 seeds × 40 hands and fresh TD enabled.
Gate call ROI:   -0.062241
Gate random ROI: -0.015504
Gate threshold:  ROI > -1.0
td_meets_gate:   True
```

**Notebook execution**: ✅ Passed

```text
Command: uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output /tmp/opencode/td_verify_exec.ipynb
Result: wrote /tmp/opencode/td_verify_exec.ipynb
```

## Fixed-Seed Report Results

| Agent | Opponent | Hands | Wins | Losses | Ties | ROI | Avg Profit | td_meets_gate |
|-------|----------|------:|-----:|-------:|-----:|----:|-----------:|---------------|
| Bayesian | Call | 120 | 60 | 55 | 5 | 0.041667 | 0.416667 | None |
| Ensemble | Call | 120 | 51 | 61 | 8 | -0.083333 | -0.833333 | None |
| Markov | Call | 120 | 60 | 52 | 8 | 0.066667 | 0.666667 | None |
| Minimax | Call | 120 | 58 | 59 | 3 | -0.008333 | -0.083333 | None |
| Random | Call | 120 | 42 | 77 | 1 | -0.044444 | -0.500000 | None |
| TDLearning (fresh) | Call | 120 | 23 | 94 | 3 | -0.327273 | -3.000000 | True |

## Spec Compliance Matrix

| Requirement | Scenario | Runtime Evidence | Result |
|-------------|----------|------------------|--------|
| State Key Preflop Bucket | Preflop state generation includes private hand-strength bucket and excludes community/opponent data | `uv run pytest` passed `tests/agents/test_preflop.py::test_preflop_bucket_boundaries`, `test_preflop_bucket_signature_exposes_no_leakage_inputs`, and `tests/agents/test_model_agents.py::test_td_preflop_state_key_includes_private_bucket_only` | ✅ COMPLIANT |
| Spanish Documentation and Reintegration Gate | Spanish report/notebook explains the preflop bucket and deferred Ensemble reintegration until ROI gate | `uv run pytest` passed `tests/test_notebook_contract.py::test_notebook_documents_td_preflop_gate`; static inspection confirms `docs/notebook_backend_report.md` includes the same Spanish explanation | ✅ COMPLIANT |
| Separated Deterministic RNG Streams | Training trajectory uses independent deterministic streams for deck, exploration, and opponent | `uv run pytest` passed `tests/evaluation/test_training.py`; static inspection confirms `train_td_agent()` creates `deck_rng`, `explore_rng`, and `opponent_rng` via `_td_training_streams()` | ✅ COMPLIANT |
| Fresh Snapshots for Verification | Evaluation uses newly trained TD snapshot and avoids stale repository artifact when fresh mode is enabled | `uv run pytest` passed `tests/evaluation/test_reporting.py::test_run_report_experiment_uses_fresh_td_by_default`; fixed report command used `POKER_REPORT_FRESH_TD=1` and returned `TDLearning (fresh)` | ✅ COMPLIANT |
| Baseline Comparison and Metric Gate | Fresh TD is compared against Random and Call on fixed seeds and reports gate result | Fixed report command computed gate ROIs on seeds `(101, 202, 303)` with 40 hands each and returned `td_meets_gate=True`; `uv run pytest` passed reporting gate tests | ✅ COMPLIANT |

**Compliance summary**: 5/5 scenarios compliant.

## Correctness (Static Evidence)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Leakage-safe preflop bucket | ✅ Implemented | `src/poker_ai/agents/preflop.py` accepts only `hole_cards`, validates exactly two private cards, and returns `premium`/`strong`/`playable`/`weak`. |
| TD state schema v2 | ✅ Implemented | `src/poker_ai/agents/td.py` uses 4-field `StateKey`, schema version 2, and migrates 3-field legacy keys to `bucket=None`. |
| RNG separation | ✅ Implemented | `src/poker_ai/evaluation/training.py` derives three `random.Random` streams from the master seed and passes them separately to deck, TD exploration, and opponent. |
| Fresh report snapshot | ✅ Implemented | `src/poker_ai/evaluation/reporting.py` defaults `POKER_REPORT_FRESH_TD` to enabled and labels fresh agents as `TDLearning (fresh)`. |
| Spanish reporting | ✅ Implemented | `render_spanish_conclusions()`, `docs/notebook_backend_report.md`, and notebook markdown state the bucket, RNG separation, metric gate, and deferred reintegration. |

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Four buckets: `premium`, `strong`, `playable`, `weak` | ✅ Yes | Implemented in pure helper. |
| Bucket uses only private hole cards | ✅ Yes | Function signature and tests prevent community/opponent inputs. |
| State key includes bucket preflop and `None` otherwise | ✅ Yes | Internal tuple is always normalized to 4 fields; serialization preserves 3-field bucketless form for compatibility. |
| Q-table schema v2 with v1 migration | ✅ Yes | Loader accepts version 1 and current version. |
| RNG separation from one master seed | ✅ Yes | Three derived streams are created. |
| Fresh TD verification default-on | ✅ Yes | Environment flag defaults to enabled. |
| Metric gate `ROI > -1.0` vs Random and Call | ✅ Yes | Gate returns true for verified run: Call -0.062241, Random -0.015504. |
| Ensemble reintegration out of scope | ✅ Yes | Default Ensemble remains `Minimax`, `Bayesian`, `Markov`; TD is not reintegrated. |

## Findings

**CRITICAL**: None.

**WARNING**: None.

**SUGGESTION**:
- Consider a follow-up that uses a stronger TD reintegration gate than `ROI > -1.0`, for example positive ROI with confidence intervals over more hands/opponents. The current gate proves TD is no longer catastrophically stale/degenerate, not that it is Ensemble-worthy.
- Consider strengthening `tests/evaluation/test_training.py` with a direct assertion over `_td_training_streams()` or controlled RNG draws, so the decoupling guarantee is tested more explicitly rather than mostly proven by implementation inspection plus reproducibility tests.

## TD Reintegration Recommendation

Defer TD reintegration into `Ensemble`.

Rationale: the fresh TD gate technically passes (`td_meets_gate=True`) because both gate ROIs are above `-1.0`, but the report experiment still shows `TDLearning (fresh)` at ROI `-0.327273` vs Call, substantially below Markov (`0.066667`), Bayesian (`0.041667`), Random (`-0.044444`), Minimax (`-0.008333`), and the current Ensemble (`-0.083333`) in the same fixed run. Reintegration now would dilute Ensemble quality and blur causality. Treat this change as TD signal hardening; make reintegration a later change only after TD clears a stronger, stable positive-performance gate.

## Risks

- TD performance is improved enough to pass the minimal freshness gate but remains negative in the fixed report run.
- The current metric sample is small: 3 seeds × 40 hands for the fixed verification report and 120 hands per gate opponent.
- The simulator remains simplified with terminal reward only, so TD learning quality may be sensitive to state sparsity and opponent panel choices.

## Verdict

PASS WITH WARNINGS.

The implementation satisfies the specs/tasks/design and all required runtime checks pass. Warnings are strategic rather than blocking: TD should stay out of Ensemble until stronger metrics justify reintegration.
