"""Orquestación del checkpoint seleccionado, inferencia y artefactos."""

from __future__ import annotations

import copy
import json
import os
import random
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
import mlflow

from polysight_seg.data.dataset import build_dataloader, load_data_config
from polysight_seg.evaluation.artifacts import write_evaluation_artifacts
from polysight_seg.evaluation.checkpoint import load_selected_checkpoint
from polysight_seg.evaluation.engine import evaluate_segmentation
from polysight_seg.evaluation.qualitative import generate_qualitative_panels
from polysight_seg.models import build_model, load_model_config
from polysight_seg.tracking_config import apply_mlflow_environment
from polysight_seg.training.tracking import (
    ExperimentTracker,
    ManagedMlflowServer,
    flatten_parameters,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError(f"Configuración no soportada: {path}")
    return config


def _git_status(project_root: Path) -> str:
    return subprocess.run(
        ("git", "status", "--porcelain"), cwd=project_root,
        check=True, capture_output=True, text=True
    ).stdout.strip()


def run_evaluation(
    evaluation_config_path: Path,
    *,
    split_override: str | None = None,
    max_batches: int | None = None,
) -> dict[str, Any]:
    """Ejecuta smoke en validation o evaluación final completa en test."""

    project_root = Path.cwd().resolve()
    evaluation_config = _load_yaml(evaluation_config_path.resolve())
    split = split_override or evaluation_config["run"]["split"]
    if split not in {"validation", "test"}:
        raise ValueError("La evaluación solo admite validation o test")
    if split == "test" and max_batches is not None:
        raise ValueError("Test no admite evaluación parcial; debe ejecutarse una sola vez")
    if split == "validation" and max_batches is None:
        raise ValueError("El smoke de validation requiere --max-batches")
    dirty = _git_status(project_root)
    if dirty:
        raise RuntimeError(f"El repositorio debe estar limpio antes de evaluar:\n{dirty}")

    references = evaluation_config["references"]
    data_config = load_data_config(project_root / references["data_config"])
    model_config = load_model_config(project_root / references["model_config"])
    tracking_config = apply_mlflow_environment(
        _load_yaml(project_root / references["tracking_config"])
    )
    model_config = copy.deepcopy(model_config)
    model_config["model"]["encoder_weights"] = None

    seed = int(evaluation_config["run"]["seed"])
    reproducibility = evaluation_config["runtime"]["reproducibility"]
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = reproducibility["cublas_workspace_config"]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(
        reproducibility["deterministic_algorithms"],
        warn_only=reproducibility["deterministic_warn_only"],
    )
    torch.backends.cudnn.benchmark = reproducibility["cudnn_benchmark"]
    if evaluation_config["runtime"]["device"] != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("La evaluación real requiere CUDA dentro de Slurm")
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
    torch.cuda.manual_seed_all(seed)

    model = build_model(model_config).to(device)
    checkpoint = evaluation_config["checkpoint"]
    checkpoint_path = project_root / checkpoint["path"]
    load_selected_checkpoint(
        checkpoint_path,
        expected_sha256=checkpoint["sha256"],
        expected_run_id=checkpoint["source_run_id"],
        expected_epoch=int(checkpoint["selected_epoch"]),
        expected_selection_metric=checkpoint["selection_metric"],
        expected_selection_value=float(checkpoint["selection_value"]),
        model=model,
        map_location=device,
    )
    dataloader = build_dataloader(data_config, split, seed)
    prediction = evaluation_config["prediction"]
    amp = evaluation_config["runtime"]["mixed_precision"]
    run_mode = "full_test_evaluation" if split == "test" else "smoke_validation"
    output_base = project_root / evaluation_config["outputs"]["directory"]
    if run_mode == "smoke_validation":
        output_root = output_base / "smoke" / os.environ.get("SLURM_JOB_ID", "local")
    else:
        output_root = output_base / "test"
    if run_mode == "full_test_evaluation" and output_root.exists():
        raise RuntimeError(
            "El directorio final de test ya existe; no se repetirá la evaluación"
        )

    result = evaluate_segmentation(
        model,
        dataloader,
        device,
        threshold=float(prediction["threshold"]),
        threshold_values=[
            float(value) for value in evaluation_config["threshold_analysis"]["values"]
        ],
        amp_enabled=bool(amp["enabled"]),
        amp_dtype=torch.float16,
        preserve_probability_maps=bool(prediction["preserve_probability_maps"]),
        max_batches=max_batches,
    )

    paths = write_evaluation_artifacts(result, output_root, evaluation_config["outputs"])
    qualitative = evaluation_config["qualitative_analysis"]
    selection_path = generate_qualitative_panels(
        dataloader.dataset,
        result,
        output_root / evaluation_config["outputs"]["qualitative_directory"],
        threshold=float(prediction["threshold"]),
        best_cases=int(qualitative["best_cases"]),
        median_cases=int(qualitative["median_cases"]),
        worst_cases=int(qualitative["worst_cases"]),
    )
    summary: dict[str, Any] = {
        "run_mode": run_mode,
        "split": split,
        "sample_count": result.aggregate["sample_count"],
        "dice": result.aggregate["dice"],
        "iou": result.aggregate["iou"],
        "checkpoint_sha256": checkpoint["sha256"],
        "source_training_run_id": checkpoint["source_run_id"],
        "output_directory": str(output_root),
        "metrics_path": str(paths.metrics),
        "qualitative_selection_path": str(selection_path),
    }
    slurm_job_id = os.environ.get("SLURM_JOB_ID", "no-slurm")
    tags = {
        "code_commit": subprocess.run(
            ("git", "rev-parse", "HEAD"), cwd=project_root,
            check=True, capture_output=True, text=True
        ).stdout.strip(),
        "slurm_job_id": slurm_job_id,
        "model_name": model_config["model"]["name"],
        "dataset_name": data_config["dataset"]["name"],
        "run_mode": run_mode,
        "evaluation_split": split,
        "source_training_run_id": checkpoint["source_run_id"],
        "checkpoint_sha256": checkpoint["sha256"],
    }
    tracker = ExperimentTracker(tracking_config)
    with ManagedMlflowServer(tracking_config["server"], project_root):
        tracker.configure()
        with tracker.start_run(
            run_name=f"{evaluation_config['run']['name']}-{run_mode}-job{slurm_job_id}",
            tags=tags,
        ) as active_run:
            tracker.validate_artifact_uri(active_run.info.artifact_uri)
            mlflow.log_params(flatten_parameters(evaluation_config, prefix="evaluation"))
            mlflow.log_metrics(
                {
                    f"test_{name}" if split == "test" else f"smoke_val_{name}": float(value)
                    for name, value in result.aggregate.items()
                },
                synchronous=True,
            )
            mlflow.log_artifact(str(evaluation_config_path), artifact_path="configs")
            mlflow.log_artifacts(str(output_root), artifact_path="evaluation")
            summary["mlflow_run_id"] = active_run.info.run_id
            mlflow.log_dict(summary, "evaluation/run-summary.json")
            mlflow.set_tags(tags)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary
