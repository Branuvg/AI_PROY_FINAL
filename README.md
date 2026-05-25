# PokerAI — Comparativa final de modelos de IA para Texas Hold'em

Proyecto final de inteligencia artificial para comparar modelos de decisión en una versión simplificada de póker Texas Hold'em. El sistema evalúa modelos individuales y modelos combinados bajo el mismo motor de simulación, usando métricas reproducibles como tasa de victoria, ganancia promedio y ROI sobre fichas realmente invertidas.

## Resultado del proyecto

El proyecto entrega un backend modular en Python, un notebook de presentación y una suite de pruebas automatizadas. La lógica central ya no vive duplicada en el notebook: está organizada en módulos importables dentro de `src/poker_ai`.

| Componente | Estado |
|---|---|
| Motor de juego simplificado | Implementado |
| Agentes individuales | Implementados |
| Ensembles comparativos | Implementados |
| TD Learning con Q-table persistente | Implementado |
| Notebook de reporte | Implementado |
| Pruebas automatizadas | Implementadas |
| Gestión de entorno con `uv` | Implementada |

## Modelos comparados

| Modelo | Descripción |
|---|---|
| `Minimax` | Evalúa decisiones mediante búsqueda estratégica simplificada. |
| `Bayesian` | Usa reglas probabilísticas explicables para decidir acciones. |
| `Markov` | Decide usando una política basada en estados y transiciones. |
| `TDLearning` | Aprende una política mediante Q-learning y persistencia de Q-table. |
| `EnsembleNoTD` | Combina Minimax, Bayesian y Markov. |
| `EnsembleWithTD` | Combina Minimax, Bayesian, Markov y TDLearning. |

## Estructura

```text
src/poker_ai/
  engine/        motor del juego, estado, reglas y simulación
  agents/        modelos individuales y ensembles
  evaluation/    métricas, reportes, entrenamiento TD y CLI

tests/           pruebas automatizadas
docs/            reporte técnico complementario
artifacts/       snapshots generados, como la Q-table de TD
openspec/        artefactos SDD del proceso de desarrollo
```

## Instalación

```bash
uv sync --extra dev
```

## Verificación

```bash
uv run pytest
```

Resultado esperado:

```text
56 passed
```

## Ejecución del proyecto

### Entrenar TD Learning

```bash
uv run python -m poker_ai.evaluation.train_td --hands 200 --seed 17 --output artifacts/td_qtable.json
```

### Ejecutar reporte por consola

```bash
uv run python -m poker_ai.evaluation.cli report
```

### Ejecutar notebook final

```bash
uv run jupyter nbconvert \
  --to notebook \
  --execute poker_ia_comparativa_final.ipynb \
  --output poker_ia_comparativa_final.executed.ipynb
```

### Abrir en JupyterLab

```bash
uv run jupyter lab
```

## Experimento final documentado

La última verificación usó TD fresco y evaluación reproducible con semillas fijas.

| Parámetro | Valor |
|---|---:|
| Manos por semilla | 40 |
| Semillas | 101, 202, 303 |
| Total por agente | 120 manos |
| Oponente base | `Call` |
| TD fresco | Sí |
| ROI | Profit / fichas realmente invertidas |

Comando equivalente:

```bash
POKER_REPORT_HANDS=40 \
POKER_REPORT_SEEDS=101,202,303 \
POKER_REPORT_FRESH_TD=1 \
uv run jupyter nbconvert \
  --to notebook \
  --execute poker_ia_comparativa_final.ipynb \
  --output resultados_finales.ipynb
```

## Resultados finales observados

| Agente | W-L-T | ROI | Ganancia promedio |
|---|---:|---:|---:|
| `EnsembleWithTD (fresh)` | 65-48-7 | 0.142 | 1.417 |
| `Markov` | 60-52-8 | 0.067 | 0.667 |
| `Bayesian` | 60-55-5 | 0.042 | 0.417 |
| `Minimax` | 58-59-3 | -0.008 | -0.083 |
| `Random` | 42-77-1 | -0.044 | -0.500 |
| `EnsembleNoTD` | 51-61-8 | -0.083 | -0.833 |
| `TDLearning (fresh)` | 23-94-3 | -0.327 | -3.000 |

## Conclusiones finales

1. **El mejor resultado observado fue `EnsembleWithTD (fresh)`**, con ROI `0.142` y ganancia promedio de `1.417` fichas por mano.
2. **El enfoque combinado fue útil**: integrar señales de varios modelos permitió superar a los modelos individuales en la corrida final documentada.
3. **TD Learning individual no fue competitivo**, pero su incorporación con peso bajo dentro del ensemble aportó diversidad suficiente para mejorar el resultado combinado.
4. **Markov fue el mejor modelo individual** en esta corrida, con ROI `0.067`.
5. **El ROI se calcula correctamente sobre fichas realmente invertidas**, no sobre una referencia artificial como `n_hands * BIG_BLIND`.

Conclusión general:

> El modelo combinado `EnsembleWithTD` obtuvo el mejor desempeño observado en el experimento final. Aunque `TDLearning` por sí solo fue débil, su señal con peso bajo ayudó al ensemble. Por eso, el resultado principal del proyecto es que una combinación controlada de Minimax, Bayesian, Markov y TD Learning puede superar a los modelos individuales bajo el entorno experimental implementado.

## Pesos de los modelos combinados

### `EnsembleNoTD`

| Modelo | Peso |
|---|---:|
| Minimax | 0.50 |
| Bayesian | 0.30 |
| Markov | 0.20 |

### `EnsembleWithTD`

| Modelo | Peso |
|---|---:|
| Minimax | 0.45 |
| Bayesian | 0.27 |
| Markov | 0.18 |
| TDLearning | 0.10 |

## Métricas usadas

| Métrica | Definición |
|---|---|
| Win rate | Proporción de manos ganadas. |
| Profit | Fichas ganadas o perdidas. |
| ROI | Profit dividido entre fichas realmente invertidas. |
| Ganancia promedio | Profit total dividido entre manos jugadas. |

## Alcance del proyecto

El proyecto usa un entorno simplificado de Texas Hold'em para comparar modelos bajo condiciones controladas. No pretende ser un bot profesional de póker real; su propósito es académico: demostrar implementación, comparación, evaluación y análisis de modelos de IA aplicados a toma de decisiones en póker.

## Notebook final

El notebook principal es:

```text
poker_ia_comparativa_final.ipynb
```

Ese notebook funciona como presentación del proyecto y consume el backend modular. Las pruebas automatizadas verifican que no vuelva a incluir lógica duplicada del motor, agentes, evaluación o ROI.
