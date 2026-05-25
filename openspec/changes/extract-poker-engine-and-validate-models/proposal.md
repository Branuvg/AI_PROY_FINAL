# Proposal: Extract Poker Engine and Validate Models

## Intent
Refactor the monolithic poker AI notebook into testable Python modules while keeping the notebook as a presentation layer. This resolves simulator limitations, invalid metric calculations, and structural issues compromising experimental results.

## Scope

### In Scope
- Extract poker engine (simulator, rules, betting) into testable Python modules.
- Extract AI models (Markov, TD, Ensemble) into modular components.
- Fix simulator flaws (action limits, re-raise chains, history propagation).
- Fix evaluation metrics (correct ROI calculation).
- Write tests for the engine and metrics.
- Refactor notebook to consume modules for report generation.

### Out of Scope
- Implementing entirely new AI models.
- Extending the game to more than 2 players if unsupported currently.
- Web or GUI development.

## Capabilities

### New Capabilities
- `poker-engine`: Core Texas Hold'em simulator, betting rules, and game state management.
- `ai-agents`: Implementation of Markov, TD, and Ensemble agents with standard interfaces.
- `evaluation-metrics`: Evaluation harness, training loops, and corrected ROI metrics.

### Modified Capabilities
None

## Approach
Extract components systematically:
1. Create `engine` package with simulator rules and tests.
2. Create `metrics` package with corrected evaluation logic and tests.
3. Create `agents` package wrapping existing Markov/TD/Ensemble logic with tests.
4. Refactor the existing Jupyter Notebook to import modules, reproduce training, and generate the report.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `poker_ia_comparativa_final.ipynb` | Modified | Stripped of backend logic, converted to presentation |
| `src/` | New | Python modules for engine, agents, and metrics |
| `tests/` | New | Unit and integration tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Scope creep across multiple agents/features | High | Strictly focus on extracting existing logic first |
| Broken notebook during extraction | Med | Build modules alongside it, swap only when ready |
| Missing dependencies during verification | Low | Document and set up `requirements.txt` early |

## Rollback Plan
Revert to the original monolithic `poker_ia_comparativa_final.ipynb` and remove the `src/` and `tests/` directories using git reset.

## Dependencies
- `treys`, `pgmpy`, `numpy`, `pandas`.
- Python virtual environment.

## Success Criteria
- [ ] Poker engine and rules are extracted and covered by unit tests.
- [ ] ROI metrics and evaluation logic are extracted, corrected, and tested.
- [ ] Notebook runs successfully and generates plots/reports using the new modules.
- [ ] No game logic or model implementations remain inside the notebook.
