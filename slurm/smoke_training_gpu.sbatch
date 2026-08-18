#!/usr/bin/env bash
#SBATCH --job-name=polysight-training-smoke
#SBATCH --partition=gpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:a100-sxm4-40gb:1
#SBATCH --time=00:15:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2
module load cuda/12.4

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"
export NO_ALBUMENTATIONS_UPDATE=1

nvidia-smi
srun python scripts/train.py \
  --max-train-batches 2 \
  --max-validation-batches 2
