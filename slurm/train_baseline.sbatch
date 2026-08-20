#!/usr/bin/env bash
#SBATCH --job-name=polysight-baseline
#SBATCH --partition=gpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:a100-sxm4-40gb:1
#SBATCH --time=06:00:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2
module load cuda/12.4

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"
export NO_ALBUMENTATIONS_UPDATE=1
export POLYSIGHT_MLFLOW_PORT="${POLYSIGHT_MLFLOW_PORT:-$((15000 + SLURM_JOB_ID % 40000))}"

nvidia-smi
training_config="${TRAINING_CONFIG:-configs/training/unet-resnet34-baseline.yaml}"
if [[ ! -f "${training_config}" ]]; then
  echo "No existe la configuración de entrenamiento: ${training_config}" >&2
  exit 2
fi
echo "TRAINING_CONFIG=${training_config}"
echo "POLYSIGHT_MLFLOW_PORT=${POLYSIGHT_MLFLOW_PORT}"
srun python scripts/train.py --config "${training_config}"
