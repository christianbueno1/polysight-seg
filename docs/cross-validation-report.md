# Reporte de validación cruzada de cinco folds

## Objetivo

Este experimento evalúa cuánto cambia U-Net/ResNet-34 cuando varía la composición de
los datos, manteniendo arquitectura, hiperparámetros, semilla de entrenamiento y umbral
`0,5`. Complementa las tres semillas, que midieron sensibilidad al azar del
entrenamiento bajo un único split.

Es un análisis posterior: el test original ya había sido observado. Por ello se presenta
como evidencia interna adicional sobre Kvasir-SEG, no como nueva validación ciega,
externa o clínica.

## Protocolo

Cada iteración utilizó 700 imágenes para train, 100 para seleccionar el checkpoint por
Dice de validation y 200 como fold externo. Los cinco folds externos son mutuamente
excluyentes y cubren las 1.000 imágenes exactamente una vez. Los estratos de tamaño y
los grupos de duplicados se conservaron.

## Checkpoints seleccionados

| Fold | Job training | Run training | Época | Val Dice | Época de parada |
|---:|---:|---|---:|---:|---:|
| 1 | `23465` | `35e2759238e0407591f1342b07c9c3f2` | 23 | 0.904296 | 33 |
| 2 | `23466` | `99b74c96e55648f3a7552629eb0bcaa2` | 21 | 0.913945 | 31 |
| 3 | `23467` | `d3b539791b414a64b0713a8f50595e4f` | 19 | 0.890212 | 29 |
| 4 | `23474` | `7cb48b16e0c545338c9b0434b52b5fb5` | 19 | 0.908378 | 29 |
| 5 | `23469` | `2171470488fc4c378d2dd1232f076a67` | 13 | 0.921156 | 23 |

Las rutas y SHA-256 completos están en
[`results/cross-validation/training-runs.csv`](results/cross-validation/training-runs.csv).

## Resultados externos por fold

| Fold | Job | Run evaluación | Dice | IoU | Precisión | Recall |
|---:|---:|---|---:|---:|---:|---:|
| 1 | `23476` | `0cd67437fc3e45b2b3096521707a2c6a` | 0.896130 | 0.811808 | 0.908640 | 0.883960 |
| 2 | `23477` | `8baff02557ef4b1c96c47abc21d3219b` | 0.900056 | 0.818274 | 0.914030 | 0.886502 |
| 3 | `23478` | `fe142fc7de324c7a802a666e59df6d3e` | 0.896149 | 0.811838 | 0.909943 | 0.882767 |
| 4 | `23479` | `b99d30dab9f2466c9097e5a39a54360b` | 0.903138 | 0.823384 | 0.914697 | 0.891867 |
| 5 | `23480` | `afd16a9402b242e68669eb2f54364f64` | 0.890629 | 0.802823 | 0.899168 | 0.882250 |

Cada evaluación produjo 200 métricas por imagen, 200 mapas de probabilidad y 15 paneles
cualitativos. En conjunto se verificaron 1.000 UUID únicos, 1.000 mapas y 75 paneles.

## Resumen entre folds

La media y desviación estándar muestral de los cinco resultados externos son:

| Métrica | Media ± DE | Mínimo–máximo |
|---|---:|---:|
| Dice | **`0.8972 ± 0.0047`** | `0.8906–0.9031` |
| IoU | `0.8136 ± 0.0077` | `0.8028–0.8234` |
| Precisión | `0.9093 ± 0.0062` | `0.8992–0.9147` |
| Recall | `0.8855 ± 0.0039` | `0.8822–0.8919` |

El rango Dice entre folds fue aproximadamente `0,0125`. Esto indica que el resultado
es relativamente estable ante estas cinco particiones, aunque la composición de los
datos produce más variación que las tres semillas del split original (`± 0,0031`).

## Perspectiva agrupada y por imagen

Al sumar los conteos de píxeles de las 1.000 predicciones *out of fold*, el Dice agrupado
es `0,897232`, IoU `0,813618`, precisión `0,909289` y recall `0,885491`. Esta agregación
pondera más las imágenes con regiones grandes.

Por imagen, la mediana Dice es `0,946319` y el 50 % central se encuentra entre `0,894365`
y `0,967887`. El mínimo es `0,0`: al menos un caso quedó completamente sin solapamiento.
Por ello, la estabilidad global no elimina la necesidad de analizar fallos individuales.

## Conclusión

U-Net/ResNet-34 obtuvo Dice externo **`0,8972 ± 0,0047`** en cinco folds. El rendimiento
se mantuvo cercano al cambiar la composición del dataset y cada una de las 1.000 imágenes
fue evaluada fuera de su entrenamiento. La evidencia fortalece la reproducibilidad
interna del baseline, pero no sustituye evaluación en datos de otros centros.

## Fuentes canónicas

- Entrenamientos: [`results/cross-validation/training-runs.csv`](results/cross-validation/training-runs.csv).
- Evaluaciones: [`results/cross-validation/evaluation-runs.csv`](results/cross-validation/evaluation-runs.csv).
- Resumen: [`results/cross-validation/summary.json`](results/cross-validation/summary.json).
- Protocolo previo: [`cross-validation-protocol.md`](cross-validation-protocol.md).
