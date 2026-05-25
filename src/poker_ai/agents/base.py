"""Common interfaces and baseline poker agents."""

from __future__ import annotations

import random
from collections.abc import Iterable
from dataclasses import dataclass, field

from poker_ai.engine import Action, GameState, legal_actions


ACTION_ORDER = [Action.FOLD, Action.CHECK, Action.CALL, Action.BET, Action.RAISE]
PASSIVE_ACTIONS = {Action.CHECK, Action.CALL}
AGGRESSIVE_ACTIONS = {Action.BET, Action.RAISE}


def ordered_legal_actions(state: GameState) -> list[Action]:
    """Return legal actions in a stable order for deterministic agents/tests."""

    legal = legal_actions(state)
    return [action for action in ACTION_ORDER if action in legal]


def default_amount_for(state: GameState, action: Action) -> int | None:
    """Return the engine-compatible amount for a selected action."""

    if action in {Action.FOLD, Action.CHECK, Action.CALL}:
        return None
    return state.current_bet + state.min_raise


def coerce_legal_action(state: GameState, action: Action | str) -> Action:
    """Map an intended action to the closest legal engine action."""

    intended = Action(action)
    legal = ordered_legal_actions(state)
    if intended in legal:
        return intended
    for fallback in (Action.CALL, Action.CHECK, Action.FOLD):
        if fallback in legal:
            return fallback
    return legal[0]


def infer_opponent_tendency(history: Iterable[dict], player_id: int) -> str:
    """Infer opponent tendency from propagated engine action history."""

    opponent = 1 - player_id
    opponent_actions = [entry for entry in history if entry.get("player") == opponent]
    if not opponent_actions:
        return "passive"
    aggressive = sum(1 for entry in opponent_actions if entry.get("action") in {"bet", "raise"})
    return "aggressive" if aggressive / len(opponent_actions) > 0.3 else "passive"


@dataclass(slots=True)
class BaseAgent:
    """Stable agent interface consumed by `poker_ai.engine.play_hand`."""

    name: str = "BaseAgent"
    rewards: list[float] = field(default_factory=list)

    def choose_action(self, state: GameState) -> Action:
        raise NotImplementedError

    def act(self, state: GameState) -> tuple[Action, int | None]:
        action = coerce_legal_action(state, self.choose_action(state))
        return action, default_amount_for(state, action)

    def observe_reward(self, reward: float, state: GameState | None = None) -> None:
        self.rewards.append(reward)


class RandomAgent(BaseAgent):
    """Uniform random baseline over legal actions."""

    def __init__(self, rng: random.Random | None = None):
        super().__init__(name="Random")
        self.rng = rng or random.Random()

    def choose_action(self, state: GameState) -> Action:
        return self.rng.choice(ordered_legal_actions(state))


class CallAgent(BaseAgent):
    """Passive baseline: call/check when possible, fold only as fallback."""

    def __init__(self):
        super().__init__(name="Call")

    def choose_action(self, state: GameState) -> Action:
        legal = ordered_legal_actions(state)
        for action in (Action.CALL, Action.CHECK):
            if action in legal:
                return action
        return legal[0]
