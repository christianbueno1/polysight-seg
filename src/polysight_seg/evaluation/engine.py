"""Motor de evaluación binaria con evidencia agregada y por imagen."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import Any, Sized

import numpy as np
import torch
from torch import Tensor, nn


@dataclass(frozen=True)
class EvaluationResult:
    """Resultados suficientes para reconstruir métricas y artefactos."""

    aggregate: dict[str, float | int]
    per_image: list[dict[str, float | int | str]]
    threshold_curve: list[dict[str, float | int]]
    probability_maps: dict[str, np.ndarray]


def _metrics(tp: int, fp: int, fn: int, tn: int) -> dict[str, float | int]:
    def divide(numerator: int, denominator: int, zero: float) -> float:
        return numerator / denominator if denominator else zero

    return {
        "dice": divide(2 * tp, 2 * tp + fp + fn, 1.0),
        "iou": divide(tp, tp + fp + fn, 1.0),
        "precision": divide(tp, tp + fp, 0.0),
        "recall": divide(tp, tp + fn, 0.0),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
    }


def _counts(probabilities: Tensor, targets: Tensor, threshold: float) -> Tensor:
    predictions = probabilities >= threshold
    target_pixels = targets >= 0.5
    spatial_dims = tuple(range(1, predictions.ndim))
    return torch.stack(
        (
            (predictions & target_pixels).sum(dim=spatial_dims),
            (predictions & ~target_pixels).sum(dim=spatial_dims),
            (~predictions & target_pixels).sum(dim=spatial_dims),
            (~predictions & ~target_pixels).sum(dim=spatial_dims),
        ),
        dim=1,
    ).to(device="cpu", dtype=torch.int64)


@torch.inference_mode()
def evaluate_segmentation(
    model: nn.Module,
    dataloader: Sized,
    device: torch.device,
    *,
    threshold: float,
    threshold_values: list[float],
    amp_enabled: bool = False,
    amp_dtype: torch.dtype = torch.float16,
    preserve_probability_maps: bool = True,
    max_batches: int | None = None,
) -> EvaluationResult:
    """Evalúa sin gradientes y conserva evidencia por imagen y por umbral."""

    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold debe estar entre cero y uno")
    if not threshold_values or any(not 0.0 < value < 1.0 for value in threshold_values):
        raise ValueError("threshold_values debe contener valores entre cero y uno")
    if len(set(threshold_values)) != len(threshold_values):
        raise ValueError("threshold_values no puede contener duplicados")
    if amp_enabled and device.type != "cuda":
        raise ValueError("AMP float16 está configurado únicamente para CUDA")
    available_batches = len(dataloader)
    if available_batches <= 0:
        raise ValueError("El DataLoader no contiene batches")
    if max_batches is not None and max_batches <= 0:
        raise ValueError("max_batches debe ser mayor que cero")
    planned_batches = min(available_batches, max_batches or available_batches)

    model.eval()
    per_image: list[dict[str, float | int | str]] = []
    probability_maps: dict[str, np.ndarray] = {}
    aggregate_counts = torch.zeros(4, dtype=torch.int64)
    threshold_counts = {
        value: torch.zeros(4, dtype=torch.int64) for value in threshold_values
    }
    seen_ids: set[str] = set()

    for batch in islice(dataloader, planned_batches):
        images = batch.get("image")
        targets = batch.get("mask")
        sample_ids = batch.get("sample_id")
        if not isinstance(images, Tensor) or not isinstance(targets, Tensor):
            raise TypeError("image y mask deben ser tensores")
        if not isinstance(sample_ids, (list, tuple)) or len(sample_ids) != images.shape[0]:
            raise ValueError("sample_id debe identificar cada imagen del batch")
        if images.shape[0] <= 0 or images.shape[0] != targets.shape[0]:
            raise ValueError("El batch está vacío o tiene tamaños inconsistentes")

        images = images.to(device, non_blocking=device.type == "cuda")
        targets = targets.to(device, non_blocking=device.type == "cuda")
        with torch.autocast(
            device_type=device.type,
            dtype=amp_dtype,
            enabled=amp_enabled,
        ):
            logits = model(images)
        if logits.shape != targets.shape:
            raise ValueError("Logits y máscaras deben tener la misma forma")
        if not torch.isfinite(logits).all():
            raise FloatingPointError("El modelo produjo logits no finitos")
        probabilities = torch.sigmoid(logits.float())
        batch_counts = _counts(probabilities, targets, threshold)
        aggregate_counts += batch_counts.sum(dim=0)
        for value in threshold_values:
            threshold_counts[value] += _counts(probabilities, targets, value).sum(dim=0)

        foreground = (targets >= 0.5).flatten(1).float().mean(dim=1).cpu()
        for index, raw_sample_id in enumerate(sample_ids):
            sample_id = str(raw_sample_id)
            if not sample_id or sample_id in seen_ids:
                raise ValueError(f"sample_id vacío o duplicado: {sample_id!r}")
            seen_ids.add(sample_id)
            tp, fp, fn, tn = (int(value) for value in batch_counts[index].tolist())
            row: dict[str, float | int | str] = {"sample_id": sample_id}
            row.update(_metrics(tp, fp, fn, tn))
            row["foreground_fraction"] = float(foreground[index].item())
            per_image.append(row)
            if preserve_probability_maps:
                probability_maps[sample_id] = (
                    probabilities[index].detach().cpu().numpy().astype(np.float16)
                )

    tp, fp, fn, tn = (int(value) for value in aggregate_counts.tolist())
    aggregate = _metrics(tp, fp, fn, tn)
    aggregate["sample_count"] = len(per_image)
    curve = []
    for value in sorted(threshold_values):
        counts = (int(item) for item in threshold_counts[value].tolist())
        row = {"threshold": value}
        row.update(_metrics(*counts))
        curve.append(row)
    return EvaluationResult(aggregate, per_image, curve, probability_maps)

