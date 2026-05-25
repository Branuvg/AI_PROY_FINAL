# Poker Engine Specification

## Purpose
Provides an importable, testable Texas Hold'em game simulator with enforced betting rules and game state tracking.

## Requirements

### Requirement: Legal Actions
The engine MUST enforce legal betting actions and rules.
#### Scenario: Re-raise chain
- GIVEN a player has raised
- WHEN the next player attempts to re-raise
- THEN the engine accepts the action if it meets minimum raise requirements and valid chips remain
- AND updates the current pot and to-call amounts.

### Requirement: Action History
The engine MUST propagate opponent action history for observability.
#### Scenario: Track opponent moves
- GIVEN a hand is in progress
- WHEN a player makes a betting action
- THEN the action is appended to the game state history
- AND the updated history is provided to the next acting agent.
