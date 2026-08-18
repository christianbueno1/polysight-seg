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
