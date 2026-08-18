"""Loops de train y validation para segmentación binaria."""

from __future__ import annotations

from collections.abc import Mapping, Sized
from itertools import islice
from typing import Any

import torch
from torch import Tensor, nn

from polysight_seg.metrics import BinarySegmentationMetrics


EpochResult = dict[str, float | int]


def _planned_batches(dataloader: Sized, max_batches: int | None) -> int:
    available_batches = len(dataloader)
    if available_batches <= 0:
        raise ValueError("El DataLoader no contiene batches")
    if max_batches is None:
        return available_batches
    if max_batches <= 0:
        raise ValueError("max_batches debe ser mayor que cero")
    return min(available_batches, max_batches)


def _move_batch(
    batch: Mapping[str, Any], device: torch.device
) -> tuple[Tensor, Tensor]:
    try:
        images = batch["image"]
        targets = batch["mask"]
    except KeyError as error:
        raise ValueError("Cada batch debe contener image y mask") from error
    if not isinstance(images, Tensor) or not isinstance(targets, Tensor):
        raise TypeError("image y mask deben ser tensores")
    non_blocking = device.type == "cuda"
    return (
        images.to(device, non_blocking=non_blocking),
        targets.to(device, non_blocking=non_blocking),
    )


def _validate_forward(logits: Tensor, targets: Tensor, loss: Tensor) -> None:
    if logits.shape != targets.shape:
        raise ValueError(
            f"Forma de salida inválida: {tuple(logits.shape)} != {tuple(targets.shape)}"
        )
    if not torch.isfinite(logits).all():
        raise FloatingPointError("El modelo produjo logits no finitos")
    if loss.ndim != 0:
        raise ValueError("La función de pérdida debe devolver un escalar")
    if not torch.isfinite(loss):
        raise FloatingPointError("La pérdida no es finita")


def _summarize_epoch(
    prefix: str,
    weighted_loss: float,
    sample_count: int,
    metrics: BinarySegmentationMetrics,
) -> EpochResult:
    if sample_count <= 0:
        raise ValueError("No se procesaron muestras durante la época")
    result: EpochResult = {f"{prefix}_loss": weighted_loss / sample_count}
    result.update(
        {f"{prefix}_{name}": value for name, value in metrics.compute().items()}
    )
    counts = metrics.confusion_counts()
    result.update(
        {
            f"{prefix}_tp": counts["true_positive"],
            f"{prefix}_fp": counts["false_positive"],
            f"{prefix}_fn": counts["false_negative"],
            f"{prefix}_tn": counts["true_negative"],
        }
    )
    return result


def _validate_runtime_options(
    device: torch.device,
    amp_enabled: bool,
    grad_scaler: Any | None,
    gradient_accumulation_steps: int,
    gradient_clip_max_norm: float | None,
) -> None:
    if amp_enabled and device.type != "cuda":
        raise ValueError("AMP float16 está configurado únicamente para CUDA")
    if amp_enabled and grad_scaler is None:
        raise ValueError("AMP requiere un GradScaler")
    if gradient_accumulation_steps <= 0:
        raise ValueError("gradient_accumulation_steps debe ser mayor que cero")
    if gradient_clip_max_norm is not None and gradient_clip_max_norm <= 0:
        raise ValueError("gradient_clip_max_norm debe ser mayor que cero")


def train_one_epoch(
    model: nn.Module,
    dataloader: Sized,
    loss_function: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    *,
    threshold: float,
    amp_enabled: bool = False,
    amp_dtype: torch.dtype = torch.float16,
    grad_scaler: Any | None = None,
    gradient_accumulation_steps: int = 1,
    gradient_clip_max_norm: float | None = None,
    zero_grad_set_to_none: bool = True,
    max_batches: int | None = None,
) -> EpochResult:
    """Entrena una época y agrega pérdida y métricas sobre todas sus muestras."""

    _validate_runtime_options(
        device,
        amp_enabled,
        grad_scaler,
        gradient_accumulation_steps,
        gradient_clip_max_norm,
    )
    planned_batches = _planned_batches(dataloader, max_batches)
    model.train()
    metrics = BinarySegmentationMetrics(threshold=threshold)
    weighted_loss = 0.0
    sample_count = 0
    optimizer.zero_grad(set_to_none=zero_grad_set_to_none)

    for batch_index, batch in enumerate(islice(dataloader, planned_batches)):
        images, targets = _move_batch(batch, device)
        current_batch_size = int(images.shape[0])
        if current_batch_size <= 0:
            raise ValueError("Se recibió un batch vacío")

        group_start = (batch_index // gradient_accumulation_steps) * (
            gradient_accumulation_steps
        )
        group_size = min(
            gradient_accumulation_steps,
            planned_batches - group_start,
        )
        with torch.autocast(
            device_type=device.type,
            dtype=amp_dtype,
            enabled=amp_enabled,
        ):
            logits = model(images)
            loss = loss_function(logits, targets)
        _validate_forward(logits, targets, loss)

        loss_for_backward = loss / group_size
        if amp_enabled:
            grad_scaler.scale(loss_for_backward).backward()
        else:
            loss_for_backward.backward()

        metrics.update(logits.detach(), targets)
        weighted_loss += float(loss.detach().item()) * current_batch_size
        sample_count += current_batch_size

        closes_group = (
            (batch_index + 1) % gradient_accumulation_steps == 0
            or batch_index + 1 == planned_batches
        )
        if closes_group:
            if gradient_clip_max_norm is not None:
                if amp_enabled:
                    grad_scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), gradient_clip_max_norm
                )
            if amp_enabled:
                grad_scaler.step(optimizer)
                grad_scaler.update()
            else:
                optimizer.step()
            optimizer.zero_grad(set_to_none=zero_grad_set_to_none)

    result = _summarize_epoch("train", weighted_loss, sample_count, metrics)
    result["learning_rate"] = float(optimizer.param_groups[0]["lr"])
    return result


@torch.inference_mode()
def validate_one_epoch(
    model: nn.Module,
    dataloader: Sized,
    loss_function: nn.Module,
    device: torch.device,
    *,
    threshold: float,
    amp_enabled: bool = False,
    amp_dtype: torch.dtype = torch.float16,
    max_batches: int | None = None,
) -> EpochResult:
    """Evalúa validation sin gradientes y agrega métricas sobre toda la época."""

    if amp_enabled and device.type != "cuda":
        raise ValueError("AMP float16 está configurado únicamente para CUDA")
    planned_batches = _planned_batches(dataloader, max_batches)
    model.eval()
    metrics = BinarySegmentationMetrics(threshold=threshold)
    weighted_loss = 0.0
    sample_count = 0

    for batch_index, batch in enumerate(islice(dataloader, planned_batches)):
        images, targets = _move_batch(batch, device)
        current_batch_size = int(images.shape[0])
        if current_batch_size <= 0:
            raise ValueError("Se recibió un batch vacío")

        with torch.autocast(
            device_type=device.type,
            dtype=amp_dtype,
            enabled=amp_enabled,
        ):
            logits = model(images)
            loss = loss_function(logits, targets)
        _validate_forward(logits, targets, loss)

        metrics.update(logits, targets)
        weighted_loss += float(loss.item()) * current_batch_size
        sample_count += current_batch_size

    return _summarize_epoch("val", weighted_loss, sample_count, metrics)
