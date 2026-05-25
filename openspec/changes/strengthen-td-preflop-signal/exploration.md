## Exploration: strengthen-td-preflop-signal

### Current State
`TDAgent` now updates and persists a Q-table, but the learning signal is still too weak to produce a useful standalone policy. The biggest constraint is NOT the update formula anymore — it is the information the agent sees. `src/poker_ai/agents/td.py` still keys Q-values only by `(phase, to_call, history_len)`, and in the current simulator that produces only three reachable states: `('preflop', 5, 0)`, `('preflop', 10, 2)`, and `('preflop', 10, 4)`. That means the agent cannot distinguish premium starting hands from trash hands, so it learns one average preflop behavior for everything.

The training path also has quality issues. `train_td_agent()` currently shares one RNG across deck dealing, TD exploration, and the default `RandomAgent` opponent, which couples trajectories in a way that is reproducible but poor for training quality. The persisted snapshot loaded by reporting still prefers `fold` from the opening small-blind state (`artifacts/td_qtable.json`), which explains the observed ROI `-1.0` against `Call` in smoke/report runs.

Exploration probes confirm the direction: when TD is trained with independent RNG streams and a leakage-safe private hand-strength bucket, the reachable state space expands materially and TD becomes much less degenerate. Reward-only tweaks helped less than better state signal because the current state abstraction cannot tell when continuing is actually justified.

### Affected Areas
- `src/poker_ai/agents/td.py` — current state key is too coarse; this is the main bottleneck for learning quality.
- `src/poker_ai/evaluation/training.py` — training currently shares RNG streams and uses a single weak default opponent path.
- `src/poker_ai/evaluation/train_td.py` — CLI should stay aligned with the improved deterministic training contract.
- `src/poker_ai/evaluation/reporting.py` — reporting should verify a fresh trained snapshot path, not silently depend on stale artifacts.
- `src/poker_ai/engine/state.py` — exposes private hole cards needed for a leakage-safe preflop bucket.
- `src/poker_ai/engine/simulator.py` — confirms the current environment is effectively preflop-only for TD state design.
- `tests/agents/test_model_agents.py` — needs coverage for the richer non-leaking state abstraction and policy guardrails.
- `tests/evaluation/test_training.py` — needs coverage for independent seeds/RNG streams, non-stale persistence, and metric improvement checks.
- `tests/evaluation/test_reporting.py` — needs coverage for auto-verification using a trained temporary snapshot before report assertions.

### Approaches
1. **Reward shaping first** — Add fold penalties / continuation rewards / normalized terminal profit while keeping the current state key.
   - Pros: Small code delta; directly addresses fold-heavy behavior.
   - Cons: Weakest leverage. With only three reachable states, shaping still teaches one average action for all starting hands.
   - Effort: Low

2. **Leakage-safe preflop state signal + training hygiene** — Add a coarse private-hand-strength bucket to TD state, separate RNG streams for deck/opponent/exploration, and auto-verified fresh-snapshot reporting.
   - Pros: Best quality-per-line ratio; fixes the real learning bottleneck without a simulator rewrite; stays valid academically because it uses only the acting player’s hole cards.
   - Cons: Slightly broader than agent-only work because training/tests/report verification must move together.
   - Effort: Medium

3. **Broader curriculum and ensemble-ready calibration** — Add opponent mixtures, epsilon schedule tuning, metric gates, and TD ensemble re-entry in the same change.
   - Pros: Closer to the end goal.
   - Cons: Scope creep. Harder to attribute which intervention improved TD, and likely exceeds the safe review budget.
   - Effort: High

### Recommendation
Recommend **Approach 2** under the change name **`strengthen-td-preflop-signal`**.

Minimum effective improvement:
1. Expand `TDAgent` state from `(phase, to_call, history_len)` to a leakage-safe preflop abstraction that includes a **coarse private hole-card strength bucket** plus the existing pressure/action context.
2. Split RNG responsibilities in training so deck dealing, TD exploration, and stochastic opponents do not all consume the same random stream.
3. Keep reward shaping conservative in this change — at most a small explicit fold/continuation bias if metrics still collapse after the state fix. Do NOT lead with heavy shaping.
4. Add automatic verification that trains a fresh TD snapshot to a temporary path and asserts improved standalone metrics against agreed baselines, so stale `artifacts/td_qtable.json` cannot mislead reporting again.
5. Keep Ensemble reintegration **out of this change**. Treat it as a follow-up only if TD clears the metric gate.

Suggested metric gate for the follow-up:
- TD trained snapshot MUST beat `Random` on ROI over fixed held-out seeds.
- TD SHOULD be at least competitive with `Markov` before receiving a non-trivial ensemble weight.
- If reintroduced, TD weight should start small and calibrated (for example, 0.10–0.15) rather than displacing the current strong trio.

Why not same change as Ensemble reintegration: right now the codebase still needs to prove that TD improved because of better signal, not because the ensemble diluted its weakness. Mixing both concerns in one change would muddy causality and make review harder.

### Risks
- If the hand-strength bucket is too fine, Q-table sparsity returns and learning quality may not improve enough.
- If the bucket uses shared or future-visible card information, the improvement becomes academically weak due to leakage.
- If verification still loads the repository artifact by default, stale snapshots can hide regressions or create false confidence.
- If ensemble reintegration is bundled immediately, the review will likely exceed the 400-line budget and blur whether TD itself actually improved.

### Ready for Proposal
Yes — propose `strengthen-td-preflop-signal` as a focused TD-quality change. Include state-signal improvement, training/seed hygiene, and automatic fresh-snapshot verification in the same change. Keep Ensemble reintegration as a separate follow-up change gated on measured TD improvement.

Decision needed before apply: Yes
Chained PRs recommended: No
400-line budget risk: Medium
