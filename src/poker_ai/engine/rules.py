"""Legal-action and lightweight card helpers."""

from __future__ import annotations

import random

from .state import Action, GameState

RANKS = "23456789TJQKA"
SUITS = "cdhs"


def build_deck() -> list[str]:
    return [rank + suit for rank in RANKS for suit in SUITS]


def deal_cards(rng: random.Random) -> tuple[list[list[str]], list[str]]:
    deck = build_deck()
    rng.shuffle(deck)
    return [deck[:2], deck[2:4]], deck[4:9]


def evaluate_high_card(cards: list[str]) -> tuple[int, list[int]]:
    """Small deterministic wrapper until full treys scoring is wired."""

    values = sorted((RANKS.index(card[0]) for card in cards), reverse=True)
    return (values[0], values[:5])


def legal_actions(state: GameState) -> set[Action]:
    """Return legal actions for the current player view."""

    actions: set[Action] = {Action.FOLD}
    stack = state.stacks[state.player_id]
    if state.to_call == 0:
        actions.add(Action.CHECK)
        if stack > 0 and state.raises_this_street < state.max_raises_per_street:
            actions.add(Action.BET)
    else:
        if stack >= state.to_call:
            actions.add(Action.CALL)
        if _can_raise(state):
            actions.add(Action.RAISE)
    return actions


def normalize_action(state: GameState, action: Action | str, amount: int | None) -> tuple[Action, int]:
    normalized = Action(action)
    if normalized not in legal_actions(state):
        raise ValueError(f"Illegal action {normalized.value} for player {state.player_id}")
    if normalized in {Action.FOLD, Action.CHECK}:
        return normalized, 0
    if normalized is Action.CALL:
        return normalized, min(state.to_call, state.stacks[state.player_id])
    minimum_total = state.current_bet + state.min_raise
    target_total = amount if amount is not None else minimum_total
    if target_total < minimum_total:
        raise ValueError("Raise amount does not meet minimum raise")
    if target_total > state.contributions[state.player_id] + state.stacks[state.player_id]:
        raise ValueError("Action exceeds available stack")
    return normalized, target_total - state.contributions[state.player_id]


def _can_raise(state: GameState) -> bool:
    stack_after_call = state.stacks[state.player_id] - state.to_call
    return state.raises_this_street < state.max_raises_per_street and stack_after_call >= state.min_raise
