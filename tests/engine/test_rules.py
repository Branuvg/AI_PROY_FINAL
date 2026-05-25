from poker_ai.engine import Action, GameState, legal_actions


def test_legal_actions_allow_raise_when_minimum_chips_remain():
    state = GameState(player_id=0, stacks=[100, 100], current_bet=10, contributions=[5, 10])

    assert {Action.FOLD, Action.CALL, Action.RAISE} == legal_actions(state)


def test_legal_actions_block_raise_after_cap():
    state = GameState(
        player_id=0,
        stacks=[100, 100],
        current_bet=10,
        contributions=[5, 10],
        raises_this_street=4,
    )

    assert Action.RAISE not in legal_actions(state)
    assert Action.CALL in legal_actions(state)
