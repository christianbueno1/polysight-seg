#!/usr/bin/env bash
# Envía a Slurm dos réplicas del baseline enlazadas mediante afterok.

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"

seed_18_config="configs/training/unet-resnet34-seed-20260818.yaml"
seed_19_config="configs/training/unet-resnet34-seed-20260819.yaml"
job_script="slurm/train_baseline.sbatch"

for required_file in "${seed_18_config}" "${seed_19_config}" "${job_script}"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "No existe el archivo requerido: ${required_file}" >&2
    exit 2
  fi
done

first_submission="$(
  sbatch --parsable \
    --job-name=polysight-seed18 \
    --output=slurm-polysight-seed18-%j.out \
    --export="ALL,TRAINING_CONFIG=${seed_18_config}" \
    "${job_script}"
)"
first_job_id="${first_submission%%;*}"

second_submission="$(
  sbatch --parsable \
    --dependency="afterok:${first_job_id}" \
    --job-name=polysight-seed19 \
    --output=slurm-polysight-seed19-%j.out \
    --export="ALL,TRAINING_CONFIG=${seed_19_config}" \
    "${job_script}"
)"
second_job_id="${second_submission%%;*}"

printf '{"seed_20260818_job":"%s","seed_20260819_job":"%s","dependency":"afterok:%s"}\n' \
  "${first_job_id}" "${second_job_id}" "${first_job_id}"
