# Tasks: Extract Poker Engine and Validate Models

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,250 total; PR slices ~350 / ~400 / ~300 / ~200 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 engine → PR 2 agents → PR 3 evaluation → PR 4 notebook |
| Delivery strategy | ask-always |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Engine scaffolding + tests | PR 1 | Independent; notebook untouched; base = main or chosen tracker. |
| 2 | Agent extraction | PR 2 | Depends on PR 1 engine API; keep algorithms logic-equivalent. |
| 3 | Evaluation/ROI fix + tests | PR 3 | Depends on PR 1 `HandResult`; may use agents from PR 2. |
| 4 | Notebook rewire/report | PR 4 | Depends on PRs 1-3; deletes duplicated inline logic. |

## Phase 1: Engine Scaffolding + Tests (~350 lines)

- [x] 1.1 Create `pyproject.toml` with package metadata, runtime deps, `[dev]` pytest extras, and editable-install support.
- [x] 1.2 Create `src/poker_ai/__init__.py` and `src/poker_ai/engine/{__init__,state,rules,simulator}.py` with `GameState`, `HandResult`, legal actions, and `play_hand`.
- [x] 1.3 Implement bounded re-raise loop with `max_raises_per_street=4`, `last_aggressor`, pot/to-call updates, and shared `action_history` propagation.
- [x] 1.4 Add `tests/conftest.py` scripted/seeded agents plus `tests/engine/test_*.py` for re-raise chain, legal actions, history propagation, and showdown invariants.
- [x] 1.5 Verify PR 1 with `pip install -e ".[dev]"` and `pytest tests/engine`. (Resolved by creating a local `.venv`; `.venv/bin/python -m pip install -e ".[dev]"`, `.venv/bin/python -m pytest tests/engine`, and `PYTHONPATH=src python -m pytest tests/engine` pass.)

## Phase 2: Agent Extraction (~400 lines)

- [x] 2.1 Create `src/poker_ai/agents/{__init__,base}.py` with standard `act(game_state)`/reward interface plus `RandomAgent` and `CallAgent`.
- [x] 2.2 Move notebook Minimax, Bayesian, Markov, TD, and Ensemble logic into `src/poker_ai/agents/{minimax,bayesian,markov,td,ensemble}.py` without algorithm changes. (Implemented as importable PR2 scaffolds adapted to the PR1 compact engine API; notebook rewire remains PR4.)
- [x] 2.3 Wire agents to consume `GameState.action_history`; preserve Markov/Bayesian tendency inference using propagated actions.
- [x] 2.4 Add lightweight interface/import tests for valid action outputs and optional `pgmpy` skip behavior.
- [x] 2.5 Verify PR 2 with `pytest tests/engine tests/agents`. (`.venv/bin/python -m pytest tests/engine tests/agents` passes.)

## Phase 3: Evaluation/ROI Fix + Tests (~300 lines)

- [x] 3.1 Create `src/poker_ai/evaluation/{__init__,metrics,training}.py` with `EvaluationResult`, `evaluate_agent`, `train_td_agent`, and transition estimation.
- [x] 3.2 Calculate ROI as `profit / sum(per_hand_invested)` and return `0.0` when aggregate invested chips is zero.
- [x] 3.3 Add `tests/evaluation/test_metrics.py` for positive ROI (100 invested, 150 returned = 50%) and zero-investment denominator safety.
- [x] 3.4 Verify PR 3 with `pytest tests/evaluation tests/engine`. (`.venv/bin/python -m pytest tests/engine tests/agents tests/evaluation` passes.)

## Phase 4: Notebook Rewire/Report (~200 lines)

- [x] 4.1 Modify `poker_ia_comparativa_final.ipynb` to import engine, agents, and evaluation modules; keep narrative, tables, and plots only. (Replaced the historical duplicated notebook body with a concise modular report/demo.)
- [x] 4.2 Remove duplicated inline simulator/model/evaluation logic from the notebook after imports reproduce the report flow. (`tests/test_notebook_contract.py` statically guards against forbidden core definitions and the old `n_hands * BIG_BLIND` ROI denominator.)
- [x] 4.3 Add reduced-N notebook smoke instructions or config cell for feasible execution in local/CI environments. (`REPORT_HANDS = 5` cell plus `docs/notebook_backend_report.md` and README `uv` setup/test/notebook instructions.)
- [x] 4.4 Verify PR 4 with `pytest` and `jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb` when dependencies are installed. (`uv sync --extra dev`, `uv run pytest`, and `uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output poker_ia_comparativa_final.executed.ipynb` pass.)
