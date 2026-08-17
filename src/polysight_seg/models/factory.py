"""Factoría declarativa de modelos para ejecución en CEDIA."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


SUPPORTED_LIBRARY = "segmentation_models_pytorch"
SUPPORTED_ARCHITECTURE = "Unet"


def _validate_model_config(config: Any) -> dict[str, Any]:
    """Valida el contrato mínimo aceptado por la factoría."""
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError("Versión de configuración de modelo no soportada")

    model = config.get("model")
    if not isinstance(model, dict):
        raise ValueError("La configuración no contiene la sección model")
    if model.get("library") != SUPPORTED_LIBRARY:
        raise ValueError(f"Librería de modelos no soportada: {model.get('library')}")
    if model.get("architecture") != SUPPORTED_ARCHITECTURE:
        raise ValueError(f"Arquitectura no soportada: {model.get('architecture')}")
    if model.get("in_channels") != 3 or model.get("classes") != 1:
        raise ValueError("El baseline requiere entrada RGB y una salida binaria")
    if model.get("activation") is not None:
        raise ValueError("El modelo debe devolver logits sin activación")
    return config


def load_model_config(path: Path) -> dict[str, Any]:
    """Carga y valida el contrato YAML del baseline."""
    with path.open(encoding="utf-8") as file:
        return _validate_model_config(yaml.safe_load(file))


def build_model(config: dict[str, Any]) -> Any:
    """Construye el modelo; importa PyTorch solo en el entorno de CEDIA."""
    config = _validate_model_config(config)
    model = config["model"]

    import segmentation_models_pytorch as smp

    return smp.Unet(
        encoder_name=model["encoder_name"],
        encoder_weights=model["encoder_weights"],
        in_channels=model["in_channels"],
        classes=model["classes"],
        activation=model["activation"],
    )
