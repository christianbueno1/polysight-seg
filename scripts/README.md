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
- `evaluate.py`: ejecuta un smoke limitado sobre validation o la evaluación completa y
  no fraccionable sobre test.

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
