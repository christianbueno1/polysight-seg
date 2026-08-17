"""Validación estructural e integridad de Kvasir-SEG sin usar PyTorch."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError

from polysight_seg.data.masks import MASK_THRESHOLD


class DatasetValidationError(ValueError):
    """Indica que el dataset no cumple el contrato esperado."""


def _load_image_metadata(path: Path) -> tuple[tuple[int, int], str]:
    """Decodifica un archivo completo y devuelve tamaño y modo."""
    try:
        with Image.open(path) as candidate:
            if candidate.format != "JPEG":
                raise DatasetValidationError(f"Formato no JPEG: {path}")
            candidate.verify()
        with Image.open(path) as candidate:
            candidate.load()
            return candidate.size, candidate.mode
    except (OSError, UnidentifiedImageError) as error:
        raise DatasetValidationError(f"Imagen corrupta: {path}: {error}") from error


def _validate_bbox(sample_id: str, record: Any, size: tuple[int, int]) -> list[str]:
    errors: list[str] = []
    width, height = size
    if not isinstance(record, dict):
        return [f"Bounding box inválido para {sample_id}: no es un objeto"]
    if record.get("width") != width or record.get("height") != height:
        errors.append(f"Dimensiones del bounding box no coinciden: {sample_id}")

    boxes = record.get("bbox")
    if not isinstance(boxes, list) or not boxes:
        return [*errors, f"Lista de bounding boxes vacía o inválida: {sample_id}"]
    for index, box in enumerate(boxes):
        if not isinstance(box, dict) or box.get("label") != "polyp":
            errors.append(f"Bounding box {index} sin etiqueta polyp: {sample_id}")
            continue
        coordinates = tuple(box.get(key) for key in ("xmin", "ymin", "xmax", "ymax"))
        if not all(isinstance(value, int) for value in coordinates):
            errors.append(f"Coordenadas no enteras en bbox {index}: {sample_id}")
            continue
        xmin, ymin, xmax, ymax = coordinates
        if not (0 <= xmin < xmax <= width and 0 <= ymin < ymax <= height):
            errors.append(f"Bounding box {index} fuera de límites: {sample_id}")
    return errors


def validate_dataset(root: Path, expected_pairs: int = 1_000) -> dict[str, Any]:
    """Valida integridad, nombres, pares, dimensiones y bounding boxes."""
    root = root.resolve(strict=True)
    images_dir = root / "images"
    masks_dir = root / "masks"
    bbox_path = root / "bounding-boxes.json"
    errors: list[str] = []

    image_paths = sorted(images_dir.glob("*.jpg"))
    mask_paths = sorted(masks_dir.glob("*.jpg"))
    image_ids = {path.stem for path in image_paths}
    mask_ids = {path.stem for path in mask_paths}

    if len(image_paths) != expected_pairs:
        errors.append(f"Se esperaban {expected_pairs} imágenes; se encontraron {len(image_paths)}")
    if len(mask_paths) != expected_pairs:
        errors.append(f"Se esperaban {expected_pairs} máscaras; se encontraron {len(mask_paths)}")
    if image_ids != mask_ids:
        errors.append(
            f"Pares incompletos: {len(image_ids - mask_ids)} sin máscara y "
            f"{len(mask_ids - image_ids)} sin imagen"
        )

    for sample_id in image_ids | mask_ids:
        try:
            if str(uuid.UUID(sample_id)) != sample_id:
                errors.append(f"Nombre no canónico: {sample_id}")
        except ValueError:
            errors.append(f"Nombre no UUID: {sample_id}")

    try:
        bounding_boxes = json.loads(bbox_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DatasetValidationError(f"JSON de bounding boxes inválido: {error}") from error
    if not isinstance(bounding_boxes, dict):
        raise DatasetValidationError("El JSON de bounding boxes no es un objeto")
    bbox_ids = set(bounding_boxes)
    if bbox_ids != image_ids:
        errors.append(
            f"Bounding boxes incompletos: {len(image_ids - bbox_ids)} faltantes y "
            f"{len(bbox_ids - image_ids)} sin imagen"
        )

    image_modes: dict[str, int] = {}
    mask_modes: dict[str, int] = {}
    total_mask_pixels = 0
    total_foreground_pixels = 0
    masks_with_intermediate_values = 0
    for sample_id in sorted(image_ids & mask_ids):
        image_path = images_dir / f"{sample_id}.jpg"
        mask_path = masks_dir / f"{sample_id}.jpg"
        try:
            image_size, image_mode = _load_image_metadata(image_path)
            mask_size, mask_mode = _load_image_metadata(mask_path)
        except DatasetValidationError as error:
            errors.append(str(error))
            continue
        image_modes[image_mode] = image_modes.get(image_mode, 0) + 1
        mask_modes[mask_mode] = mask_modes.get(mask_mode, 0) + 1
        if image_size != mask_size:
            errors.append(f"Dimensiones imagen–máscara diferentes: {sample_id}")
        if sample_id in bounding_boxes:
            errors.extend(_validate_bbox(sample_id, bounding_boxes[sample_id], image_size))

        with Image.open(mask_path) as mask:
            histogram = mask.convert("L").histogram()
        pixel_count = sum(histogram)
        foreground_pixels = sum(histogram[MASK_THRESHOLD:])
        total_mask_pixels += pixel_count
        total_foreground_pixels += foreground_pixels
        if sum(histogram[1:255]) > 0:
            masks_with_intermediate_values += 1
        if foreground_pixels == 0 or foreground_pixels == pixel_count:
            errors.append(f"Máscara vacía tras binarizar con umbral 128: {sample_id}")

    if errors:
        preview = "\n".join(f"- {error}" for error in errors[:20])
        suffix = f"\n- ... y {len(errors) - 20} errores más" if len(errors) > 20 else ""
        raise DatasetValidationError(f"Falló la validación:\n{preview}{suffix}")

    return {
        "status": "ok",
        "pairs": len(image_ids),
        "bounding_box_records": len(bounding_boxes),
        "image_modes": image_modes,
        "mask_modes": mask_modes,
        "mask_threshold": MASK_THRESHOLD,
        "masks_with_intermediate_values": masks_with_intermediate_values,
        "foreground_fraction": total_foreground_pixels / total_mask_pixels,
    }
