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

if rg -n '^\s*(from|import) torch' src main.py tests; then
    echo "El código validado localmente no debe importar PyTorch" >&2
    exit 1
fi

echo "Validaciones locales completadas sin PyTorch"
