"""Reproducible report experiments for the presentation notebook."""

from __future__ import annotations

import os
import random
import warnings
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from poker_ai.agents import (
    BayesianAgent,
    CallAgent,
    MarkovAgent,
    MinimaxAgent,
    RandomAgent,
    TDAgent,
    build_ensemble_no_td,
    build_ensemble_with_td,
)

from .metrics import EvaluationResult, calculate_roi, evaluate_agent
from .training import DEFAULT_TD_ALPHA, DEFAULT_TD_QTABLE_PATH, DEFAULT_TD_TRAIN_HANDS, DEFAULT_TD_TRAIN_SEED, train_td_agent


DEFAULT_REPORT_HANDS = 5
DEFAULT_REPORT_SEEDS = (42,)
TD_QTABLE_ENV_VAR = "POKER_TD_QTABLE_PATH"
TD_FRESH_ENV_VAR = "POKER_REPORT_FRESH_TD"
TD_GATE_SEEDS = (101, 202, 303)
TD_GATE_HANDS = 40
TD_GATE_MIN_ROI = -1.0


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Configuration for repeatable report experiments."""

    hands_per_seed: int = DEFAULT_REPORT_HANDS
    seeds: tuple[int, ...] = DEFAULT_REPORT_SEEDS
    starting_stack: int = 1_000
    max_raises_per_street: int = 4

    @property
    def total_hands_per_agent(self) -> int:
        return self.hands_per_seed * len(self.seeds)


@dataclass(frozen=True, slots=True)
class ReportRow:
    """Aggregated report row for one agent across all configured seeds."""

    agent_name: str
    opponent_name: str
    seeds: int
    hands_per_seed: int
    total_hands: int
    wins: int
    losses: int
    ties: int
    win_rate: float
    total_profit: int
    total_invested: int
    roi: float
    avg_profit: float
    avg_decision_ms: float
    composition: tuple[str, ...] = ()
    weights: tuple[float, ...] = ()
    td_meets_gate: bool | None = None

    def as_dict(self) -> dict[str, int | float | bool | None | str | tuple[str, ...] | tuple[float, ...]]:
        return {
            "agent_name": self.agent_name,
            "opponent_name": self.opponent_name,
            "seeds": self.seeds,
            "hands_per_seed": self.hands_per_seed,
            "total_hands": self.total_hands,
            "wins": self.wins,
            "losses": self.losses,
            "ties": self.ties,
            "win_rate": self.win_rate,
            "total_profit": self.total_profit,
            "total_invested": self.total_invested,
            "roi": self.roi,
            "avg_profit": self.avg_profit,
            "avg_decision_ms": self.avg_decision_ms,
            "composition": self.composition,
            "weights": self.weights,
            "td_meets_gate": self.td_meets_gate,
        }


def parse_seed_list(value: str | None) -> tuple[int, ...]:
    """Parse comma-separated integer seeds, falling back to the smoke seed."""

    if value is None or not value.strip():
        return DEFAULT_REPORT_SEEDS
    seeds = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not seeds:
        raise ValueError("At least one seed is required.")
    return seeds


def config_from_env(env: Mapping[str, str] | None = None) -> ExperimentConfig:
    """Build report config from environment variables with CI-safe defaults."""

    source = env or os.environ
    hands = int(source.get("POKER_REPORT_HANDS", DEFAULT_REPORT_HANDS))
    if hands <= 0:
        raise ValueError("POKER_REPORT_HANDS must be positive.")
    return ExperimentConfig(
        hands_per_seed=hands,
        seeds=parse_seed_list(source.get("POKER_REPORT_SEEDS")),
    )


def run_report_experiment(config: ExperimentConfig) -> list[ReportRow]:
    """Evaluate all report agents against the passive Call baseline."""

    grouped: dict[str, list[EvaluationResult]] = defaultdict(list)
    metadata: dict[str, tuple[tuple[str, ...], tuple[float, ...]]] = {}
    for seed in config.seeds:
        agents = _build_report_agents(seed)
        if not metadata:
            metadata = _report_agent_metadata_from_agents(agents)
        for index, agent in enumerate(agents):
            result = evaluate_agent(
                agent,
                CallAgent(),
                n_hands=config.hands_per_seed,
                rng=random.Random(seed + index * 10_000),
                starting_stack=config.starting_stack,
                max_raises_per_street=config.max_raises_per_street,
            )
            grouped[result.agent_name].append(result)
    td_gate = evaluate_td_metric_gate() if _fresh_td_enabled() else None
    return [
        _aggregate_results(
            results,
            config,
            metadata.get(results[0].agent_name),
            td_meets_gate=td_gate if results[0].agent_name.startswith("TDLearning") else None,
        )
        for results in grouped.values()
    ]


def _build_report_agents(seed: int):
    td_agent = _load_report_td_agent(seed)
    td_status = _td_status_suffix(td_agent)
    ensemble_with_td = build_ensemble_with_td(td_agent, seed)
    ensemble_with_td.name = f"EnsembleWithTD{td_status}"
    return [
        RandomAgent(random.Random(seed)),
        MinimaxAgent(),
        BayesianAgent(),
        MarkovAgent(),
        td_agent,
        build_ensemble_no_td(seed),
        ensemble_with_td,
    ]


def _td_status_suffix(td_agent: TDAgent) -> str:
    if "fresh" in td_agent.name:
        return " (fresh)"
    if "untrained" in td_agent.name:
        return " (untrained)"
    return ""


def _load_report_td_agent(seed: int) -> TDAgent:
    if _fresh_td_enabled():
        agent = train_td_agent(n_hands=DEFAULT_TD_TRAIN_HANDS, master_seed=DEFAULT_TD_TRAIN_SEED + seed)
        agent.name = "TDLearning (fresh)"
        return agent
    path = _td_qtable_path()
    if path.exists():
        return TDAgent.load(path, rng=random.Random(seed))
    warnings.warn(
        f"TD Q-table snapshot not found at {path}; evaluating untrained TDLearning fallback.",
        RuntimeWarning,
        stacklevel=2,
    )
    agent = TDAgent(rng=random.Random(seed))
    agent.name = "TDLearning (untrained)"
    return agent


def _td_qtable_path() -> Path:
    return Path(os.environ.get(TD_QTABLE_ENV_VAR, DEFAULT_TD_QTABLE_PATH))


def _fresh_td_enabled() -> bool:
    return os.environ.get(TD_FRESH_ENV_VAR, "1").strip().lower() not in {"0", "false", "no", "off"}


def evaluate_td_metric_gate(
    *,
    seeds: tuple[int, ...] = TD_GATE_SEEDS,
    hands_per_seed: int = TD_GATE_HANDS,
    min_roi: float = TD_GATE_MIN_ROI,
) -> bool:
    """Verify fresh TD ROI against Random and Call on fixed seeds."""

    if hands_per_seed <= 0:
        raise ValueError("hands_per_seed must be positive.")
    call_roi = _td_gate_roi("call", seeds=seeds, hands_per_seed=hands_per_seed)
    random_roi = _td_gate_roi("random", seeds=seeds, hands_per_seed=hands_per_seed)
    return call_roi > min_roi and random_roi > min_roi


def _td_gate_roi(opponent_name: str, *, seeds: tuple[int, ...], hands_per_seed: int) -> float:
    total_profit = 0
    total_invested = 0
    for seed in seeds:
        td_agent = train_td_agent(n_hands=DEFAULT_TD_TRAIN_HANDS, master_seed=DEFAULT_TD_TRAIN_SEED + seed)
        opponent = CallAgent() if opponent_name == "call" else RandomAgent(random.Random(seed + 90_000))
        result = evaluate_agent(td_agent, opponent, n_hands=hands_per_seed, rng=random.Random(seed + 70_000))
        total_profit += result.total_profit
        total_invested += result.total_invested
    return calculate_roi(total_profit, total_invested)


def _aggregate_results(
    results: list[EvaluationResult],
    config: ExperimentConfig,
    metadata: tuple[tuple[str, ...], tuple[float, ...]] | None = None,
    td_meets_gate: bool | None = None,
) -> ReportRow:
    first = results[0]
    composition, weights = metadata or ((), ())
    total_hands = sum(result.hands for result in results)
    total_profit = sum(result.total_profit for result in results)
    total_invested = sum(result.total_invested for result in results)
    wins = sum(result.wins for result in results)
    losses = sum(result.losses for result in results)
    ties = sum(result.ties for result in results)
    return ReportRow(
        agent_name=first.agent_name,
        opponent_name=first.opponent_name,
        seeds=len(config.seeds),
        hands_per_seed=config.hands_per_seed,
        total_hands=total_hands,
        wins=wins,
        losses=losses,
        ties=ties,
        win_rate=wins / total_hands if total_hands else 0.0,
        total_profit=total_profit,
        total_invested=total_invested,
        roi=calculate_roi(total_profit, total_invested),
        avg_profit=total_profit / total_hands if total_hands else 0.0,
        avg_decision_ms=sum(result.avg_decision_ms for result in results) / len(results),
        composition=composition,
        weights=weights,
        td_meets_gate=td_meets_gate,
    )


def _report_agent_metadata_from_agents(agents: list[object]) -> dict[str, tuple[tuple[str, ...], tuple[float, ...]]]:
    metadata: dict[str, tuple[tuple[str, ...], tuple[float, ...]]] = {}
    for agent in agents:
        if not hasattr(agent, "agents") or not hasattr(agent, "weights"):
            continue
        composition = tuple(agent.agents.keys())
        weights = tuple(float(agent.weights[name]) for name in composition)
        metadata[agent.name] = (composition, weights)
    return metadata


def render_spanish_conclusions(rows: list[ReportRow]) -> str:
    """Render data-bound Spanish conclusions for the report and notebook."""

    if not rows:
        return "No hay resultados disponibles para generar conclusiones."

    ranked = sorted(rows, key=lambda row: (row.roi, row.avg_profit), reverse=True)
    best = ranked[0]
    no_td_ensemble = next((row for row in rows if row.agent_name == "EnsembleNoTD"), None)
    with_td_ensemble = next((row for row in rows if row.agent_name.startswith("EnsembleWithTD")), None)
    lines = [
        "## Conclusiones según los resultados observados",
        "",
        (
            f"La evaluación usó {best.seeds} semilla(s) y {best.hands_per_seed} mano(s) por semilla "
            "contra el baseline pasivo Call, con ROI corregido sobre la inversión real agregada."
        ),
        (
            f"El mejor resultado por ROI fue {best.agent_name}: ROI {best.roi:.6f}, "
            f"win rate {best.win_rate:.3f} y ganancia promedio {best.avg_profit:.3f} fichas por mano."
        ),
    ]
    if no_td_ensemble is not None:
        composition = ", ".join(no_td_ensemble.composition)
        weights = ", ".join(
            f"{name}={weight:.6g}" for name, weight in zip(no_td_ensemble.composition, no_td_ensemble.weights)
        )
        lines.append(
            f"EnsembleNoTD usa {composition} con pesos {weights}; obtuvo ROI "
            f"{no_td_ensemble.roi:.6f}, win rate {no_td_ensemble.win_rate:.3f} y ganancia promedio "
            f"{no_td_ensemble.avg_profit:.3f}."
        )
    if with_td_ensemble is not None:
        composition = ", ".join(with_td_ensemble.composition)
        weights = ", ".join(
            f"{name}={weight:.6g}" for name, weight in zip(with_td_ensemble.composition, with_td_ensemble.weights)
        )
        lines.append(
            f"{with_td_ensemble.agent_name} usa {composition} con pesos {weights}; obtuvo ROI "
            f"{with_td_ensemble.roi:.6f}, win rate {with_td_ensemble.win_rate:.3f} y ganancia promedio "
            f"{with_td_ensemble.avg_profit:.3f}."
        )
    if no_td_ensemble is not None and with_td_ensemble is not None:
        delta_roi = no_td_ensemble.roi - with_td_ensemble.roi
        if delta_roi >= 0:
            lines.append(
                "Recomendación: mantener EnsembleNoTD como baseline principal para la presentación; "
                f"en esta corrida supera a la variante con TD por ΔROI={delta_roi:.6f} y evita que una señal TD todavía inestable arrastre la votación."
            )
        else:
            lines.append(
                "Recomendación: aunque EnsembleWithTD supera puntualmente al baseline no-TD "
                f"por ΔROI={abs(delta_roi):.6f}, mantener EnsembleNoTD como baseline principal prudente hasta validar TD con más manos, más semillas y otros oponentes."
            )
    td_row = next((row for row in rows if row.agent_name.startswith("TDLearning")), None)
    if td_row is not None:
        if td_row.td_meets_gate is None:
            gate_note = "td_meets_gate=None: la compuerta TD no se calculó porque se desactivó el snapshot fresco."
        else:
            gate_note = f"td_meets_gate={td_row.td_meets_gate}: ROI > {TD_GATE_MIN_ROI} contra Random y Call con semillas {TD_GATE_SEEDS}."
        snapshot_note = "snapshot fresco en memoria" if "fresh" in td_row.agent_name else f"snapshot `{_td_qtable_path()}`"
        fallback_note = "; fallback no entrenado" if "untrained" in td_row.agent_name else ""
        lines.append(
            f"TDLearning se evalúa con {snapshot_note}{fallback_note}. "
            f"Parámetros de entrenamiento documentados: α={DEFAULT_TD_ALPHA}, "
            f"episodios={DEFAULT_TD_TRAIN_HANDS}, semilla={DEFAULT_TD_TRAIN_SEED}. "
            "Ahora su estado preflop incluye un bucket privado y leakage-safe, y el entrenamiento separa RNG de mazo, exploración y oponente. "
            f"{gate_note} La comparación con TD se reporta como EnsembleWithTD, pero no reemplaza el baseline no-TD."
        )
    lines.append(
        "Caveat: la calibración se hizo con una grilla pequeña y semillas fijas frente a Call, "
        "Random y Markov; además, el simulador simplificado expone una sola recompensa terminal por mano. "
        "Estos resultados son reproducibles, pero no reemplazan una validación estadística con más manos, "
        "más oponentes e intervalos de confianza."
    )
    return "\n".join(lines)
