#!/usr/bin/env python3
"""Deriva configuraciones declarativas para los cinco entrenamientos CV."""

from __future__ import annotations

import copy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _write(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def main() -> None:
    baseline_data = _load(ROOT / "configs/data/kvasir-seg.yaml")
    baseline_training = _load(ROOT / "configs/training/unet-resnet34-baseline.yaml")
    for fold in range(1, 6):
        suffix = f"{fold:02d}"
        data = copy.deepcopy(baseline_data)
        data["dataset"]["name"] = f"kvasir-seg-cv-fold-{suffix}"
        data["dataset"]["splits"] = (
            f"data/processed/kvasir-seg/cross-validation/fold-{suffix}/splits.csv"
        )
        data_path = ROOT / f"configs/data/kvasir-seg-cv-fold-{suffix}.yaml"
        _write(data_path, data)

        training = copy.deepcopy(baseline_training)
        training["run"]["name"] = f"unet-resnet34-cv-fold-{suffix}"
        training["references"]["data_config"] = str(data_path.relative_to(ROOT))
        training["checkpointing"]["directory"] = (
            f"checkpoints/cross-validation/fold-{suffix}"
        )
        training["test"]["phase"] = 11
        _write(
            ROOT / f"configs/training/unet-resnet34-cv-fold-{suffix}.yaml",
            training,
        )


if __name__ == "__main__":
    main()
