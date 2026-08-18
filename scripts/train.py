#!/usr/bin/env python3
"""Entrena el baseline versionado y registra el run en MLflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from polysight_seg.training.runner import run_training


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/training/unet-resnet34-baseline.yaml"),
    )
    parser.add_argument(
        "--max-train-batches",
        type=int,
        default=None,
        help="Límite exclusivo para smokes; omitir en entrenamiento completo.",
    )
    parser.add_argument(
        "--max-validation-batches",
        type=int,
        default=None,
        help="Límite exclusivo para smokes; omitir en entrenamiento completo.",
    )
    args = parser.parse_args()
    run_training(
        args.config,
        max_train_batches=args.max_train_batches,
        max_validation_batches=args.max_validation_batches,
    )


if __name__ == "__main__":
    main()
