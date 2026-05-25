# Proposal: compare-ensemble-td-variants

## Intent

To provide side-by-side reporting of the strong default `no-TD` ensemble against an explicit `with-TD` ensemble comparison variant, updating the Spanish reporting and documentation narrative without redefining the recommended baseline or changing the underlying ensemble algorithm.

## Scope

### In Scope
- Define explicit builder variants: `build_ensemble_no_td()` (baseline) and `build_ensemble_with_td()` with small committed TD weight.
- Expose stable report labels (`EnsembleNoTD`, `EnsembleWithTD`) and compositional metadata in reporting.
- Ensure the `with-TD` variant correctly utilizes trained or fresh TD snapshot paths.
- Update `ReportRow` and Spanish conclusions to reflect side-by-side comparison.
- Update notebook and documentation narrative to clarify the variants.

### Out of Scope
- Broad algorithmic changes to TD training.
- Changing the primary default or recommended ensemble from the current calibrated `no-TD` baseline.
- Adding entirely new agents to the ensemble pool.

## Capabilities

### New Capabilities
- `ensemble-td-comparison`: Defines ensemble variant builders, composition labels, weights, and explicit side-by-side reporting rules.

### Modified Capabilities
None

## Approach

Follow Approach 1 from exploration: keep the existing `EnsembleAgent` class but expose explicit builder functions (`build_ensemble_no_td`, `build_ensemble_with_td`). Update the `Reporting` runner to evaluate both side-by-side with clear, non-colliding row labels. Update metadata capture and Spanish conclusion generation to explicitly discuss the comparison while preserving the recommendation for the `no-TD` baseline.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/poker_ai/agents/ensemble.py` | Modified | Add `with-TD` builder and variant aliases. |
| `src/poker_ai/agents/__init__.py` | Modified | Export new builders. |
| `src/poker_ai/evaluation/reporting.py` | Modified | Add the second ensemble row, update labels and Spanish narrative. |
| `tests/agents/test_model_agents.py` | Modified | Add tests ensuring correct default behavior and variant composition. |
| `tests/evaluation/test_reporting.py` | Modified | Asserts multiple ensemble rows and distinct metadata. |
| `docs/notebook_backend_report.md` | Modified | Update documentation text for comparison. |
| `poker_ia_comparativa_final.ipynb` | Modified | Update markdown cells reflecting the side-by-side approach. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Row label collision in reporting | Low | Hardcode distinct and stable labels (`EnsembleNoTD`, `EnsembleWithTD`) in the reporting loop. |
| Redefining baseline unintentionally | Low | Document and enforce `no-TD` as the primary default in code and tests. Use small TD weights. |
| Stale TD models causing bad results | Medium | Continue utilizing existing fresh/snapshot reporting logic to provide reliable agents. |

## Rollback Plan

Revert the commits introducing the new builders and reporting logic, restoring `build_default_ensemble()` as the sole ensemble and rolling back notebook markdown text to the "deferred TD reintegration" language.

## Dependencies

- Existing trained TD models or fresh in-memory training fallback for the `with-TD` variant.

## Success Criteria

- [ ] `reporting.py` outputs two distinct ensemble rows with correct labels and metadata.
- [ ] The `no-TD` ensemble retains current calibrated weights (0.5/0.3/0.2) and behavior.
- [ ] Spanish text in reports explicitly mentions both variants and recommends the `no-TD` baseline.
- [ ] Notebook markdown matches the new side-by-side comparison narrative.