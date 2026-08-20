# Opciones de evaluación para el póster

Si solo cabe una figura, se recomienda usar la primera opción. El orden prioriza la
comprensión inmediata de una audiencia general sin ocultar las limitaciones del modelo.

## Orden recomendado

1. **Comparación cualitativa — recomendada.** Contrasta un caso cercano a la mediana
   con el peor caso y muestra imagen, máscara real, probabilidad, predicción y overlay.
   Permite entender en segundos qué hace el modelo y cómo puede fallar. Incluye Dice,
   IoU, recall, tamaño del test y umbral.
2. **Resumen cuantitativo.** Presenta Dice global como resultado principal, acompañado
   de IoU, precisión, recall y variabilidad por imagen. Es la opción más compacta y
   rigurosa cuando el diseño exige principalmente cifras.
3. **Dice frente al tamaño del pólipo.** Explica una posible fuente de variabilidad y
   evita concluir que todos los fallos provienen de pólipos pequeños. Requiere más
   tiempo de lectura que las dos anteriores.

## Figuras listas para usar

- [`assets/poster/01-qualitative-comparison.svg`](assets/poster/01-qualitative-comparison.svg)
- [`assets/poster/02-metrics-summary.svg`](assets/poster/02-metrics-summary.svg)
- [`assets/poster/03-dice-by-polyp-size.svg`](assets/poster/03-dice-by-polyp-size.svg)

Los tres SVG son autónomos y escalables. La primera figura incrusta sus imágenes en el
propio archivo, por lo que no depende de rutas externas al exportar el póster.

La comparación cualitativa es evidencia visual, no una métrica agregada. Sus cifras
proceden de casos reales de test y deben acompañarse verbalmente con el Dice global
`0.9184` si el espacio permite una línea adicional.
