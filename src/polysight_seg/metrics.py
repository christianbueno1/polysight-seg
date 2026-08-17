"""Métricas acumuladas por píxel para segmentación binaria."""

from __future__ import annotations

from typing import Any

import torch
from torch import Tensor


def _safe_divide(numerator: int, denominator: int, zero_division: float) -> float:
    if denominator == 0:
        return zero_division
    return numerator / denominator


class BinarySegmentationMetrics:
    """Acumula una matriz de confusión y calcula métricas micro por píxel."""

    def __init__(self, threshold: float = 0.5) -> None:
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold debe estar entre cero y uno")
        self.threshold = threshold
        self.reset()

    def reset(self) -> None:
        """Descarta los conteos acumulados del split anterior."""
        self.true_positive = 0
        self.false_positive = 0
        self.false_negative = 0
        self.true_negative = 0

    @torch.no_grad()
    def update(self, logits: Tensor, targets: Tensor) -> None:
        """Agrega los conteos de un batch de logits y máscaras binarias."""
        if logits.shape != targets.shape:
            raise ValueError(
                f"Logits y targets deben tener la misma forma: "
                f"{tuple(logits.shape)} != {tuple(targets.shape)}"
            )
        if logits.ndim < 3:
            raise ValueError("Se esperan tensores [B, C, ...] con dimensiones espaciales")

        predictions = torch.sigmoid(logits) >= self.threshold
        target_pixels = targets >= 0.5
        self.true_positive += int((predictions & target_pixels).sum().item())
        self.false_positive += int((predictions & ~target_pixels).sum().item())
        self.false_negative += int((~predictions & target_pixels).sum().item())
        self.true_negative += int((~predictions & ~target_pixels).sum().item())

    def compute(self) -> dict[str, float]:
        """Calcula Dice, IoU, precisión y recall desde los conteos acumulados."""
        tp = self.true_positive
        fp = self.false_positive
        fn = self.false_negative
        return {
            "dice": _safe_divide(2 * tp, 2 * tp + fp + fn, zero_division=1.0),
            "iou": _safe_divide(tp, tp + fp + fn, zero_division=1.0),
            "precision": _safe_divide(tp, tp + fp, zero_division=0.0),
            "recall": _safe_divide(tp, tp + fn, zero_division=0.0),
        }

    def confusion_counts(self) -> dict[str, int]:
        """Devuelve TP, FP, FN y TN para auditoría o matriz de confusión."""
        return {
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "true_negative": self.true_negative,
        }


def build_metrics(config: dict[str, Any]) -> BinarySegmentationMetrics:
    """Construye el acumulador usando el umbral inicial versionado."""
    output = config.get("output")
    if not isinstance(output, dict) or "initial_threshold" not in output:
        raise ValueError("La configuración no define output.initial_threshold")
    return BinarySegmentationMetrics(threshold=float(output["initial_threshold"]))
