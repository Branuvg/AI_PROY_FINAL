## Exploration: make-td-learning-viable

### Current State
`TDLearning` is effectively **untrained** in the current report path. `run_report_experiment()` instantiates `TDAgent()` directly, so the report evaluates a fresh zero-table policy, not a trained one. The nominal training helper also does not produce learning in practice: `train_td_agent()` only calls `observe_reward(result.profit[0])`, but `TDAgent` does not override `observe_reward`, so rewards are appended to `BaseAgent.rewards` and never turned into Q-value updates.

The default zero-table policy is also pathological. `TDAgent.choose_action()` uses `max(legal, key=lambda action: scores.get(action, 0.0))`; with unseen states all legal actions score `0.0`, and `ordered_legal_actions()` is `[fold, check, call, bet, raise]`, so ties prefer `fold` whenever folding is legal. A quick runtime check with the current preflop blind state returns `legal=['fold','call','raise']` and `chosen='fold'`.

The state/reward design is too weak for competitive learning. The TD state key is only `(phase, min(to_call, 100), len(action_history))`, which ignores hand strength, stack depth, pot size, position pressure beyond `to_call`, opponent tendency, and any card abstraction. It also relies on `phase`, but the simulator never advances from `preflop` to `flop/turn/river`; it jumps straight to `showdown`. On top of that, all community cards are dealt at hand start, so any future card-aware state feature would see leaked information unless the engine contract changes. Finally, there is no persistence layer or explicit train-then-evaluate pipeline for TD.

### Affected Areas
- `src/poker_ai/agents/td.py` — zero-table action selection, sparse state key, and non-TD `update()` logic.
- `src/poker_ai/agents/base.py` — inherited `observe_reward()` only stores reward history; no hook updates TD values.
- `src/poker_ai/evaluation/training.py` — `train_td_agent()` suggests a training path but does not mutate the Q-table meaningfully.
- `src/poker_ai/evaluation/reporting.py` — report evaluates `TDAgent()` directly, i.e. an untrained/default policy.
- `src/poker_ai/engine/simulator.py` — simulator never advances betting streets and exposes showdown cards from hand start, constraining defensible TD state design.
- `src/poker_ai/engine/state.py` / `src/poker_ai/engine/rules.py` — current state fields and legal-action ordering create the fold-on-tie default.
- `tests/agents/test_model_agents.py` — currently validates TD only as a constructible agent, not as a learning agent.
- `tests/evaluation/test_reporting.py` and `tests/evaluation/test_training.py` — would need coverage for train-before-report behavior, persistence, and viability gates.

### Approaches
1. **Minimal TD viability inside the current simplified engine** — Keep the existing simulator contract, but make TD actually learn and stop default-folding.
   - Pros: Smallest path to a useful standalone TD baseline; reviewable; directly answers why TD is currently unusable.
   - Cons: Still learns inside a simplified single-street environment; academic claims remain limited.
   - Effort: Medium

2. **TD viability + explicit training artifact/persistence** — Add real learning plus save/load support and require report evaluation to use a trained snapshot or deterministic training pass.
   - Pros: Makes TD useful both standalone and as a candidate ensemble member; reproducible and auditable.
   - Cons: Broader than agent-only changes because reporting/tests/artifacts must move together.
   - Effort: Medium

3. **Full environment-faithful TD redesign** — Fix street progression/visibility first, then redesign TD state and rewards around a more realistic simulator.
   - Pros: Strongest long-term research story.
   - Cons: Too large for the next focused change; spills into poker-engine architecture, not just TD.
   - Effort: High

### Recommendation
Recommended path: pursue **Approach 2 as a separate change from `calibrate-ensemble-strategy`**.

Minimum viable improvement:
1. Make TD actually learn by recording the last `(state, action)` and applying a real incremental update on reward observation (at minimum alpha-based Q update; preferably a simple bootstrapped TD/Q-learning update).
2. Change unseen-state tie-breaking so zero-Q states prefer a non-losing legal default (`check`/`call`) instead of `fold`.
3. Expand the state representation just enough to be useful in the current engine: include `to_call`, pot-pressure or stack bucket, action-history bucket, and a coarse private-hand-strength bucket. Do **not** rely on future community cards for the MVP.
4. Add Q-table persistence plus an explicit training pipeline so report experiments and ensemble calibration can evaluate a trained TD snapshot, not a blank agent.
5. Gate ensemble inclusion on evidence: only give TD a non-trivial ensemble weight if the trained snapshot beats `Random` and is at least competitive with `Markov` on held-out seeds/baselines.

Why separate from `calibrate-ensemble-strategy`: that change intentionally removed TD from the default ensemble to keep calibration honest. Reintroducing TD now requires fixing agent learning, evaluation provenance, and possibly state abstractions. Combining that with ensemble calibration would blur causality and likely blow past the review budget.

### Risks
- If learning is wired without changing tie-breaking, TD may still spend too much time in degenerate fold-heavy trajectories.
- If state features use pre-dealt community cards, TD may improve numerically for the wrong reason and produce academically weak conclusions.
- If persistence is skipped, report runs can silently regress to evaluating an untrained agent again.
- If scope expands into full street progression now, the change will likely exceed the 400-line review budget and should be split.

### Ready for Proposal
Yes — propose a new change focused on TD viability (agent learning + persistence + trained evaluation path), explicitly separate from ensemble calibration. The proposal should treat ensemble re-entry as an evidence-based outcome, not as a precommitted requirement.

Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
