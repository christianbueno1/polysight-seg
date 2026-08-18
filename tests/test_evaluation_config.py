"""Contratos ligeros de la evaluación final del baseline."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs/evaluation/unet-resnet34-baseline.yaml"


class EvaluationConfigurationTest(unittest.TestCase):
    """Impide consumir test con un checkpoint o protocolo ambiguo."""

    @classmethod
    def setUpClass(cls) -> None:
        with CONFIG_PATH.open(encoding="utf-8") as file:
            cls.config = yaml.safe_load(file)

    def test_schema_split_and_references_are_fixed(self) -> None:
        self.assertEqual(self.config["schema_version"], 1)
        self.assertEqual(self.config["run"]["split"], "test")
        self.assertEqual(self.config["run"]["seed"], 20260817)
        for config_path in self.config["references"].values():
            with self.subTest(config_path=config_path):
                self.assertTrue((PROJECT_ROOT / config_path).is_file())

    def test_selected_checkpoint_is_best_and_auditable(self) -> None:
        checkpoint = self.config["checkpoint"]
        self.assertTrue(checkpoint["path"].endswith("/best.pt"))
        self.assertNotIn("last.pt", checkpoint["path"])
        self.assertRegex(checkpoint["sha256"], re.compile(r"^[0-9a-f]{64}$"))
        self.assertEqual(checkpoint["selection_metric"], "val_dice")
        self.assertEqual(checkpoint["selected_epoch"], 22)

    def test_operational_threshold_cannot_be_changed_by_test(self) -> None:
        self.assertEqual(self.config["prediction"]["threshold"], 0.5)
        analysis = self.config["threshold_analysis"]
        self.assertTrue(analysis["enabled"])
        self.assertEqual(analysis["purpose"], "descriptive_only")
        self.assertFalse(analysis["changes_operational_threshold"])

    def test_outputs_preserve_reconstructable_evidence(self) -> None:
        outputs = self.config["outputs"]
        required = {
            "metrics",
            "per_image_metrics",
            "confusion_counts",
            "confusion_normalized_true",
            "threshold_curve",
            "probability_maps_directory",
            "plots_directory",
            "qualitative_directory",
        }
        self.assertTrue(required.issubset(outputs))
        self.assertTrue(self.config["prediction"]["preserve_probability_maps"])
        self.assertTrue(self.config["tracking"]["create_separate_run"])


if __name__ == "__main__":
    unittest.main()

