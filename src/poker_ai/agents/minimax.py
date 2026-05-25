"""Minimax-style poker agent scaffold."""

from __future__ import annotations

from poker_ai.engine import Action, GameState, evaluate_high_card


from .base import BaseAgent, coerce_legal_action, ordered_legal_actions


class MinimaxAgent(BaseAgent):
    """Lightweight lookahead placeholder preserving the notebook agent boundary."""

    def __init__(self, max_depth: int = 2):
        super().__init__(name="Minimax")
        self.max_depth = max_depth

    def choose_action(self, state: GameState) -> Action:
        legal = ordered_legal_actions(state)
        if len(legal) == 1:
            return legal[0]
        cards = state.hole_cards[state.player_id] + state.community_cards if state.hole_cards else []
        strength = evaluate_high_card(cards)[0] if cards else 6
        if strength >= 10 and state.to_call == 0:
            return coerce_legal_action(state, Action.BET)
        if strength >= 8:
            return coerce_legal_action(state, Action.CALL)
        return coerce_legal_action(state, Action.CHECK)
