# Design: Extract Poker Engine and Validate Models

## Technical Approach

Extract the monolithic notebook into three Python packages under `src/poker_ai/`: `engine`, `agents`, `evaluation`. Each package is independently testable and consumed by the notebook as a thin presentation layer. We preserve existing agent algorithms (logic-equivalent) but fix three validated defects: betting loop (2-action cap, no history propagation), ROI denominator, and Markov phase-transition bias. Existing notebook logic is the source of truth for behavior to preserve; specs are the source of truth for behavior to fix.

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|---|---|---|---|
| Layout | `src/poker_ai/{engine,agents,evaluation}` + `tests/` | Flat `src/` modules | Clear capability boundary matches spec capabilities; supports `pip install -e .` |
| Build | `pyproject.toml` + editable install | `setup.py`, requirements-only | Standard modern Python, lets tests import without path hacks |
| Engine API | `play_hand(agent0, agent1, rng, config)` returns `HandResult(winner, profit, invested, history)` | Tuple return | Named result enables ROI fix and history assertions in tests |
| Betting loop | Streets iterate `while not street_closed`, tracking `last_aggressor` | Keep 2-action cap | Spec requires re-raise chains; loop closes when all non-folded players have matched current_bet after the last raise |
| Action history | `GameState.action_history` is a single shared list mutated by the engine and passed by reference into `agent.choose_action(state)` | Pass via side channel | Spec `ai-agents` requires agents receive propagated history |
| ROI | `roi = profit / sum(per_hand_invested)` with `0.0` when denominator is `0` | Keep `n_hands * BIG_BLIND` divisor | Spec scenarios require accuracy on actual chips invested and divide-by-zero safety |
| Notebook role | Imports modules, runs evaluation, renders tables/plots only | Keep logic inline | Spec `evaluation-metrics` forbids duplicated core logic in notebook |
| Test runner | `pytest` with `tests/` package, `conftest.py` for shared fixtures (seeded RNG, scripted agents) | `unittest` | Pytest fixtures + parametrize keep simulator tests compact |
| Simulator fidelity | Cap re-raises per street with `max_raises_per_street=4` (configurable, default 4) | Unlimited re-raises | Bounded scope; matches real heads-up no-limit convention; prevents infinite loops |
| Dependency strategy | `pyproject.toml` declares `treys`, `pgmpy`, `numpy`, `pandas`; CI/local install via `pip install -e ".[dev]"`; tests skip with clear marker if `pgmpy` missing | Vendor or stub | Deps not currently installed; document install once, mark integration tests requiring `pgmpy` |

## Data Flow

    notebook ──imports──> agents ──uses──> engine.GameState
        │                   │                    ▲
        │                   └─ reads ─ action_history (propagated by engine)
        ▼
    evaluation.evaluate_agent ──drives──> engine.play_hand
        │                                       │
        └────── aggregates HandResult ──────────┘
                       │
                       ▼
                  metrics (ROI, WinRate, AvgProfit)

## File Changes

| File | Action | Description |
|---|---|---|
| `pyproject.toml` | Create | Package metadata, deps, `[dev]` extra (pytest, pytest-cov) |
| `src/poker_ai/__init__.py` | Create | Package marker |
| `src/poker_ai/engine/state.py` | Create | `Phase`, `Action`, `GameState`, `HandResult`, constants |
| `src/poker_ai/engine/rules.py` | Create | `get_legal_actions`, `action_to_bet_size`, hand eval helpers |
| `src/poker_ai/engine/simulator.py` | Create | `deal_hand`, `play_hand` with re-raise loop + history propagation |
| `src/poker_ai/agents/base.py` | Create | `BaseAgent`, `RandomAgent`, `CallAgent` |
| `src/poker_ai/agents/{minimax,bayesian,markov,td,ensemble}.py` | Create | One agent per file (lift from notebook, no logic changes beyond receiving history) |
| `src/poker_ai/evaluation/metrics.py` | Create | `evaluate_agent` with corrected ROI; returns `EvaluationResult` |
| `src/poker_ai/evaluation/training.py` | Create | `train_td_agent`, transition matrix estimator |
| `tests/conftest.py` | Create | Seeded RNG, scripted agent fixtures |
| `tests/engine/test_*.py` | Create | Re-raise chain, history propagation, legal actions, showdown |
| `tests/evaluation/test_metrics.py` | Create | ROI positive/zero-investment scenarios from spec |
| `poker_ia_comparativa_final.ipynb` | Modify | Replace inline logic with imports; keep narrative + plots |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Legal actions, ROI formula, action history mutation, state transitions | Pytest with hand-built `GameState` |
| Integration | `play_hand` with scripted agents (FoldBot, RaiseBot) asserting end-state invariants | Seeded RNG, golden hand sequences |
| Notebook smoke | `jupyter nbconvert --execute` on a reduced-N config | Optional CI job; skipped if deps missing |

## Migration / Rollout

Phased per **chained-pr** (>400 line forecast):
1. **PR1 — Scaffolding + engine** (~350 lines): `pyproject.toml`, `engine/`, engine tests. Notebook untouched.
2. **PR2 — Agents extraction** (~400 lines): all five agents moved verbatim, importing from `engine`. Notebook still self-contained.
3. **PR3 — Evaluation + ROI fix** (~300 lines): `evaluation/`, ROI tests proving spec scenarios.
4. **PR4 — Notebook rewire** (~200 lines): notebook imports modules; old inline code deleted.

Each PR is independently green. Rollback = revert PR; notebook keeps working until PR4.

## Open Questions

- [ ] Confirm `max_raises_per_street=4` matches academic expectations (vs. unlimited).
- [ ] Should TD Q-table be persisted to disk (`.pkl`) so PR4 notebook doesn't retrain every run? Recommend yes, in `artifacts/`.
