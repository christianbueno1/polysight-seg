"""Generación reproducible del manifest de Kvasir-SEG."""

from __future__ import annotations

import csv
import json
import statistics
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image

from polysight_seg.data.archive import SOURCE_MARKER, sha256_file
from polysight_seg.data.masks import MASK_THRESHOLD
from polysight_seg.data.validate import validate_dataset


MANIFEST_COLUMNS = (
    "sample_id",
    "image_path",
    "mask_path",
    "width",
    "height",
    "image_sha256",
    "mask_sha256",
    "duplicate_group",
    "foreground_pixels",
    "total_pixels",
    "foreground_fraction",
)


def _duplicate_groups(hashes: list[str]) -> dict[str, str]:
    counts = Counter(hashes)
    return {
        digest: f"sha256:{digest}"
        for digest, count in counts.items()
        if count > 1
    }


def generate_manifest(dataset: Path, output: Path) -> dict[str, Any]:
    """Valida el dataset y escribe manifest CSV y resumen JSON atómicamente."""
    dataset = dataset.resolve(strict=True)
    validation = validate_dataset(dataset)
    source = json.loads((dataset / SOURCE_MARKER).read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    for image_path in sorted((dataset / "images").glob("*.jpg")):
        sample_id = image_path.stem
        mask_path = dataset / "masks" / image_path.name
        with Image.open(image_path) as image:
            width, height = image.size
        with Image.open(mask_path) as mask:
            histogram = mask.convert("L").histogram()
        total_pixels = sum(histogram)
        foreground_pixels = sum(histogram[MASK_THRESHOLD:])
        rows.append(
            {
                "sample_id": sample_id,
                "image_path": f"images/{image_path.name}",
                "mask_path": f"masks/{mask_path.name}",
                "width": width,
                "height": height,
                "image_sha256": sha256_file(image_path),
                "mask_sha256": sha256_file(mask_path),
                "foreground_pixels": foreground_pixels,
                "total_pixels": total_pixels,
                "foreground_fraction": f"{foreground_pixels / total_pixels:.10f}",
            }
        )

    image_groups = _duplicate_groups([row["image_sha256"] for row in rows])
    for row in rows:
        row["duplicate_group"] = image_groups.get(row["image_sha256"], "")

    fractions = [float(row["foreground_fraction"]) for row in rows]
    duplicate_samples = sum(1 for row in rows if row["duplicate_group"])
    summary = {
        "schema_version": 1,
        "source_sha256": source["sha256"],
        "mask_threshold": MASK_THRESHOLD,
        "pairs": validation["pairs"],
        "duplicate_image_groups": len(image_groups),
        "samples_in_duplicate_image_groups": duplicate_samples,
        "foreground_fraction": {
            "min": min(fractions),
            "mean": statistics.fmean(fractions),
            "median": statistics.median(fractions),
            "max": max(fractions),
        },
    }

    output.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=output, delete=False
    ) as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
        temporary_manifest = Path(manifest_file.name)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=output, delete=False
    ) as summary_file:
        json.dump(summary, summary_file, indent=2, sort_keys=True)
        summary_file.write("\n")
        temporary_summary = Path(summary_file.name)

    temporary_manifest.replace(output / "manifest.csv")
    temporary_summary.replace(output / "summary.json")
    return summary
