"""CLI para generar el manifest reproducible de Kvasir-SEG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polysight_seg.data.manifest import generate_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dataset",
        nargs="?",
        type=Path,
        default=Path("data/raw/kvasir-seg"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/kvasir-seg"),
    )
    args = parser.parse_args()
    print(json.dumps(generate_manifest(args.dataset, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
