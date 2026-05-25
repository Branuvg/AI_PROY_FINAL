## Exploration: calibrate-ensemble-strategy

### Current State
The extracted backend has a minimal `EnsembleAgent` that only aggregates hard actions with normalized static weights and picks the legal action with the highest vote. It has no offline calibration path, no phase/context awareness, and no confidence interface. More importantly, the report experiment currently evaluates an ensemble built from `RandomAgent` + `CallAgent`, not from the stronger `Minimax` / `Bayesian` / `Markov` agents, so the published underperformance is expected from the present default wiring rather than from TD contamination alone.

### Affected Areas
- `src/poker_ai/agents/ensemble.py` — current weighted-vote implementation, default weight behavior, and possible phase-aware routing point.
- `src/poker_ai/evaluation/reporting.py` — defines the evaluated default ensemble composition and is the main reason the reported ensemble is weak today.
- `src/poker_ai/agents/td.py` — shows TD is a sparse scaffold with no meaningful learned policy unless a real training/calibration path is added.
- `src/poker_ai/evaluation/training.py` — likely place for lightweight validation-seed calibration helpers if static optimized weights are added.
- `tests/agents/test_model_agents.py` — current ensemble behavior tests; would need expansion for calibrated/default behavior.
- `tests/evaluation/test_reporting.py` — would need assertions for the new default report ensemble and reproducible calibration path.

### Approaches
1. **Composition + static calibrated weights** — Replace the default report ensemble with stronger base agents and add reproducible fixed weights chosen from validation seeds.
   - Pros: Directly addresses the real current weakness; academically defendible because weights come from a documented validation procedure; low interface churn.
   - Cons: Still global/static; may overfit to the `Call` baseline if validation remains too narrow.
   - Effort: Low

2. **Phase-specific calibrated weights** — Keep the same hard-vote interface, but select different weight maps for `preflop/flop/turn/river`.
   - Pros: Uses existing `GameState.phase`; captures context without changing all agent APIs; stronger research story than one global vector.
   - Cons: More tuning surface and more evaluation variance; needs careful scope control to stay reviewable.
   - Effort: Medium

3. **Confidence/soft-score ensemble** — Extend agents so they can expose action scores or confidence, then aggregate soft preferences instead of only final actions.
   - Pros: Best long-term ensemble design; avoids information loss from hard voting.
   - Cons: Not feasible as a focused next change because current agent interfaces only expose `choose_action/act`; this would ripple across every agent and test.
   - Effort: High

4. **Opponent-diversity evaluation only** — Keep ensemble logic mostly unchanged but add broader validation opponents during evaluation/calibration.
   - Pros: Improves academic defensibility and reduces overclaiming from a single `Call` baseline.
   - Cons: Does not fix the weak default ensemble by itself; should be secondary unless calibration results remain unstable.
   - Effort: Low

### Recommendation
Recommended path: pursue **Approach 1** as the core change, with a narrow allowance for **phase-specific weights only if implemented as static precomputed maps rather than online learning**. Concretely: change the default evaluated ensemble composition to use stronger agents, exclude TD from the default ensemble unless validation proves benefit, and add a reproducible validation-seed calibration step that produces documented fixed weights checked into code/config. This is the best balance of competitiveness, academic defensibility, and scope control.

Why this and not the others: the present evidence shows the main issue is NOT sophisticated weighting yet — it is that the evaluated default ensemble is currently composed of weak members (`Random` + `Call`) and the TD scaffold is not meaningfully trained. Soft-score aggregation is architecturally better, but it is too broad for the next SDD slice.

### Risks
- Validation can overfit if calibration uses only `CallAgent`; add at least one stronger held-out opponent if results remain unstable.
- Phase-specific tuning can expand quickly into a matrix-search problem; cap the first change to a small fixed schema.
- TD should not be included by default unless a real trained signal is demonstrated, because current training only records rewards and does not establish a robust policy benchmark.

### Ready for Proposal
Yes — propose `calibrate-ensemble-strategy` as a focused change that improves default ensemble composition and reproducible weight calibration first, while explicitly deferring confidence-based interface redesign.

Decision needed before apply: No
Chained PRs recommended: No
400-line budget risk: Medium
