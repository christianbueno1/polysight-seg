#!/usr/bin/env python3
"""Genera cinco folds externos con validation interna, estratos y grupos intactos."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


FOLD_COUNT = 5
VALIDATION_COUNT = 100
SEED = 20260820
SPLITS = ("train", "validation", "test")


def _hash(seed: int, *values: str) -> str:
    return hashlib.sha256(":".join((str(seed), *values)).encode()).hexdigest()


def _read_rows(manifest_path: Path, reference_splits_path: Path) -> list[dict[str, str]]:
    with manifest_path.open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    with reference_splits_path.open(newline="", encoding="utf-8") as stream:
        reference = {row["sample_id"]: row for row in csv.DictReader(stream)}
    if len(manifest) != 1000 or set(reference) != {row["sample_id"] for row in manifest}:
        raise ValueError("Manifest y split de referencia deben cubrir exactamente 1.000 muestras")
    return [
        {
            "sample_id": row["sample_id"],
            "size_stratum": reference[row["sample_id"]]["size_stratum"],
            "duplicate_group": row["duplicate_group"],
            "group_id": row["duplicate_group"] or f"sample:{row['sample_id']}",
        }
        for row in manifest
    ]


def _groups(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        members[row["group_id"]].append(row)
    groups = []
    for group_id, group_rows in members.items():
        strata = {row["size_stratum"] for row in group_rows}
        if len(strata) != 1:
            raise ValueError(f"El grupo {group_id} cruza estratos")
        groups.append(
            {
                "group_id": group_id,
                "size_stratum": strata.pop(),
                "members": sorted(group_rows, key=lambda row: row["sample_id"]),
                "size": len(group_rows),
            }
        )
    return groups


def _outer_assignments(groups: list[dict[str, object]]) -> dict[str, int]:
    assignments: dict[str, int] = {}
    total_counts = [0] * FOLD_COUNT
    stratum_counts: dict[str, list[int]] = defaultdict(lambda: [0] * FOLD_COUNT)
    for stratum in ("small", "medium", "large"):
        candidates = sorted(
            (group for group in groups if group["size_stratum"] == stratum),
            key=lambda group: _hash(SEED, "outer", str(group["group_id"])),
        )
        for group in candidates:
            fold = min(
                range(FOLD_COUNT),
                key=lambda index: (stratum_counts[stratum][index], total_counts[index], index),
            )
            assignments[str(group["group_id"])] = fold
            size = int(group["size"])
            stratum_counts[stratum][fold] += size
            total_counts[fold] += size
    if total_counts != [200] * FOLD_COUNT:
        raise ValueError(f"Los folds externos no tienen 200 muestras: {total_counts}")
    return assignments


def _validation_groups(
    groups: list[dict[str, object]], outer: dict[str, int], fold: int
) -> set[str]:
    selected: list[dict[str, object]] = []
    available = [group for group in groups if outer[str(group["group_id"])] != fold]
    targets = {"small": 34, "medium": 33, "large": 33}
    for stratum, target in targets.items():
        candidates = sorted(
            (group for group in available if group["size_stratum"] == stratum),
            key=lambda group: _hash(SEED, f"fold-{fold + 1}", str(group["group_id"])),
        )
        count = 0
        for group in candidates:
            if count == target:
                break
            if count + int(group["size"]) > target:
                continue
            selected.append(group)
            count += int(group["size"])
        if count != target:
            raise ValueError(f"No se pudo formar validation para fold {fold + 1}, {stratum}")
    identifiers = {str(group["group_id"]) for group in selected}
    if sum(int(group["size"]) for group in selected) != VALIDATION_COUNT:
        raise AssertionError("Validation no contiene 100 muestras")
    return identifiers


def generate(manifest: Path, reference_splits: Path, output: Path) -> dict[str, object]:
    rows = _read_rows(manifest.resolve(strict=True), reference_splits.resolve(strict=True))
    groups = _groups(rows)
    outer = _outer_assignments(groups)
    summaries = []
    all_test_ids: list[str] = []
    for fold in range(FOLD_COUNT):
        validation = _validation_groups(groups, outer, fold)
        fold_rows = []
        for row in rows:
            group_id = row["group_id"]
            split = "test" if outer[group_id] == fold else (
                "validation" if group_id in validation else "train"
            )
            fold_rows.append({key: row[key] for key in ("sample_id", "size_stratum", "duplicate_group")} | {"split": split})
        fold_rows.sort(key=lambda row: row["sample_id"])
        counts = {split: sum(row["split"] == split for row in fold_rows) for split in SPLITS}
        if counts != {"train": 700, "validation": 100, "test": 200}:
            raise ValueError(f"Conteos inválidos en fold {fold + 1}: {counts}")
        test_ids = [row["sample_id"] for row in fold_rows if row["split"] == "test"]
        all_test_ids.extend(test_ids)
        digest_input = "".join(
            f"{row['sample_id']},{row['split']},{row['size_stratum']},{row['duplicate_group']}\n"
            for row in fold_rows
        )
        summary = {
            "schema_version": 1,
            "experiment": "five-fold-cross-validation",
            "seed": SEED,
            "fold": fold + 1,
            "fold_count": FOLD_COUNT,
            "counts": counts,
            "assignment_sha256": hashlib.sha256(digest_input.encode()).hexdigest(),
            "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        }
        fold_root = output / f"fold-{fold + 1:02d}"
        fold_root.mkdir(parents=True, exist_ok=True)
        with (fold_root / "splits.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=("sample_id", "split", "size_stratum", "duplicate_group"))
            writer.writeheader()
            writer.writerows(fold_rows)
        (fold_root / "splits-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summaries.append(summary)
    if len(all_test_ids) != 1000 or len(set(all_test_ids)) != 1000:
        raise ValueError("Cada muestra debe aparecer exactamente una vez como test externo")
    experiment_summary = {
        "schema_version": 1,
        "experiment": "five-fold-cross-validation",
        "seed": SEED,
        "fold_count": FOLD_COUNT,
        "test_coverage": 1000,
        "folds": summaries,
    }
    (output / "summary.json").write_text(json.dumps(experiment_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return experiment_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/processed/kvasir-seg/manifest.csv"))
    parser.add_argument("--reference-splits", type=Path, default=Path("data/processed/kvasir-seg/splits.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/kvasir-seg/cross-validation"))
    args = parser.parse_args()
    print(json.dumps(generate(args.manifest, args.reference_splits, args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
