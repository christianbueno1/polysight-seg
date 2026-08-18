#!/usr/bin/env python3
"""Evalúa el checkpoint seleccionado sin modificar sus pesos."""

from __future__ import annotations

import argparse
from pathlib import Path

from polysight_seg.evaluation.runner import run_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/evaluation/unet-resnet34-baseline.yaml"),
    )
    parser.add_argument(
        "--split",
        choices=("validation", "test"),
        default=None,
        help="Solo se sobrescribe para el smoke limitado en validation.",
    )
    parser.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Exclusivo del smoke en validation; está prohibido para test.",
    )
    args = parser.parse_args()
    run_evaluation(args.config, split_override=args.split, max_batches=args.max_batches)


if __name__ == "__main__":
    main()

