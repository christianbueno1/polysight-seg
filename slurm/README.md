# Trabajos Slurm

Aquí se mantendrán los archivos `.sbatch` utilizados para solicitar recursos y ejecutar
trabajos reproducibles en CEDIA HPC.

- `setup_cluster_env.sbatch`: crea `.venv-cluster` y registra módulos, runtime y
  dependencias efectivas desde un nodo de cómputo CPU.
- `validate_mlflow.sbatch`: prueba en `cpu-dev` la versión fijada y un ciclo efímero
  servidor-cliente con SQLite, métricas y artefactos.
- `prepare_dataset.sbatch`: reconstruye y valida dataset, manifest y splits desde el ZIP
  original almacenado fuera de Git.
- `test_baseline_cpu.sbatch`: ejecuta contratos numéricos del modelo, pérdida y métricas
  en `cpu-dev`, sin solicitar GPU.
- `smoke_training_engine.sbatch`: valida en `cpu-dev` agregación por época, actualización
  en train e inmutabilidad del modelo durante validation.
- `test_training_cpu.sbatch`: ejecuta la suite CPU de loops, checkpoints, tracking y
  runner, seguida por un servidor MLflow efímero real.
- `smoke_baseline.sbatch`: ejecuta un batch real del baseline con pesos ImageNet,
  forward/backward y una A100 en `gpu-dev`.
- `test_evaluation_cpu.sbatch`: valida métricas y artefactos con casos sintéticos sin GPU.
- `smoke_evaluation_gpu.sbatch`: prueba `best.pt` y dos batches reales de validation
  antes de habilitar la evaluación única sobre test.
- `evaluate_test.sbatch`: evalúa una sola vez `best.pt` sobre las 150 imágenes de test.
- `train_baseline.sbatch`: entrena la configuración indicada mediante la variable
  `TRAINING_CONFIG`; usa el baseline original si no se define.

## Réplicas encadenadas por semilla

Desde la raíz del proyecto en CEDIA:

```bash
scripts/submit_seed_replicates.sh
```

El comando envía primero la semilla `20260818` y crea la semilla `20260819` con
dependencia `afterok`. La segunda solo puede comenzar si la primera termina con éxito.
Ambas usan el mismo split e hiperparámetros del baseline; un contrato local verifica que
la única diferencia de configuración sea `run.seed`.

Cuando ambos entrenamientos terminen y sus checkpoints estén fijados por SHA-256, las
evaluaciones completas de test se envían también en cadena:

```bash
scripts/submit_seed_evaluations.sh
```

Cada semilla escribe en un directorio de evaluación separado y conserva el umbral `0.5`.

## Validación cruzada de cinco folds

El entrenamiento se prepara y envía desde CEDIA con:

```bash
scripts/submit_cross_validation_training.sh
```

El script regenera los folds y envía cinco jobs seriales. Cada job depende con `afterok`
del anterior, usa un directorio de checkpoints independiente y recibe un puerto MLflow
derivado de su `SLURM_JOB_ID`. El puerto por job evita reutilizar `5000` si quedó un
servidor huérfano; SQLite continúa protegido porque nunca hay dos escritores CV activos.

Esta es la etapa 1. Al terminar, se fijan run, época, Dice de validation y SHA-256 de
cada checkpoint. Solo después se versionan y encadenan las cinco evaluaciones externas.
