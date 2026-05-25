"""Agent evaluation metrics with ROI based on actual invested chips."""

from __future__ import annotations

import random
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol

from poker_ai.engine import HandResult, play_hand


class Agent(Protocol):
    name: str

    def act(self, state): ...


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    """Aggregated results for one evaluated agent."""

    agent_name: str
    opponent_name: str
    hands: int
    wins: int
    losses: int
    ties: int
    win_rate: float
    total_profit: int
    total_invested: int
    roi: float
    avg_profit: float
    avg_decision_ms: float
    per_hand_profit: list[int] = field(default_factory=list)
    per_hand_invested: list[int] = field(default_factory=list)


def calculate_roi(total_profit: int | float, total_invested: int | float) -> float:
    """Return profit divided by actual chips invested, or 0.0 when no chips were invested."""

    if total_invested == 0:
        return 0.0
    return float(total_profit) / float(total_invested)


def summarize_results(
    results: Iterable[HandResult],
    *,
    player_id: int = 0,
    agent_name: str = "Agent",
    opponent_name: str = "Opponent",
    avg_decision_ms: float = 0.0,
) -> EvaluationResult:
    """Aggregate engine `HandResult` objects for the selected player."""

    hand_results = list(results)
    opponent_id = 1 - player_id
    wins = sum(1 for result in hand_results if result.winner == player_id)
    losses = sum(1 for result in hand_results if result.winner == opponent_id)
    ties = sum(1 for result in hand_results if result.winner is None)
    per_hand_profit = [result.profit[player_id] for result in hand_results]
    per_hand_invested = [result.invested[player_id] for result in hand_results]
    total_profit = sum(per_hand_profit)
    total_invested = sum(per_hand_invested)
    hands = len(hand_results)
    return EvaluationResult(
        agent_name=agent_name,
        opponent_name=opponent_name,
        hands=hands,
        wins=wins,
        losses=losses,
        ties=ties,
        win_rate=wins / hands if hands else 0.0,
        total_profit=total_profit,
        total_invested=total_invested,
        roi=calculate_roi(total_profit, total_invested),
        avg_profit=total_profit / hands if hands else 0.0,
        avg_decision_ms=avg_decision_ms,
        per_hand_profit=per_hand_profit,
        per_hand_invested=per_hand_invested,
    )


def evaluate_agent(
    agent: Agent,
    opponent: Agent,
    *,
    n_hands: int = 100,
    rng: random.Random | None = None,
    starting_stack: int = 1_000,
    max_raises_per_street: int = 4,
) -> EvaluationResult:
    """Play agent-vs-agent hands and return aggregated metrics for `agent`."""

    rng = rng or random.Random()
    timed_agent = _TimedAgent(agent)
    timed_opponent = _TimedAgent(opponent)
    hand_results: list[HandResult] = []
    for _ in range(n_hands):
        result = play_hand(
            timed_agent,
            timed_opponent,
            rng,
            starting_stack=starting_stack,
            max_raises_per_street=max_raises_per_street,
        )
        hand_results.append(result)
        _observe(agent, result.profit[0])
        _observe(opponent, result.profit[1])
    return summarize_results(
        hand_results,
        player_id=0,
        agent_name=getattr(agent, "name", agent.__class__.__name__),
        opponent_name=getattr(opponent, "name", opponent.__class__.__name__),
        avg_decision_ms=timed_agent.avg_decision_ms,
    )


class _TimedAgent:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.total_decision_ms = 0.0
        self.decisions = 0

    @property
    def avg_decision_ms(self) -> float:
        return self.total_decision_ms / self.decisions if self.decisions else 0.0

    def act(self, state):
        started = time.perf_counter()
        action = self.agent.act(state)
        self.total_decision_ms += (time.perf_counter() - started) * 1_000
        self.decisions += 1
        return action


def _observe(agent: Agent, reward: int) -> None:
    observer = getattr(agent, "observe_reward", None)
    if observer is not None:
        observer(reward)
