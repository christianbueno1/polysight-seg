# Trabajos Slurm

Aquí se mantendrán los archivos `.sbatch` utilizados para solicitar recursos y ejecutar
trabajos reproducibles en CEDIA HPC.

- `setup_cluster_env.sbatch`: crea `.venv-cluster` y registra módulos, runtime y
  dependencias efectivas desde un nodo de cómputo CPU.
- `prepare_dataset.sbatch`: reconstruye y valida dataset, manifest y splits desde el ZIP
  original almacenado fuera de Git.
