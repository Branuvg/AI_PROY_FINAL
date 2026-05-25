# Design: Strengthen TD Preflop Signal

## Technical Approach

Extend the TD state key with a leakage-safe preflop hand-strength bucket derived strictly from the acting player's `hole_cards`. Decouple training RNGs into three independent streams (deck, exploration, opponent) seeded deterministically. Update reporting verification to train a fresh in-memory snapshot per run before evaluating, so reported ROI reflects current learning, not the stale `artifacts/td_qtable.json`. Update the Spanish notebook/report with the new abstraction and the ROI metric gate for future Ensemble reintegration. Specs covered: `td-agent-learning` (bucket, docs gate) and `model-training-pipeline` (RNG separation, fresh snapshot, baseline gate).

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| Bucket granularity | 4 categories: `premium`, `strong`, `playable`, `weak` | 3 (sparser), Chen formula numeric | 4 is coarse enough to avoid sparsity at 200 training hands, fine enough to separate AA-KK from 72o. |
| Bucket function placement | New helper `preflop_bucket(hole)` in `poker_ai/agents/preflop.py` | Inline in `td.py`; method on `GameState` | Pure function, reusable for tests; keeps `td.py` focused; avoids leaking engine concerns. |
| Bucket inputs | Only `hole_cards[player_id]` ranks + suited flag | Use `community_cards` or `action_history` | Spec mandates no leakage; ranks/suited is sufficient for preflop. |
| State key extension | Tuple `(phase, to_call_bucket, history_len, hand_bucket_or_none)` — `None` postflop | Always include bucket; multiple keys per phase | Backward compatibility: postflop key shape preserved; only preflop gets the new dimension. |
| Q-table persistence | Schema v2; loader migrates v1 by treating legacy keys as postflop (`hand_bucket=None`) | Break v1; force retrain | Existing `artifacts/td_qtable.json` keeps loading; learned values not lost. |
| RNG separation | Three `random.Random` instances seeded from one master seed via `Random(master).randint` | `numpy.random.Generator`; SystemRandom | Stays in stdlib; deterministic; minimal diff. |
| Fresh snapshot verification | `_load_report_td_agent` trains an ephemeral TD with `DEFAULT_TD_TRAIN_HANDS` then evaluates, ignoring on-disk artifact when `POKER_REPORT_FRESH_TD=1` (default on) | Always read disk; always retrain | Env flag preserves opt-out; default-on guarantees freshness in `uv run pytest` and notebook execution. |
| Metric gate | `ROI > -1.0` vs Random AND `ROI > -1.0` vs Call on seeds `(101, 202, 303)` over 40 hands each, reported as `td_meets_gate: bool` | Hard-coded ROI > 0; manual review | Matches proposal Success Criteria; deterministic; surfaces gate result for Ensemble follow-up. |

## Data Flow

    play_hand(rng_deck) ──→ deal_cards ──→ GameState.hole_cards
                                                │
                                                ▼
                                  preflop_bucket(hole) ──→ hand_bucket
                                                │
    TDAgent.choose_action(state, rng_explore) ──┴──→ state_key = (phase, to_call_b, hist_len, hand_bucket?)
                                                │
                                                ▼
                                          Q[state_key][action]
                                                │
                                                ▼
                                  observe_reward(profit) ──→ alpha update

Training loop:

    master_seed ──┬──→ Random(s1) → deck shuffles
                  ├──→ Random(s2) → TDAgent.rng (exploration)
                  └──→ Random(s3) → RandomAgent.rng (opponent)

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/poker_ai/agents/preflop.py` | Create | Pure `preflop_bucket(hole: list[str]) -> str` over 4 categories. |
| `src/poker_ai/agents/td.py` | Modify | Extend `_state_key` with `hand_bucket` when `phase == preflop`; bump `QTABLE_SCHEMA_VERSION = 2`; serializer/deserializer accepts 3- or 4-field keys; loader migrates v1 by inserting `None` bucket. |
| `src/poker_ai/evaluation/training.py` | Modify | `train_td_agent` accepts `master_seed` and constructs three RNGs; `play_hand` receives `rng_deck`; TDAgent gets `rng_explore`; opponent gets `rng_opp`. |
| `src/poker_ai/evaluation/reporting.py` | Modify | `_load_report_td_agent` honors `POKER_REPORT_FRESH_TD` (default `1`) and calls `train_td_agent` per seed; add `td_meets_gate` computation + Spanish line. |
| `src/poker_ai/evaluation/metrics.py` | (no change expected) | — |
| `tests/agents/test_preflop.py` | Create | Bucket boundary tests (AA→premium, 72o→weak, leakage check: identical hole → identical bucket regardless of community). |
| `tests/agents/test_model_agents.py` | Modify | Assert preflop state key includes bucket; postflop key shape unchanged; v1 snapshot loads without error. |
| `tests/evaluation/test_training.py` | Modify | Assert three independent RNGs produce reproducible runs and that swapping one stream's seed does not perturb the others. |
| `tests/evaluation/test_reporting.py` | Modify | Assert fresh-snapshot path retrains TD and emits `td_meets_gate` in Spanish conclusions. |
| `poker_ia_comparativa_final.ipynb` | Modify | Add Spanish markdown cell documenting (a) preflop bucket addition, (b) RNG separation, (c) ROI metric gate, (d) deferred Ensemble reintegration. |
| `docs/notebook_backend_report.md` | Modify | Append Spanish section mirroring notebook explanation. |

## Interfaces / Contracts

```python
# src/poker_ai/agents/preflop.py
PreflopBucket = Literal["premium", "strong", "playable", "weak"]

def preflop_bucket(hole_cards: list[str]) -> PreflopBucket:
    """Coarse preflop strength from two hole cards. No community/opponent input."""
```

```python
# src/poker_ai/agents/td.py — state key
StateKey = tuple[str, int, int] | tuple[str, int, int, str | None]
# preflop  → ("preflop", to_call_b, hist_len, "premium")
# postflop → ("flop",    to_call_b, hist_len, None)  # serialized as 3-field for back-compat
```

```python
# src/poker_ai/evaluation/training.py
def train_td_agent(
    agent: TDAgent | None = None,
    opponent=None,
    *,
    n_hands: int = DEFAULT_TD_TRAIN_HANDS,
    master_seed: int | None = DEFAULT_TD_TRAIN_SEED,
    starting_stack: int = 1_000,
    save_path: str | Path | None = None,
) -> TDAgent: ...
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `preflop_bucket` correctness + leakage (no kwargs accept community) | `tests/agents/test_preflop.py` with pytest parametrize for boundary hands. |
| Unit | TD state key shape (preflop vs postflop) | Extend `test_model_agents.py`. |
| Unit | v1 → v2 Q-table migration | Load fixture JSON, assert keys are bucketless and agent operates. |
| Integration | RNG separation determinism | `test_training.py`: same master seed → identical trajectory; perturbing one sub-seed only changes its stream. |
| Integration | Fresh snapshot verification & gate | `test_reporting.py`: with `POKER_REPORT_FRESH_TD=1`, ROI row reflects retrained TD; `td_meets_gate` present in Spanish output. |
| Notebook contract | New Spanish cells render | Extend `tests/test_notebook_contract.py` with substring assertions on the new cells. |

Verification commands:

```bash
uv run pytest tests/agents/test_preflop.py tests/agents/test_model_agents.py
uv run pytest tests/evaluation/test_training.py tests/evaluation/test_reporting.py
uv run pytest                            # full suite
uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output _exec.ipynb
```

## Migration / Rollout

Single-step rollout. Q-table schema bumps v1→v2 with backward-compatible loader (v1 keys treated as bucketless). No data migration script needed; legacy `artifacts/td_qtable.json` continues to load. With `POKER_REPORT_FRESH_TD=1` (default) every report run regenerates the snapshot; set `POKER_REPORT_FRESH_TD=0` to fall back to on-disk artifact for ad-hoc comparisons.

## Open Questions

- [ ] Should `to_call` discretization also be coarsened (e.g., buckets `{0, ≤BB, >BB}`) to combat sparsity further? Default: keep current `min(to_call, 100)` unchanged in this change; revisit in follow-up if sparsity persists.
