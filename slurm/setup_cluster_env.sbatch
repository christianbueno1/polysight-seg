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
# El módulo exporta un PYTHONPATH que precede al site-packages del virtualenv.
# El entorno conserva acceso a PyTorch mediante --system-site-packages.
unset PYTHONPATH
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

print(f"torch={torch.__version__}")
print(f"torch_cuda={torch.version.cuda}")
print(f"cudnn={torch.backends.cudnn.version()}")
print(f"torch_path={torch.__file__}")
PY
echo "=== pip ==="
python -m pip --version
python -m pip freeze
