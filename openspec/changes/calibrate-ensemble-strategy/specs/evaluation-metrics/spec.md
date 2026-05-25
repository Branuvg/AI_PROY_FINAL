# evaluation-metrics Specification

## Purpose
Specifies the evaluation reporting behavior for the ensemble strategy, ensuring correct metrics, reproducible weights, and accurate professional conclusions in Spanish.

## Requirements

### Requirement: Ensemble Evaluation Report
The system MUST expose the ensemble's composition and weights in the evaluation report and use corrected Return on Investment (ROI) metrics.

#### Scenario: Generating evaluation report
- GIVEN a calibrated `EnsembleAgent` has completed evaluation matches
- WHEN the report is generated
- THEN the report includes the list of constituent agents and their respective weights
- AND the report displays the corrected ROI metric

### Requirement: Spanish Conclusions
The system MUST output professional Spanish conclusions in the reporting module that accurately reflect the post-calibration results and caveats.

#### Scenario: Outputting report conclusions
- GIVEN the evaluation metrics have been calculated for the ensemble
- WHEN the report's conclusion section is rendered
- THEN it contains professional text in Spanish accurately describing the ensemble's performance and any calibration caveats
