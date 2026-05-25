"""Bayesian poker agent scaffold with optional pgmpy support."""

from __future__ import annotations

from poker_ai.engine import Action, GameState


from .base import BaseAgent, coerce_legal_action, infer_opponent_tendency


def pgmpy_available() -> bool:
    try:
        import pgmpy  # noqa: F401
    except ImportError:
        return False
    return True


class BayesianAgent(BaseAgent):
    """Guarded Bayesian scaffold that remains importable without pgmpy."""

    def __init__(self):
        super().__init__(name="Bayesian")
        self.has_pgmpy = pgmpy_available()
        self.last_tendency = "passive"

    def choose_action(self, state: GameState) -> Action:
        self.last_tendency = infer_opponent_tendency(state.action_history, state.player_id)
        if state.to_call > state.pot and self.last_tendency == "aggressive":
            return coerce_legal_action(state, Action.FOLD)
        if state.to_call == 0 and self.last_tendency == "passive":
            return coerce_legal_action(state, Action.BET)
        return coerce_legal_action(state, Action.CALL)
