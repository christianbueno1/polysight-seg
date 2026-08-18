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
