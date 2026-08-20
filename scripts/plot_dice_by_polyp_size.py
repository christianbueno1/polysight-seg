#!/usr/bin/env python3
"""Genera un SVG de Dice frente a fracción real de pólipo para el split de test."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


WIDTH = 1200
HEIGHT = 700
LEFT = 105
RIGHT = 1145
TOP = 85
BOTTOM = 585
COLORS = {"small": "#2563eb", "medium": "#7c3aed", "large": "#e11d48"}
LABELS = {"small": "Pequeño", "medium": "Mediano", "large": "Grande"}


def _load_rows(metrics_path: Path, splits_path: Path) -> list[dict[str, str | float]]:
    with splits_path.open(newline="", encoding="utf-8") as stream:
        assignments = {
            row["sample_id"]: row
            for row in csv.DictReader(stream)
            if row["split"] == "test"
        }
    with metrics_path.open(newline="", encoding="utf-8") as stream:
        metrics = list(csv.DictReader(stream))
    rows = [
        {
            "sample_id": row["sample_id"],
            "dice": float(row["dice"]),
            "foreground_fraction": float(row["foreground_fraction"]),
            "size_stratum": assignments[row["sample_id"]]["size_stratum"],
        }
        for row in metrics
    ]
    if len(rows) != 150 or set(assignments) != {str(row["sample_id"]) for row in rows}:
        raise ValueError("Se esperaban exactamente las 150 muestras asignadas a test")
    return rows


def _scale(value: float, lower: float, upper: float, start: float, end: float) -> float:
    return start + (value - lower) * (end - start) / (upper - lower)


def _render(rows: list[dict[str, str | float]]) -> str:
    elements: list[str] = []
    for tick in range(6):
        value = tick / 5
        y = _scale(value, 0, 1, BOTTOM, TOP)
        elements.extend(
            [
                f'<line x1="{LEFT}" y1="{y:.2f}" x2="{RIGHT}" y2="{y:.2f}" class="grid"/>',
                f'<text x="{LEFT - 16}" y="{y + 5:.2f}" class="tick" text-anchor="end">{value:.1f}</text>',
            ]
        )
    for percent in (0, 15, 30, 45, 60, 75):
        x = _scale(percent / 100, 0, 0.75, LEFT, RIGHT)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{BOTTOM}" x2="{x:.2f}" y2="{BOTTOM + 7}" class="axis"/>',
                f'<text x="{x:.2f}" y="{BOTTOM + 30}" class="tick" text-anchor="middle">{percent}%</text>',
            ]
        )
    elements.extend(
        [
            f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{BOTTOM}" class="axis"/>',
            f'<line x1="{LEFT}" y1="{BOTTOM}" x2="{RIGHT}" y2="{BOTTOM}" class="axis"/>',
        ]
    )

    for row in rows:
        x = _scale(float(row["foreground_fraction"]), 0, 0.75, LEFT, RIGHT)
        y = _scale(float(row["dice"]), 0, 1, BOTTOM, TOP)
        color = COLORS[str(row["size_stratum"])]
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="{color}" '
            'fill-opacity="0.68" stroke="#ffffff" stroke-width="1">'
            f'<title>{row["sample_id"]}: Dice {float(row["dice"]):.4f}, '
            f'pólipo {float(row["foreground_fraction"]):.2%}</title></circle>'
        )

    legend_x = 140
    for stratum in ("small", "medium", "large"):
        subset = [row for row in rows if row["size_stratum"] == stratum]
        median = statistics.median(float(row["dice"]) for row in subset)
        elements.extend(
            [
                f'<circle cx="{legend_x}" cy="655" r="7" fill="{COLORS[stratum]}"/>',
                f'<text x="{legend_x + 14}" y="660" class="legend">{LABELS[stratum]} '
                f'(n={len(subset)}, mediana {median:.4f})</text>',
            ]
        )
        legend_x += 330

    body = "\n  ".join(elements)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Dice frente al tamaño real del pólipo en test</title>
  <desc id="desc">Gráfico de dispersión de 150 imágenes. Cada punto relaciona Dice con la fracción de píxeles de la máscara real y el color identifica el estrato de tamaño.</desc>
  <style>
    text {{ font-family: Inter, system-ui, sans-serif; fill: #172033; }}
    .title {{ font-size: 25px; font-weight: 700; }}
    .axis-label {{ font-size: 17px; font-weight: 600; }}
    .tick {{ font-size: 14px; fill: #526077; }}
    .legend {{ font-size: 15px; }}
    .grid {{ stroke: #dce2ea; stroke-width: 1; }}
    .axis {{ stroke: #728096; stroke-width: 1.5; }}
  </style>
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{LEFT}" y="42" class="title">Dice frente al tamaño real del pólipo</text>
  <text x="{(LEFT + RIGHT) / 2}" y="632" class="axis-label" text-anchor="middle">Fracción de la imagen ocupada por el pólipo real</text>
  <text x="28" y="{(TOP + BOTTOM) / 2}" class="axis-label" text-anchor="middle" transform="rotate(-90 28 {(TOP + BOTTOM) / 2})">Dice por imagen</text>
  {body}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("splits", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = _load_rows(args.metrics, args.splits)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_render(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
