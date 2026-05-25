"""Temporal-difference agent with a small persistent Q-table."""

from __future__ import annotations

import random
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from poker_ai.engine import Action, GameState


from .base import BaseAgent, ordered_legal_actions
from .preflop import PreflopBucket, preflop_bucket


QTABLE_SCHEMA_VERSION = 2
TD_ACTION_PREFERENCE = [Action.CHECK, Action.CALL, Action.BET, Action.RAISE, Action.FOLD]
StateKey = tuple[str, int, int, PreflopBucket | None]


class TDAgent(BaseAgent):
    """Small Q-table-backed agent with the standard act/reward interface."""

    def __init__(
        self,
        epsilon: float = 0.0,
        alpha: float = 0.1,
        rng: random.Random | None = None,
        q_values: dict[tuple, dict[Action, float]] | None = None,
    ):
        super().__init__(name="TDLearning")
        self.epsilon = epsilon
        self.alpha = alpha
        self.rng = rng or random.Random()
        self.q_values: defaultdict[StateKey, dict[Action, float]] = defaultdict(dict)
        if q_values:
            for state_key, action_values in q_values.items():
                self.q_values[self._normalize_state_key(state_key)] = {
                    Action(action): float(value) for action, value in action_values.items()
                }
        self._episode_trace: list[tuple[StateKey, Action]] = []

    def choose_action(self, state: GameState) -> Action:
        legal = ordered_legal_actions(state)
        if self.epsilon > 0 and self.rng.random() < self.epsilon:
            action = self.rng.choice(legal)
            self._record_trace(state, action)
            return action
        key = self._state_key(state)
        scores = self.q_values[key]
        best_score = max(scores.get(action, 0.0) for action in legal)
        preferred_legal = [action for action in TD_ACTION_PREFERENCE if action in legal]
        action = next(action for action in preferred_legal if scores.get(action, 0.0) == best_score)
        self._episode_trace.append((key, action))
        return action

    def update(self, state: GameState, action: Action, reward: float) -> None:
        key = self._state_key(state)
        self._update_q_value(key, action, reward)

    def observe_reward(self, reward: float, state: GameState | None = None) -> None:
        """Apply a terminal reward update to every action observed in the hand."""

        super().observe_reward(reward, state)
        for key, action in self._episode_trace:
            self._update_q_value(key, action, reward)
        self._episode_trace.clear()

    def save(
        self,
        path: str | Path,
        *,
        episodes: int | None = None,
        seed: int | None = None,
    ) -> None:
        """Persist the Q-table as deterministic JSON."""

        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "version": QTABLE_SCHEMA_VERSION,
            "alpha": self.alpha,
            "episodes": episodes,
            "seed": seed,
            "q_values": {
                self._serialize_state_key(key): {action.value: value for action, value in sorted(actions.items())}
                for key, actions in sorted(self.q_values.items(), key=lambda item: self._serialize_state_key(item[0]))
                if actions
            },
        }
        target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path, **kwargs) -> "TDAgent":
        """Load a saved Q-table snapshot."""

        source = Path(path)
        payload = json.loads(source.read_text(encoding="utf-8"))
        version = payload.get("version", 1)
        if version not in {1, QTABLE_SCHEMA_VERSION}:
            raise ValueError(f"Unsupported TD Q-table schema version: {payload.get('version')!r}")
        alpha = kwargs.pop("alpha", float(payload.get("alpha", 0.1)))
        q_values = {
            cls._deserialize_state_key(state_key): {Action(action): float(value) for action, value in actions.items()}
            for state_key, actions in payload.get("q_values", {}).items()
        }
        return cls(alpha=alpha, q_values=q_values, **kwargs)

    def _state_key(self, state: GameState) -> StateKey:
        bucket: PreflopBucket | None = None
        if state.phase.value == "preflop":
            hole_cards = state.hole_cards[state.player_id] if state.hole_cards else []
            if len(hole_cards) == 2:
                bucket = preflop_bucket(hole_cards)
        return (state.phase.value, min(state.to_call, 100), len(state.action_history), bucket)

    def _record_trace(self, state: GameState, action: Action) -> None:
        self._episode_trace.append((self._state_key(state), action))

    def _update_q_value(self, key: StateKey, action: Action, reward: float) -> None:
        current = self.q_values[key].get(action, 0.0)
        self.q_values[key][action] = current + self.alpha * (float(reward) - current)

    @staticmethod
    def _serialize_state_key(key: tuple) -> str:
        phase, to_call, history_len, bucket = TDAgent._normalize_state_key(key)
        if bucket is None:
            return f"{phase}|{to_call}|{history_len}"
        return f"{phase}|{to_call}|{history_len}|{bucket}"

    @staticmethod
    def _deserialize_state_key(value: str) -> StateKey:
        parts = value.split("|")
        if len(parts) == 3:
            phase, to_call, history_len = parts
            return phase, int(to_call), int(history_len), None
        if len(parts) == 4:
            phase, to_call, history_len, bucket = parts
            return phase, int(to_call), int(history_len), bucket or None
        raise ValueError(f"Invalid TD state key: {value!r}")

    @staticmethod
    def _normalize_state_key(key: tuple) -> StateKey:
        if len(key) == 3:
            phase, to_call, history_len = key
            return phase, int(to_call), int(history_len), None
        if len(key) == 4:
            phase, to_call, history_len, bucket = key
            return phase, int(to_call), int(history_len), bucket
        raise ValueError(f"Invalid TD state key: {key!r}")
