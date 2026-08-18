#!/usr/bin/env bash
#SBATCH --job-name=polysight-train-loop
#SBATCH --partition=cpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"

echo "commit=$(git rev-parse HEAD)"
srun python scripts/smoke_training_engine.py
