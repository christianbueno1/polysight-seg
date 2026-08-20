# PHASE_CURRENT

## Fase 11 — Visualización del rendimiento de segmentación

**Objetivo:** Preparar tablas y visualizaciones que comuniquen el rendimiento del
U-Net/ResNet-34 sin ocultar la variabilidad entre imágenes ni los fallos espaciales.

**Contexto:** Los resultados canónicos proceden de `docs/results/test/` y corresponden
a una única evaluación de 150 imágenes de test con umbral binario `0.5`.

---

### Tareas

- [x] Crear tabla resumen con métricas globales y distribución por imagen
- [x] Publicar la tabla resumen en el reporte técnico final
- [x] Descartar el boxplot de Dice e IoU por redundancia y falta de espacio en el póster
- [x] Crear gráfico de Dice frente al tamaño real del pólipo
- [x] Consolidar paneles cualitativos de casos mejores, medianos y peores
- [x] Preparar y ordenar tres figuras autónomas para elegir una en el póster
- [x] Redactar viñetas y explicación corta de resultados para el póster
- [x] Redactar la sección de solución para la sustentación del póster
- [x] Explicar la elección y los límites de los hiperparámetros del baseline
- [x] Crear configuraciones de réplica que difieren únicamente en la semilla
- [x] Preparar envío Slurm encadenado mediante dependencia `afterok`
- [x] Sincronizar el commit aprobado en CEDIA y enviar ambos entrenamientos
- [x] Verificar el entrenamiento con semilla `20260818` — job `23457`
- [x] Verificar el entrenamiento con semilla `20260819` — job `23458`
- [x] Fijar checkpoints de ambas réplicas mediante run, época, Dice y SHA-256
- [x] Evaluar en cadena ambas réplicas sobre test con umbral fijo `0.5`
- [x] Verificar integridad de métricas, mapas y paneles de ambas evaluaciones
- [x] Recuperar en MLflow el registro de la semilla `20260819` sin repetir inferencia
- [x] Resumir las tres semillas sin seleccionar solo la mejor
- [x] Crear reporte de estabilidad con runs, métricas y limitaciones
- [x] Integrar la estabilidad de tres semillas en la guía oral y la figura del póster
- [x] Preparar validación cruzada de cinco folds con jobs seriales y puertos MLflow por job
- [x] Sincronizar en CEDIA y enviar los cinco entrenamientos mediante `afterok`
- [x] Verificar los cinco entrenamientos y fijar sus checkpoints
- [x] Preparar evaluaciones externas después de fijar los cinco checkpoints
- [x] Ejecutar y verificar las cinco evaluaciones externas encadenadas
- [x] Consolidar los cinco folds sin seleccionar solamente el mejor
- [x] Integrar método, barreras, validación cruzada y siguiente encoder en el guion oral
- [ ] Presentar la matriz de confusión binaria explícitamente como matriz por píxel

---

### Notas y decisiones

- La columna global usa los conteos agregados de todos los píxeles; mediana, P25–P75 y
  peor caso se calculan sobre las 150 métricas individuales.
- Se reportan ambas perspectivas porque la agregación micro pondera más las imágenes
  con pólipos grandes y puede ocultar casos individuales deficientes.
- El peor caso se define como el mínimo de cada métrica, por lo que no necesariamente
  corresponde al mismo UUID en todas las filas.
- La tabla ya comunica mediana y P25–P75; se descarta el boxplot para priorizar en el
  póster evidencia espacial que pueda interpretarse rápidamente.
- Los paneles conservan el mapa de probabilidad además de las cuatro vistas mínimas,
  porque permite observar incertidumbre antes de aplicar el umbral.
- El tamaño no explica por sí solo los fallos: las medianas son 0.9411, 0.9630 y
  0.9608 para pólipos pequeños, medianos y grandes, y el peor caso es grande.
- Para una audiencia general se prioriza la comparación cualitativa, seguida del
  resumen cuantitativo y del análisis de Dice frente al tamaño.
- El texto del póster combina el resultado global con la mediana y el mínimo para
  comunicar rendimiento y limitaciones sin depender de un único promedio.
- La explicación oral usa la secuencia pregunta, evidencia, giro y conclusión para
  contar los resultados sin recitar todas las métricas del resumen escrito.
- La sección de solución conecta dataset, arquitectura y protocolo antes de revelar los
  resultados, siguiendo el orden narrativo problema–solución–evidencia.
- Los hiperparámetros se presentan como elecciones conservadoras y reproducibles, no
  como óptimos demostrados mediante una búsqueda que no se realizó.
- Dos semillas adicionales son válidas como análisis posterior de estabilidad si solo
  cambia la semilla y se reportan las tres ejecuciones completas.
- Las réplicas usan `20260818` y `20260819`; un contrato compara el YAML completo con
  el baseline y permite como única diferencia `run.seed`.
- El segundo job usa `afterok` respecto del primero para evitar escrituras concurrentes
  en MLflow y no consumir GPU si falla la primera réplica.
- CEDIA ejecuta el commit `1f178c06612a5dc27abd3ff2dcedd6d10edebf56`.
- Ambos jobs terminaron `COMPLETED (0:0)`: semilla `20260818` seleccionó la época 32
  con val Dice `0.9039459519026185`; semilla `20260819` seleccionó la época 25 con val
  Dice `0.8942383180146468`.
- Las evaluaciones conservan test completo, umbral `0.5`, métricas y análisis cualitativo,
  y escriben en directorios separados por semilla.
- La evaluación `23459` terminó correctamente. `23460` completó inferencia y artefactos,
  pero falló al iniciar MLflow porque el puerto `127.0.0.1:5000` seguía ocupado.
- Ambas salidas contienen 150 métricas por imagen, 150 mapas y 15 paneles; test no se
  repitió durante la recuperación del registro MLflow de `20260819`.
- El job CPU `23461` registró los artefactos existentes en el run MLflow
  `2ec54777437b4ee2a0c84235e9275bdb` con `inference_repeated=false`.
- Las tres semillas obtuvieron Dice test `0.9170853927141387 ± 0.0031005861277978437`
  usando desviación estándar muestral; se conservan además todos los valores individuales.
- El póster mantiene la comparación cualitativa por su lectura inmediata y añade un sello
  con Dice `0.9171 ± 0.0031` para comunicar en una sola figura calidad y estabilidad.
- La validación cruzada usa cinco folds externos de 200 casos; cada iteración conserva
  700 para train y 100 para validation, con una sola semilla para aislar el efecto del split.
- Los entrenamientos se ejecutarán en cadena `afterok`. Cada job deriva un puerto MLflow
  de su ID y SQLite conserva un único escritor; las evaluaciones se preparan solo después
  de fijar los cinco checkpoints mediante run, época, Dice y SHA-256.
- La cadena enviada es `23465 → 23466 → 23467 → 23468 → 23469`. El fold 01 inició en
  `compute-0-1` con su configuración correcta y el puerto MLflow `38465`.
- Los folds 01–03 terminaron correctamente. `23468` recibió `SIGKILL` a los 28 segundos
  con ~1,7 GiB de RAM, sin timeout, OOM, checkpoint ni proceso MLflow remanente; se trata
  como terminación externa transitoria. El fold 04 se reenvió como `23474` y la
  dependencia de `23469` se actualizó a `afterok:23474`.
- Los cinco checkpoints quedaron fijados en `docs/results/cross-validation/training-runs.csv`;
  las épocas seleccionadas fueron 23, 21, 19, 19 y 13, con Dice de validation entre
  `0.8902119542398623` y `0.92115585618545`.
- Las evaluaciones `23476–23480` terminaron `COMPLETED (0:0)` y cubren 1.000 UUID únicos,
  con 1.000 mapas de probabilidad y 75 paneles cualitativos.
- El Dice externo entre folds es `0.8972203103581422 ± 0.004712834228618429`; el Dice
  agrupado sobre las 1.000 predicciones *out of fold* es `0.8972319282731822`.
- El guion presenta semillas y folds como preguntas complementarias, explica AdamW y
  BCE + Dice mediante analogías, y propone EfficientNet-B0 como comparación pareada por
  fold sin afirmar por anticipado que será superior.
