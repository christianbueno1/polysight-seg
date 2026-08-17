"""CLI para validar la copia extraída de Kvasir-SEG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polysight_seg.data.validate import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dataset",
        nargs="?",
        type=Path,
        default=Path("data/raw/kvasir-seg"),
    )
    args = parser.parse_args()
    print(json.dumps(validate_dataset(args.dataset), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
