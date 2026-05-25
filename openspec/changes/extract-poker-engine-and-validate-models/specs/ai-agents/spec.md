# AI Agents Specification

## Purpose
Provides standard interfaces for Markov, TD, and Ensemble poker agents, allowing them to be imported, trained independently, and evaluated.

## Requirements

### Requirement: Standard Interface
All agents MUST implement a standard, importable interface for taking actions and receiving rewards.
#### Scenario: Agent acts
- GIVEN an initialized agent
- WHEN `act(game_state)` is called
- THEN the agent returns a valid, legally-defined action and amount.

### Requirement: Bayesian/Markov Tendency Inference
Agents utilizing opponent history MUST have access to propagated game actions to make inferences.
#### Scenario: Infer opponent tendency
- GIVEN the engine propagates an opponent's consistent raising history
- WHEN the Markov agent is queried for an action
- THEN it incorporates the opponent's action history as real data to update probabilities and decide its move.
