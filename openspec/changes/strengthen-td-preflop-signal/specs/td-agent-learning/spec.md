# td-agent-learning Specification

## Purpose

Defines the state representation and learning constraints for the TD agent, specifically addressing preflop hand-strength and the conditions for future ensemble reintegration.

## Requirements

### Requirement: State Key Preflop Bucket

The TD agent MUST incorporate a coarse hand-strength bucket into its state key during the preflop phase, derived strictly from the acting player's private hole cards.

#### Scenario: Preflop state generation
- GIVEN the TD agent is acting preflop
- WHEN the state key is generated
- THEN the key MUST include a hand-strength bucket (e.g., premium, playable, trash)
- AND the bucket MUST NOT use community cards or opponent cards

### Requirement: Spanish Documentation and Reintegration Gate

The project documentation (in Spanish) MUST explicitly state how the TD state has been improved and that its reintegration into the Ensemble agent is deferred until metric gates are met.

#### Scenario: Documentation update
- GIVEN the TD agent improvements are implemented
- WHEN the Spanish report/notebook is updated
- THEN it MUST explain the preflop bucket addition
- AND it MUST state that Ensemble reintegration is deferred until the TD agent meets the ROI metric gate
