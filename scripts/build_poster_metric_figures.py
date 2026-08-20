#!/usr/bin/env python3
"""Genera tres figuras SVG autónomas para comunicar la evaluación en un póster."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import statistics
from pathlib import Path


COLORS = {"small": "#2563eb", "medium": "#7c3aed", "large": "#e11d48"}
LABELS = {"small": "Pequeño", "medium": "Mediano", "large": "Grande"}


def _svg(body: str, width: int, height: int, title: str, description: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{description}</desc>
  <style>
    text {{ font-family: Inter, Arial, sans-serif; fill: #172033; }}
    .title {{ font-size: 38px; font-weight: 750; }}
    .subtitle {{ font-size: 21px; fill: #526077; }}
    .section {{ font-size: 25px; font-weight: 700; }}
    .value {{ font-size: 52px; font-weight: 800; }}
    .label {{ font-size: 19px; font-weight: 650; }}
    .body {{ font-size: 18px; }}
    .small {{ font-size: 16px; fill: #526077; }}
    .inverse {{ fill: #ffffff; }}
    .inverse-muted {{ fill: #cbd5e1; }}
    .grid {{ stroke: #dce2ea; stroke-width: 1; }}
    .axis {{ stroke: #728096; stroke-width: 1.5; }}
  </style>
  <rect width="100%" height="100%" rx="22" fill="#ffffff"/>
  {body}
</svg>
'''


def _load(metrics_path: Path, splits_path: Path) -> tuple[dict[str, float], list[dict[str, str | float]]]:
    global_metrics = json.loads(metrics_path.with_name("metrics.json").read_text())
    with splits_path.open(newline="", encoding="utf-8") as stream:
        strata = {
            row["sample_id"]: row["size_stratum"]
            for row in csv.DictReader(stream)
            if row["split"] == "test"
        }
    with metrics_path.open(newline="", encoding="utf-8") as stream:
        rows = [
            {
                "sample_id": row["sample_id"],
                "dice": float(row["dice"]),
                "iou": float(row["iou"]),
                "precision": float(row["precision"]),
                "recall": float(row["recall"]),
                "foreground_fraction": float(row["foreground_fraction"]),
                "size_stratum": strata[row["sample_id"]],
            }
            for row in csv.DictReader(stream)
        ]
    if len(rows) != 150:
        raise ValueError("Se esperaban exactamente 150 métricas de test")
    return global_metrics, rows


def _data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _qualitative(assets: Path) -> str:
    median = _data_uri(assets / "median-case.png")
    worst = _data_uri(assets / "worst-case.png")
    body = f'''
  <text x="70" y="64" class="title">¿Qué segmenta el modelo?</text>
  <text x="70" y="101" class="subtitle">Imagen → máscara real → probabilidad → predicción → superposición</text>
  <rect x="1130" y="25" width="415" height="88" rx="18" fill="#172033"/>
  <text x="1155" y="57" font-size="16" font-weight="700" class="inverse-muted">3 EJECUCIONES · MISMO TEST</text>
  <text x="1155" y="92" font-size="27" font-weight="800" class="inverse">Dice 0.9171 ± 0.0031</text>
  <rect x="55" y="130" width="1490" height="340" rx="18" fill="#f5f8ff" stroke="#cdd8ee"/>
  <text x="80" y="168" class="section">Caso típico · Dice 0.9546 · IoU 0.9131</text>
  <image x="80" y="188" width="1440" height="260" preserveAspectRatio="xMidYMid meet" href="{median}"/>
  <rect x="55" y="495" width="1490" height="340" rx="18" fill="#fff6f7" stroke="#f2c7cf"/>
  <text x="80" y="533" class="section">Principal limitación · Dice 0.0775 · recall 0.0404</text>
  <image x="80" y="553" width="1440" height="260" preserveAspectRatio="xMidYMid meet" href="{worst}"/>
  <rect x="55" y="860" width="1490" height="92" rx="16" fill="#172033"/>
  <text x="80" y="899" font-size="20" font-weight="700" class="inverse">Lectura:</text>
  <text x="165" y="899" font-size="19" class="inverse">el rendimiento habitual es alto, pero existen omisiones severas en casos particulares.</text>
  <text x="80" y="930" font-size="16" class="inverse-muted">Paneles: run original · estabilidad: 3 semillas sobre las mismas 150 imágenes · umbral 0.5</text>'''
    return _svg(
        body, 1600, 1000, "Comparación cualitativa de segmentación",
        "Caso cercano a la mediana y peor caso con imagen, máscara, probabilidad, predicción y overlay.",
    )


def _summary(global_metrics: dict[str, float], rows: list[dict[str, str | float]]) -> str:
    dice_values = sorted(float(row["dice"]) for row in rows)
    median = statistics.median(dice_values)
    p25, p75 = statistics.quantiles(dice_values, n=4, method="inclusive")[0::2]
    worst = min(dice_values)
    cards = [
        ("IoU", global_metrics["iou"], "Solapamiento respecto a la unión"),
        ("Precisión", global_metrics["precision"], "De lo marcado, cuánto era pólipo"),
        ("Recall", global_metrics["recall"], "Del pólipo real, cuánto se detectó"),
    ]
    card_svg = []
    for index, (label, value, note) in enumerate(cards):
        x = 65 + index * 435
        card_svg.append(
            f'<rect x="{x}" y="325" width="400" height="185" rx="20" fill="#f5f8ff" stroke="#cdd8ee"/>'
            f'<text x="{x + 28}" y="370" class="label">{label}</text>'
            f'<text x="{x + 28}" y="435" class="value">{value:.4f}</text>'
            f'<text x="{x + 28}" y="480" class="small">{note}</text>'
        )
    body = f'''
  <text x="65" y="68" class="title">Rendimiento del modelo en test</text>
  <text x="65" y="107" class="subtitle">U-Net/ResNet-34 · segmentación binaria · 150 imágenes · umbral 0.5</text>
  <rect x="65" y="145" width="1270" height="145" rx="22" fill="#172033"/>
  <text x="100" y="190" font-size="22" font-weight="700" class="inverse-muted">DICE GLOBAL</text>
  <text x="100" y="260" font-size="66" font-weight="800" class="inverse">{global_metrics['dice']:.4f}</text>
  <text x="390" y="213" font-size="21" class="inverse">Mide el solapamiento entre la máscara real y la predicción.</text>
  <text x="390" y="250" font-size="18" class="inverse-muted">1.0 = coincidencia perfecta · 0.0 = sin solapamiento</text>
  {''.join(card_svg)}
  <text x="65" y="565" class="section">Variabilidad entre imágenes</text>
  <rect x="65" y="600" width="1270" height="155" rx="20" fill="#fff8e8" stroke="#ead7a6"/>
  <text x="105" y="648" class="label">Mediana Dice</text><text x="105" y="710" class="value">{median:.4f}</text>
  <text x="470" y="648" class="label">50% central (P25–P75)</text><text x="470" y="710" class="value">{p25:.4f}–{p75:.4f}</text>
  <text x="1030" y="648" class="label">Peor caso</text><text x="1030" y="710" class="value" fill="#be123c">{worst:.4f}</text>
  <text x="65" y="815" class="body">Conclusión: el resultado agregado es fuerte, pero el mínimo confirma fallos severos que el promedio no muestra.</text>
  <text x="65" y="855" class="small">Fuente: evaluación única del checkpoint ganador sobre Kvasir-SEG test. Uso experimental, no clínico.</text>'''
    return _svg(body, 1400, 900, "Resumen cuantitativo de segmentación", "Dice, IoU, precisión, recall y distribución por imagen.")


def _size_scatter(rows: list[dict[str, str | float]]) -> str:
    left, right, top, bottom = 105, 1335, 150, 690
    parts = []
    for tick in range(6):
        value = tick / 5
        y = bottom - value * (bottom - top)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid"/><text x="88" y="{y + 5:.1f}" class="small" text-anchor="end">{value:.1f}</text>')
    for percent in (0, 15, 30, 45, 60, 75):
        x = left + percent / 75 * (right - left)
        parts.append(f'<text x="{x:.1f}" y="725" class="small" text-anchor="middle">{percent}%</text>')
    for row in rows:
        x = left + float(row["foreground_fraction"]) / 0.75 * (right - left)
        y = bottom - float(row["dice"]) * (bottom - top)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{COLORS[str(row["size_stratum"])]}" fill-opacity="0.7" stroke="#fff"/>')
    legend = []
    x = 170
    for stratum in ("small", "medium", "large"):
        subset = [float(row["dice"]) for row in rows if row["size_stratum"] == stratum]
        legend.append(f'<circle cx="{x}" cy="795" r="8" fill="{COLORS[stratum]}"/><text x="{x + 16}" y="801" class="body">{LABELS[stratum]} · n=50 · mediana {statistics.median(subset):.4f}</text>')
        x += 425
    body = f'''
  <text x="65" y="62" class="title">¿El tamaño del pólipo explica los errores?</text>
  <text x="65" y="101" class="subtitle">Cada punto es una imagen de test; el color indica el estrato usado en el split.</text>
  {''.join(parts)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/><line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>
  <text x="720" y="758" class="label" text-anchor="middle">Porcentaje de la imagen ocupado por el pólipo real</text>
  <text x="30" y="420" class="label" text-anchor="middle" transform="rotate(-90 30 420)">Dice por imagen</text>
  {''.join(legend)}
  <rect x="65" y="835" width="1270" height="92" rx="18" fill="#172033"/>
  <text x="95" y="873" font-size="20" font-weight="700" class="inverse">Conclusión:</text>
  <text x="215" y="873" font-size="19" class="inverse">los pequeños rinden algo peor en mediana, pero el fallo más severo es grande.</text>
  <text x="95" y="904" font-size="16" class="inverse-muted">El tamaño influye, pero no explica por sí solo todos los errores.</text>'''
    return _svg(body, 1400, 960, "Dice frente al tamaño real del pólipo", "Dispersión de Dice por imagen y fracción real de pólipo para 150 casos de test.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics", type=Path)
    parser.add_argument("splits", type=Path)
    parser.add_argument("qualitative_assets", type=Path)
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    global_metrics, rows = _load(args.metrics, args.splits)
    args.output_directory.mkdir(parents=True, exist_ok=True)
    figures = {
        "01-qualitative-comparison.svg": _qualitative(args.qualitative_assets),
        "02-metrics-summary.svg": _summary(global_metrics, rows),
        "03-dice-by-polyp-size.svg": _size_scatter(rows),
    }
    for filename, content in figures.items():
        (args.output_directory / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
