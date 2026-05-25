from poker_ai.engine import Action, play_hand


def test_re_raise_chain_updates_pot_and_history(scripted_agent, rng):
    agent0 = scripted_agent([(Action.RAISE, 20), (Action.RAISE, 60), (Action.CALL, None)])
    agent1 = scripted_agent([(Action.RAISE, 40), (Action.CALL, None)])

    result = play_hand(agent0, agent1, rng, starting_stack=200)

    assert result.invested == [60, 60]
    assert [entry["action"] for entry in result.history[:4]] == ["raise", "raise", "raise", "call"]
    assert result.profit[0] + result.profit[1] == 0


def test_action_history_is_visible_to_next_agent(scripted_agent, rng):
    raiser = scripted_agent([(Action.RAISE, 20), (Action.CALL, None)])
    observer = scripted_agent([(Action.CALL, None)])

    play_hand(raiser, observer, rng, starting_stack=200)

    assert observer.seen_histories[0][-1]["action"] == "raise"
    assert observer.seen_histories[0][-1]["player"] == 0


def test_fold_ends_hand_with_accounting(scripted_agent, rng):
    folder = scripted_agent([(Action.FOLD, None)])
    caller = scripted_agent([])

    result = play_hand(folder, caller, rng, starting_stack=200)

    assert result.winner == 1
    assert result.invested == [5, 10]
    assert result.profit == [-5, 5]
