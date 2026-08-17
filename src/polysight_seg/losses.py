"""Funciones de pérdida para segmentación binaria."""

from __future__ import annotations

from typing import Any

import torch
from torch import Tensor, nn


class DiceLoss(nn.Module):
    """Calcula `1 - Dice` por muestra a partir de logits."""

    def __init__(self, smooth: float = 1.0e-7) -> None:
        super().__init__()
        if smooth <= 0:
            raise ValueError("smooth debe ser mayor que cero")
        self.smooth = smooth

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        if logits.shape != targets.shape:
            raise ValueError(
                f"Logits y targets deben tener la misma forma: "
                f"{tuple(logits.shape)} != {tuple(targets.shape)}"
            )
        if logits.ndim < 3:
            raise ValueError("Se esperan tensores [B, C, ...] con dimensiones espaciales")

        targets = targets.to(dtype=logits.dtype)
        probabilities = torch.sigmoid(logits)
        reduction_dims = tuple(range(1, logits.ndim))
        intersection = (probabilities * targets).sum(dim=reduction_dims)
        denominator = probabilities.sum(dim=reduction_dims) + targets.sum(
            dim=reduction_dims
        )
        dice = (2.0 * intersection + self.smooth) / (denominator + self.smooth)
        return 1.0 - dice.mean()


class BCEDiceLoss(nn.Module):
    """Suma ponderada de BCEWithLogitsLoss y DiceLoss."""

    def __init__(
        self,
        bce_weight: float = 1.0,
        dice_weight: float = 1.0,
        smooth: float = 1.0e-7,
    ) -> None:
        super().__init__()
        if bce_weight <= 0 or dice_weight <= 0:
            raise ValueError("Los pesos de BCE y Dice deben ser mayores que cero")
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight
        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss(smooth=smooth)

    def forward(self, logits: Tensor, targets: Tensor) -> Tensor:
        if logits.shape != targets.shape:
            raise ValueError(
                f"Logits y targets deben tener la misma forma: "
                f"{tuple(logits.shape)} != {tuple(targets.shape)}"
            )
        targets = targets.to(dtype=logits.dtype)
        return (
            self.bce_weight * self.bce(logits, targets)
            + self.dice_weight * self.dice(logits, targets)
        )


def build_loss(config: dict[str, Any]) -> BCEDiceLoss:
    """Construye la pérdida combinada desde la configuración del baseline."""
    loss = config.get("loss")
    if not isinstance(loss, dict) or loss.get("name") != "bce_dice":
        raise ValueError("Configuración de pérdida no soportada")
    return BCEDiceLoss(
        bce_weight=float(loss["bce_weight"]),
        dice_weight=float(loss["dice_weight"]),
        smooth=float(loss["smooth"]),
    )
