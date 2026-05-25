"""Markov-style poker agent scaffold using propagated action history."""

from __future__ import annotations

from poker_ai.engine import Action, GameState


from .base import BaseAgent, coerce_legal_action, infer_opponent_tendency


class MarkovAgent(BaseAgent):
    """Compact Markov scaffold that biases actions from observed tendency."""

    def __init__(self):
        super().__init__(name="Markov")
        self.last_tendency = "passive"

    def choose_action(self, state: GameState) -> Action:
        self.last_tendency = infer_opponent_tendency(state.action_history, state.player_id)
        if self.last_tendency == "aggressive":
            return coerce_legal_action(state, Action.CALL)
        if state.to_call == 0:
            return coerce_legal_action(state, Action.BET)
        return coerce_legal_action(state, Action.CALL)
