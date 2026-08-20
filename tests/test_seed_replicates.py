"""Contratos para las dos réplicas adicionales del baseline."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_CONFIGS = PROJECT_ROOT / "configs/training"


def _load(name: str) -> dict:
    with (TRAINING_CONFIGS / name).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


class SeedReplicateConfigurationTest(unittest.TestCase):
    def test_replicates_change_only_the_seed(self) -> None:
        baseline = _load("unet-resnet34-baseline.yaml")
        expected_seeds = {
            "unet-resnet34-seed-20260818.yaml": 20260818,
            "unet-resnet34-seed-20260819.yaml": 20260819,
        }

        for filename, expected_seed in expected_seeds.items():
            with self.subTest(filename=filename):
                replicate = _load(filename)
                self.assertEqual(replicate["run"]["seed"], expected_seed)
                normalized = copy.deepcopy(replicate)
                normalized["run"]["seed"] = baseline["run"]["seed"]
                self.assertEqual(normalized, baseline)

    def test_all_three_seeds_are_distinct(self) -> None:
        filenames = (
            "unet-resnet34-baseline.yaml",
            "unet-resnet34-seed-20260818.yaml",
            "unet-resnet34-seed-20260819.yaml",
        )
        seeds = {_load(filename)["run"]["seed"] for filename in filenames}
        self.assertEqual(seeds, {20260817, 20260818, 20260819})


if __name__ == "__main__":
    unittest.main()
