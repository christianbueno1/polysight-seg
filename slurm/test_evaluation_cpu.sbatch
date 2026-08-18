#!/usr/bin/env bash
#SBATCH --job-name=polysight-evaluation-tests
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
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}:src"
export NO_ALBUMENTATIONS_UPDATE=1

python - <<'PY'
import torch

if torch.cuda.is_available():
    raise SystemExit("Las pruebas de evaluación CPU no deben recibir GPU")
print(f"evaluation_contract_device=cpu torch={torch.__version__}")
PY

srun python -m unittest discover \
  -s tests \
  -p 'test_evaluation_components.py' \
  -v
