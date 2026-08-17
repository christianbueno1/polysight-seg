"""Generación determinista de splits estratificados para Kvasir-SEG."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

from polysight_seg.data.archive import sha256_file


SPLIT_RATIOS = {"train": Decimal("0.70"), "validation": Decimal("0.15"), "test": Decimal("0.15")}
SPLIT_ORDER = tuple(SPLIT_RATIOS)
SIZE_STRATA = ("small", "medium", "large")
DEFAULT_SEED = 20260817
EXPECTED_SPLIT_COUNTS = {"train": 700, "validation": 150, "test": 150}


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    required = {"sample_id", "duplicate_group", "foreground_fraction"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Manifest vacío o sin columnas requeridas: {sorted(required)}")
    if len({row["sample_id"] for row in rows}) != len(rows):
        raise ValueError("El manifest contiene sample_id duplicados")
    return rows


def _group_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        group_id = row["duplicate_group"] or f"sample:{row['sample_id']}"
        grouped[group_id].append(row)

    groups = []
    for group_id, members in grouped.items():
        fractions = [Decimal(member["foreground_fraction"]) for member in members]
        groups.append(
            {
                "group_id": group_id,
                "members": sorted(members, key=lambda item: item["sample_id"]),
                "size": len(members),
                "foreground_fraction": sum(fractions) / len(fractions),
            }
        )
    return groups


def _stratum_thresholds(groups: list[dict[str, Any]]) -> tuple[Decimal, Decimal]:
    fractions = sorted(group["foreground_fraction"] for group in groups)
    small_index = (len(fractions) - 1) // 3
    medium_index = (2 * len(fractions) - 1) // 3
    return fractions[small_index], fractions[medium_index]


def _stratum(fraction: Decimal, thresholds: tuple[Decimal, Decimal]) -> str:
    small_max, medium_max = thresholds
    if fraction <= small_max:
        return "small"
    if fraction <= medium_max:
        return "medium"
    return "large"


def _target_counts(total: int) -> dict[str, int]:
    exact = {name: Decimal(total) * ratio for name, ratio in SPLIT_RATIOS.items()}
    targets = {name: int(value) for name, value in exact.items()}
    remaining = total - sum(targets.values())
    priority = sorted(
        SPLIT_ORDER,
        key=lambda name: (exact[name] - targets[name], -SPLIT_ORDER.index(name)),
        reverse=True,
    )
    for name in priority[:remaining]:
        targets[name] += 1
    return targets


def _assign_groups(
    groups: list[dict[str, Any]], targets: dict[str, int], seed: int
) -> dict[str, str]:
    ordered = sorted(
        groups,
        key=lambda group: hashlib.sha256(
            f"{seed}:{group['group_id']}".encode()
        ).hexdigest(),
    )
    counts = {name: 0 for name in SPLIT_ORDER}
    assignments: dict[str, str] = {}
    for group in ordered:
        destination = max(
            SPLIT_ORDER,
            key=lambda name: (targets[name] - counts[name], -SPLIT_ORDER.index(name)),
        )
        assignments[group["group_id"]] = destination
        counts[destination] += group["size"]
    return assignments


def generate_splits(manifest: Path, output: Path, seed: int = DEFAULT_SEED) -> dict[str, Any]:
    """Genera `splits.csv` y un resumen determinista desde el manifest."""
    manifest = manifest.resolve(strict=True)
    rows = _read_manifest(manifest)
    groups = _group_rows(rows)
    thresholds = _stratum_thresholds(groups)
    groups_by_stratum: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group in groups:
        group["size_stratum"] = _stratum(group["foreground_fraction"], thresholds)
        groups_by_stratum[group["size_stratum"]].append(group)

    assignments: dict[str, str] = {}
    for size_stratum in SIZE_STRATA:
        stratum_groups = groups_by_stratum[size_stratum]
        sample_count = sum(group["size"] for group in stratum_groups)
        assignments.update(_assign_groups(stratum_groups, _target_counts(sample_count), seed))

    split_rows = []
    for group in groups:
        for member in group["members"]:
            split_rows.append(
                {
                    "sample_id": member["sample_id"],
                    "split": assignments[group["group_id"]],
                    "size_stratum": group["size_stratum"],
                    "duplicate_group": member["duplicate_group"],
                }
            )
    split_rows.sort(key=lambda row: row["sample_id"])

    counts = {
        split: sum(row["split"] == split for row in split_rows)
        for split in SPLIT_ORDER
    }
    stratum_counts = {
        split: {
            size: sum(
                row["split"] == split and row["size_stratum"] == size
                for row in split_rows
            )
            for size in SIZE_STRATA
        }
        for split in SPLIT_ORDER
    }
    assignment_digest = hashlib.sha256(
        "".join(
            f"{row['sample_id']},{row['split']},{row['size_stratum']},{row['duplicate_group']}\n"
            for row in split_rows
        ).encode()
    ).hexdigest()
    summary = {
        "schema_version": 1,
        "seed": seed,
        "ratios": {name: float(ratio) for name, ratio in SPLIT_RATIOS.items()},
        "manifest_sha256": sha256_file(manifest),
        "assignment_sha256": assignment_digest,
        "samples": len(split_rows),
        "groups": len(groups),
        "counts": counts,
        "stratum_counts": stratum_counts,
        "stratum_thresholds": {
            "small_max": float(thresholds[0]),
            "medium_max": float(thresholds[1]),
        },
    }

    output.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=output, delete=False
    ) as split_file:
        writer = csv.DictWriter(
            split_file,
            fieldnames=("sample_id", "split", "size_stratum", "duplicate_group"),
        )
        writer.writeheader()
        writer.writerows(split_rows)
        temporary_splits = Path(split_file.name)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=output, delete=False
    ) as summary_file:
        json.dump(summary, summary_file, indent=2, sort_keys=True)
        summary_file.write("\n")
        temporary_summary = Path(summary_file.name)

    temporary_splits.replace(output / "splits.csv")
    temporary_summary.replace(output / "splits-summary.json")
    return summary


def validate_splits(manifest: Path, splits: Path) -> dict[str, Any]:
    """Comprueba cobertura, exclusividad, conteos, estratos y grupos."""
    manifest_rows = _read_manifest(manifest.resolve(strict=True))
    with splits.resolve(strict=True).open(newline="", encoding="utf-8") as file:
        split_rows = list(csv.DictReader(file))
    required = {"sample_id", "split", "size_stratum", "duplicate_group"}
    if not split_rows or not required.issubset(split_rows[0]):
        raise ValueError(f"Splits vacíos o sin columnas requeridas: {sorted(required)}")

    manifest_by_id = {row["sample_id"]: row for row in manifest_rows}
    split_ids = [row["sample_id"] for row in split_rows]
    if len(split_ids) != len(set(split_ids)):
        raise ValueError("Un sample_id aparece más de una vez en splits.csv")
    if set(split_ids) != set(manifest_by_id):
        missing = set(manifest_by_id) - set(split_ids)
        unexpected = set(split_ids) - set(manifest_by_id)
        raise ValueError(
            f"Cobertura inválida: {len(missing)} faltantes y {len(unexpected)} inesperados"
        )

    invalid_splits = {row["split"] for row in split_rows} - set(SPLIT_ORDER)
    invalid_strata = {row["size_stratum"] for row in split_rows} - set(SIZE_STRATA)
    if invalid_splits:
        raise ValueError(f"Nombres de split inválidos: {sorted(invalid_splits)}")
    if invalid_strata:
        raise ValueError(f"Estratos inválidos: {sorted(invalid_strata)}")

    grouped_splits: dict[str, set[str]] = defaultdict(set)
    for row in split_rows:
        manifest_group = manifest_by_id[row["sample_id"]]["duplicate_group"]
        if row["duplicate_group"] != manifest_group:
            raise ValueError(f"Grupo alterado para {row['sample_id']}")
        if manifest_group:
            grouped_splits[manifest_group].add(row["split"])
    leaked_groups = [group for group, values in grouped_splits.items() if len(values) > 1]
    if leaked_groups:
        raise ValueError(f"Grupos presentes en varios splits: {len(leaked_groups)}")

    counts = {
        split: sum(row["split"] == split for row in split_rows)
        for split in SPLIT_ORDER
    }
    if counts != EXPECTED_SPLIT_COUNTS:
        raise ValueError(f"Conteos inesperados: {counts}")
    stratum_counts = {
        split: {
            size: sum(
                row["split"] == split and row["size_stratum"] == size
                for row in split_rows
            )
            for size in SIZE_STRATA
        }
        for split in SPLIT_ORDER
    }
    if any(count == 0 for values in stratum_counts.values() for count in values.values()):
        raise ValueError("Al menos un split no contiene todos los estratos")

    return {
        "status": "ok",
        "samples": len(split_rows),
        "counts": counts,
        "stratum_counts": stratum_counts,
        "duplicate_groups_checked": len(grouped_splits),
    }
