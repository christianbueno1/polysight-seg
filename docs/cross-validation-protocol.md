# Protocolo de validación cruzada de cinco folds

## Pregunta experimental

¿El rendimiento de U-Net/ResNet-34 se mantiene cuando cambia la composición de los
datos de entrenamiento y evaluación, y no solamente cuando cambia la semilla?

Este experimento es posterior a la evaluación original y al análisis de tres semillas.
Por tanto, amplía la evidencia de estabilidad sobre Kvasir-SEG, pero no se presenta como
una nueva validación ciega ni como validación externa o clínica.

## Diseño fijado antes de ejecutar

- Cinco folds externos mutuamente excluyentes de 200 imágenes.
- En cada iteración: 700 imágenes de train, 100 de validation y 200 del fold externo.
- Cada imagen aparece exactamente una vez en un fold externo.
- Los estratos pequeño, mediano y grande se conservan en todas las particiones.
- Los duplicados exactos permanecen agrupados para impedir *data leakage*.
- Arquitectura, inicialización ImageNet, resolución, augmentations, pérdida,
  optimizador, scheduler, early stopping, semilla `20260817` y umbral `0,5` permanecen
  fijos.
- El checkpoint se elige únicamente por Dice de validation interna.
- La etiqueta técnica `test` dentro de cada CSV significa “fold externo retenido”; no
  es el conjunto original de 150 imágenes repetido cinco veces.

Los folds se generan determinísticamente con la semilla de partición `20260820`. Los
CSV derivados viven bajo `data/processed/` y no se versionan porque el dataset completo
se reconstruye en CEDIA; sus hashes quedan en `splits-summary.json` y MLflow.

## Ejecución en dos etapas

### Etapa 1 — Entrenamiento

```bash
scripts/submit_cross_validation_training.sh
```

El comando regenera los folds y envía cinco entrenamientos en cadena estricta:

```text
fold-01 ─afterok→ fold-02 ─afterok→ fold-03 ─afterok→ fold-04 ─afterok→ fold-05
```

Si un job falla, los posteriores no consumen GPU. Cada fold escribe en
`checkpoints/cross-validation/fold-XX/<run-id>/`.

### Etapa 2 — Evaluación externa

No se prepara automáticamente antes del entrenamiento. Primero se registra para cada
fold el run MLflow, la época seleccionada, el Dice de validation y el SHA-256 de
`best.pt`. Con esos valores se crean configuraciones de evaluación inmutables y después
se envían las cinco evaluaciones mediante otra cadena `afterok`. Esta pausa impide
evaluar un checkpoint no auditado o elegirlo después de mirar el fold externo.

Los checkpoints ya fijados se encuentran en
[`results/cross-validation/training-runs.csv`](results/cross-validation/training-runs.csv).
Las cinco evaluaciones se envían con:

```bash
scripts/submit_cross_validation_evaluations.sh
```

## Protección de MLflow

Los jobs continúan serializados para evitar escritores concurrentes sobre `mlflow.db`.
Además, `train_baseline.sbatch` y `evaluate_test.sbatch` calculan un puerto local por job:

```text
POLYSIGHT_MLFLOW_PORT = 15000 + (SLURM_JOB_ID mod 40000)
```

El runner actualiza en memoria tanto el puerto como el `tracking_uri`; el YAML canónico
permanece intacto. Antes de iniciar, MLflow comprueba que el puerto esté libre y falla de
forma segura si existe una colisión. El servidor administrado se detiene al salir del
runner, incluso cuando ocurre una excepción dentro del contexto.

## Resultado que se reportará

Se conservarán los cinco Dice externos individuales y se resumirán mediante media y
desviación estándar muestral. También se consolidarán las 1.000 predicciones *out of
fold* para análisis por imagen. No se escogerá el mejor fold como resultado final.
