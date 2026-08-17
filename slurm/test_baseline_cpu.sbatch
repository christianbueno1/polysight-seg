#!/usr/bin/env bash
#SBATCH --job-name=polysight-contracts
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

python - <<'PY'
import torch

if torch.cuda.is_available():
    raise SystemExit("El job de contratos no debe recibir una GPU")
print(f"python_contract_device=cpu torch={torch.__version__}")
PY

srun python -m unittest discover \
  -s tests \
  -p 'test_baseline_contracts.py' \
  -v
