# Proposal: Strengthen TD Preflop Signal

## Intent

The `TDAgent` learning signal is currently too weak to produce a standalone policy because it relies on an overly coarse state abstraction (`(phase, to_call, history_len)`) that cannot distinguish premium hands from trash. This results in a degenerate fold-heavy policy. We need to strengthen the TD signal by adding a leakage-safe preflop hand-strength bucket to the state and fixing training environment RNG coupling, allowing the agent to learn meaningful starting-hand actions.

## Scope

### In Scope
- Add coarse preflop bucket to TD state using only private hole cards.
- Separate RNG streams for deck dealing, TD exploration, and stochastic opponents.
- Minor training parameters/reward shaping tweaks if needed (conservative).
- Train/evaluate with fresh snapshots and hold-out seeds to prevent stale artifact reporting.
- Define a metric gate for future TD reintegration.
- Update Spanish docs/notebook to explain improved TD and criteria.

### Out of Scope
- Reintegration of TD into the Ensemble agent (deferred to follow-up).
- Multi-phase (flop/turn/river) state abstraction.
- Rewrite of the simulator core.

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `td-agent-learning`: Update state key abstraction to include private preflop hand-strength buckets.
- `model-training-pipeline`: Isolate RNG streams for training trajectories and use fresh paths for verification.

## Approach

We will implement a coarse hand-strength evaluation (e.g., premium, playable, trash) for preflop scenarios using only the agent's private hole cards, ensuring no future or community card leakage. This bucket will be appended to the existing TD state key. We will update the training loop to instantiate separate random number generators for the deck, the exploring agent, and the opponent to decouple their behaviors. Verification will be updated to train a temporary snapshot and evaluate it directly against baselines, ensuring reporting reflects actual learning rather than the stale repository artifact.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/poker_ai/agents/td.py` | Modified | Add preflop bucket to TD state key. |
| `src/poker_ai/evaluation/training.py` | Modified | Split RNG streams for deck, agent, opponent. |
| `src/poker_ai/evaluation/reporting.py` | Modified | Verify fresh snapshot instead of stale artifact. |
| `src/poker_ai/engine/state.py` | Modified | Expose private hole cards safely. |
| `tests/agents/test_model_agents.py` | Modified | Coverage for richer state abstraction. |
| `tests/evaluation/test_training.py` | Modified | Coverage for independent RNGs. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Bucket is too fine, causing sparsity | Medium | Use a very coarse bucket (e.g., 3-5 categories). |
| Leakage from shared information | Low | Restrict bucket evaluation strictly to `player.hand`. |
| Stale snapshots mask regression | Low | Auto-verification script will enforce fresh snapshot training before evaluating. |

## Rollback Plan

Revert changes to `td.py` state formulation and `training.py` RNG usage via Git. The existing `artifacts/td_qtable.json` will remain intact if the temporary snapshot verification fails.

## Dependencies

None

## Success Criteria

- [ ] TD state abstraction includes a private hand-strength bucket without leaking community/future data.
- [ ] Training uses independent RNG streams for deck, TD exploration, and opponent.
- [ ] Reporting auto-verifies metrics using a freshly trained snapshot on held-out seeds.
- [ ] TD trained snapshot achieves an ROI > -1.0 (ideally > 0 against Random) on hold-out seeds.
- [ ] Spanish documentation and notebooks reflect the new state abstraction and metric gates.
