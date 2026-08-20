#!/usr/bin/env python3
"""Registra en MLflow una evaluación completa existente sin repetir inferencia."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
from pathlib import Path

import mlflow
import yaml

from polysight_seg.training.tracking import (
    ExperimentTracker,
    ManagedMlflowServer,
    flatten_parameters,
)


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"Configuración no soportada: {path}")
    return value


def _validate_output(output: Path) -> dict[str, int | float]:
    required = (
        "metrics.json",
        "per-image-metrics.csv",
        "confusion-matrix-counts.csv",
        "confusion-matrix-normalized-true.csv",
        "threshold-curve.csv",
        "qualitative/selection.csv",
    )
    missing = [name for name in required if not (output / name).is_file()]
    if missing:
        raise ValueError(f"Faltan artefactos de evaluación: {missing}")
    metrics = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
    with (output / "per-image-metrics.csv").open(newline="", encoding="utf-8") as stream:
        per_image_count = sum(1 for _ in csv.DictReader(stream))
    probability_count = sum(1 for _ in (output / "probability-maps").glob("*.npz"))
    panel_count = sum(1 for _ in (output / "qualitative").glob("*.png"))
    observed = {
        "sample_count": int(metrics["sample_count"]),
        "per_image_count": per_image_count,
        "probability_map_count": probability_count,
        "qualitative_panel_count": panel_count,
    }
    if observed != {
        "sample_count": 150,
        "per_image_count": 150,
        "probability_map_count": 150,
        "qualitative_panel_count": 15,
    }:
        raise ValueError(f"La evaluación no está completa: {observed}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--original-job-id", required=True)
    parser.add_argument("--original-code-commit", required=True)
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()

    project_root = Path.cwd().resolve()
    evaluation_config_path = args.evaluation_config.resolve()
    evaluation_config = _load_yaml(evaluation_config_path)
    if evaluation_config["run"]["split"] != "test":
        raise ValueError("Solo se recuperan evaluaciones completas de test")
    output = args.output.resolve()
    metrics = _validate_output(output)
    tracking_config = _load_yaml(
        project_root / evaluation_config["references"]["tracking_config"]
    )
    tracking_config = copy.deepcopy(tracking_config)
    host = str(tracking_config["server"]["host"])
    tracking_config["server"]["port"] = args.port
    tracking_config["server"]["tracking_uri"] = f"http://{host}:{args.port}"

    checkpoint = evaluation_config["checkpoint"]
    recovery_job_id = os.environ.get("SLURM_JOB_ID", "no-slurm")
    tags = {
        "code_commit": args.original_code_commit,
        "recovery_code_commit": os.environ.get("RECOVERY_CODE_COMMIT", "unknown"),
        "slurm_job_id": args.original_job_id,
        "recovery_slurm_job_id": recovery_job_id,
        "model_name": "unet-resnet34",
        "dataset_name": "kvasir-seg",
        "run_mode": "full_test_evaluation_artifact_recovery",
        "evaluation_split": "test",
        "source_training_run_id": checkpoint["source_run_id"],
        "checkpoint_sha256": checkpoint["sha256"],
        "inference_repeated": "false",
    }
    summary = {
        "run_mode": "full_test_evaluation_artifact_recovery",
        "split": "test",
        "sample_count": int(metrics["sample_count"]),
        "dice": float(metrics["dice"]),
        "iou": float(metrics["iou"]),
        "checkpoint_sha256": checkpoint["sha256"],
        "source_training_run_id": checkpoint["source_run_id"],
        "original_slurm_job_id": args.original_job_id,
        "recovery_slurm_job_id": recovery_job_id,
        "inference_repeated": False,
        "output_directory": str(output),
    }
    tracker = ExperimentTracker(tracking_config)
    with ManagedMlflowServer(tracking_config["server"], project_root):
        tracker.configure()
        with tracker.start_run(
            run_name=f"{evaluation_config['run']['name']}-recovered-job{args.original_job_id}",
            tags=tags,
        ) as active_run:
            tracker.validate_artifact_uri(active_run.info.artifact_uri)
            mlflow.log_params(flatten_parameters(evaluation_config, prefix="evaluation"))
            mlflow.log_metrics(
                {f"test_{name}": float(value) for name, value in metrics.items()},
                synchronous=True,
            )
            mlflow.log_artifact(str(evaluation_config_path), artifact_path="configs")
            mlflow.log_artifacts(str(output), artifact_path="evaluation")
            summary["mlflow_run_id"] = active_run.info.run_id
            mlflow.log_dict(summary, "evaluation/run-summary.json")
            mlflow.set_tags(tags)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
