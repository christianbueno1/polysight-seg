"""Orquestación reproducible del entrenamiento baseline con MLflow."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import mlflow
import numpy as np
import torch
import yaml

from polysight_seg.data.dataset import build_dataloader, load_data_config
from polysight_seg.losses import build_loss
from polysight_seg.models import build_model, load_model_config
from polysight_seg.tracking_config import apply_mlflow_environment
from polysight_seg.training.checkpointing import (
    load_training_checkpoint,
    save_epoch_checkpoints,
)
from polysight_seg.training.engine import train_one_epoch, validate_one_epoch
from polysight_seg.training.tracking import (
    ExperimentTracker,
    ManagedMlflowServer,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError(f"Configuración no soportada: {path}")
    return config


def _run_command(*command: str, cwd: Path) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dataset_hashes(data_config: dict[str, Any]) -> dict[str, str]:
    dataset = data_config["dataset"]
    manifest_path = Path(dataset["manifest"])
    splits_path = Path(dataset["splits"])
    summary_path = manifest_path.parent / "summary.json"
    splits_summary_path = splits_path.parent / "splits-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    splits_summary = json.loads(splits_summary_path.read_text(encoding="utf-8"))
    hashes = {
        "source_sha256": str(summary["source_sha256"]),
        "manifest_sha256": _sha256(manifest_path),
        "splits_sha256": _sha256(splits_path),
        "split_assignment_sha256": str(splits_summary["assignment_sha256"]),
        "dataset_summary_sha256": _sha256(summary_path),
        "splits_summary_sha256": _sha256(splits_summary_path),
    }
    if hashes["manifest_sha256"] != str(splits_summary["manifest_sha256"]):
        raise ValueError("El hash real del manifest no coincide con splits-summary.json")
    return hashes


def _runtime_info(device: torch.device) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "torch": str(torch.__version__),
        "mlflow": mlflow.__version__,
        "cuda_build": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "device": str(device),
        "device_name": (
            torch.cuda.get_device_name(device) if device.type == "cuda" else "cpu"
        ),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_partition": os.environ.get("SLURM_JOB_PARTITION"),
        "loaded_modules": os.environ.get("LOADEDMODULES", ""),
    }


def _write_history(path: Path, history: list[dict[str, Any]]) -> None:
    if not history:
        raise ValueError("No existe historial para guardar")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(history[0])
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            writer = csv.DictWriter(temporary_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(history)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _load_history(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _metric_improved(
    current: float,
    best: float | None,
    mode: str,
    min_delta: float,
) -> bool:
    if best is None:
        return True
    if mode == "max":
        return current > best + min_delta
    if mode == "min":
        return current < best - min_delta
    raise ValueError(f"Modo de selección no soportado: {mode}")


def _resolve_configs(
    training_config_path: Path,
    project_root: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[Path],
]:
    training_config = _load_yaml(training_config_path)
    references = training_config["references"]
    data_path = (project_root / references["data_config"]).resolve()
    model_path = (project_root / references["model_config"]).resolve()
    tracking_path = (project_root / references["tracking_config"]).resolve()
    data_config = load_data_config(data_path)
    model_config = load_model_config(model_path)
    tracking_config = apply_mlflow_environment(_load_yaml(tracking_path))
    if training_config["test"]["enabled"]:
        raise ValueError("Test debe permanecer deshabilitado durante la Fase 5")
    if training_config["validation"]["split"] != "validation":
        raise ValueError("La selección debe usar exclusivamente validation")
    return (
        training_config,
        data_config,
        model_config,
        tracking_config,
        [training_config_path, data_path, model_path, tracking_path],
    )


def run_training(
    training_config_path: Path,
    *,
    max_train_batches: int | None = None,
    max_validation_batches: int | None = None,
) -> dict[str, Any]:
    """Ejecuta entrenamiento, tracking, selección y early stopping."""

    project_root = Path.cwd().resolve()
    training_config_path = training_config_path.resolve()
    (
        training_config,
        data_config,
        model_config,
        tracking_config,
        config_paths,
    ) = _resolve_configs(training_config_path, project_root)

    dirty_files = _run_command("git", "status", "--porcelain", cwd=project_root)
    if dirty_files:
        raise RuntimeError(f"El repositorio debe estar limpio antes de entrenar:\n{dirty_files}")
    code_commit = _run_command("git", "rev-parse", "HEAD", cwd=project_root)
    pip_freeze = _run_command(sys.executable, "-m", "pip", "freeze", cwd=project_root)
    dataset_hashes = _dataset_hashes(data_config)

    seed = int(training_config["run"]["seed"])
    reproducibility = training_config["runtime"]["reproducibility"]
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = reproducibility[
        "cublas_workspace_config"
    ]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(
        reproducibility["deterministic_algorithms"],
        warn_only=reproducibility["deterministic_warn_only"],
    )
    torch.backends.cudnn.benchmark = reproducibility["cudnn_benchmark"]

    if training_config["runtime"]["device"] != "cuda":
        raise ValueError("El baseline completo está configurado exclusivamente para CUDA")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA no está disponible dentro del job Slurm")
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
    torch.cuda.manual_seed_all(seed)

    train_loader = build_dataloader(data_config, "train", seed)
    validation_loader = build_dataloader(data_config, "validation", seed)
    model = build_model(model_config).to(device)
    loss_function = build_loss(model_config).to(device)
    optimizer_config = training_config["optimizer"]
    if optimizer_config["name"] != "adamw":
        raise ValueError("Optimizador no soportado")
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(optimizer_config["learning_rate"]),
        weight_decay=float(optimizer_config["weight_decay"]),
        betas=tuple(float(value) for value in optimizer_config["betas"]),
        eps=float(optimizer_config["epsilon"]),
    )
    scheduler_config = training_config["scheduler"]
    if scheduler_config["name"] != "reduce_lr_on_plateau":
        raise ValueError("Scheduler no soportado")
    selection = training_config["selection"]
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode=selection["mode"],
        factor=float(scheduler_config["factor"]),
        patience=int(scheduler_config["patience_epochs"]),
        threshold=float(scheduler_config["threshold"]),
        threshold_mode=scheduler_config["threshold_mode"],
        cooldown=int(scheduler_config["cooldown_epochs"]),
        min_lr=float(scheduler_config["min_learning_rate"]),
    )
    amp_config = training_config["runtime"]["mixed_precision"]
    if amp_config["dtype"] != "float16":
        raise ValueError("Dtype AMP no soportado")
    amp_enabled = bool(amp_config["enabled"])
    grad_scaler = torch.amp.GradScaler(
        "cuda",
        enabled=amp_enabled and bool(amp_config["gradient_scaling"]),
    )

    threshold = float(model_config["output"]["initial_threshold"])
    checkpoint_config = training_config["checkpointing"]
    resume_value = checkpoint_config["resume_from"]
    resume_path = (project_root / resume_value).resolve() if resume_value else None
    start_epoch = 1
    best_metric: float | None = None
    epochs_without_improvement = 0
    global_step = 0
    resumed_run_id: str | None = None
    checkpoint_directory: Path | None = None
    history: list[dict[str, Any]] = []
    if resume_path is not None:
        payload = load_training_checkpoint(
            resume_path,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            grad_scaler=grad_scaler,
            map_location=device,
        )
        start_epoch = int(payload["next_epoch"])
        best_metric = float(payload["selection"]["best_metric"])
        epochs_without_improvement = int(
            payload["trainer_state"]["epochs_without_improvement"]
        )
        global_step = int(payload["trainer_state"]["global_step"])
        generator_state = payload["trainer_state"].get("data_loader_generator_state")
        if generator_state is not None:
            train_loader.generator.set_state(generator_state)
        resumed_run_id = payload["metadata"].get("mlflow_run_id")
        checkpoint_directory = resume_path.parent
        history = _load_history(checkpoint_directory / "history.csv")

    tracker = ExperimentTracker(tracking_config)
    run_mode = (
        "smoke"
        if max_train_batches is not None or max_validation_batches is not None
        else "full"
    )
    slurm_job_id = os.environ.get("SLURM_JOB_ID", "no-slurm")
    run_name = (
        f"{tracking_config['experiment']['run_name_prefix']}-"
        f"seed{seed}-job{slurm_job_id}"
    )
    tags = {
        "code_commit": code_commit,
        "slurm_job_id": slurm_job_id,
        "model_name": model_config["model"]["name"],
        "dataset_name": data_config["dataset"]["name"],
        "run_mode": run_mode,
    }
    config_snapshot = {
        "training": training_config,
        "data": data_config,
        "model": model_config,
        "tracking": tracking_config,
    }

    with ManagedMlflowServer(tracking_config["server"], project_root):
        tracker.configure()
        with tracker.start_run(
            run_name=run_name,
            tags=tags,
            run_id=resumed_run_id,
        ) as active_run:
            mlflow.set_tags(tags)
            tracker.validate_artifact_uri(active_run.info.artifact_uri)
            tracker.log_initial_state(
                configs=config_snapshot,
                config_paths=config_paths,
                dataset_hashes=dataset_hashes,
                runtime=_runtime_info(device),
                pip_freeze=pip_freeze,
            )
            if checkpoint_directory is None:
                checkpoint_directory = (
                    project_root
                    / checkpoint_config["directory"]
                    / active_run.info.run_id
                )
            history_path = checkpoint_directory / "history.csv"
            stop_reason = "max_epochs"
            last_checkpoint_path: Path | None = None

            for epoch in range(start_epoch, int(training_config["run"]["max_epochs"]) + 1):
                train_metrics = train_one_epoch(
                    model,
                    train_loader,
                    loss_function,
                    optimizer,
                    device,
                    threshold=threshold,
                    amp_enabled=amp_enabled,
                    grad_scaler=grad_scaler,
                    gradient_accumulation_steps=int(
                        training_config["training"]["gradient_accumulation_steps"]
                    ),
                    gradient_clip_max_norm=float(
                        training_config["training"]["gradient_clip_max_norm"]
                    ),
                    zero_grad_set_to_none=bool(
                        training_config["training"]["zero_grad_set_to_none"]
                    ),
                    max_batches=max_train_batches,
                )
                validation_metrics = validate_one_epoch(
                    model,
                    validation_loader,
                    loss_function,
                    device,
                    threshold=threshold,
                    amp_enabled=amp_enabled,
                    max_batches=max_validation_batches,
                )
                epoch_metrics = {**train_metrics, **validation_metrics}
                current_metric = float(epoch_metrics[selection["metric"]])
                improved = _metric_improved(
                    current_metric,
                    best_metric,
                    selection["mode"],
                    float(selection["min_delta"]),
                )
                epochs_without_improvement = (
                    0 if improved else epochs_without_improvement + 1
                )
                planned_train_batches = min(
                    len(train_loader),
                    max_train_batches if max_train_batches is not None else len(train_loader),
                )
                global_step += planned_train_batches
                scheduler.step(current_metric)

                checkpoint_result = save_epoch_checkpoints(
                    directory=checkpoint_directory,
                    last_filename=checkpoint_config["last_filename"],
                    best_filename=checkpoint_config["best_filename"],
                    epoch=epoch,
                    current_metric=current_metric,
                    best_metric=best_metric,
                    selection_metric=selection["metric"],
                    selection_mode=selection["mode"],
                    min_delta=float(selection["min_delta"]),
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    grad_scaler=grad_scaler,
                    metrics=epoch_metrics,
                    trainer_state={
                        "global_step": global_step,
                        "epochs_without_improvement": epochs_without_improvement,
                        "data_loader_generator_state": train_loader.generator.get_state(),
                    },
                    config_snapshot=config_snapshot,
                    code_commit=code_commit,
                    dataset_hashes=dataset_hashes,
                    architecture=model_config["model"],
                    threshold=threshold,
                    slurm_job_id=slurm_job_id,
                    mlflow_run_id=active_run.info.run_id,
                )
                if checkpoint_result.improved != improved:
                    raise RuntimeError("Checkpoint y runner discrepan sobre best.pt")
                best_metric = checkpoint_result.best_metric
                last_checkpoint_path = checkpoint_result.last_path
                history.append(
                    {
                        "epoch": epoch,
                        **epoch_metrics,
                        "is_best": improved,
                        "best_val_dice": best_metric,
                    }
                )
                _write_history(history_path, history)
                tracker.log_epoch(epoch_metrics, epoch)
                tracker.log_history(history_path)
                if checkpoint_result.best_path is not None:
                    tracker.log_checkpoint(
                        checkpoint_result.best_path,
                        "checkpoints/best",
                    )

                print(json.dumps(history[-1], sort_keys=True), flush=True)
                if (
                    training_config["early_stopping"]["enabled"]
                    and epochs_without_improvement
                    >= int(training_config["early_stopping"]["patience_epochs"])
                ):
                    stop_reason = "early_stopping"
                    break

            if last_checkpoint_path is None or best_metric is None:
                raise RuntimeError("El entrenamiento terminó sin producir checkpoints")
            tracker.log_checkpoint(last_checkpoint_path, "checkpoints/last")
            summary = {
                "run_id": active_run.info.run_id,
                "run_mode": run_mode,
                "start_epoch": start_epoch,
                "end_epoch": int(history[-1]["epoch"]),
                "best_val_dice": best_metric,
                "stop_reason": stop_reason,
                "global_step": global_step,
                "checkpoint_directory": str(checkpoint_directory),
            }
            tracker.log_summary(summary)
            mlflow.set_tag("training.stop_reason", stop_reason)
            print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
            return summary
