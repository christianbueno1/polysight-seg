"""Checkpoints atómicos y auditables para reanudar entrenamiento."""

from __future__ import annotations

import copy
import hashlib
import os
import platform
import random
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn


CHECKPOINT_SCHEMA_VERSION = 1
CHECKPOINT_KIND = "polysight-training-checkpoint"


@dataclass(frozen=True)
class CheckpointSaveResult:
    """Rutas, hashes y decisión de selección de una época."""

    last_path: Path
    last_sha256: str
    best_path: Path | None
    best_sha256: str | None
    best_metric: float
    improved: bool


def capture_rng_state() -> dict[str, Any]:
    """Captura RNG globales usando tipos compatibles con carga segura."""

    numpy_state = np.random.get_state()
    return {
        "python": random.getstate(),
        "numpy": {
            "bit_generator": numpy_state[0],
            "state": numpy_state[1].tolist(),
            "position": numpy_state[2],
            "has_gauss": numpy_state[3],
            "cached_gaussian": numpy_state[4],
        },
        "torch_cpu": torch.get_rng_state(),
        "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
    }


def restore_rng_state(rng_state: dict[str, Any]) -> None:
    """Restaura los RNG capturados por :func:`capture_rng_state`."""

    random.setstate(tuple(rng_state["python"]))
    numpy_state = rng_state["numpy"]
    np.random.set_state(
        (
            numpy_state["bit_generator"],
            np.asarray(numpy_state["state"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gauss"]),
            float(numpy_state["cached_gaussian"]),
        )
    )
    torch.set_rng_state(rng_state["torch_cpu"])
    if torch.cuda.is_available() and rng_state["torch_cuda"]:
        torch.cuda.set_rng_state_all(rng_state["torch_cuda"])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _atomic_torch_save(payload: dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        torch.save(payload, temporary_path)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    digest = _sha256(path)
    _atomic_write_text(path.with_suffix(f"{path.suffix}.sha256"), f"{digest}  {path.name}\n")
    return digest


def verify_checkpoint_hash(path: Path, expected_digest: str | None = None) -> str:
    """Comprueba el sidecar y, si se fija, un SHA-256 externo al checkpoint."""

    sidecar = path.with_suffix(f"{path.suffix}.sha256")
    if not sidecar.is_file():
        raise FileNotFoundError(f"Falta el hash del checkpoint: {sidecar}")
    fields = sidecar.read_text(encoding="utf-8").strip().split()
    if len(fields) != 2 or fields[1] != path.name:
        raise ValueError(f"Formato SHA-256 inválido: {sidecar}")
    sidecar_digest = fields[0]
    actual_digest = _sha256(path)
    if actual_digest != sidecar_digest:
        raise ValueError(
            f"SHA-256 inválido para {path}: {actual_digest} != {sidecar_digest}"
        )
    if expected_digest is not None and actual_digest != expected_digest:
        raise ValueError(
            f"SHA-256 distinto al fijado en configuración para {path}: "
            f"{actual_digest} != {expected_digest}"
        )
    return actual_digest


def _is_improvement(
    current_metric: float,
    best_metric: float | None,
    mode: str,
    min_delta: float,
) -> bool:
    if mode not in {"max", "min"}:
        raise ValueError(f"Modo de selección no soportado: {mode}")
    if min_delta < 0:
        raise ValueError("min_delta no puede ser negativo")
    if best_metric is None:
        return True
    if mode == "max":
        return current_metric > best_metric + min_delta
    return current_metric < best_metric - min_delta


def save_epoch_checkpoints(
    *,
    directory: Path,
    last_filename: str,
    best_filename: str,
    epoch: int,
    current_metric: float,
    best_metric: float | None,
    selection_metric: str,
    selection_mode: str,
    min_delta: float,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any | None,
    grad_scaler: Any | None,
    metrics: dict[str, float | int],
    trainer_state: dict[str, Any],
    config_snapshot: dict[str, Any],
    code_commit: str,
    dataset_hashes: dict[str, str],
    architecture: dict[str, Any],
    threshold: float,
    slurm_job_id: str | None = None,
    mlflow_run_id: str | None = None,
) -> CheckpointSaveResult:
    """Guarda `last` y, si corresponde, el nuevo `best` de forma atómica."""

    if epoch <= 0:
        raise ValueError("epoch debe ser mayor que cero")
    if not torch.isfinite(torch.tensor(current_metric)):
        raise ValueError("La métrica de selección debe ser finita")
    if best_metric is not None and not torch.isfinite(torch.tensor(best_metric)):
        raise ValueError("La mejor métrica previa debe ser finita")
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold debe estar entre cero y uno")
    if not code_commit:
        raise ValueError("code_commit es obligatorio")
    if not dataset_hashes:
        raise ValueError("dataset_hashes no puede estar vacío")

    improved = _is_improvement(
        current_metric,
        best_metric,
        selection_mode,
        min_delta,
    )
    updated_best_metric = current_metric if improved else float(best_metric)
    payload: dict[str, Any] = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "kind": CHECKPOINT_KIND,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "epoch": epoch,
        "next_epoch": epoch + 1,
        "selection": {
            "metric": selection_metric,
            "mode": selection_mode,
            "min_delta": min_delta,
            "current_metric": current_metric,
            "best_metric": updated_best_metric,
            "is_best": improved,
        },
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scheduler_state": scheduler.state_dict() if scheduler is not None else None,
        "grad_scaler_state": (
            grad_scaler.state_dict() if grad_scaler is not None else None
        ),
        "rng_state": capture_rng_state(),
        "metrics": copy.deepcopy(metrics),
        "trainer_state": copy.deepcopy(trainer_state),
        "metadata": {
            "code_commit": code_commit,
            "slurm_job_id": slurm_job_id,
            "mlflow_run_id": mlflow_run_id,
            "dataset_hashes": copy.deepcopy(dataset_hashes),
            "architecture": copy.deepcopy(architecture),
            "threshold": threshold,
            "config": copy.deepcopy(config_snapshot),
            "versions": {
                "python": platform.python_version(),
                "torch": str(torch.__version__),
                "cuda_build": torch.version.cuda,
                "cudnn": torch.backends.cudnn.version(),
            },
        },
    }

    last_path = directory / last_filename
    last_sha256 = _atomic_torch_save(payload, last_path)
    saved_best_path: Path | None = None
    saved_best_sha256: str | None = None
    if improved:
        saved_best_path = directory / best_filename
        saved_best_sha256 = _atomic_torch_save(payload, saved_best_path)

    return CheckpointSaveResult(
        last_path=last_path,
        last_sha256=last_sha256,
        best_path=saved_best_path,
        best_sha256=saved_best_sha256,
        best_metric=updated_best_metric,
        improved=improved,
    )


def load_training_checkpoint(
    path: Path,
    *,
    model: nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    scheduler: Any | None = None,
    grad_scaler: Any | None = None,
    map_location: str | torch.device = "cpu",
    restore_rng: bool = True,
) -> dict[str, Any]:
    """Verifica y restaura estados desde un checkpoint confiable del proyecto."""

    verify_checkpoint_hash(path)
    payload = torch.load(path, map_location=map_location, weights_only=True)
    if not isinstance(payload, dict):
        raise ValueError("El checkpoint no contiene un diccionario")
    if payload.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
        raise ValueError("Versión de checkpoint no soportada")
    if payload.get("kind") != CHECKPOINT_KIND:
        raise ValueError("El archivo no es un checkpoint de entrenamiento PolySight")

    model.load_state_dict(payload["model_state"])
    if optimizer is not None:
        optimizer.load_state_dict(payload["optimizer_state"])
    if scheduler is not None and payload["scheduler_state"] is not None:
        scheduler.load_state_dict(payload["scheduler_state"])
    if grad_scaler is not None and payload["grad_scaler_state"] is not None:
        grad_scaler.load_state_dict(payload["grad_scaler_state"])
    if restore_rng:
        restore_rng_state(payload["rng_state"])
    return payload
