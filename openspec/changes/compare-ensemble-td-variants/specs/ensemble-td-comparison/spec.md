# Ensemble TD Comparison Specification

## Purpose

Defines ensemble variant builders, composition labels, weights, and explicit side-by-side reporting rules to compare a default no-TD ensemble against a with-TD ensemble.

## Requirements

### Requirement: Default No-TD Ensemble

The system MUST provide a `build_ensemble_no_td()` builder that returns an ensemble containing only Minimax, Bayesian, and Markov agents. It MUST NOT contain TD, Random, or Call agents.

#### Scenario: Instantiate default ensemble
- GIVEN a request for the default no-TD ensemble
- WHEN `build_ensemble_no_td()` is called
- THEN it returns an ensemble with Minimax (weight 0.5), Bayesian (weight 0.3), and Markov (weight 0.2)
- AND the ensemble contains no TD agent.

### Requirement: With-TD Ensemble Comparison Variant

The system MUST provide a `build_ensemble_with_td()` builder that returns an ensemble containing Minimax, Bayesian, Markov, and a TD agent with explicit weights.

#### Scenario: Instantiate with-TD ensemble with valid TD path
- GIVEN a valid path to a trained TD model
- WHEN `build_ensemble_with_td()` is called
- THEN it returns an ensemble with Minimax, Bayesian, Markov, and TD components
- AND the TD component has a small assigned weight
- AND no Random or Call agents are included.

### Requirement: Reporting Composition

The system MUST report both ensemble variants in the evaluation report with distinct row labels and no aggregation collision.

#### Scenario: Generate evaluation report
- GIVEN the evaluation reporting runner is executed
- WHEN it aggregates the results
- THEN two distinct rows appear: `EnsembleNoTD` and `EnsembleWithTD`
- AND the metadata for each exposes its composition and weights
- AND the with-TD row uses either the trained TD path or clearly labels the fallback.

### Requirement: Spanish Conclusions

The system MUST generate Spanish conclusions comparing both variants and recommending the default baseline based on observed metrics.

#### Scenario: Generate Spanish report conclusions
- GIVEN the report results contain both ensemble variants
- WHEN the Spanish conclusion string is generated
- THEN it explicitly mentions both variants
- AND it recommends the `no-TD` baseline over the `with-TD` variant based on metrics.
