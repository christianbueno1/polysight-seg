# Configuraciones

Aquí se versionarán las configuraciones declarativas de datos, modelos, entrenamiento
y evaluación. No se guardarán secretos ni rutas personales.

## Configuraciones disponibles

- `data/kvasir-seg.yaml`: rutas, DataLoader, resolución, normalización y transformaciones.
- `models/unet-resnet34.yaml`: contrato del baseline U-Net con encoder ResNet-34.
- `training/unet-resnet34-baseline.yaml`: protocolo de optimización, reproducibilidad,
  selección, early stopping y checkpoints del primer entrenamiento.
- `tracking/mlflow.yaml`: servidor local al job, experimento y contrato de tracking.
- `evaluation/unet-resnet34-baseline.yaml`: checkpoint seleccionado, protocolo de test,
  métricas y artefactos de la evaluación final del baseline.
- `data/kvasir-seg-cv-fold-*.yaml`: selección de train, validation y fold externo para
  cada partición de la validación cruzada.
- `training/unet-resnet34-cv-fold-*.yaml`: cinco entrenamientos con arquitectura,
  hiperparámetros y semilla fijos; solo cambian datos, nombre y salida del fold.

La configuración del modelo conserva `activation: null`: la red devuelve logits y la
sigmoid con umbral se aplica solamente durante métricas o inferencia.
