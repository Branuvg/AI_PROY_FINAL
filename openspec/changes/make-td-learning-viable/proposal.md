# Proposal: Make TDLearning Viable

## Intent
Transform `TDAgent` from an untrained, non-learning placeholder into a functional Q-learning baseline that actually updates its policy based on rewards and avoids pathological default-folding, establishing a verifiable learning pipeline.

## Scope

### In Scope
- Fix zero-Q/unseen-state action selection so TD does not default to `fold`.
- Implement actual TD/Q-learning updates with meaningful rewards.
- Add train-before-evaluate/report pipeline.
- Add Q-table persistence (load/save) so reports use trained TD when available.
- Add tests proving TD updates Q-values and can select non-fold actions after training.
- Update Spanish explanation/conclusions about TD limitations and improvement.

### Out of Scope
- Reintegrating TD into the Ensemble (deferred until metrics demonstrate viability).
- DQN, deep RL, or advanced neural network abstractions.
- Full simulator overhaul (street progression/visibility fixes).

## Capabilities

### New Capabilities
- `td-agent-learning`: Core Q-learning updates, state abstraction, and non-fold default action selection.
- `q-table-persistence`: Mechanism to save and load trained Q-tables for reproducible evaluation.
- `model-training-pipeline`: Explicit train-before-evaluate flow for reporting.

### Modified Capabilities
- None

## Approach
Implement a minimal viable Q-learning update within the existing simplified engine. `TDAgent` will record the last `(state, action)` and apply an incremental update (e.g., alpha-based Q-update) upon reward observation. Unseen states will default to non-losing actions (`check` or `call`) instead of `fold`. We will introduce a persistence mechanism and a training script so that `run_report_experiment()` can load a trained snapshot instead of instantiating a blank policy. Finally, the report's Spanish conclusions will be updated to accurately reflect TD's new behavior and theoretical limitations in the current simulator.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/poker_ai/agents/td.py` | Modified | Add Q-updates, state tracking, and fix default action selection |
| `src/poker_ai/evaluation/training.py` | Modified | Implement actual training loop/Q-table mutation |
| `src/poker_ai/evaluation/reporting.py` | Modified | Use trained snapshot for evaluation |
| `tests/agents/test_model_agents.py` | Modified | Add tests for Q-value updates and action selection |
| `tests/evaluation/` | Modified | Add coverage for training pipeline and persistence |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| TD still converges to fold-heavy policy | Medium | Ensure reward structure adequately penalizes unnecessary folding and tie-breaking strongly prefers `check`/`call`. |
| Flawed state representation due to simulator limits | High | Use a conservative, coarse state abstraction (e.g., `to_call`, stack bucket) without relying on leaked future cards. |
| PR exceeds 400-line budget | Medium | Keep persistence simple (JSON/Pickle) and strictly avoid simulator refactoring. |

## Rollback Plan
Revert changes to `src/poker_ai/agents/td.py` and evaluation scripts, restoring `TDAgent` to its previous stub state, and remove any generated Q-table artifacts.

## Dependencies
- None

## Success Criteria
- [ ] `TDAgent` updates its Q-values after receiving rewards.
- [ ] Untrained `TDAgent` chooses `check` or `call` over `fold` in unseen states.
- [ ] Training pipeline successfully saves a Q-table artifact.
- [ ] Report generation loads the trained artifact and evaluates it successfully.
- [ ] All new behaviors are proven via unit tests.