"""Contratos locales del experimento de validación cruzada."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
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

    def test_external_evaluations_are_fixed_to_audited_checkpoints(self) -> None:
        with (ROOT / "docs/results/cross-validation/training-runs.csv").open(
            newline="", encoding="utf-8"
        ) as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual([int(row["fold"]) for row in rows], [1, 2, 3, 4, 5])
        outputs = set()
        for row in rows:
            suffix = f"{int(row['fold']):02d}"
            with (
                ROOT / f"configs/evaluation/unet-resnet34-cv-fold-{suffix}.yaml"
            ).open(encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
            checkpoint = config["checkpoint"]
            self.assertEqual(config["run"]["split"], "test")
            self.assertEqual(config["prediction"]["threshold"], 0.5)
            self.assertEqual(checkpoint["path"], row["checkpoint_path"])
            self.assertEqual(checkpoint["source_run_id"], row["run_id"])
            self.assertEqual(checkpoint["selected_epoch"], int(row["selected_epoch"]))
            self.assertEqual(checkpoint["selection_value"], float(row["best_val_dice"]))
            self.assertEqual(checkpoint["sha256"], row["checkpoint_sha256"])
            self.assertEqual(len(checkpoint["sha256"]), hashlib.sha256().digest_size * 2)
            outputs.add(config["outputs"]["directory"])
        self.assertEqual(len(outputs), 5)

    def test_versioned_external_summary_matches_fold_runs(self) -> None:
        results = ROOT / "docs/results/cross-validation"
        with (results / "evaluation-runs.csv").open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        summary = json.loads((results / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 5)
        self.assertEqual(sum(int(row["sample_count"]) for row in rows), 1000)
        self.assertEqual(summary["ddof"], 1)
        for metric in ("dice", "iou", "precision", "recall"):
            values = [float(row[metric]) for row in rows]
            observed = summary["fold_metrics"][metric]
            self.assertEqual(observed["mean"], statistics.mean(values))
            self.assertEqual(observed["sample_standard_deviation"], statistics.stdev(values))
        counts = {name: sum(int(row[name]) for row in rows) for name in ("tp", "fp", "fn", "tn")}
        self.assertEqual(counts, {name: summary["pooled_out_of_fold"][name] for name in counts})
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        self.assertEqual(summary["pooled_out_of_fold"]["dice"], 2 * tp / (2 * tp + fp + fn))


if __name__ == "__main__":
    unittest.main()
