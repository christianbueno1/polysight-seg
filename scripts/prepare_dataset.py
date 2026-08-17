"""CLI para extraer Kvasir-SEG sin depender de PyTorch."""

from __future__ import annotations

import argparse
from pathlib import Path

from polysight_seg.data.archive import extract_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="ZIP oficial de Kvasir-SEG")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/kvasir-seg"),
        help="directorio de salida (default: data/raw/kvasir-seg)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = extract_dataset(args.archive, args.output)
    print(f"dataset_status={result}")
    print(f"dataset_path={args.output.resolve()}")


if __name__ == "__main__":
    main()
