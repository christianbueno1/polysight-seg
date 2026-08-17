#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"

python3 -c 'import sys; assert sys.version_info >= (3, 11), "Se requiere Python 3.11 o posterior para validar"'
python3 -c 'import pathlib, tomllib; tomllib.loads(pathlib.Path("pyproject.toml").read_text())'
python3 -m compileall -q src main.py tests
PYTHONPATH=src python3 -m unittest discover -s tests -v

for job_file in slurm/*.sbatch; do
    bash -n "${job_file}"
done

local_safe_paths=(
    main.py
    tests
    src/polysight_seg/__init__.py
    src/polysight_seg/cli.py
    src/polysight_seg/data/archive.py
    src/polysight_seg/data/manifest.py
    src/polysight_seg/data/masks.py
    src/polysight_seg/data/splits.py
    src/polysight_seg/data/validate.py
)
if rg -n '^\s*(from|import) torch' "${local_safe_paths[@]}"; then
    echo "El código validado localmente no debe importar PyTorch" >&2
    exit 1
fi

echo "Validaciones locales completadas sin PyTorch"
