from __future__ import annotations

import random

import pytest

from poker_ai.engine import Action, legal_actions


class ScriptedAgent:
    def __init__(self, actions):
        self.actions = list(actions)
        self.seen_histories = []

    def act(self, state):
        self.seen_histories.append(list(state.action_history))
        if self.actions:
            return self.actions.pop(0)
        if Action.CHECK in legal_actions(state):
            return Action.CHECK, None
        return Action.CALL, None


@pytest.fixture
def rng():
    return random.Random(7)


@pytest.fixture
def scripted_agent():
    return ScriptedAgent
