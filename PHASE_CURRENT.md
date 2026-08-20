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
- [ ] Crear boxplot de Dice e IoU por imagen
- [ ] Crear gráfico de Dice frente al tamaño real del pólipo
- [ ] Consolidar paneles cualitativos de casos mejores, medianos y peores
- [ ] Presentar la matriz de confusión binaria explícitamente como matriz por píxel

---

### Notas y decisiones

- La columna global usa los conteos agregados de todos los píxeles; mediana, P25–P75 y
  peor caso se calculan sobre las 150 métricas individuales.
- Se reportan ambas perspectivas porque la agregación micro pondera más las imágenes
  con pólipos grandes y puede ocultar casos individuales deficientes.
- El peor caso se define como el mínimo de cada métrica, por lo que no necesariamente
  corresponde al mismo UUID en todas las filas.
