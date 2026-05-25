## Exploration: compare-ensemble-td-variants

### Current State
The current backend exposes one strong default ensemble only: `build_default_ensemble()` returns `Minimax + Bayesian + Markov` with fixed calibrated weights `0.5 / 0.3 / 0.2` from `src/poker_ai/agents/ensemble.py`. Report execution in `src/poker_ai/evaluation/reporting.py` evaluates that ensemble under the single row name `Ensemble`, records composition/weights metadata, and generates Spanish conclusions that explicitly say TD reintegration is deferred.

TD reporting already exists as a standalone `TDLearning` row backed by either a fresh in-memory training run or a saved snapshot. The codebase therefore already has the pieces to compare TD separately, but NOT yet to compare two explicit ensemble variants side by side with stable labels, distinct compositions, and narrative that preserves the no-TD ensemble as the default baseline.

### Affected Areas
- `src/poker_ai/agents/ensemble.py` — current default builder, weight constants, and best place to define explicit no-TD / with-TD ensemble builders or naming helpers.
- `src/poker_ai/agents/__init__.py` — export surface for any new builder names used by reporting/tests/notebook.
- `src/poker_ai/evaluation/reporting.py` — report agent list, metadata capture, row labels, TD snapshot wiring, and Spanish conclusions.
- `src/poker_ai/evaluation/training.py` — natural place for a committed small TD comparison weight constant if the with-TD variant is calibrated/documented.
- `tests/agents/test_model_agents.py` — needs guards that the default ensemble remains no-TD while the TD comparison variant includes TD intentionally.
- `tests/evaluation/test_reporting.py` — needs assertions for two ensemble rows, metadata exposure, labels, and conclusion text.
- `tests/test_notebook_contract.py` — likely needs updated narrative assertions once the notebook/documentation stops saying TD reintegration is simply deferred.
- `docs/notebook_backend_report.md` and `poker_ia_comparativa_final.ipynb` — must present both variants and Spanish interpretation without regressing the current backend-import contract.

### Approaches
1. **Explicit builder functions, same `EnsembleAgent` class** — keep one generic class and add builders such as `build_ensemble_no_td()` and `build_ensemble_with_td()` plus stable report labels.
   - Pros: Smallest safe change; preserves current architecture; easy to test; avoids class explosion when the real difference is composition + weights.
   - Cons: Names/metadata must be handled carefully so report rows and notebook labels stay human-readable.
   - Effort: Low

2. **Dedicated subclasses (`EnsembleNoTD`, `EnsembleWithTD`)** — wrap the two variants in separate classes with fixed names.
   - Pros: Very explicit semantics at call sites; row names become automatic.
   - Cons: More surface area for little behavioral gain; duplicates composition logic unless carefully refactored.
   - Effort: Medium

3. **Report-only aliasing** — keep a single backend builder API and create the two variants only inside reporting by cloning weights/composition and overriding labels there.
   - Pros: Minimal agent-layer churn.
   - Cons: Pushes domain semantics into reporting; weaker testability/reuse; easy for notebook/report drift to reappear.
   - Effort: Low

### Recommendation
Recommend **Approach 1** under the change name **`compare-ensemble-td-variants`**.

Focused implementation path:
1. Keep `build_default_ensemble()` as the no-TD strong baseline for backward compatibility.
2. Add one explicit no-TD alias/builder and one explicit with-TD builder, both returning `EnsembleAgent`, with stable names/labels surfaced to reporting. Example intent: `EnsembleNoTD` / `EnsembleWithTD` as report-facing labels even if the underlying type stays `EnsembleAgent`.
3. Preserve the current calibrated no-TD weights `0.5 / 0.3 / 0.2` unchanged.
4. Add the with-TD variant using the same strong trio plus TD at a small committed weight, ideally documented in code as comparison-only and sourced from the trained snapshot/fresh training path already used by reporting. Keep the no-TD variant as the default/best baseline regardless of whether the TD variant wins or loses in a given small run.
5. Extend `ReportRow` metadata and Spanish conclusions so both ensemble rows show composition, weights, and a short interpretation that explains the no-TD baseline remains the recommendation while the TD variant is included for explicit comparison.
6. Update notebook/docs wording from “TD reintegration is deferred” to the more precise statement: TD is NOT the default ensemble constituent, but a limited-weight comparison variant is reported separately.

Why this path: the code already separates concerns reasonably well. The missing piece is not a new ensemble algorithm; it is explicit variant construction and report narration. Putting those semantics in builders keeps reporting thin and avoids removing existing no-TD behavior.

### Risks
- If the with-TD variant reuses the generic row name `Ensemble`, report aggregation will collide and hide one variant.
- If TD is given more than a small committed weight, the comparison can accidentally redefine the baseline rather than test TD incrementally.
- If the notebook/docs keep the old “deferred reintegration” wording unchanged, the narrative will contradict the new explicit comparison rows.
- If the with-TD path depends on stale disk snapshots only, results will be noisy or misleading; reporting should keep using the existing fresh/snapshot logic and label provenance clearly.

### Ready for Proposal
Yes — propose `compare-ensemble-td-variants` as a focused reporting/backend change. Scope it to explicit variant builders/labels, report metadata, notebook/doc narrative, and regression tests; do NOT reopen TD training quality or default ensemble calibration in the same slice.

Decision needed before apply: No
Chained PRs recommended: No
400-line budget risk: Medium
