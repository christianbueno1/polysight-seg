"""Contratos ligeros entre resultados canónicos y documentación final."""

from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIRECTORY = PROJECT_ROOT / "docs/results/test"


class DocumentationConsistencyTest(unittest.TestCase):
    """Evita publicar cifras o estado experimental contradictorios."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.metrics = json.loads(
            (RESULTS_DIRECTORY / "metrics.json").read_text(encoding="utf-8")
        )
        with (RESULTS_DIRECTORY / "per-image-metrics.csv").open(
            encoding="utf-8", newline=""
        ) as file:
            cls.per_image = list(csv.DictReader(file))
        cls.readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        cls.presentation = (PROJECT_ROOT / "docs/presentacion.md").read_text(
            encoding="utf-8"
        )
        cls.final_report = (PROJECT_ROOT / "docs/final-report.md").read_text(
            encoding="utf-8"
        )
        cls.model_card = (PROJECT_ROOT / "docs/model-card.md").read_text(
            encoding="utf-8"
        )

    def test_exact_aggregate_metrics_are_in_formal_documents(self) -> None:
        for metric in ("dice", "iou", "precision", "recall"):
            expected = str(self.metrics[metric])
            for name, document in (
                ("final-report", self.final_report),
                ("model-card", self.model_card),
            ):
                with self.subTest(metric=metric, document=name):
                    self.assertIn(expected, document)

    def test_rounded_metrics_are_in_summary_documents(self) -> None:
        for metric in ("dice", "iou", "precision", "recall"):
            dot_value = f"{self.metrics[metric]:.4f}"
            comma_value = dot_value.replace(".", ",")
            with self.subTest(metric=metric, document="README"):
                self.assertIn(dot_value, self.readme)
            with self.subTest(metric=metric, document="presentacion"):
                self.assertIn(comma_value, self.presentation)

    def test_per_image_summary_matches_canonical_csv(self) -> None:
        dice_values = [float(row["dice"]) for row in self.per_image]
        sorted_values = sorted(dice_values)
        middle = len(sorted_values) // 2
        expected = {
            "minimum": min(dice_values),
            "median": (sorted_values[middle - 1] + sorted_values[middle]) / 2,
            "maximum": max(dice_values),
        }
        for value in expected.values():
            with self.subTest(value=value):
                self.assertIn(str(value), self.model_card)
                self.assertIn(str(value), self.final_report)

    def test_final_documents_do_not_announce_test_as_pending(self) -> None:
        stale_claim = "se evaluará en la siguiente fase"
        self.assertNotIn(stale_claim, self.presentation)
        self.assertIn("una sola vez sobre las 150 imágenes de test", self.presentation)


if __name__ == "__main__":
    unittest.main()
