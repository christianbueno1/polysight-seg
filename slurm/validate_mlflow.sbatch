#!/usr/bin/env bash
#SBATCH --job-name=polysight-mlflow
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
export NO_ALBUMENTATIONS_UPDATE=1

echo "commit=$(git rev-parse HEAD)"
echo "python=$(python --version 2>&1)"
srun python scripts/validate_mlflow.py
python scripts/train.py --help
