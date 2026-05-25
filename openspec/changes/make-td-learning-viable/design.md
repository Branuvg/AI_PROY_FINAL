# Design: Make TD Learning Viable

## Technical Approach

Convert `TDAgent` into a minimal, deterministic Q-learning baseline that (1) avoids `fold` on unseen/tied-Q states, (2) updates its Q-table from the **single terminal reward** the engine already exposes via `observe_reward(profit)`, and (3) can be trained once, saved to disk, and reloaded by `run_report_experiment()`. No engine, simulator, or ensemble changes.

Key constraint: `play_hand` does not emit per-step rewards — only a final `HandResult.profit`. So per-step Q-updates must be done by replaying the episode's `(state_key, action)` trace inside the agent itself when `observe_reward` fires (Monte Carlo–style TD(0) with terminal reward broadcast).

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|---|---|---|---|
| Reward signaling | Override `observe_reward` in `TDAgent` to drain a per-hand `(state_key, action)` trace and apply update with terminal reward | Modify engine to emit per-step rewards | Engine change is out of scope; episode-end broadcast is standard for TD on terminal-reward MDPs |
| Update rule | `Q ← Q + α · (R − Q)` per visited `(s,a)`, applied at episode end (constant α, no discount since reward is terminal) | Full TD(λ) or n-step backup | Simplest formula that satisfies spec ("reflects reward algebraically via α"); 1-line change |
| Unseen-state policy | If all candidate Q-values for legal actions are 0 (or missing), pick first available of `CHECK → CALL → BET → RAISE → FOLD` | Random over legal; pick `FOLD` (current bug) | Spec mandates non-losing fallback; deterministic tie-break also fixes "all-zero argmax picks FOLD" pathology when FOLD is first in ACTION_ORDER |
| Tie-break for non-zero ties | Same ordered preference (`CHECK,CALL,BET,RAISE,FOLD`) over actions sharing max Q | Random tie-break | Determinism required for reproducible reports |
| Persistence format | JSON file with `{state_key_str: {action_value_str: q_float}}` | Pickle | JSON is human-inspectable, diff-friendly, safe across Python versions; Q-table is tiny |
| Artifact path | `artifacts/td_qtable.json` (configurable via `POKER_TD_QTABLE_PATH` env var) | Hard-coded under `src/` | Keeps generated data out of source tree; env var lets CI/notebook override |
| State key | Keep current `(phase, min(to_call,100), len(action_history))` | Add hole-card buckets | Spec calls for "conservative coarse abstraction"; engine doesn't reliably expose street progression for richer features in scope |
| Training trigger | New CLI entry `python -m poker_ai.evaluation.train_td` + `train_td_agent(..., save_path=...)` helper | Auto-train inside report | Keeps report fast/deterministic; explicit train step matches spec's train-before-evaluate flow |
| Report integration | `run_report_experiment` loads snapshot if exists, else instantiates blank `TDAgent` and logs warning (renames agent display to `TDLearning (untrained)`) | Hard-fail when missing | Spec allows "untrained fallback" but must mark clearly |

## Data Flow

    train_td_agent(n_hands=N)
        │
        ├─ play_hand(td, opponent)   ──→ td.choose_action records (s,a) into trace
        │                                 (called many times per hand)
        ├─ play_hand returns HandResult
        └─ td.observe_reward(profit) ──→ apply α·(R−Q) to each (s,a) in trace
                                          then clear trace

    save_qtable(td, path) ──→ artifacts/td_qtable.json

    run_report_experiment()
        ├─ load_qtable(path) if exists  ──→ TDAgent(q_values=loaded)
        └─ else                          ──→ TDAgent() + warning, name suffix "(untrained)"

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/poker_ai/agents/td.py` | Modify | Add episode trace, override `choose_action` to record + use ordered tie-break, override `observe_reward` to apply α-update, add `save`/`load` classmethods, accept optional `alpha`, `q_values` init |
| `src/poker_ai/evaluation/training.py` | Modify | Extend `train_td_agent` with `save_path` param; add `DEFAULT_TD_QTABLE_PATH`, `DEFAULT_TD_ALPHA=0.1`, `DEFAULT_TD_TRAIN_HANDS=200` constants |
| `src/poker_ai/evaluation/train_td.py` | Create | Tiny CLI: `python -m poker_ai.evaluation.train_td` — trains and saves with fixed seed for determinism |
| `src/poker_ai/evaluation/reporting.py` | Modify | `_build_report_agents` loads Q-table when present; sets agent name suffix when untrained; expose loaded path in Spanish conclusions |
| `tests/agents/test_model_agents.py` | Modify | Add: (a) unseen-state returns non-FOLD, (b) `observe_reward` mutates Q-values toward reward sign |
| `tests/evaluation/test_training.py` | Modify | Add: (a) `train_td_agent(save_path=tmp)` writes file, (b) Q-table round-trip equals original |
| `tests/evaluation/test_reporting.py` | Modify | Add: report uses snapshot when present; falls back with "(untrained)" suffix and warning when absent |
| `README.md` / notebook Spanish text | Modify | Add short section: TD params (α, episodes, seed), limitations in current simulator, how to retrain |
| `artifacts/.gitkeep` | Create | Reserve artifacts dir; `.gitignore` excludes `*.json` inside |

## Interfaces / Contracts

```python
class TDAgent(BaseAgent):
    def __init__(
        self,
        epsilon: float = 0.0,
        alpha: float = 0.1,
        rng: random.Random | None = None,
        q_values: dict[tuple, dict[Action, float]] | None = None,
    ): ...

    def choose_action(self, state: GameState) -> Action: ...  # records trace, ordered tie-break
    def observe_reward(self, reward: float, state: GameState | None = None) -> None: ...  # applies α-update + clears trace
    def save(self, path: str | os.PathLike) -> None: ...
    @classmethod
    def load(cls, path: str | os.PathLike, **kwargs) -> "TDAgent": ...
```

```python
# training.py
DEFAULT_TD_QTABLE_PATH = "artifacts/td_qtable.json"
DEFAULT_TD_ALPHA = 0.1
DEFAULT_TD_TRAIN_HANDS = 200
DEFAULT_TD_TRAIN_SEED = 17

def train_td_agent(
    agent: TDAgent | None = None,
    opponent=None,
    *,
    n_hands: int = DEFAULT_TD_TRAIN_HANDS,
    rng: random.Random | None = None,
    starting_stack: int = 1_000,
    save_path: str | os.PathLike | None = None,  # NEW
) -> TDAgent: ...
```

JSON schema (`td_qtable.json`):

```json
{
  "version": 1,
  "alpha": 0.1,
  "episodes": 200,
  "seed": 17,
  "q_values": {
    "preflop|10|0": {"check": 0.0, "call": 1.5, "fold": -0.2}
  }
}
```

State key serialized as `"{phase}|{to_call}|{history_len}"`.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|--------------|----------|
| Unit (agents) | Unseen state returns non-FOLD; ordered tie-break picks CHECK before CALL before FOLD; α-update moves Q toward reward | Direct `choose_action`/`observe_reward` calls with constructed `GameState` |
| Unit (persistence) | Save→load round-trip equals original Q-table; missing file raises `FileNotFoundError`; load with `**kwargs` preserves α/epsilon | Use `tmp_path` fixture |
| Integration (training) | `train_td_agent(n_hands=10, save_path=tmp)` writes JSON and Q-table is non-empty | Fixed seed, RandomAgent opponent |
| Integration (reporting) | Report with snapshot present uses loaded Q-values; report without snapshot logs warning and renames agent | Monkeypatch path env var; assert on warning + row.agent_name suffix |

Verification commands:

```bash
uv run pytest tests/agents/test_model_agents.py tests/evaluation/test_training.py tests/evaluation/test_reporting.py -q
uv run python -m poker_ai.evaluation.train_td   # produces artifacts/td_qtable.json
uv run python -m poker_ai.evaluation.cli report  # report consumes snapshot
```

Training runtime budget: ≤ 5 s for 200 hands on dev laptop. Test suite addition: ≤ 1 s.

## Migration / Rollout

No migration. First report run after merge without a trained artifact will log a warning and label TD as `TDLearning (untrained)`. Running `python -m poker_ai.evaluation.train_td` once produces the snapshot and subsequent reports use it. Rollback = delete `artifacts/td_qtable.json` and revert files listed above.

## Open Questions

- None blocking. Future work (out of scope): richer state abstraction once simulator exposes per-street visibility; reintroducing TD to the ensemble after measured ROI > Call baseline.
