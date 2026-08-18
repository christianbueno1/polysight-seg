"""Inferencia reutilizable de una imagen con el checkpoint seleccionado."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import yaml
from PIL import Image
from torch import nn

from polysight_seg.data.dataset import load_data_config
from polysight_seg.data.transforms import build_transforms
from polysight_seg.evaluation.checkpoint import load_selected_checkpoint
from polysight_seg.models import build_model, load_model_config


@dataclass(frozen=True)
class InferenceResult:
    """Salidas listas para inspección o visualización."""

    probability: np.ndarray
    mask: np.ndarray
    overlay: np.ndarray
    foreground_fraction: float
    original_size: tuple[int, int]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError(f"Configuración no soportada: {path}")
    return config


def resolve_device(requested: str = "auto") -> torch.device:
    """Resuelve CPU/CUDA sin asumir que el entorno tiene GPU."""

    if requested == "auto":
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if requested not in {"cpu", "cuda"}:
        raise ValueError("device debe ser auto, cpu o cuda")
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("Se solicitó CUDA, pero no está disponible")
    return torch.device("cuda:0" if requested == "cuda" else "cpu")


def load_verified_model(
    project_root: Path,
    checkpoint_path: Path,
    *,
    evaluation_config_path: Path | None = None,
    device: str = "auto",
) -> tuple[nn.Module, torch.device, dict[str, Any], dict[str, Any]]:
    """Construye el modelo y carga el checkpoint con todos sus contratos."""

    root = project_root.resolve()
    evaluation_path = evaluation_config_path or (
        root / "configs/evaluation/unet-resnet34-baseline.yaml"
    )
    evaluation = _load_yaml(evaluation_path.resolve())
    references = evaluation["references"]
    model_config = load_model_config(root / references["model_config"])
    data_config = load_data_config(root / references["data_config"])
    model_config = copy.deepcopy(model_config)
    model_config["model"]["encoder_weights"] = None
    selected_device = resolve_device(device)
    model = build_model(model_config).to(selected_device)
    checkpoint = evaluation["checkpoint"]
    load_selected_checkpoint(
        checkpoint_path.resolve(),
        expected_sha256=checkpoint["sha256"],
        expected_run_id=checkpoint["source_run_id"],
        expected_epoch=int(checkpoint["selected_epoch"]),
        expected_selection_metric=checkpoint["selection_metric"],
        expected_selection_value=float(checkpoint["selection_value"]),
        model=model,
        map_location=selected_device,
    )
    return model, selected_device, data_config, evaluation


def prepare_image(image: Image.Image, data_config: dict[str, Any]) -> tuple[np.ndarray, torch.Tensor]:
    """Convierte a RGB y aplica exactamente las transforms de validation."""

    rgb = np.asarray(image.convert("RGB"))
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.size == 0:
        raise ValueError("La entrada no pudo convertirse a una imagen RGB válida")
    transformed = build_transforms(data_config, "validation")(image=rgb)["image"]
    tensor = torch.from_numpy(np.ascontiguousarray(transformed.transpose(2, 0, 1)))
    return rgb, tensor.unsqueeze(0)


def postprocess_prediction(
    image_rgb: np.ndarray,
    probability_256: np.ndarray,
    *,
    threshold: float,
    overlay_alpha: float = 0.45,
) -> InferenceResult:
    """Restaura tamaño original y crea máscara y overlay deterministas."""

    if probability_256.ndim != 2:
        raise ValueError("El mapa de probabilidad debe tener dos dimensiones")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("El umbral debe estar entre 0 y 1")
    if not 0.0 <= overlay_alpha <= 1.0:
        raise ValueError("overlay_alpha debe estar entre 0 y 1")
    height, width = image_rgb.shape[:2]
    probability = cv2.resize(
        probability_256.astype(np.float32),
        (width, height),
        interpolation=cv2.INTER_LINEAR,
    )
    mask_256 = (probability_256 >= threshold).astype(np.uint8)
    mask = cv2.resize(mask_256, (width, height), interpolation=cv2.INTER_NEAREST)
    overlay = image_rgb.copy()
    red = np.zeros_like(image_rgb)
    red[..., 0] = 255
    selected = mask.astype(bool)
    overlay[selected] = np.clip(
        (1.0 - overlay_alpha) * image_rgb[selected] + overlay_alpha * red[selected],
        0,
        255,
    ).astype(np.uint8)
    return InferenceResult(
        probability=probability,
        mask=(mask * 255).astype(np.uint8),
        overlay=overlay,
        foreground_fraction=float(mask.mean()),
        original_size=(width, height),
    )


def predict_image(
    model: nn.Module,
    image: Image.Image,
    data_config: dict[str, Any],
    device: torch.device,
    *,
    threshold: float = 0.5,
) -> InferenceResult:
    """Ejecuta una inferencia sin modificar pesos ni gradientes."""

    image_rgb, batch = prepare_image(image, data_config)
    with torch.inference_mode():
        logits = model(batch.to(device, non_blocking=device.type == "cuda"))
        if logits.shape != (1, 1, 256, 256):
            raise RuntimeError(f"Salida inesperada del modelo: {tuple(logits.shape)}")
        probability = torch.sigmoid(logits)[0, 0].float().cpu().numpy()
    return postprocess_prediction(image_rgb, probability, threshold=threshold)
