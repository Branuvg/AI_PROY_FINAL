## Exploration: mejorar/convertir el proyecto Python de IA para póker

### Current State
El proyecto vive casi por completo en `poker_ia_comparativa_final.ipynb`. El notebook mezcla reglas del simulador, modelos de IA, entrenamiento, evaluación y conclusiones en un solo archivo JSON. Hoy la base funcional tiene varias limitaciones estructurales y de validez experimental: el simulador permite solo dos acciones por calle, no modela cadenas reales de re-raise, `action_history` no se propaga en la ejecución real, el ROI reportado sigue normalizado por `n_hands * BIG_BLIND`, el agente Markov premia avanzar de fase con CHECK mientras los raises quedan en la misma fase, y TD aprende una cobertura muy baja del espacio de estados.

### Affected Areas
- `poker_ia_comparativa_final.ipynb` — contiene TODO: motor del juego, agentes, entrenamiento, evaluación y reporte final.
- `openspec/config.yaml` — ya registra restricciones del proyecto, modo híbrido y riesgos conocidos; será la base del cambio SDD.
- `openspec/changes/extract-poker-engine-and-validate-models/exploration.md` — artefacto de exploración para continuar con proposal/spec/design.

### Approaches
1. **Mejorar el notebook in-place** — corregir simulador, métricas y modelos directamente dentro del `.ipynb`.
   - Pros: cambio inicial rápido; mantiene el entregable académico intacto; evita trabajo de empaquetado al principio.
   - Cons: baja testabilidad; diffs ruidosos por JSON; difícil aislar regresiones; mezclar reglas, evaluación y visualización hace muy caro verificar cambios; alto riesgo de seguir publicando métricas incorrectas.
   - Effort: Medium

2. **Extraer módulos Python + tests y dejar el notebook como demo/reporte** — mover lógica del motor, agentes y evaluación a módulos testeables; el notebook pasa a consumir esos módulos para mostrar resultados.
   - Pros: permite tests unitarios e integración; reduce riesgo al corregir simulador/ROI/Markov/TD; hace revisable el código; separa experimento de infraestructura; deja al notebook como capa de presentación reproducible.
   - Cons: mayor inversión inicial; requiere definir estructura de paquetes y fixtures mínimas; probablemente necesita dividir entrega en varias unidades.
   - Effort: High

### Recommendation
Recomiendo **extraer módulos Python + tests y conservar el notebook como reporte/demo**. El problema NO es solo cosmético ni de organización: los hallazgos afectan la validez del simulador, de las métricas y de la comparación entre agentes. Hacer eso dentro del notebook mantiene el proyecto frágil y casi imposible de verificar bien. La mejor ruta SDD es crear primero un núcleo testeable del juego/evaluación y luego reconectar el notebook a ese núcleo para reproducir tablas y gráficas.

### Risks
- El alcance cruza simulador, evaluación, Markov, TD y ensemble; puede crecer rápido si no se corta por slices.
- Dependencias (`treys`, `pgmpy`, `numpy`, `pandas`) no están instaladas en esta máquina, así que la verificación ejecutable requerirá entorno dedicado.
- Cambiar el simulador probablemente altere todas las métricas publicadas; habrá que rehacer resultados y conclusiones.
- El sesgo actual del entorno puede haber inflado resultados de Markov y ocultado debilidades del TD/ensemble.

### Ready for Proposal
Yes — el próximo paso recomendado es proponer un cambio enfocado en extraer un engine modular y validar la comparación experimental con métricas y tests confiables.
