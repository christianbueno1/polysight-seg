"""Persistencia atómica de evidencia regenerable de evaluación."""

from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from polysight_seg.evaluation.engine import EvaluationResult


SAFE_SAMPLE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class EvaluationArtifactPaths:
    metrics: Path
    per_image_metrics: Path
    confusion_counts: Path
    confusion_normalized_true: Path
    threshold_curve: Path
    probability_maps_directory: Path


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            temporary = Path(stream.name)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _csv_text(rows: list[dict[str, Any]], fieldnames: list[str]) -> str:
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _matrix_rows(aggregate: dict[str, float | int], normalized: bool) -> list[dict[str, Any]]:
    tn, fp = int(aggregate["tn"]), int(aggregate["fp"])
    fn, tp = int(aggregate["fn"]), int(aggregate["tp"])
    if not normalized:
        return [
            {"actual": "background", "predicted_background": tn, "predicted_object": fp},
            {"actual": "object", "predicted_background": fn, "predicted_object": tp},
        ]

    background_total = tn + fp
    object_total = fn + tp
    return [
        {
            "actual": "background",
            "predicted_background": tn / background_total if background_total else 0.0,
            "predicted_object": fp / background_total if background_total else 0.0,
        },
        {
            "actual": "object",
            "predicted_background": fn / object_total if object_total else 0.0,
            "predicted_object": tp / object_total if object_total else 0.0,
        },
    ]


def _atomic_probability_map(path: Path, probabilities: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", suffix=".npz", delete=False
        ) as stream:
            temporary = Path(stream.name)
        np.savez_compressed(temporary, probabilities=probabilities.astype(np.float16))
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_evaluation_artifacts(
    result: EvaluationResult,
    directory: Path,
    outputs: dict[str, str],
) -> EvaluationArtifactPaths:
    """Escribe datos canónicos sin exponer archivos parciales."""

    directory.mkdir(parents=True, exist_ok=True)
    metrics_path = directory / outputs["metrics"]
    per_image_path = directory / outputs["per_image_metrics"]
    counts_path = directory / outputs["confusion_counts"]
    normalized_path = directory / outputs["confusion_normalized_true"]
    curve_path = directory / outputs["threshold_curve"]
    maps_directory = directory / outputs["probability_maps_directory"]

    _atomic_text(
        metrics_path,
        json.dumps(result.aggregate, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    per_image_fields = [
        "sample_id", "dice", "iou", "precision", "recall",
        "tp", "fp", "fn", "tn", "foreground_fraction",
    ]
    _atomic_text(per_image_path, _csv_text(result.per_image, per_image_fields))
    matrix_fields = ["actual", "predicted_background", "predicted_object"]
    _atomic_text(counts_path, _csv_text(_matrix_rows(result.aggregate, False), matrix_fields))
    _atomic_text(
        normalized_path,
        _csv_text(_matrix_rows(result.aggregate, True), matrix_fields),
    )
    curve_fields = ["threshold", "dice", "iou", "precision", "recall", "tp", "fp", "fn", "tn"]
    _atomic_text(curve_path, _csv_text(result.threshold_curve, curve_fields))

    for sample_id, probabilities in result.probability_maps.items():
        if not SAFE_SAMPLE_ID.fullmatch(sample_id):
            raise ValueError(f"sample_id inseguro para ruta de artefacto: {sample_id!r}")
        _atomic_probability_map(maps_directory / f"{sample_id}.npz", probabilities)

    return EvaluationArtifactPaths(
        metrics_path,
        per_image_path,
        counts_path,
        normalized_path,
        curve_path,
        maps_directory,
    )

