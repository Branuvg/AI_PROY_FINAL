import random

from poker_ai.agents import CallAgent, RandomAgent
from poker_ai.engine import HandResult
from poker_ai.evaluation import calculate_roi, evaluate_agent, summarize_results


def test_roi_uses_actual_invested_chips():
    result = summarize_results(
        [HandResult(winner=0, profit=[50, -50], invested=[100, 100], history=[])],
        agent_name="Winner",
        opponent_name="Loser",
    )

    assert result.total_profit == 50
    assert result.total_invested == 100
    assert result.roi == 0.5
    assert calculate_roi(50, 100) == 0.5


def test_roi_returns_zero_when_no_chips_were_invested():
    result = summarize_results(
        [HandResult(winner=None, profit=[0, 0], invested=[0, 0], history=[])],
        agent_name="Idle",
        opponent_name="IdleOpponent",
    )

    assert result.roi == 0.0
    assert calculate_roi(10, 0) == 0.0


def test_evaluate_agent_integrates_with_baseline_agents():
    result = evaluate_agent(
        CallAgent(),
        RandomAgent(random.Random(3)),
        n_hands=5,
        rng=random.Random(7),
        starting_stack=200,
    )

    assert result.hands == 5
    assert result.wins + result.losses + result.ties == 5
    assert result.total_invested == sum(result.per_hand_invested)
    assert result.roi == calculate_roi(result.total_profit, result.total_invested)
    assert result.avg_decision_ms >= 0.0
