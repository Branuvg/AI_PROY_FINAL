import inspect

import pytest

from poker_ai.agents.preflop import preflop_bucket


@pytest.mark.parametrize(
    ("hole_cards", "expected"),
    [
        (["Ah", "Ad"], "premium"),
        (["As", "Ks"], "premium"),
        (["Qh", "Qs"], "premium"),
        (["9c", "9d"], "strong"),
        (["Ah", "Td"], "strong"),
        (["8h", "7h"], "playable"),
        (["Tc", "8c"], "playable"),
        (["7h", "2d"], "weak"),
    ],
)
def test_preflop_bucket_boundaries(hole_cards, expected) -> None:
    assert preflop_bucket(hole_cards) == expected


def test_preflop_bucket_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        preflop_bucket(["Ah"])
    with pytest.raises(ValueError):
        preflop_bucket(["Ah", "Xd"])


def test_preflop_bucket_signature_exposes_no_leakage_inputs() -> None:
    signature = inspect.signature(preflop_bucket)

    assert tuple(signature.parameters) == ("hole_cards",)
