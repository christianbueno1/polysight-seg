# PolySight Seg

Entrenamiento y evaluación reproducibles de segmentación binaria de pólipos sobre
Kvasir-SEG. El baseline usa U-Net con encoder ResNet-34 preentrenado en ImageNet, recibe
imágenes RGB de `256 × 256` y devuelve una máscara de un canal.

## Resultado principal

El checkpoint seleccionado en la época 22 se evaluó una sola vez sobre las 150 imágenes
de test, con umbral fijo `0.5`:

| Métrica | Resultado test |
|---|---:|
| Dice | `0.9184` |
| IoU | `0.8491` |
| Precisión | `0.9237` |
| Recall | `0.9131` |

El Dice mediano por imagen fue `0.9549`, pero el mínimo fue `0.0775`; por eso el estudio
incluye análisis de mejores, medianos y peores casos además de las métricas agregadas.
Los resultados describen Kvasir-SEG y no constituyen validación clínica externa.

## Protocolo experimental

- Dataset: 1.000 pares imagen/máscara de Kvasir-SEG.
- Split inmutable: 700 train, 150 validation y 150 test.
- Selección: mejor Dice de validation; test no participa en ajuste ni selección.
- Entrenamiento: AdamW, pérdida BCE + Dice, máximo 50 épocas y early stopping.
- Ejecución: NVIDIA A100 en CEDIA, AMP `float16` y semilla `20260817`.
- Trazabilidad: configuraciones, hashes, métricas, checkpoints y artefactos en MLflow.

Runs principales:

- entrenamiento: `5fdf1b9929ec443da426c6442d9e20f1`;
- evaluación final: `73876309ec7c45e09023574a02a47475`.

## Evidencia versionada

- [Métricas y datos fuente de test](docs/results/test/)
- [Curvas de entrenamiento](docs/assets/unet-resnet34-training-curves.svg)
- [Resultados y análisis para presentación](docs/presentacion.md)
- [Reporte técnico final](docs/final-report.md)
- [Ficha del modelo](docs/model-card.md)
- [Recuperación de checkpoint, resultados y runs](docs/artifact-recovery.md)
- [Índice de artefactos y fuentes canónicas](docs/artifact-index.md)
- [Configuración de entrenamiento](configs/training/unet-resnet34-baseline.yaml)
- [Configuración de evaluación](configs/evaluation/unet-resnet34-baseline.yaml)

Los CSV y JSON son las fuentes canónicas; las figuras son derivados regenerables.

## Ejecución

PyTorch, CUDA, entrenamiento y evaluación acelerada se ejecutan en el clúster HPC de
CEDIA. El equipo local se usa únicamente para desarrollo y validaciones ligeras:

```bash
scripts/validate_local.sh
```

Los jobs reproducibles están en [`slurm/`](slurm/) y los comandos Python en
[`scripts/`](scripts/). Los datos, checkpoints, `mlflow.db` y artefactos generados no se
guardan en Git.

## Documentación

- [Entornos de ejecución](docs/execution-environments.md)
- [Preparación del proyecto en CEDIA](docs/cedia-project-setup.md)
- [Preparación y transferencia de Kvasir-SEG](docs/dataset-preparation.md)
- [Material para la presentación](docs/presentacion.md)
- [Referencia general de MLflow](docs/mlflow-guide.md)
- [MLflow en PolySight Seg](docs/mlflow-project-guide.md)
- [Guía general del clúster CEDIA](docs/cedia-cluster-guide.md)
- [Guía del proyecto de segmentación](docs/segmentation-project-guide.md)
