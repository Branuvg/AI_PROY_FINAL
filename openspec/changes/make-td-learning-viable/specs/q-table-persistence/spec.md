# q-table-persistence Specification

## Purpose
Defines the mechanism to save and load trained Q-tables to enable reproducible evaluation of the `TDAgent` policy.

## Requirements

### Requirement: Save Trained Policy

The system MUST support saving the `TDAgent`'s learned Q-table to a persistent artifact.

#### Scenario: Successful Training Completion
- GIVEN the `TDAgent` has completed a training loop
- WHEN the training script finalizes
- THEN the system MUST save the Q-table to disk (e.g., JSON or Pickle format)

### Requirement: Load Trained Policy

The system MUST support loading a previously saved Q-table into a `TDAgent` instance.

#### Scenario: Agent Initialization with Artifact
- GIVEN a saved Q-table artifact exists on disk
- WHEN a new `TDAgent` is instantiated for evaluation
- THEN it MUST successfully load the Q-table and use it for action selection

### Requirement: Persistence Testing

The system MUST prove via tests that persistence round-trips correctly.

#### Scenario: Round-trip Test
- GIVEN a `TDAgent` with a specific non-empty Q-table
- WHEN it is saved to disk and loaded into a new instance
- THEN the loaded Q-table MUST exactly match the original Q-table