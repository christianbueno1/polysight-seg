#!/usr/bin/env bash
#SBATCH --job-name=polysight-data
#SBATCH --partition=cpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
export PYTHONPATH=src

srun python scripts/smoke_data_pipeline.py
