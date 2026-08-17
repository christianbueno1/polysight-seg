"""CLI para generar splits deterministas de Kvasir-SEG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polysight_seg.data.splits import DEFAULT_SEED, generate_splits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path("data/processed/kvasir-seg/manifest.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/kvasir-seg"),
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    print(json.dumps(generate_splits(args.manifest, args.output, args.seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
