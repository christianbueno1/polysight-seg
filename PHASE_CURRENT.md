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
