"""Leakage-safe preflop hand buckets for two private cards."""

from __future__ import annotations

from typing import Literal


PreflopBucket = Literal["premium", "strong", "playable", "weak"]

RANK_VALUE = {rank: index for index, rank in enumerate("23456789TJQKA", start=2)}


def preflop_bucket(hole_cards: list[str] | tuple[str, str]) -> PreflopBucket:
    """Return a coarse preflop strength bucket from exactly two hole cards.

    The function intentionally accepts only private hole cards. It does not use
    board cards, opponent cards, action history, or any future information.
    """

    if len(hole_cards) != 2:
        raise ValueError("preflop_bucket requires exactly two hole cards.")
    first, second = (_parse_card(card) for card in hole_cards)
    high = max(first[0], second[0])
    low = min(first[0], second[0])
    suited = first[1] == second[1]
    pair = high == low

    if pair and high >= RANK_VALUE["J"]:
        return "premium"
    if {high, low} == {RANK_VALUE["A"], RANK_VALUE["K"]} and suited:
        return "premium"

    if pair and high >= RANK_VALUE["8"]:
        return "strong"
    if high == RANK_VALUE["A"] and low >= RANK_VALUE["T"]:
        return "strong"
    if high == RANK_VALUE["K"] and low >= RANK_VALUE["Q"]:
        return "strong"

    connected = high - low <= 1
    one_gap = high - low == 2
    if pair:
        return "playable"
    if high == RANK_VALUE["A"] and low >= RANK_VALUE["7"]:
        return "playable"
    if high >= RANK_VALUE["T"] and low >= RANK_VALUE["9"]:
        return "playable"
    if suited and high >= RANK_VALUE["T"] and low >= RANK_VALUE["7"]:
        return "playable"
    if connected and high >= RANK_VALUE["8"]:
        return "playable"
    if suited and one_gap and high >= RANK_VALUE["9"]:
        return "playable"
    return "weak"


def _parse_card(card: str) -> tuple[int, str]:
    if len(card) != 2:
        raise ValueError(f"Invalid card: {card!r}")
    rank, suit = card[0].upper(), card[1].lower()
    if rank not in RANK_VALUE or suit not in {"c", "d", "h", "s"}:
        raise ValueError(f"Invalid card: {card!r}")
    return RANK_VALUE[rank], suit
