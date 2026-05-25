# ai-agents Specification

## Purpose
Specifies the behavior and composition of the Ensemble Agent for the poker simulation, ensuring robust default configurations and reproducible weight calibration.

## Requirements

### Requirement: Default Ensemble Composition
The system MUST construct the default `EnsembleAgent` using strong model agents (Minimax, Bayesian, Markov) rather than Random or Call constituents.

#### Scenario: Instantiating default ensemble
- GIVEN no explicit constituent agents are provided
- WHEN an `EnsembleAgent` is instantiated
- THEN it uses Minimax, Bayesian, and Markov agents as its constituents
- AND it does NOT include RandomAgent or CallAgent

### Requirement: Exclude TD Agent by Default
The system MUST exclude or zero-weight the TD agent from the default ensemble unless explicit calibration enables it.

#### Scenario: Verifying TD agent exclusion
- GIVEN default instantiation of the `EnsembleAgent`
- WHEN inspecting its constituents or weights
- THEN the TD agent is absent or has a weight of 0

### Requirement: Reproducible Calibration Weights
The system MUST establish reproducible static weights derived from validation seeds, overriding equal default weights.

#### Scenario: Applying calibrated weights
- GIVEN a set of reproducible validation seeds
- WHEN the ensemble calibration is run
- THEN it produces static, documented weights that are applied during voting

### Requirement: Guard Against Regression
The system MUST guard against regression to the Random+Call default ensemble and prevent the reintroduction of forbidden old notebook logic.

#### Scenario: Running regression tests
- GIVEN the test suite
- WHEN the ensemble tests are executed
- THEN assertions confirm the default constituents are correct and no old notebook code paths are active
