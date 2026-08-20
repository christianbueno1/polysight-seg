"""Contratos locales del experimento de validación cruzada."""

from __future__ import annotations

import csv
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from polysight_seg.tracking_config import apply_mlflow_environment


ROOT = Path(__file__).resolve().parents[1]


class CrossValidationContractTest(unittest.TestCase):
    def test_each_sample_is_external_test_exactly_once(self) -> None:
        appearances: dict[str, int] = {}
        for fold in range(1, 6):
            path = ROOT / f"data/processed/kvasir-seg/cross-validation/fold-{fold:02d}/splits.csv"
            with path.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            counts = {name: sum(row["split"] == name for row in rows) for name in ("train", "validation", "test")}
            self.assertEqual(counts, {"train": 700, "validation": 100, "test": 200})
            for row in rows:
                if row["split"] == "test":
                    appearances[row["sample_id"]] = appearances.get(row["sample_id"], 0) + 1
        self.assertEqual(len(appearances), 1000)
        self.assertEqual(set(appearances.values()), {1})

    def test_training_configs_keep_protocol_and_isolate_outputs(self) -> None:
        checkpoints = set()
        for fold in range(1, 6):
            suffix = f"{fold:02d}"
            with (ROOT / f"configs/training/unet-resnet34-cv-fold-{suffix}.yaml").open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            self.assertEqual(config["run"]["seed"], 20260817)
            self.assertFalse(config["test"]["enabled"])
            self.assertEqual(config["validation"]["split"], "validation")
            self.assertEqual(config["references"]["data_config"], f"configs/data/kvasir-seg-cv-fold-{suffix}.yaml")
            checkpoints.add(config["checkpointing"]["directory"])
        self.assertEqual(len(checkpoints), 5)

    def test_mlflow_port_override_is_validated_and_updates_uri(self) -> None:
        config = {"server": {"host": "127.0.0.1", "port": 5000, "tracking_uri": "http://127.0.0.1:5000"}}
        with patch.dict(os.environ, {"POLYSIGHT_MLFLOW_PORT": "23456"}):
            resolved = apply_mlflow_environment(config)
        self.assertEqual(resolved["server"]["port"], 23456)
        self.assertEqual(resolved["server"]["tracking_uri"], "http://127.0.0.1:23456")
        self.assertEqual(config["server"]["port"], 5000)
        with patch.dict(os.environ, {"POLYSIGHT_MLFLOW_PORT": "80"}):
            with self.assertRaises(ValueError):
                apply_mlflow_environment(config)


if __name__ == "__main__":
    unittest.main()
