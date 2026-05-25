# model-training-pipeline Specification

## Purpose
Defines the explicit train-before-evaluate flow, ensuring that reporting and evaluation use a trained model snapshot when available, and updates documentation appropriately.

## Requirements

### Requirement: Evaluate with Trained Snapshot

The reporting and evaluation system MUST use a trained `TDAgent` snapshot if available.

#### Scenario: Snapshot Available
- GIVEN a trained Q-table snapshot exists
- WHEN the evaluation or report generation script runs
- THEN it MUST load the snapshot for the `TDAgent`
- AND evaluate its performance against the baseline

#### Scenario: Snapshot Unavailable
- GIVEN no trained snapshot exists
- WHEN the evaluation script runs
- THEN it MUST clearly mark the `TDAgent` as an untrained fallback
- AND it SHOULD log a warning

### Requirement: Report Documentation

The Spanish documentation and report MUST explain the TD agent's limitations and parameters.

#### Scenario: Report Generation
- GIVEN the experiment report is generated
- WHEN reviewing the Spanish conclusions section
- THEN it MUST accurately explain the TD limitations in the current simulator
- AND it MUST list the current training parameters (e.g., alpha, episodes)