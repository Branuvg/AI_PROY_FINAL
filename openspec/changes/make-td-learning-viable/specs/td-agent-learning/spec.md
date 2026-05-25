# td-agent-learning Specification

## Purpose
Defines the core Q-learning updates, state abstraction, and default action selection for the `TDAgent` to enable rudimentary but verifiable reinforcement learning.

## Requirements

### Requirement: Default Action Selection

The system MUST avoid pathological default `fold` actions for unseen or zero-Q states.

#### Scenario: Unseen State Encountered
- GIVEN the `TDAgent` is in an unseen state with no prior Q-values
- WHEN it must choose an action
- THEN it MUST select a non-losing action (e.g., `check` or `call`) instead of `fold`

### Requirement: Q-Value Updates

The system MUST perform actual Q-value updates based on observed transitions and rewards.

#### Scenario: Reward Observation
- GIVEN the `TDAgent` has taken an action in a specific state
- WHEN the hand concludes and a reward is distributed
- THEN the agent MUST incrementally update the Q-value for that `(state, action)` pair using the reward
- AND the updated Q-value MUST reflect the received reward algebraically (e.g., via learning rate $\alpha$)

### Requirement: TD Learning Tests

The system MUST prove via automated tests that Q-values update and non-fold actions are selected.

#### Scenario: Training Verification Test
- GIVEN a basic testing environment
- WHEN the `TDAgent` is trained
- THEN a test MUST prove that its Q-values updated successfully
- AND a test MUST prove the agent selects non-fold actions in basic scenarios