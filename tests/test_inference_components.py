"""Contratos de inferencia ejecutables en entornos con PyTorch."""

from __future__ import annotations

import unittest

import numpy as np
import torch
from PIL import Image
from torch import nn

from polysight_seg.inference import postprocess_prediction, predict_image, resolve_device


class ConstantModel(nn.Module):
    def forward(self, batch: torch.Tensor) -> torch.Tensor:
        return torch.zeros((batch.shape[0], 1, 256, 256), device=batch.device)


class InferenceComponentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data_config = {
            "input": {"height": 256, "width": 256},
            "normalization": {
                "mean": [0.485, 0.456, 0.406],
                "std": [0.229, 0.224, 0.225],
            },
            "transforms": {"train": {}},
        }

    def test_cpu_prediction_preserves_original_size(self) -> None:
        image = Image.new("RGB", (41, 29), color=(20, 40, 60))
        result = predict_image(
            ConstantModel().eval(), image, self.data_config, resolve_device("cpu")
        )
        self.assertEqual(result.original_size, (41, 29))
        self.assertEqual(result.mask.shape, (29, 41))
        self.assertEqual(result.overlay.shape, (29, 41, 3))
        self.assertTrue(np.all(result.mask == 255))

    def test_postprocessing_uses_fixed_binary_mask(self) -> None:
        image = np.zeros((2, 2, 3), dtype=np.uint8)
        probability = np.zeros((256, 256), dtype=np.float32)
        probability[:, 128:] = 1.0
        result = postprocess_prediction(image, probability, threshold=0.5)
        self.assertEqual(set(np.unique(result.mask)), {0, 255})
        self.assertAlmostEqual(result.foreground_fraction, 0.5)

    def test_explicit_cuda_fails_when_unavailable(self) -> None:
        if torch.cuda.is_available():
            self.skipTest("CUDA está disponible")
        with self.assertRaises(RuntimeError):
            resolve_device("cuda")


if __name__ == "__main__":
    unittest.main()
