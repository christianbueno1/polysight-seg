# Scripts

Este directorio contendrá comandos reproducibles para preparar datos, entrenar,
evaluar y ejecutar inferencia. Las cargas que importen PyTorch se ejecutarán en CEDIA.

- `smoke_baseline.py`: valida un batch real con forward, pérdida, métricas y backward
  del U-Net/ResNet-34 en GPU.
- `validate_mlflow.py`: levanta un servidor efímero y comprueba persistencia de una
  métrica y un artefacto mediante el cliente MLflow.
- `smoke_training_engine.py`: comprueba en CPU los contratos básicos de los loops de
  train y validation con un modelo diminuto.
- `train.py`: ejecuta el runner versionado con MLflow; los límites de batches se usan
  solo para smokes y se omiten durante el entrenamiento completo.
- `plot_training_history.py`: genera las curvas editables de pérdida y Dice desde el
  historial CSV versionado.
- `plot_dice_by_polyp_size.py`: genera el gráfico editable de Dice frente a la fracción
  real de pólipo y colorea cada punto por estrato de tamaño.
- `build_poster_metric_figures.py`: genera tres figuras SVG autónomas y preparadas para
  comparar opciones de evaluación en el póster.
- `evaluate.py`: ejecuta un smoke limitado sobre validation o la evaluación completa y
  no fraccionable sobre test.
- `generate_cross_validation.py`: crea cinco folds externos reproducibles de 200 casos,
  cada uno con 700 casos de train y 100 de validation interna.
- `generate_cross_validation_configs.py`: deriva del baseline los YAML de datos y
  entrenamiento para los cinco folds.
- `submit_cross_validation_training.sh`: genera los folds y encadena sus cinco
  entrenamientos mediante dependencias `afterok`.

## Curvas del entrenamiento

`plot_training_history.py` genera una figura SVG editable de pérdida y Dice para train
y validation usando únicamente la biblioteca estándar de Python:

```bash
python scripts/plot_training_history.py \
  docs/results/unet-resnet34-baseline-history.csv \
  docs/assets/unet-resnet34-training-curves.svg
```

El script calcula la mejor época directamente desde `val_dice` y la marca en ambos
paneles; el CSV continúa siendo la fuente canónica de la figura.

## Dice frente al tamaño del pólipo

`plot_dice_by_polyp_size.py` cruza las métricas por imagen con la asignación reproducible
de splits y genera un SVG usando únicamente la biblioteca estándar:

```bash
python scripts/plot_dice_by_polyp_size.py \
  docs/results/test/per-image-metrics.csv \
  data/processed/kvasir-seg/splits.csv \
  docs/assets/test/dice-by-polyp-size.svg
```

## Figuras de evaluación para el póster

```bash
python scripts/build_poster_metric_figures.py \
  docs/results/test/per-image-metrics.csv \
  data/processed/kvasir-seg/splits.csv \
  docs/assets/test \
  docs/assets/poster
```

El comando produce una comparación cualitativa, un resumen cuantitativo y un gráfico
de Dice frente al tamaño. Los SVG incluyen títulos, definiciones, contexto y conclusión
para poder interpretarse sin consultar el reporte.
