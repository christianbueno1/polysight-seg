#!/usr/bin/env bash
#SBATCH --job-name=polysight-data-prep
#SBATCH --partition=cpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"

python scripts/prepare_dataset.py \
  "${HOME}/datasets/hyper-kvasir-segmented-images.zip"
python scripts/validate_dataset.py
python scripts/generate_manifest.py
python scripts/generate_splits.py
python scripts/validate_splits.py

sha256sum \
  data/processed/kvasir-seg/manifest.csv \
  data/processed/kvasir-seg/summary.json \
  data/processed/kvasir-seg/splits.csv \
  data/processed/kvasir-seg/splits-summary.json
