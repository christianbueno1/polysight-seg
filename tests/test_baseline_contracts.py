"""Contratos numéricos del baseline que solo requieren CPU."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

try:
    import torch
except ModuleNotFoundError:
    torch = None

if torch is not None:
    from polysight_seg.losses import build_loss
    from polysight_seg.metrics import BinarySegmentationMetrics, build_metrics
    from polysight_seg.models import build_model, load_model_config


@unittest.skipIf(torch is None, "PyTorch se valida en CEDIA, no en el equipo local")
class BaselineContractTest(unittest.TestCase):
    """Comprueba formas, gradientes y resultados numéricos conocidos."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_model_config(
            PROJECT_ROOT / "configs/models/unet-resnet34.yaml"
        )

    def test_model_maps_rgb_input_to_one_logit_channel(self) -> None:
        config = copy.deepcopy(self.config)
        self.assertEqual(config["model"]["encoder_weights"], "imagenet")
        config["model"]["encoder_weights"] = None
        model = build_model(config).eval()
        inputs = torch.zeros(1, 3, 256, 256)
        with torch.no_grad():
            logits = model(inputs)
        self.assertEqual(tuple(logits.shape), (1, 1, 256, 256))

    def test_loss_prefers_correct_logits_and_backpropagates(self) -> None:
        loss_function = build_loss(self.config)
        targets = torch.ones(2, 1, 8, 8)
        good_loss = loss_function(torch.full_like(targets, 8.0), targets)
        bad_loss = loss_function(torch.full_like(targets, -8.0), targets)
        self.assertLess(good_loss.item(), bad_loss.item())

        logits = torch.zeros_like(targets, requires_grad=True)
        loss = loss_function(logits, targets)
        loss.backward()
        self.assertTrue(torch.isfinite(loss))
        self.assertIsNotNone(logits.grad)
        self.assertTrue(torch.isfinite(logits.grad).all())

    def test_metrics_match_known_confusion_matrix(self) -> None:
        metrics = build_metrics(self.config)
        logits = torch.tensor([[[[10.0, -10.0], [10.0, -10.0]]]])
        targets = torch.tensor([[[[1.0, 1.0], [0.0, 0.0]]]])
        metrics.update(logits, targets)

        self.assertEqual(
            metrics.confusion_counts(),
            {
                "true_positive": 1,
                "false_positive": 1,
                "false_negative": 1,
                "true_negative": 1,
            },
        )
        result = metrics.compute()
        self.assertAlmostEqual(result["dice"], 0.5)
        self.assertAlmostEqual(result["iou"], 1.0 / 3.0)
        self.assertAlmostEqual(result["precision"], 0.5)
        self.assertAlmostEqual(result["recall"], 0.5)

    def test_perfect_metrics_and_reset(self) -> None:
        metrics = BinarySegmentationMetrics(threshold=0.5)
        targets = torch.tensor([[[[1.0, 0.0], [0.0, 1.0]]]])
        logits = torch.where(targets == 1, 10.0, -10.0)
        metrics.update(logits, targets)
        self.assertEqual(
            metrics.compute(),
            {"dice": 1.0, "iou": 1.0, "precision": 1.0, "recall": 1.0},
        )
        metrics.reset()
        self.assertEqual(
            metrics.confusion_counts(),
            {
                "true_positive": 0,
                "false_positive": 0,
                "false_negative": 0,
                "true_negative": 0,
            },
        )

    def test_shape_mismatch_is_rejected(self) -> None:
        logits = torch.zeros(1, 1, 8, 8)
        targets = torch.zeros(1, 1, 4, 4)
        with self.assertRaises(ValueError):
            build_loss(self.config)(logits, targets)
        with self.assertRaises(ValueError):
            build_metrics(self.config).update(logits, targets)


if __name__ == "__main__":
    unittest.main()
