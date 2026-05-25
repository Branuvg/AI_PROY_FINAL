"""Weighted-vote ensemble agent."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from poker_ai.engine import Action, GameState


from .base import BaseAgent, coerce_legal_action, ordered_legal_actions
from .bayesian import BayesianAgent
from .markov import MarkovAgent
from .minimax import MinimaxAgent


DEFAULT_ENSEMBLE_WEIGHTS: dict[str, float] = {
    "minimax": 0.5,
    "bayesian": 0.3,
    "markov": 0.2,
}

WITH_TD_ENSEMBLE_WEIGHTS: dict[str, float] = {
    "minimax": 0.45,
    "bayesian": 0.27,
    "markov": 0.18,
    "td": 0.10,
}


class EnsembleAgent(BaseAgent):
    """Combine standard agents by legal weighted vote."""

    def __init__(
        self,
        agents: Mapping[str, BaseAgent] | None = None,
        weights: Mapping[str, float] | None = None,
        name: str = "Ensemble",
    ):
        super().__init__(name=name)
        if agents is None:
            agents = _default_agents()
            weights = weights or DEFAULT_ENSEMBLE_WEIGHTS
        self.agents = dict(agents)
        self.weights = dict(weights or {name: 1.0 for name in self.agents})
        self.last_recommendations: dict[str, Action] = {}

    def choose_action(self, state: GameState) -> Action:
        legal = ordered_legal_actions(state)
        votes: defaultdict[Action, float] = defaultdict(float)
        total = sum(self.weights.values()) or 1.0
        for name, agent in self.agents.items():
            try:
                action = coerce_legal_action(state, agent.choose_action(state))
            except Exception:
                action = legal[0]
            self.last_recommendations[name] = action
            votes[action] += self.weights.get(name, 0.0) / total
        return max(legal, key=lambda action: votes.get(action, 0.0))

    def update_weights(self, winning_action: Action, lr: float = 0.02) -> None:
        for name, action in self.last_recommendations.items():
            if action == winning_action:
                self.weights[name] = self.weights.get(name, 0.0) + lr
        total = sum(self.weights.values()) or 1.0
        self.weights = {name: weight / total for name, weight in self.weights.items()}


def build_ensemble_no_td(seed: int | None = None, *, name: str = "EnsembleNoTD") -> EnsembleAgent:
    """Build the explicit no-TD ensemble comparison variant."""

    _ = seed  # Reserved for future seeded constituents; keeps the public contract stable.
    return EnsembleAgent(_default_agents(), DEFAULT_ENSEMBLE_WEIGHTS, name=name)


def build_ensemble_with_td(td_agent: BaseAgent, seed: int | None = None, *, name: str = "EnsembleWithTD") -> EnsembleAgent:
    """Build the with-TD ensemble comparison variant using an injected TD agent."""

    _ = seed  # Reserved for future seeded constituents; keeps the public contract stable.
    return EnsembleAgent(
        {**_default_agents(), "td": td_agent},
        WITH_TD_ENSEMBLE_WEIGHTS,
        name=name,
    )


def build_default_ensemble(seed: int | None = None) -> EnsembleAgent:
    """Build the backward-compatible calibrated ensemble used by legacy callers."""

    return build_ensemble_no_td(seed, name="Ensemble")


def _default_agents() -> dict[str, BaseAgent]:
    return {
        "minimax": MinimaxAgent(),
        "bayesian": BayesianAgent(),
        "markov": MarkovAgent(),
    }
