import random

from poker_ai.agents import CallAgent, RandomAgent
from poker_ai.engine import Action, GameState, legal_actions, play_hand


def test_call_agent_prefers_call_then_check():
    call_state = GameState(player_id=0, stacks=[100, 100], current_bet=10, contributions=[5, 10])
    check_state = GameState(player_id=0, stacks=[100, 100])

    assert CallAgent().act(call_state) == (Action.CALL, None)
    assert CallAgent().act(check_state) == (Action.CHECK, None)


def test_random_agent_is_deterministic_with_seed():
    state = GameState(player_id=0, stacks=[100, 100])
    first = RandomAgent(random.Random(4)).act(state)
    second = RandomAgent(random.Random(4)).act(state)

    assert first == second
    assert first[0] in legal_actions(state)


def test_baseline_agents_integrate_with_engine(rng):
    result = play_hand(CallAgent(), RandomAgent(random.Random(3)), rng, starting_stack=200)

    assert result.profit[0] + result.profit[1] == 0
    assert result.history
