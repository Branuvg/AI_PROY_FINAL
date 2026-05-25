# model-training-pipeline Specification

## Purpose

Defines the requirements for the model training and evaluation pipeline, ensuring deterministic, decoupled RNG streams, and valid artifact verification.

## Requirements

### Requirement: Separated Deterministic RNG Streams

The training loop MUST use separated, deterministic RNG streams for the deck, the exploring agent, and the stochastic opponents.

#### Scenario: Training trajectory generation
- GIVEN the training loop is instantiated
- WHEN a new trajectory is generated
- THEN the deck shuffling, agent exploration, and opponent actions MUST pull from independent RNG seeds
- AND their randomness MUST NOT be coupled

### Requirement: Fresh Snapshots for Verification

The training and evaluation pipeline MUST generate and use fresh snapshots for metric verification to avoid reporting stale results.

#### Scenario: Snapshot verification
- GIVEN the evaluation pipeline is run
- WHEN the TD agent is verified
- THEN a newly trained snapshot MUST be used
- AND the pipeline MUST NOT evaluate against a stale repository artifact

### Requirement: Baseline Comparison and Metric Gate

Verification MUST compare the freshly trained TD agent against Random and Call baselines using fixed seeds, and explicitly report whether the metric gate is met.

#### Scenario: Baseline evaluation
- GIVEN a freshly trained TD snapshot
- WHEN evaluation occurs
- THEN it MUST play against Random and Call baselines on fixed seeds
- AND the evaluation report MUST indicate whether the required ROI metric gate is achieved
