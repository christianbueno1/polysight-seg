# Reporte de estabilidad del baseline en tres semillas

## Objetivo

Este reporte reúne tres ejecuciones de U-Net/ResNet-34 para estimar cuánto cambia el
resultado al modificar únicamente la semilla. Las réplicas conservan arquitectura,
split `700/150/150`, resolución, augmentations, pérdida, optimizador, scheduler, early
stopping y umbral `0.5`. Un contrato automático compara los YAML y permite como única
diferencia de entrenamiento `run.seed`.

La semilla `20260817` corresponde al experimento original. Las semillas `20260818` y
`20260819` se ejecutaron después de observar el primer resultado de test; por tanto, son
un análisis posterior de estabilidad y no dos nuevas validaciones ciegas.

## Runs y checkpoints

| Semilla | Job training | Run training | Época elegida | Val Dice | Job test | Run evaluación |
|---:|---:|---|---:|---:|---:|---|
| `20260817` | `23312` | `5fdf1b9929ec443da426c6442d9e20f1` | 22 | 0.897763 | `23325` | `73876309ec7c45e09023574a02a47475` |
| `20260818` | `23457` | `5be446e9eabd40e4ba92d4d2873d333e` | 32 | 0.903946 | `23459` | `b4fac4a0df96443981af1628206176fd` |
| `20260819` | `23458` | `59a6e9f0b6124001a1af360b4f22dea2` | 25 | 0.894238 | `23460` | `2ec54777437b4ee2a0c84235e9275bdb` |

Cada run de evaluación está vinculado al checkpoint elegido exclusivamente por Dice de
validation. Los SHA-256 completos y los identificadores operativos están en
[`results/seed-stability/runs.csv`](results/seed-stability/runs.csv).

## Resultados individuales de test

| Semilla | Dice | IoU | Precisión | Recall |
|---:|---:|---:|---:|---:|
| `20260817` | 0.918397 | 0.849107 | 0.923740 | 0.913115 |
| `20260818` | 0.919315 | 0.850678 | 0.937617 | 0.901713 |
| `20260819` | 0.913545 | 0.840849 | 0.932206 | 0.895615 |

No se seleccionó una semilla ganadora: las tres forman parte del resultado.

## Resumen de estabilidad

La tabla usa la media aritmética y la desviación estándar muestral (`n-1`) de las tres
ejecuciones:

| Métrica | Media | Desviación estándar | Forma breve |
|---|---:|---:|---:|
| Mejor Dice de validation | 0.898649 | 0.004914 | `0.8986 ± 0.0049` |
| Dice test | 0.917085 | 0.003101 | `0.9171 ± 0.0031` |
| IoU test | 0.846878 | 0.005280 | `0.8469 ± 0.0053` |
| Precisión test | 0.931188 | 0.006994 | `0.9312 ± 0.0070` |
| Recall test | 0.903481 | 0.008883 | `0.9035 ± 0.0089` |

El Dice varió entre `0.913545` y `0.919315`, un rango absoluto de aproximadamente
`0.0058`. Bajo este split y protocolo, el resultado agregado muestra poca variación ante
estas tres semillas. Recall presentó la mayor desviación relativa entre las cuatro
métricas, lo que indica que la cantidad de pólipo omitido fue más sensible a la réplica
que la superposición global.

Tres ejecuciones solo ofrecen una estimación inicial: no permiten caracterizar por
completo la distribución de resultados ni sustituyen validación cruzada o datos
externos. Además, las tres evaluaciones usan exactamente las mismas 150 imágenes de test;
no representan 450 casos independientes.

## Incidente y recuperación de MLflow

La evaluación `23460` completó las 150 inferencias y generó 150 métricas por imagen,
150 mapas de probabilidad y 15 paneles cualitativos. Después falló al iniciar MLflow
porque el puerto `127.0.0.1:5000` seguía ocupado tras el job anterior.

No se repitió inferencia ni se borraron resultados. El job CPU `23461` validó la
integridad de la salida y registró los artefactos existentes en el run
`2ec54777437b4ee2a0c84235e9275bdb`, etiquetado con `inference_repeated=false`, el job
original y el job de recuperación.

## Conclusión para el póster

Una formulación compacta y defendible es:

> En tres ejecuciones que difieren únicamente en la semilla, U-Net/ResNet-34 obtuvo
> Dice test `0.9171 ± 0.0031`. La baja dispersión observada sugiere estabilidad inicial
> del baseline bajo el mismo split, aunque no reemplaza validación cruzada ni externa.

## Fuentes canónicas

- Runs individuales: [`results/seed-stability/runs.csv`](results/seed-stability/runs.csv).
- Estadísticos: [`results/seed-stability/summary.json`](results/seed-stability/summary.json).
- Configuraciones: [`../configs/training/`](../configs/training/) y
  [`../configs/evaluation/`](../configs/evaluation/).
- Estado grande no versionado: `mlflow.db`, `artifacts/`, `checkpoints/` y `evaluation/`.
