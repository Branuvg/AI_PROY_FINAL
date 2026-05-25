# Evaluation Metrics Specification

## Purpose
Defines the training loop harness, metrics calculations, and precise reporting, ensuring correct ROI metrics based on actual chips invested.

## Requirements

### Requirement: ROI Calculation
The system MUST calculate profit and ROI accurately based on actual invested chips.
#### Scenario: Positive ROI
- GIVEN an agent invested 100 chips across multiple hands
- WHEN the agent returns 150 chips total
- THEN the ROI metric is calculated as exactly 50%.
#### Scenario: Clear denominator
- GIVEN an agent folds pre-flop and invests 0 chips in a hand
- WHEN evaluating the agent's ROI
- THEN the hand contributes correctly to the aggregate statistics without causing divide-by-zero or skewing the base invested chips.

### Requirement: Notebook Consumption
The evaluation harness MUST be importable by the presentation notebook.
#### Scenario: Report Generation
- GIVEN the metrics module is imported
- WHEN the notebook runs the evaluation function
- THEN it successfully receives the aggregated training data and generates a report
- AND the notebook itself contains no core logic or duplicated engine behavior.
