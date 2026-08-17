"""Pruebas de splits y configuración que no requieren PyTorch."""

from __future__ import annotations

import csv
import random
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from polysight_seg.data.splits import generate_splits  # noqa: E402


class SplitGenerationTest(unittest.TestCase):
    def _write_manifest(self, path: Path, rows: list[dict[str, str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=("sample_id", "duplicate_group", "foreground_fraction"),
            )
            writer.writeheader()
            writer.writerows(rows)

    def test_assignments_ignore_manifest_row_order_and_keep_groups(self) -> None:
        rows = [
            {
                "sample_id": f"sample-{index:02d}",
                "duplicate_group": "shared" if index in {0, 1} else "",
                "foreground_fraction": f"{(index + 1) / 100:.2f}",
            }
            for index in range(12)
        ]
        shuffled = list(rows)
        random.Random(99).shuffle(shuffled)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_manifest = root / "first.csv"
            second_manifest = root / "second.csv"
            first_output = root / "first"
            second_output = root / "second"
            self._write_manifest(first_manifest, rows)
            self._write_manifest(second_manifest, shuffled)

            first = generate_splits(first_manifest, first_output)
            second = generate_splits(second_manifest, second_output)

            self.assertEqual(first["assignment_sha256"], second["assignment_sha256"])
            self.assertEqual(
                (first_output / "splits.csv").read_bytes(),
                (second_output / "splits.csv").read_bytes(),
            )
            with (first_output / "splits.csv").open(encoding="utf-8") as file:
                assignments = {
                    row["sample_id"]: row["split"] for row in csv.DictReader(file)
                }
            self.assertEqual(assignments["sample-00"], assignments["sample-01"])


class DataConfigurationTest(unittest.TestCase):
    def test_evaluation_is_deterministic_and_mask_uses_nearest(self) -> None:
        config_path = PROJECT_ROOT / "configs/data/kvasir-seg.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        self.assertEqual(config["dataset"]["mask_threshold"], 128)
        self.assertEqual(config["input"]["mask_interpolation"], "nearest")
        self.assertFalse(config["transforms"]["validation"]["random_augmentations"])
        self.assertFalse(config["transforms"]["test"]["random_augmentations"])


if __name__ == "__main__":
    unittest.main()
