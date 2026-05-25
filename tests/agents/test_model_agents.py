import pytest

from poker_ai.agents import (
    DEFAULT_ENSEMBLE_WEIGHTS,
    WITH_TD_ENSEMBLE_WEIGHTS,
    BayesianAgent,
    CallAgent,
    EnsembleAgent,
    MarkovAgent,
    MinimaxAgent,
    RandomAgent,
    TDAgent,
    build_default_ensemble,
    build_ensemble_no_td,
    build_ensemble_with_td,
)
from poker_ai.engine import Action, GameState, Phase, legal_actions


@pytest.mark.parametrize("agent", [BayesianAgent(), MarkovAgent(), MinimaxAgent(), TDAgent()])
def test_model_agents_return_legal_actions(agent):
    state = GameState(
        player_id=0,
        stacks=[100, 100],
        current_bet=10,
        contributions=[5, 10],
        hole_cards=[["Ah", "Kd"], ["2c", "7d"]],
        community_cards=["3h", "8s", "Tc"],
    )

    action, amount = agent.act(state)

    assert action in legal_actions(state)
    assert amount is None or amount >= 0


def test_markov_agent_consumes_action_history():
    state = GameState(
        player_id=0,
        stacks=[100, 100],
        current_bet=20,
        contributions=[10, 20],
        action_history=[{"player": 1, "action": "raise"}],
    )
    agent = MarkovAgent()

    action, _ = agent.act(state)

    assert agent.last_tendency == "aggressive"
    assert action in {Action.CALL, Action.FOLD}


def test_bayesian_agent_imports_without_requiring_pgmpy_for_actions():
    state = GameState(player_id=0, stacks=[100, 100])
    agent = BayesianAgent()

    action, _ = agent.act(state)

    assert isinstance(agent.has_pgmpy, bool)
    assert action in legal_actions(state)


def test_ensemble_uses_weighted_legal_votes():
    state = GameState(player_id=0, stacks=[100, 100])
    ensemble = EnsembleAgent({"call": CallAgent(), "markov": MarkovAgent()}, {"call": 0.8, "markov": 0.2})

    assert ensemble.act(state) == (Action.CHECK, None)


def test_default_ensemble_uses_calibrated_strong_constituents_only():
    ensemble = build_default_ensemble(seed=42)

    assert tuple(ensemble.agents) == ("minimax", "bayesian", "markov")
    assert ensemble.weights == DEFAULT_ENSEMBLE_WEIGHTS
    assert isinstance(ensemble.agents["minimax"], MinimaxAgent)
    assert isinstance(ensemble.agents["bayesian"], BayesianAgent)
    assert isinstance(ensemble.agents["markov"], MarkovAgent)
    assert not any(isinstance(agent, (RandomAgent, CallAgent, TDAgent)) for agent in ensemble.agents.values())


def test_build_ensemble_no_td_exposes_explicit_variant_name_and_weights():
    ensemble = build_ensemble_no_td(seed=42)

    assert ensemble.name == "EnsembleNoTD"
    assert tuple(ensemble.agents) == ("minimax", "bayesian", "markov")
    assert ensemble.weights == DEFAULT_ENSEMBLE_WEIGHTS
    assert sum(ensemble.weights.values()) == pytest.approx(1.0)
    assert isinstance(ensemble.agents["minimax"], MinimaxAgent)
    assert isinstance(ensemble.agents["bayesian"], BayesianAgent)
    assert isinstance(ensemble.agents["markov"], MarkovAgent)
    assert not any(isinstance(agent, (RandomAgent, CallAgent, TDAgent)) for agent in ensemble.agents.values())


def test_build_ensemble_with_td_uses_small_td_band_and_excludes_random_call():
    td_agent = TDAgent()
    ensemble = build_ensemble_with_td(td_agent, seed=42)

    assert ensemble.name == "EnsembleWithTD"
    assert tuple(ensemble.agents) == ("minimax", "bayesian", "markov", "td")
    assert ensemble.agents["td"] is td_agent
    assert ensemble.weights == WITH_TD_ENSEMBLE_WEIGHTS
    assert ensemble.weights["td"] == pytest.approx(0.10)
    assert sum(ensemble.weights.values()) == pytest.approx(1.0)
    assert not any(isinstance(agent, (RandomAgent, CallAgent)) for agent in ensemble.agents.values())


def test_ensemble_without_explicit_agents_uses_same_calibrated_default():
    ensemble = EnsembleAgent()

    assert tuple(ensemble.agents) == ("minimax", "bayesian", "markov")
    assert ensemble.weights == DEFAULT_ENSEMBLE_WEIGHTS


def test_explicit_ensemble_constructor_still_preserves_given_agents_and_weights():
    ensemble = EnsembleAgent({"call": CallAgent(), "td": TDAgent()}, {"call": 0.75, "td": 0.25})

    assert tuple(ensemble.agents) == ("call", "td")
    assert ensemble.weights == {"call": 0.75, "td": 0.25}


def test_td_agent_unseen_state_prefers_non_fold_fallback():
    state = GameState(player_id=0, stacks=[100, 100], current_bet=10, contributions=[5, 10])
    agent = TDAgent()

    assert agent.choose_action(state) == Action.CALL


def test_td_agent_tie_break_prefers_continuing_actions_before_fold():
    state = GameState(player_id=0, stacks=[100, 100], hole_cards=[["Ah", "Ad"], ["2c", "7d"]])
    key = (state.phase.value, state.to_call, len(state.action_history), "premium")
    agent = TDAgent(q_values={key: {Action.FOLD: 0.5, Action.CHECK: 0.5, Action.BET: 0.5}})

    assert agent.choose_action(state) == Action.CHECK


def test_td_agent_observe_reward_updates_q_value_toward_terminal_reward():
    state = GameState(
        player_id=0,
        stacks=[100, 100],
        current_bet=10,
        contributions=[5, 10],
        hole_cards=[["Ah", "Ad"], ["2c", "7d"]],
    )
    agent = TDAgent(alpha=0.25)

    action = agent.choose_action(state)
    agent.observe_reward(20)

    key = (state.phase.value, state.to_call, len(state.action_history), "premium")
    assert action == Action.CALL
    assert agent.q_values[key][Action.CALL] == 5.0

    agent.choose_action(state)
    agent.observe_reward(-20)
    assert agent.q_values[key][Action.CALL] < 5.0


def test_td_preflop_state_key_includes_private_bucket_only():
    state = GameState(
        player_id=0,
        stacks=[100, 100],
        hole_cards=[["Ah", "Ad"], ["2c", "7d"]],
        community_cards=["2h", "3d", "4s"],
    )
    agent = TDAgent()

    assert agent._state_key(state) == ("preflop", 0, 0, "premium")

    state.community_cards = ["As", "Ac", "Kd"]
    assert agent._state_key(state) == ("preflop", 0, 0, "premium")


def test_td_non_preflop_state_key_uses_none_bucket():
    state = GameState(player_id=0, stacks=[100, 100], phase=Phase.FLOP, hole_cards=[["Ah", "Ad"], ["2c", "7d"]])

    assert TDAgent()._state_key(state) == ("flop", 0, 0, None)


def test_td_qtable_loader_migrates_v1_keys(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(
        '{"version": 1, "alpha": 0.2, "q_values": {"preflop|10|0": {"call": 1.5}}}',
        encoding="utf-8",
    )

    agent = TDAgent.load(path)

    assert agent.alpha == 0.2
    assert agent.q_values[("preflop", 10, 0, None)][Action.CALL] == 1.5
