"""Shared state objects for the poker engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

SMALL_BLIND = 5
BIG_BLIND = 10
STARTING_STACK = 1_000


class Phase(StrEnum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class Action(StrEnum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"


@dataclass(slots=True)
class GameState:
    """Mutable heads-up hand state observed by agents."""

    player_id: int
    stacks: list[int]
    pot: int = 0
    current_bet: int = 0
    contributions: list[int] = field(default_factory=lambda: [0, 0])
    invested: list[int] = field(default_factory=lambda: [0, 0])
    phase: Phase = Phase.PREFLOP
    hole_cards: list[list[str]] = field(default_factory=lambda: [[], []])
    community_cards: list[str] = field(default_factory=list)
    action_history: list[dict[str, Any]] = field(default_factory=list)
    raises_this_street: int = 0
    max_raises_per_street: int = 4
    min_raise: int = BIG_BLIND

    @property
    def to_call(self) -> int:
        return max(0, self.current_bet - self.contributions[self.player_id])

    def for_player(self, player_id: int) -> "GameState":
        """Return a shallow view with the same shared history list."""

        return GameState(
            player_id=player_id,
            stacks=self.stacks,
            pot=self.pot,
            current_bet=self.current_bet,
            contributions=self.contributions,
            invested=self.invested,
            phase=self.phase,
            hole_cards=self.hole_cards,
            community_cards=self.community_cards,
            action_history=self.action_history,
            raises_this_street=self.raises_this_street,
            max_raises_per_street=self.max_raises_per_street,
            min_raise=self.min_raise,
        )


@dataclass(frozen=True, slots=True)
class HandResult:
    winner: int | None
    profit: list[int]
    invested: list[int]
    history: list[dict[str, Any]]
