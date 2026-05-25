# Reporte del backend del notebook

Este reporte describe la ruta ligera de revisión del notebook: el notebook de presentación ahora apunta al backend importable `poker_ai` en lugar de exigir que los revisores inspeccionen lógica duplicada del simulador, agentes o evaluación dentro del notebook.

## Ruta rápida

1. Crear o usar el entorno local con `uv`:

   ```bash
   uv sync --extra dev
   ```

2. Ejecutar la suite de pruebas de módulos:

   ```bash
   uv run pytest
   ```

3. Ejecutar el notebook modular reducido cuando se necesite validar el reporte:

   ```bash
   uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output poker_ia_comparativa_final.executed.ipynb
   ```

   O ejecutar una corrida académica reproducible desde Python:

   ```bash
   POKER_REPORT_HANDS=200 POKER_REPORT_SEEDS=42,43,44,45,46 uv run python - <<'PY'
   from poker_ai.evaluation import config_from_env, run_report_experiment
   config = config_from_env()
   for row in sorted(run_report_experiment(config), key=lambda r: (r.roi, r.avg_profit), reverse=True):
       print(row)
   PY
   ```

## Rol del notebook

| Área | Fuente de verdad |
|------|-----------------|
| Estado del juego, acciones legales, ciclo de apuestas y simulación de manos | `src/poker_ai/engine/` |
| Interfaz de agentes y scaffolds importables por modelo | `src/poker_ai/agents/` |
| ROI, agregación de evaluación y ayudas de entrenamiento TD | `src/poker_ai/evaluation/` |
| Narrativa, tabla compacta del reporte y corrida reducida de humo | `poker_ia_comparativa_final.ipynb` |

El notebook intencionalmente no contiene definiciones copiadas del motor, agentes, evaluación ni ROI. `tests/test_notebook_contract.py` hace cumplir ese contrato de revisión.

## Guía de ejecución reproducible

- Mantener `POKER_REPORT_HANDS` bajo (`5`–`20`) y una sola semilla para verificaciones rápidas.
- Usar valores mayores y varias semillas para corridas académicas finales, porque la evaluación de modelos puede tardar más.
- Reportar siempre `POKER_REPORT_HANDS`, `POKER_REPORT_SEEDS`, oponente baseline y criterio de ranking.
- Por defecto `POKER_REPORT_FRESH_TD=1` entrena un snapshot TD fresco en memoria para evitar métricas stale de `artifacts/td_qtable.json`; usar `POKER_REPORT_FRESH_TD=0` solo para comparar un artefacto guardado explícitamente.
- El reporte muestra dos variantes de ensemble: `EnsembleNoTD` (`Minimax`/`Bayesian`/`Markov`, pesos `0.5/0.3/0.2`) y `EnsembleWithTD` (`Minimax`/`Bayesian`/`Markov`/`TD`, pesos `0.45/0.27/0.18/0.10`).
- Ejecutar `uv sync --extra dev` antes de correr el notebook completo para tener JupyterLab, nbconvert y el backend editable disponibles localmente.

## Señal preflop TD y comparación de ensembles

`TDLearning` ahora agrega al estado un bucket preflop (`premium`, `strong`, `playable`, `weak`) calculado únicamente desde las dos cartas privadas visibles del jugador que actúa. Es leakage-safe porque no acepta ni consulta cartas comunitarias, cartas del oponente, historial futuro ni resultado de la mano.

El entrenamiento también separa tres flujos determinísticos de azar desde una semilla maestra: mazo, exploración TD y oponente. Así, una variación en decisiones exploratorias no cambia implícitamente el orden del mazo ni las acciones del rival.

La mejora de TD se reporta con `td_meets_gate`: el snapshot fresco debe lograr ROI `> -1.0` contra `Random` y `Call` con semillas fijas `(101, 202, 303)` y 40 manos por semilla. En vez de reemplazar el baseline, el reporte compara `EnsembleNoTD` contra `EnsembleWithTD` como filas separadas, con composición y pesos explícitos para evitar colisiones de etiqueta.

## Conclusiones según resultados observados

Estas conclusiones se basan en `uv run pytest` y en la corrida de verificación de este cambio: `POKER_REPORT_HANDS=2`, `POKER_REPORT_SEEDS=42`, `POKER_REPORT_FRESH_TD=1`, baseline `Call` y ranking por ROI con desempate por ganancia promedio.

| Ranking | Agente | Tasa de victoria | Ganancia total | Inversión total | ROI | Ganancia promedio |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `Minimax` | 1.000 | 20 | 20 | 1.000 | 10.000 |
| 2 | `Bayesian` | 1.000 | 20 | 20 | 1.000 | 10.000 |
| 3 | `TDLearning (fresh)` | 0.500 | 0 | 20 | 0.000 | 0.000 |
| 4 | `EnsembleWithTD (fresh)` | 0.500 | 0 | 20 | 0.000 | 0.000 |
| 5 | `Markov` | 0.000 | -20 | 20 | -1.000 | -10.000 |
| 6 | `EnsembleNoTD` | 0.000 | -20 | 20 | -1.000 | -10.000 |
| 7 | `Random` | 0.000 | -25 | 25 | -1.000 | -12.500 |

- `Minimax` y `Bayesian` empataron como mejores estrategias individuales en esta corrida corta.
- `EnsembleWithTD (fresh)` superó a `EnsembleNoTD` en esta muestra mínima, pero la recomendación prudente sigue siendo tratar `EnsembleNoTD` como baseline principal hasta validar TD con más manos, más semillas y otros oponentes.
- `Random` quedó negativo y `TDLearning (fresh)` empató en ROI cero frente a `Call`; TD requiere más evidencia antes de defenderlo como estrategia competitiva.
- La conclusión sigue siendo prudente: 2 manos por agente solo prueban el contrato de reporte; no alcanzan para afirmar significancia estadística ni generalización contra otros estilos de oponente.
