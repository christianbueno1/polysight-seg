"""Contratos para las dos réplicas adicionales del baseline."""

from __future__ import annotations

import copy
import csv
import json
import statistics
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_CONFIGS = PROJECT_ROOT / "configs/training"
EVALUATION_CONFIGS = PROJECT_ROOT / "configs/evaluation"


def _load(name: str) -> dict:
    with (TRAINING_CONFIGS / name).open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _load_evaluation(name: str) -> dict:
    with (EVALUATION_CONFIGS / name).open(encoding="utf-8") as stream:
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

    def test_evaluations_are_fixed_to_each_selected_checkpoint(self) -> None:
        expected = {
            "unet-resnet34-seed-20260818.yaml": {
                "seed": 20260818,
                "run_id": "5be446e9eabd40e4ba92d4d2873d333e",
                "epoch": 32,
                "val_dice": 0.9039459519026185,
                "sha256": "e4d8121dca05927d50566ee851c8a008e3e4c7f9efa1aa537ee9c2a4278fa772",
            },
            "unet-resnet34-seed-20260819.yaml": {
                "seed": 20260819,
                "run_id": "59a6e9f0b6124001a1af360b4f22dea2",
                "epoch": 25,
                "val_dice": 0.8942383180146468,
                "sha256": "318c2ccda08c52a30da51ccdfa0f4cd924a932949df2ee3d67811326528a277d",
            },
        }
        output_directories = set()
        for filename, values in expected.items():
            with self.subTest(filename=filename):
                config = _load_evaluation(filename)
                checkpoint = config["checkpoint"]
                self.assertEqual(config["run"]["seed"], values["seed"])
                self.assertEqual(config["run"]["split"], "test")
                self.assertEqual(checkpoint["source_run_id"], values["run_id"])
                self.assertEqual(checkpoint["selected_epoch"], values["epoch"])
                self.assertEqual(checkpoint["selection_value"], values["val_dice"])
                self.assertEqual(checkpoint["sha256"], values["sha256"])
                self.assertEqual(config["prediction"]["threshold"], 0.5)
                output_directories.add(config["outputs"]["directory"])
        self.assertEqual(len(output_directories), 2)

    def test_versioned_stability_summary_matches_individual_runs(self) -> None:
        results = PROJECT_ROOT / "docs/results/seed-stability"
        with (results / "runs.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        summary = json.loads((results / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 3)
        self.assertEqual({int(row["seed"]) for row in rows}, {20260817, 20260818, 20260819})
        self.assertEqual(summary["ddof"], 1)
        fields = {
            "best_val_dice": "best_val_dice",
            "test_dice": "test_dice",
            "test_iou": "test_iou",
            "test_precision": "test_precision",
            "test_recall": "test_recall",
        }
        for summary_name, csv_name in fields.items():
            with self.subTest(metric=summary_name):
                values = [float(row[csv_name]) for row in rows]
                observed = summary["metrics"][summary_name]
                self.assertEqual(observed["mean"], statistics.mean(values))
                self.assertEqual(
                    observed["sample_standard_deviation"], statistics.stdev(values)
                )


if __name__ == "__main__":
    unittest.main()
