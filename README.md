# PokerAI — Comparativa de modelos de IA para Texas Hold'em

Este proyecto compara distintas estrategias de inteligencia artificial para tomar decisiones en una versión simplificada de póker Texas Hold'em. El objetivo es evaluar, bajo un mismo motor de simulación, modelos individuales y modelos combinados para determinar cuál obtiene mejor desempeño según métricas reproducibles.

## Resumen ejecutivo

El sistema implementa y compara:

| Modelo | Rol dentro del proyecto |
|---|---|
| `Minimax` | Búsqueda estratégica adversarial simplificada. |
| `Bayesian` | Decisión probabilística explicable. |
| `Markov` | Política basada en transición de estados. |
| `TDLearning` | Aprendizaje por refuerzo con Q-table persistente. |
| `EnsembleNoTD` | Combinación estable: Minimax + Bayesian + Markov. |
| `EnsembleWithTD` | Variante experimental: Minimax + Bayesian + Markov + TD. |

La lógica principal vive en módulos Python testeables dentro de `src/poker_ai`. El notebook `poker_ia_comparativa_final.ipynb` funciona como reporte/demo y no debe duplicar lógica del motor, agentes ni métricas.

## Estructura del proyecto

```text
src/poker_ai/
  engine/        motor del juego, acciones legales y simulación
  agents/        agentes IA individuales y ensembles
  evaluation/    métricas, reportes, entrenamiento TD y CLI

tests/           pruebas unitarias, integración y contrato del notebook
docs/            reporte técnico complementario
openspec/        artefactos SDD del desarrollo
artifacts/       snapshots generados, por ejemplo la Q-table de TD
```

## Requisitos

- Python administrado con `uv`.
- JupyterLab/nbconvert se instalan desde las dependencias de desarrollo.
- No hace falta modificar Python global.

Instalación:

```bash
uv sync --extra dev
```

Verificación completa:

```bash
uv run pytest
```

Resultado esperado actual:

```text
56 passed
```

## Cómo ejecutar el proyecto

### 1. Entrenar TD Learning

```bash
uv run python -m poker_ai.evaluation.train_td --hands 200 --seed 17 --output artifacts/td_qtable.json
```

Esto genera un snapshot persistente de la Q-table en:

```text
artifacts/td_qtable.json
```

### 2. Ejecutar reporte desde CLI

```bash
uv run python -m poker_ai.evaluation.cli report
```

### 3. Ejecutar el notebook

```bash
uv run jupyter nbconvert \
  --to notebook \
  --execute poker_ia_comparativa_final.ipynb \
  --output poker_ia_comparativa_final.executed.ipynb
```

También podés abrirlo visualmente:

```bash
uv run jupyter lab
```

## Experimento recomendado para conclusiones

Para una corrida más defendible que un smoke test:

```bash
POKER_REPORT_HANDS=40 \
POKER_REPORT_SEEDS=101,202,303 \
POKER_REPORT_FRESH_TD=1 \
uv run jupyter nbconvert \
  --to notebook \
  --execute poker_ia_comparativa_final.ipynb \
  --output resultados_ensemble_td.ipynb
```

Parámetros:

| Parámetro | Valor |
|---|---:|
| Manos por semilla | 40 |
| Semillas | 101, 202, 303 |
| Total por agente | 120 manos |
| TD fresco | Sí |
| ROI | Calculado sobre fichas realmente invertidas |

## Resultados observados

Última verificación con TD fresco y 120 manos por agente:

| Agente | W-L-T | ROI | Ganancia promedio |
|---|---:|---:|---:|
| `EnsembleWithTD (fresh)` | 65-48-7 | 0.142 | 1.417 |
| `Markov` | 60-52-8 | 0.067 | 0.667 |
| `Bayesian` | 60-55-5 | 0.042 | 0.417 |
| `Minimax` | 58-59-3 | -0.008 | -0.083 |
| `Random` | 42-77-1 | -0.044 | -0.500 |
| `EnsembleNoTD` | 51-61-8 | -0.083 | -0.833 |
| `TDLearning (fresh)` | 23-94-3 | -0.327 | -3.000 |

## Conclusiones

1. **El mejor resultado observado fue `EnsembleWithTD (fresh)`** en la corrida de verificación más reciente.
2. **TD Learning individual todavía es débil**, pero como señal complementaria con peso bajo puede aportar diversidad al ensemble.
3. **`EnsembleNoTD` sigue siendo el baseline prudente**, porque históricamente fue más estable y no depende de la calidad del snapshot TD.
4. **No se debe afirmar superioridad estadística definitiva todavía**: la corrida actual tiene 120 manos por agente y un entorno simplificado.
5. Para una defensa académica más fuerte, el siguiente paso es ejecutar más manos, más semillas, más perfiles de oponente e intervalos de confianza.

Conclusión defendible:

> El enfoque combinado puede mejorar el rendimiento cuando integra señales complementarias de varios modelos. En la última corrida, `EnsembleWithTD` obtuvo el mejor ROI, pero TD Learning aún requiere más entrenamiento y evaluación para justificarlo como componente dominante. Por eso se reportan ambos ensembles: uno estable sin TD y otro experimental con TD.

## Pesos de los ensembles

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

## Métricas

| Métrica | Definición |
|---|---|
| Win rate | Proporción de manos ganadas. |
| Profit | Fichas ganadas o perdidas. |
| ROI | Profit dividido entre fichas realmente invertidas. |
| Avg profit | Ganancia promedio por mano. |

El ROI ya no usa el denominador antiguo `n_hands * BIG_BLIND`; ahora se calcula con inversión real agregada.

## Desarrollo y pruebas

Correr todo:

```bash
uv run pytest
```

Correr solo contrato del notebook:

```bash
uv run pytest tests/test_notebook_contract.py
```

El contrato valida que el notebook:

- importe el backend modular,
- no redefina lógica central,
- no recupere el ROI antiguo,
- documente las variantes de ensemble y TD.

## Limitaciones

- El entorno de póker es simplificado.
- Los resultados dependen de semillas, cantidad de manos y tipo de oponente.
- TD Learning usa Q-table discreta, no Deep Q-Learning.
- El proyecto compara modelos bajo condiciones controladas; no pretende jugar póker real profesional.

## Trabajo futuro

- Aumentar a miles de manos por agente.
- Evaluar contra perfiles de oponente: agresivo, conservador, aleatorio y farolero.
- Agregar intervalos de confianza.
- Mejorar reward shaping de TD.
- Probar pesos del ensemble por fase del juego.
- Explorar DQN como evolución de TD Learning.
