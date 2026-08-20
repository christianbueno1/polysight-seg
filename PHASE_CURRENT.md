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
- [~] Sincronizar el commit aprobado en CEDIA y enviar ambos entrenamientos
- [ ] Verificar el entrenamiento con semilla `20260818`
- [ ] Verificar el entrenamiento con semilla `20260819`
- [ ] Evaluar y resumir las tres semillas sin seleccionar solo la mejor
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
