#!/usr/bin/env bash
# Envía las cinco evaluaciones externas CV de forma serial mediante afterok.

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"

python scripts/generate_cross_validation.py >/dev/null

job_script="slurm/evaluate_test.sbatch"
previous_job_id=""
job_ids=()

for fold in 01 02 03 04 05; do
  config="configs/evaluation/unet-resnet34-cv-fold-${fold}.yaml"
  if [[ ! -f "${config}" || ! -f "${job_script}" ]]; then
    echo "No existe el archivo requerido para fold ${fold}" >&2
    exit 2
  fi
  if [[ -z "${previous_job_id}" ]]; then
    submission="$(
      sbatch --parsable \
        --job-name="polysight-cv-eval-${fold}" \
        --output="slurm-polysight-cv-eval-${fold}-%j.out" \
        --export="ALL,EVALUATION_CONFIG=${config}" \
        "${job_script}"
    )"
  else
    submission="$(
      sbatch --parsable \
        --dependency="afterok:${previous_job_id}" \
        --job-name="polysight-cv-eval-${fold}" \
        --output="slurm-polysight-cv-eval-${fold}-%j.out" \
        --export="ALL,EVALUATION_CONFIG=${config}" \
        "${job_script}"
    )"
  fi
  previous_job_id="${submission%%;*}"
  job_ids+=("${previous_job_id}")
done

printf '{"fold_01":"%s","fold_02":"%s","fold_03":"%s","fold_04":"%s","fold_05":"%s","dependency":"afterok serial"}\n' \
  "${job_ids[0]}" "${job_ids[1]}" "${job_ids[2]}" "${job_ids[3]}" "${job_ids[4]}"
