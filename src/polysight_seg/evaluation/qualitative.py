"""Paneles cualitativos deterministas para análisis de errores."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from polysight_seg.evaluation.engine import EvaluationResult


def _selected_cases(
    rows: list[dict[str, float | int | str]], counts: dict[str, int]
) -> list[tuple[str, int, dict[str, float | int | str]]]:
    ordered = sorted(rows, key=lambda row: (float(row["dice"]), str(row["sample_id"])))
    selections: list[tuple[str, int, dict[str, float | int | str]]] = []
    groups = {
        "worst": ordered[: counts["worst_cases"]],
        "best": list(reversed(ordered[-counts["best_cases"] :])),
    }
    median_count = min(counts["median_cases"], len(ordered))
    median_start = max(0, (len(ordered) - median_count) // 2)
    groups["median"] = ordered[median_start : median_start + median_count]
    seen: set[tuple[str, str]] = set()
    for category in ("best", "median", "worst"):
        for rank, row in enumerate(groups[category], start=1):
            key = (category, str(row["sample_id"]))
            if key not in seen:
                selections.append((category, rank, row))
                seen.add(key)
    return selections


def _label(panel: np.ndarray, text: str) -> np.ndarray:
    bar = np.full((34, panel.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(bar, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (25, 32, 48), 1, cv2.LINE_AA)
    return np.vstack((bar, panel))


def generate_qualitative_panels(
    dataset: Any,
    result: EvaluationResult,
    output_directory: Path,
    *,
    threshold: float,
    best_cases: int,
    median_cases: int,
    worst_cases: int,
) -> Path:
    """Genera paneles y devuelve el CSV de selección."""

    if not result.per_image or not result.probability_maps:
        raise ValueError("Se requieren métricas y probabilidades por imagen")
    counts = {
        "best_cases": best_cases,
        "median_cases": median_cases,
        "worst_cases": worst_cases,
    }
    if any(value <= 0 for value in counts.values()):
        raise ValueError("La cantidad de casos cualitativos debe ser positiva")
    samples = {str(row["sample_id"]): row for row in dataset.samples}
    output_directory.mkdir(parents=True, exist_ok=True)
    selection_rows: list[dict[str, Any]] = []

    for category, rank, metric_row in _selected_cases(result.per_image, counts):
        sample_id = str(metric_row["sample_id"])
        if sample_id not in samples or sample_id not in result.probability_maps:
            raise ValueError(f"Faltan fuentes cualitativas para {sample_id}")
        sample = samples[sample_id]
        image = cv2.imread(str(dataset.root / sample["image_path"]), cv2.IMREAD_COLOR)
        mask = cv2.imread(str(dataset.root / sample["mask_path"]), cv2.IMREAD_GRAYSCALE)
        if image is None or mask is None:
            raise OSError(f"No se pudo decodificar el caso {sample_id}")
        probabilities = np.squeeze(result.probability_maps[sample_id]).astype(np.float32)
        height, width = probabilities.shape
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
        ground_truth = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST) >= 128
        prediction = probabilities >= threshold

        ground_panel = np.zeros_like(image)
        ground_panel[ground_truth] = (70, 190, 70)
        probability_panel = cv2.applyColorMap(
            np.clip(probabilities * 255, 0, 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS
        )
        prediction_panel = np.zeros_like(image)
        prediction_panel[prediction] = (255, 255, 255)
        overlay = image.copy()
        color = np.zeros_like(image)
        color[prediction] = (0, 0, 255)
        overlay = cv2.addWeighted(overlay, 0.72, color, 0.28, 0)
        panels = [
            _label(image, "Imagen"),
            _label(ground_panel, "Máscara real"),
            _label(probability_panel, "Probabilidad"),
            _label(prediction_panel, f"Predicción ≥ {threshold:.2f}"),
            _label(overlay, f"Overlay · Dice {float(metric_row['dice']):.4f}"),
        ]
        filename = f"{category}-{rank:02d}-{sample_id}.png"
        if not cv2.imwrite(str(output_directory / filename), np.hstack(panels)):
            raise OSError(f"No se pudo escribir {filename}")
        selection_rows.append(
            {
                "category": category,
                "rank": rank,
                "sample_id": sample_id,
                "dice": metric_row["dice"],
                "iou": metric_row["iou"],
                "filename": filename,
            }
        )

    selection_path = output_directory / "selection.csv"
    with selection_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["category", "rank", "sample_id", "dice", "iou", "filename"]
        )
        writer.writeheader()
        writer.writerows(selection_rows)
    return selection_path

