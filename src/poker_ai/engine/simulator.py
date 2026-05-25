"""Heads-up hand simulator with bounded re-raise support."""

from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Any, Protocol

from .rules import deal_cards, evaluate_high_card, legal_actions, normalize_action
from .state import BIG_BLIND, SMALL_BLIND, STARTING_STACK, Action, GameState, HandResult, Phase


class Agent(Protocol):
    def act(self, state: GameState) -> tuple[Action | str, int | None]: ...


def play_hand(
    agent0: Agent,
    agent1: Agent,
    rng: random.Random | None = None,
    *,
    starting_stack: int = STARTING_STACK,
    max_raises_per_street: int = 4,
) -> HandResult:
    """Play one compact heads-up hand and return accounting details."""

    rng = rng or random.Random()
    state = GameState(
        player_id=0,
        stacks=[starting_stack, starting_stack],
        max_raises_per_street=max_raises_per_street,
    )
    state.hole_cards, state.community_cards = deal_cards(rng)
    _post_blind(state, 0, SMALL_BLIND)
    _post_blind(state, 1, BIG_BLIND)
    state.current_bet = BIG_BLIND

    folded = _betting_round(state, [agent0, agent1], first_to_act=0)
    winner = folded if folded is not None else _showdown_winner(state)
    payouts = [-state.invested[0], -state.invested[1]]
    if winner is None:
        payouts[0] += state.pot // 2
        payouts[1] += state.pot - state.pot // 2
    else:
        payouts[winner] += state.pot
    return HandResult(winner=winner, profit=payouts, invested=state.invested.copy(), history=list(state.action_history))


def _betting_round(state: GameState, agents: Sequence[Agent], first_to_act: int) -> int | None:
    player = first_to_act
    last_aggressor = 1 - first_to_act
    acted_since_aggression: set[int] = set()
    while True:
        view = state.for_player(player)
        raw_action = _ask_agent(agents[player], view)
        action, chips = normalize_action(view, raw_action[0], raw_action[1])
        if action is Action.FOLD:
            _record(state, player, action, chips)
            return 1 - player
        _apply_chips(state, player, chips)
        if action in {Action.BET, Action.RAISE}:
            state.current_bet = state.contributions[player]
            state.raises_this_street += 1
            last_aggressor = player
            acted_since_aggression = {player}
        else:
            acted_since_aggression.add(player)
        _record(state, player, action, chips)
        other = 1 - player
        if other == last_aggressor and all(_matched_or_all_in(state, p) for p in (0, 1)):
            return None
        if len(acted_since_aggression) == 2 and all(_matched_or_all_in(state, p) for p in (0, 1)):
            return None
        player = other


def _ask_agent(agent: Agent, state: GameState) -> tuple[Action | str, int | None]:
    chooser = getattr(agent, "act", None) or getattr(agent, "choose_action")
    chosen = chooser(state)
    if isinstance(chosen, tuple):
        return chosen
    return chosen, None


def _post_blind(state: GameState, player: int, amount: int) -> None:
    _apply_chips(state, player, min(amount, state.stacks[player]))


def _apply_chips(state: GameState, player: int, chips: int) -> None:
    state.stacks[player] -= chips
    state.contributions[player] += chips
    state.invested[player] += chips
    state.pot += chips


def _record(state: GameState, player: int, action: Action, amount: int) -> None:
    state.action_history.append(
        {
            "player": player,
            "phase": state.phase.value,
            "action": action.value,
            "amount": amount,
            "pot": state.pot,
            "to_call_next": max(0, state.current_bet - state.contributions[1 - player]),
        }
    )


def _matched_or_all_in(state: GameState, player: int) -> bool:
    return state.contributions[player] == state.current_bet or state.stacks[player] == 0


def _showdown_winner(state: GameState) -> int | None:
    state.phase = Phase.SHOWDOWN
    scores = [evaluate_high_card(hand + state.community_cards) for hand in state.hole_cards]
    if scores[0] == scores[1]:
        return None
    return 0 if scores[0] > scores[1] else 1
