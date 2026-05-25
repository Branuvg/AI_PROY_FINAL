# Proposal: Calibrate Ensemble Strategy

## Intent

The current ensemble agent evaluated in the project report uses a weak default composition (`RandomAgent` + `CallAgent`), masking its true potential and leading to understated conclusions. This change replaces the default ensemble with strong model agents (Minimax, Bayesian, Markov), establishes a reproducible static weight calibration process, and updates the evaluation report's Spanish conclusions to reflect accurate findings.

## Scope

### In Scope
- Change the default report ensemble composition to Minimax, Bayesian, and Markov agents.
- Exclude the TD agent from the default ensemble unless explicit calibration proves its value.
- Add a reproducible validation-seed calibration step to generate static fixed weights.
- Update professional Spanish conclusions in the reporting module based on calibrated results.

### Out of Scope
- Implementing a soft-score (confidence) interface for action aggregation.
- Major changes to the underlying poker simulator or opponent models.
- Online learning or dynamic weight updates during evaluation.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `ai-agents`: Update the `EnsembleAgent` interface or configuration to accept and use calibrated static weights, and ensure the default composition uses stronger baseline agents.
- `evaluation-metrics`: Update `reporting.py` to evaluate the new calibrated ensemble and output corrected professional Spanish conclusions.

## Approach

Replace the default composition in `src/poker_ai/evaluation/reporting.py` with the strong model agents. Introduce a lightweight validation script or function in `src/poker_ai/evaluation/training.py` that calibrates static weights against validation seeds. Update `src/poker_ai/agents/ensemble.py` to use these weights while keeping the existing hard-vote interface. Exclude the TD agent to prevent dragging down the ensemble. Rerun reports to verify performance and update the Spanish conclusions text directly.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/poker_ai/agents/ensemble.py` | Modified | Update weighting logic and default behavior. |
| `src/poker_ai/evaluation/reporting.py` | Modified | Change default evaluated agents and update Spanish conclusions. |
| `src/poker_ai/evaluation/training.py` | Modified | Add reproducible validation-seed calibration logic. |
| `tests/agents/test_model_agents.py` | Modified | Expand tests for calibrated default behavior. |
| `tests/evaluation/test_reporting.py` | Modified | Assert the new default report ensemble and calibration path. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Validation overfitting | Medium | Use diverse validation seeds; ensure calibration doesn't overfit to a single weak opponent like `CallAgent`. |
| Reduced apparent diversity (TD excluded) | Low | Document that TD is excluded due to lack of a robust policy baseline. |

## Rollback Plan

Revert changes to `src/poker_ai/evaluation/reporting.py` to restore the previous `RandomAgent` + `CallAgent` default composition. Remove calibration scripts and restore the previous hard-coded weights in `EnsembleAgent`.

## Success Criteria

- [ ] The default ensemble evaluated in reports uses Minimax, Bayesian, and Markov agents.
- [ ] Static weights for the ensemble are derived from a reproducible calibration step using validation seeds.
- [ ] The TD agent is excluded from the default ensemble unless explicitly proven beneficial.
- [ ] The evaluation report conclusions in Spanish accurately reflect the new calibrated results.
- [ ] All tests pass and explicitly verify the new default ensemble behavior.
