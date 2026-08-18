"""Contratos CPU del motor de evaluación."""

from __future__ import annotations

import unittest
import csv
import json
import tempfile
from pathlib import Path

import numpy as np
import torch
from torch import nn

from polysight_seg.evaluation.engine import evaluate_segmentation
from polysight_seg.evaluation.artifacts import write_evaluation_artifacts


class IdentityModel(nn.Module):
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return inputs


def _batch() -> dict[str, object]:
    high = 10.0
    low = -10.0
    return {
        "image": torch.tensor(
            [
                [[[high, low], [high, low]]],
                [[[low, low], [high, high]]],
            ]
        ),
        "mask": torch.tensor(
            [
                [[[1.0, 0.0], [0.0, 0.0]]],
                [[[0.0, 1.0], [1.0, 1.0]]],
            ]
        ),
        "sample_id": ["sample-a", "sample-b"],
    }


class EvaluationEngineTest(unittest.TestCase):
    def test_aggregate_per_image_curve_and_probabilities(self) -> None:
        model = IdentityModel()
        result = evaluate_segmentation(
            model,
            [_batch()],
            torch.device("cpu"),
            threshold=0.5,
            threshold_values=[0.25, 0.5, 0.75],
        )
        self.assertFalse(model.training)
        self.assertEqual(result.aggregate["sample_count"], 2)
        self.assertEqual(result.aggregate["tp"], 3)
        self.assertEqual(result.aggregate["fp"], 1)
        self.assertEqual(result.aggregate["fn"], 1)
        self.assertEqual(result.aggregate["tn"], 3)
        self.assertAlmostEqual(result.aggregate["dice"], 0.75)
        self.assertEqual([row["sample_id"] for row in result.per_image], ["sample-a", "sample-b"])
        self.assertAlmostEqual(result.per_image[0]["foreground_fraction"], 0.25)
        self.assertEqual([row["threshold"] for row in result.threshold_curve], [0.25, 0.5, 0.75])
        self.assertEqual(set(result.probability_maps), {"sample-a", "sample-b"})
        self.assertEqual(result.probability_maps["sample-a"].dtype, np.float16)

    def test_probability_maps_can_be_disabled(self) -> None:
        result = evaluate_segmentation(
            IdentityModel(),
            [_batch()],
            torch.device("cpu"),
            threshold=0.5,
            threshold_values=[0.5],
            preserve_probability_maps=False,
        )
        self.assertEqual(result.probability_maps, {})

    def test_invalid_options_and_duplicate_ids_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_segmentation(
                IdentityModel(), [_batch()], torch.device("cpu"),
                threshold=0.5, threshold_values=[0.5, 0.5]
            )
        duplicate = _batch()
        duplicate["sample_id"] = ["same", "same"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            evaluate_segmentation(
                IdentityModel(), [duplicate], torch.device("cpu"),
                threshold=0.5, threshold_values=[0.5]
            )

    def test_artifacts_are_reconstructable_and_maps_are_compressed(self) -> None:
        result = evaluate_segmentation(
            IdentityModel(), [_batch()], torch.device("cpu"),
            threshold=0.5, threshold_values=[0.25, 0.5, 0.75]
        )
        outputs = {
            "metrics": "metrics.json",
            "per_image_metrics": "per-image-metrics.csv",
            "confusion_counts": "confusion-matrix-counts.csv",
            "confusion_normalized_true": "confusion-matrix-normalized-true.csv",
            "threshold_curve": "threshold-curve.csv",
            "probability_maps_directory": "probability-maps",
        }
        with tempfile.TemporaryDirectory() as temporary_dir:
            paths = write_evaluation_artifacts(result, Path(temporary_dir), outputs)
            metrics = json.loads(paths.metrics.read_text(encoding="utf-8"))
            self.assertEqual(metrics["tp"], 3)
            with paths.confusion_counts.open(newline="", encoding="utf-8") as stream:
                counts = list(csv.DictReader(stream))
            self.assertEqual(counts[0]["actual"], "background")
            self.assertEqual(int(counts[0]["predicted_background"]), 3)
            with paths.confusion_normalized_true.open(newline="", encoding="utf-8") as stream:
                normalized = list(csv.DictReader(stream))
            self.assertAlmostEqual(
                float(normalized[0]["predicted_background"])
                + float(normalized[0]["predicted_object"]),
                1.0,
            )
            saved = np.load(paths.probability_maps_directory / "sample-a.npz")
            self.assertEqual(saved["probabilities"].dtype, np.float16)
            self.assertEqual(len(list(csv.DictReader(paths.per_image_metrics.open()))), 2)


if __name__ == "__main__":
    unittest.main()
