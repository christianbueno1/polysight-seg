#!/usr/bin/env python3
"""Genera curvas SVG reproducibles desde el historial CSV de entrenamiento."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


WIDTH = 1200
HEIGHT = 520
MARGIN_X = 75
PANEL_GAP = 70
PANEL_WIDTH = (WIDTH - 2 * MARGIN_X - PANEL_GAP) / 2
PLOT_TOP = 75
PLOT_BOTTOM = 430


def _load_history(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [
            {key: float(value) for key, value in row.items() if key != "is_best"}
            for row in csv.DictReader(stream)
        ]
    if not rows:
        raise ValueError("El historial no contiene épocas")
    return rows


def _scale(value: float, lower: float, upper: float, start: float, end: float) -> float:
    return start + (value - lower) * (end - start) / (upper - lower)


def _polyline(
    rows: list[dict[str, float]],
    metric: str,
    x0: float,
    y_min: float,
    y_max: float,
    color: str,
) -> str:
    last_epoch = rows[-1]["epoch"]
    points = []
    for row in rows:
        x = _scale(row["epoch"], 1, last_epoch, x0, x0 + PANEL_WIDTH)
        y = _scale(row[metric], y_min, y_max, PLOT_BOTTOM, PLOT_TOP)
        points.append(f"{x:.2f},{y:.2f}")
    return (
        f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" '
        'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
    )


def _panel(
    rows: list[dict[str, float]],
    x0: float,
    title: str,
    train_metric: str,
    val_metric: str,
    y_min: float,
    y_max: float,
    best_epoch: int,
) -> list[str]:
    elements = [f'<text x="{x0:.0f}" y="45" class="panel-title">{title}</text>']
    for tick in range(6):
        value = y_min + tick * (y_max - y_min) / 5
        y = _scale(value, y_min, y_max, PLOT_BOTTOM, PLOT_TOP)
        elements.extend(
            [
                f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + PANEL_WIDTH:.2f}" '
                f'y2="{y:.2f}" class="grid"/>',
                f'<text x="{x0 - 12:.2f}" y="{y + 5:.2f}" class="tick" '
                f'text-anchor="end">{value:.2f}</text>',
            ]
        )
    last_epoch = int(rows[-1]["epoch"])
    for epoch in (1, 8, 16, 24, last_epoch):
        x = _scale(epoch, 1, last_epoch, x0, x0 + PANEL_WIDTH)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{PLOT_BOTTOM}" x2="{x:.2f}" '
                f'y2="{PLOT_BOTTOM + 6}" class="axis"/>',
                f'<text x="{x:.2f}" y="{PLOT_BOTTOM + 27}" class="tick" '
                f'text-anchor="middle">{epoch}</text>',
            ]
        )
    elements.extend(
        [
            f'<line x1="{x0}" y1="{PLOT_BOTTOM}" x2="{x0 + PANEL_WIDTH}" '
            f'y2="{PLOT_BOTTOM}" class="axis"/>',
            _polyline(rows, train_metric, x0, y_min, y_max, "#2563eb"),
            _polyline(rows, val_metric, x0, y_min, y_max, "#e11d48"),
        ]
    )
    best_x = _scale(best_epoch, 1, last_epoch, x0, x0 + PANEL_WIDTH)
    elements.append(
        f'<line x1="{best_x:.2f}" y1="{PLOT_TOP}" x2="{best_x:.2f}" '
        f'y2="{PLOT_BOTTOM}" class="best"/>'
    )
    return elements


def _render(rows: list[dict[str, float]]) -> str:
    best_row = max(rows, key=lambda row: row["val_dice"])
    best_epoch = int(best_row["epoch"])
    right_x = MARGIN_X + PANEL_WIDTH + PANEL_GAP
    elements = _panel(
        rows, MARGIN_X, "Pérdida", "train_loss", "val_loss", 0.0, 1.0, best_epoch
    )
    elements += _panel(
        rows, right_x, "Dice", "train_dice", "val_dice", 0.6, 1.0, best_epoch
    )
    elements.extend(
        [
            '<line x1="370" y1="475" x2="405" y2="475" stroke="#2563eb" '
            'stroke-width="3"/><text x="415" y="480" class="legend">Train</text>',
            '<line x1="510" y1="475" x2="545" y2="475" stroke="#e11d48" '
            'stroke-width="3"/><text x="555" y="480" class="legend">Validation</text>',
            '<line x1="710" y1="458" x2="710" y2="490" class="best"/>'
            f'<text x="722" y="480" class="legend">Mejor época: {best_epoch} '
            f'(val Dice {best_row["val_dice"]:.4f})</text>',
        ]
    )
    body = "\n  ".join(elements)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Curvas de entrenamiento y validation del baseline</title>
  <desc id="desc">Pérdida y Dice durante {len(rows)} épocas; el mejor Dice de validation ocurrió en la época {best_epoch}.</desc>
  <style>
    text {{ font-family: Inter, system-ui, sans-serif; fill: #172033; }}
    .panel-title {{ font-size: 22px; font-weight: 700; }}
    .tick {{ font-size: 13px; fill: #526077; }}
    .legend {{ font-size: 14px; }}
    .grid {{ stroke: #dce2ea; stroke-width: 1; }}
    .axis {{ stroke: #728096; stroke-width: 1.5; }}
    .best {{ stroke: #7c3aed; stroke-width: 2; stroke-dasharray: 7 5; }}
  </style>
  <rect width="100%" height="100%" fill="#ffffff"/>
  {body}
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("history", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = _load_history(args.history)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_render(rows), encoding="utf-8")


if __name__ == "__main__":
    main()
