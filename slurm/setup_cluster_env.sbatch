#!/usr/bin/env bash
#SBATCH --job-name=polysight-env
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
module load cuda/12.4

cd "${SLURM_SUBMIT_DIR}"

python -m venv --system-site-packages .venv-cluster
source .venv-cluster/bin/activate
# Priorizar paquetes fijados del virtualenv sin ocultar PyTorch provisto por el módulo.
export PYTHONPATH="${VIRTUAL_ENV}/lib/python3.11/site-packages:${PYTHONPATH:-}"
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip check

echo "=== commit ==="
git rev-parse HEAD
echo "=== modules ==="
module list 2>&1
echo "=== runtime ==="
python --version
python - <<'PY'
import torch

if "/pytorch/2.2/" not in torch.__file__:
    raise SystemExit(f"PyTorch no proviene del módulo de CEDIA: {torch.__file__}")

print(f"torch={torch.__version__}")
print(f"torch_cuda={torch.version.cuda}")
print(f"cudnn={torch.backends.cudnn.version()}")
print(f"torch_path={torch.__file__}")
PY
echo "=== pip ==="
python -m pip --version
python -m pip freeze
