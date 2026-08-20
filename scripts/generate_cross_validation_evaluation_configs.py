#!/usr/bin/env python3
"""Fija evaluaciones externas CV desde checkpoints de entrenamiento auditados."""

from __future__ import annotations

import copy
import csv
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs/results/cross-validation/training-runs.csv"
BASELINE = ROOT / "configs/evaluation/unet-resnet34-baseline.yaml"


def main() -> None:
    with BASELINE.open(encoding="utf-8") as stream:
        baseline = yaml.safe_load(stream)
    with RUNS.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if [int(row["fold"]) for row in rows] != [1, 2, 3, 4, 5]:
        raise ValueError("Se requieren exactamente los folds 1–5 en orden")

    for row in rows:
        fold = int(row["fold"])
        suffix = f"{fold:02d}"
        config = copy.deepcopy(baseline)
        config["run"]["name"] = f"unet-resnet34-cv-fold-{suffix}-external"
        config["references"]["data_config"] = (
            f"configs/data/kvasir-seg-cv-fold-{suffix}.yaml"
        )
        config["checkpoint"] = {
            "path": row["checkpoint_path"],
            "sha256": row["checkpoint_sha256"],
            "source_run_id": row["run_id"],
            "selected_epoch": int(row["selected_epoch"]),
            "selection_metric": "val_dice",
            "selection_value": float(row["best_val_dice"]),
        }
        config["outputs"]["directory"] = f"evaluation/cross-validation/fold-{suffix}"
        config["tracking"]["run_mode"] = "cross_validation_external_evaluation"
        output = ROOT / f"configs/evaluation/unet-resnet34-cv-fold-{suffix}.yaml"
        output.write_text(
            yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
