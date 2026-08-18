# Índice de artefactos y fuentes canónicas

Este índice indica qué archivo responde cada pregunta del estudio y distingue evidencia
versionada de estado experimental externo. La fuente canónica es el dato que debe
consultarse para verificar una cifra; los documentos y figuras son representaciones
derivadas.

## Identificadores principales

| Etapa | Job Slurm | Run MLflow |
|---|---:|---|
| Entrenamiento completo | `23312` | `5fdf1b9929ec443da426c6442d9e20f1` |
| Evaluación final de test | `23325` | `73876309ec7c45e09023574a02a47475` |

El checkpoint seleccionado es `best.pt` de la época 22. Su SHA-256 es
`a3900c2db01e9e17fa7fedce12da94274d8995284f1c37f6e653df402919361b`.

## Fuentes canónicas versionadas

| Pregunta | Fuente | Contenido |
|---|---|---|
| ¿Cómo se preparan y cargan los datos? | [`../configs/data/kvasir-seg.yaml`](../configs/data/kvasir-seg.yaml) | Rutas, umbral de máscara, tamaño, normalización y transforms |
| ¿Qué arquitectura se entrenó? | [`../configs/models/unet-resnet34.yaml`](../configs/models/unet-resnet34.yaml) | U-Net, encoder, forma de entrada/salida y pérdida |
| ¿Cuál fue el protocolo de entrenamiento? | [`../configs/training/unet-resnet34-baseline.yaml`](../configs/training/unet-resnet34-baseline.yaml) | Semilla, optimizador, scheduler, early stopping y selección |
| ¿Cómo se evaluó el checkpoint? | [`../configs/evaluation/unet-resnet34-baseline.yaml`](../configs/evaluation/unet-resnet34-baseline.yaml) | Hash, split, umbral, métricas y salidas |
| ¿Qué ocurrió en cada época? | [`results/unet-resnet34-baseline-history.csv`](results/unet-resnet34-baseline-history.csv) | Historial completo de 32 épocas y marca del mejor checkpoint |
| ¿Cuáles son las métricas oficiales de test? | [`results/test/metrics.json`](results/test/metrics.json) | Métricas micro, conteos y número de imágenes |
| ¿Cómo rindió cada imagen? | [`results/test/per-image-metrics.csv`](results/test/per-image-metrics.csv) | Métricas y fracción de primer plano para las 150 imágenes |
| ¿Cómo se construye la matriz? | [`results/test/confusion-matrix-counts.csv`](results/test/confusion-matrix-counts.csv) | TP, FP, FN y TN organizados como matriz |
| ¿Qué proporción se acertó por clase real? | [`results/test/confusion-matrix-normalized-true.csv`](results/test/confusion-matrix-normalized-true.csv) | Matriz normalizada por clase real |
| ¿Cómo cambian las métricas con el umbral? | [`results/test/threshold-curve.csv`](results/test/threshold-curve.csv) | Análisis descriptivo de nueve umbrales; no reajusta `0.5` |

Los JSON, CSV y YAML anteriores tienen prioridad si un resumen o una figura no coincide
con ellos.

## Derivados visuales versionados

| Artefacto | Fuente | Propósito |
|---|---|---|
| [`assets/unet-resnet34-training-curves.svg`](assets/unet-resnet34-training-curves.svg) | Historial de entrenamiento | Curva editable para documentación |
| [`assets/unet-resnet34-training-curves.png`](assets/unet-resnet34-training-curves.png) | Historial de entrenamiento | Exportación raster para presentaciones |
| [`assets/test/best-case.png`](assets/test/best-case.png) | Métricas, probabilidades e imagen | Ejemplo cualitativo de mayor Dice |
| [`assets/test/median-case.png`](assets/test/median-case.png) | Métricas, probabilidades e imagen | Ejemplo cercano a la mediana |
| [`assets/test/worst-case.png`](assets/test/worst-case.png) | Métricas, probabilidades e imagen | Ejemplo cualitativo de menor Dice |

Las figuras ayudan a interpretar el resultado, pero no sustituyen los archivos
tabulares que las originan.

## Documentos derivados

| Documento | Uso |
|---|---|
| [`../README.md`](../README.md) | Entrada breve al proyecto y resultado principal |
| [`final-report.md`](final-report.md) | Protocolo, resultados, análisis de errores y conclusión |
| [`model-card.md`](model-card.md) | Uso previsto, límites, riesgos y procedencia del modelo |
| [`presentacion.md`](presentacion.md) | Explicación para exposición y material visual |
| [`artifact-recovery.md`](artifact-recovery.md) | Sincronización y verificación de la evidencia externa |

## Estado experimental no versionado

Estos archivos están excluidos de Git por tamaño o por ser estado generado. Deben
recuperarse desde CEDIA siguiendo [`artifact-recovery.md`](artifact-recovery.md).

| Ruta local esperada | Contenido | Procedencia |
|---|---|---|
| `mlflow.db` | Experimentos, runs, parámetros, métricas y tags | Backend MLflow de ambos runs |
| `artifacts/1/5fdf1b9929ec443da426c6442d9e20f1/` | Checkpoints, configs, entorno, hashes e historial | Run de entrenamiento |
| `artifacts/1/73876309ec7c45e09023574a02a47475/` | Resultados, probabilidades y paneles de evaluación | Run de evaluación final |
| `checkpoints/unet-resnet34-baseline/5fdf1b9929ec443da426c6442d9e20f1/` | Copia de trabajo de `best.pt` y `last.pt` | Job `23312` |
| `evaluation/unet-resnet34-baseline/test/` | Salida completa reconstruible de test | Job `23325` |

La evaluación completa contiene 150 registros por imagen, 150 mapas de probabilidad y
15 paneles cualitativos. El directorio `artifacts/` ocupa aproximadamente 1.2 GB en la
copia actual; `mlflow.db` ocupa aproximadamente 1.3 MB y no contiene los archivos
binarios dentro de la base.

## Orden recomendado de verificación

1. Confirmar jobs y runs con los identificadores de este índice.
2. Verificar el SHA-256 de `best.pt` antes de cargarlo.
3. Consultar `metrics.json` para resultados agregados.
4. Consultar `per-image-metrics.csv` para variabilidad y casos extremos.
5. Usar matrices, curva descriptiva y paneles para interpretar los errores.
6. Revisar el reporte y la ficha para alcance, riesgos y límites.
