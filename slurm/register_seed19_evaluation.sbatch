#!/usr/bin/env bash
#SBATCH --job-name=polysight-register-seed19
#SBATCH --partition=cpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"
export NO_ALBUMENTATIONS_UPDATE=1
export RECOVERY_CODE_COMMIT="$(git rev-parse HEAD)"

srun python scripts/register_existing_evaluation.py \
  --evaluation-config configs/evaluation/unet-resnet34-seed-20260819.yaml \
  --output evaluation/unet-resnet34-seed-20260819/test \
  --original-job-id 23460 \
  --original-code-commit ed98bfe10fd126cc5257f5dc6f061a5cacb7707c \
  --port 5001
