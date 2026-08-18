"""Carga estricta del checkpoint seleccionado antes de consumir test."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import torch
from torch import nn

from polysight_seg.training.checkpointing import (
    CHECKPOINT_KIND,
    CHECKPOINT_SCHEMA_VERSION,
    verify_checkpoint_hash,
)


def load_selected_checkpoint(
    path: Path,
    *,
    expected_sha256: str,
    expected_run_id: str,
    expected_epoch: int,
    expected_selection_metric: str,
    expected_selection_value: float,
    model: nn.Module,
    map_location: str | torch.device = "cpu",
) -> dict[str, Any]:
    """Verifica identidad y procedencia, carga pesos y activa modo evaluación."""

    verify_checkpoint_hash(path, expected_digest=expected_sha256)
    payload = torch.load(path, map_location=map_location, weights_only=True)
    if not isinstance(payload, dict):
        raise ValueError("El checkpoint no contiene un diccionario")
    if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        raise ValueError("Versión de checkpoint no soportada")
    if payload.get("kind") != CHECKPOINT_KIND:
        raise ValueError("El archivo no es un checkpoint de entrenamiento PolySight")

    selection = payload.get("selection")
    metadata = payload.get("metadata")
    if not isinstance(selection, dict) or not isinstance(metadata, dict):
        raise ValueError("El checkpoint no contiene metadatos de selección")
    if payload.get("epoch") != expected_epoch:
        raise ValueError("La época del checkpoint no coincide con la configuración")
    if metadata.get("mlflow_run_id") != expected_run_id:
        raise ValueError("El run MLflow del checkpoint no coincide con la configuración")
    if selection.get("metric") != expected_selection_metric:
        raise ValueError("La métrica de selección no coincide con la configuración")
    if selection.get("is_best") is not True:
        raise ValueError("El checkpoint configurado no está marcado como mejor")
    best_metric = selection.get("best_metric")
    if not isinstance(best_metric, (float, int)) or not math.isclose(
        float(best_metric),
        expected_selection_value,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError("El valor de selección no coincide con la configuración")

    model.load_state_dict(payload["model_state"], strict=True)
    model.eval()
    return payload
