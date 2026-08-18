"""Contratos ligeros de la configuración versionada de entrenamiento."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "configs/training/unet-resnet34-baseline.yaml"


class TrainingConfigurationTest(unittest.TestCase):
    """Evita cambios silenciosos en el protocolo experimental."""

    @classmethod
    def setUpClass(cls) -> None:
        with CONFIG_PATH.open(encoding="utf-8") as file:
            cls.config = yaml.safe_load(file)

    def test_schema_and_references_are_valid(self) -> None:
        self.assertEqual(self.config["schema_version"], 1)
        for config_path in self.config["references"].values():
            with self.subTest(config_path=config_path):
                self.assertTrue((PROJECT_ROOT / config_path).is_file())

    def test_baseline_budget_and_seed_are_fixed(self) -> None:
        run = self.config["run"]
        self.assertEqual(run["seed"], 20260817)
        self.assertEqual(run["max_epochs"], 50)
        self.assertEqual(self.config["validation"]["every_n_epochs"], 1)

    def test_optimizer_and_scheduler_are_explicit(self) -> None:
        optimizer = self.config["optimizer"]
        scheduler = self.config["scheduler"]
        self.assertEqual(optimizer["name"], "adamw")
        self.assertAlmostEqual(optimizer["learning_rate"], 1.0e-4)
        self.assertAlmostEqual(optimizer["weight_decay"], 1.0e-4)
        self.assertEqual(scheduler["name"], "reduce_lr_on_plateau")
        self.assertGreater(scheduler["patience_epochs"], 0)
        self.assertLess(scheduler["min_learning_rate"], optimizer["learning_rate"])

    def test_selection_uses_only_validation_dice(self) -> None:
        selection = self.config["selection"]
        self.assertEqual(selection["metric"], "val_dice")
        self.assertEqual(selection["mode"], "max")
        self.assertTrue(self.config["early_stopping"]["enabled"])
        self.assertGreater(
            self.config["early_stopping"]["patience_epochs"],
            self.config["scheduler"]["patience_epochs"],
        )

    def test_test_split_is_isolated(self) -> None:
        self.assertFalse(self.config["test"]["enabled"])
        self.assertEqual(self.config["test"]["phase"], 6)


if __name__ == "__main__":
    unittest.main()
