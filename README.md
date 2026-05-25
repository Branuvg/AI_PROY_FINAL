# AI_PROY_FINAL

Proyecto comparativo de IA para Texas Hold'em con el backend reutilizable extraído en `src/poker_ai`.

## Configuración

```bash
uv sync --extra dev
```

Esto mantiene todas las dependencias de Python dentro del entorno del proyecto administrado por `uv`; no modifica la instalación global de Python.

## Pruebas

```bash
uv run pytest
```

## Entrenamiento TD reproducible

Antes, `TDLearning` podía verse peor que `Random` porque se evaluaba con una tabla Q vacía y, en empates de valor cero, podía terminar eligiendo `fold`. Ahora el agente usa un fallback legal no perdedor (`check`/`call` antes que `fold`), actualiza Q con la recompensa terminal de cada mano y persiste el snapshot en `artifacts/td_qtable.json`.

```bash
uv run python -m poker_ai.evaluation.train_td
uv run python -m poker_ai.evaluation.cli report
```

Parámetros por defecto: α=0.1, 200 manos de entrenamiento y semilla 17. El reporte carga `artifacts/td_qtable.json` o la ruta `POKER_TD_QTABLE_PATH`; si no existe, marca explícitamente `TDLearning (untrained)` para no confundir un fallback vacío con un modelo entrenado.

## Verificación del notebook

El notebook es un reporte/demo conciso que importa los módulos de `poker_ai`. No debe redefinir lógica del motor, agentes, evaluación ni ROI.

```bash
uv run jupyter nbconvert --to notebook --execute poker_ia_comparativa_final.ipynb --output poker_ia_comparativa_final.executed.ipynb
```

## Rol del notebook/reporte

- `src/poker_ai/engine/` contiene el estado del juego, acciones legales y simulación de manos.
- `src/poker_ai/agents/` contiene la interfaz estándar de agentes y los agentes por modelo.
- `src/poker_ai/evaluation/` contiene el cálculo de ROI y la agregación de evaluación.
- `poker_ia_comparativa_final.ipynb` es el notebook de presentación e incluye una ejecución reducida de humo con importaciones modulares.
- `tests/test_notebook_contract.py` protege contra lógica central duplicada y contra el denominador antiguo `n_hands * BIG_BLIND` para ROI.
- `docs/notebook_backend_report.md` documenta la ruta ligera de revisión del notebook.

## Conclusiones observadas

La corrida de humo del notebook mantiene valores pequeños por defecto. Para una conclusión académica más defendible se ejecutó una evaluación reproducible con múltiples semillas:

```bash
POKER_REPORT_HANDS=200 POKER_REPORT_SEEDS=42,43,44,45,46 uv run python - <<'PY'
from poker_ai.evaluation import config_from_env, run_report_experiment
config = config_from_env()
for row in sorted(run_report_experiment(config), key=lambda r: (r.roi, r.avg_profit), reverse=True):
    print(row)
PY
```

Parámetros: 5 semillas, 200 manos por semilla, 1,000 manos por agente, baseline `Call`, ROI calculado sobre inversión real agregada.

| Ranking | Agente | Tasa de victoria | Ganancia total | Inversión total | ROI | Ganancia promedio |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `Minimax` | 0.487 | 60 | 10000 | 0.006 | 0.060 |
| 2 | `Bayesian` | 0.485 | 40 | 10000 | 0.004 | 0.040 |
| 3 | `Markov` | 0.482 | 10 | 10000 | 0.001 | 0.010 |
| 4 | `Ensemble` | 0.345 | -1210 | 8330 | -0.145 | -1.210 |
| 5 | `Random` | 0.297 | -2510 | 11800 | -0.213 | -2.510 |
| 6 | `TDLearning` | 0.000 | -5000 | 5000 | -1.000 | -5.000 |

Interpretación profesional: en esta configuración, `Minimax`, `Bayesian` y `Markov` quedan prácticamente empatados cerca del punto de equilibrio frente a `Call`, con ventaja observada muy pequeña para `Minimax`. La recomendación defensible es presentar `Minimax` como el mejor resultado observado, pero enfatizar que la diferencia es estrecha y no prueba superioridad estadística sin más manos, más oponentes e intervalos de confianza.

Nota TD: esa tabla histórica corresponde a un TD sin snapshot entrenado. Para comparar el TD viable, primero generá el snapshot y reportá junto con los resultados la ruta usada, α, episodios, semilla y la limitación principal del simulador: la actualización recibe una sola recompensa terminal por mano.
