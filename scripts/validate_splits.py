"""CLI para validar cobertura y aislamiento de los splits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polysight_seg.data.splits import validate_splits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path("data/processed/kvasir-seg/manifest.csv"),
    )
    parser.add_argument(
        "--splits",
        type=Path,
        default=Path("data/processed/kvasir-seg/splits.csv"),
    )
    args = parser.parse_args()
    print(json.dumps(validate_splits(args.manifest, args.splits), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
