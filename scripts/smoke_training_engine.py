#!/usr/bin/env python3
"""Smoke CPU de los loops de train y validation."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import torch
from torch import nn

from polysight_seg.training import (
    load_training_checkpoint,
    save_epoch_checkpoints,
    train_one_epoch,
    validate_one_epoch,
    verify_checkpoint_hash,
)


def main() -> None:
    if torch.cuda.is_available():
        raise RuntimeError("Este smoke contractual no debe recibir una GPU")

    model = nn.Conv2d(1, 1, kernel_size=1, bias=False)
    with torch.no_grad():
        model.weight.fill_(0.2)
    batches = [
        {
            "image": torch.zeros(2, 1, 2, 2),
            "mask": torch.ones(2, 1, 2, 2),
        },
        {
            "image": torch.ones(1, 1, 2, 2),
            "mask": torch.ones(1, 1, 2, 2),
        },
    ]
    loss_function = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)

    with torch.no_grad():
        batch_losses = [
            loss_function(model(batch["image"]), batch["mask"]).item()
            for batch in batches
        ]
    expected_train_loss = (2 * batch_losses[0] + batch_losses[1]) / 3
    weight_before_train = model.weight.detach().clone()
    train_result = train_one_epoch(
        model,
        batches,
        loss_function,
        optimizer,
        torch.device("cpu"),
        threshold=0.5,
        gradient_accumulation_steps=2,
        gradient_clip_max_norm=1.0,
    )
    if not torch.isclose(
        torch.tensor(train_result["train_loss"]),
        torch.tensor(expected_train_loss),
    ):
        raise RuntimeError("La pérdida de train no está ponderada por muestra")
    if torch.equal(weight_before_train, model.weight.detach()):
        raise RuntimeError("Train no modificó los parámetros")

    weight_before_validation = model.weight.detach().clone()
    validation_result = validate_one_epoch(
        model,
        batches,
        loss_function,
        torch.device("cpu"),
        threshold=0.5,
    )
    if not torch.equal(weight_before_validation, model.weight.detach()):
        raise RuntimeError("Validation modificó los parámetros")

    expected_train_keys = {
        "train_loss",
        "train_dice",
        "train_iou",
        "train_precision",
        "train_recall",
        "train_tp",
        "train_fp",
        "train_fn",
        "train_tn",
        "learning_rate",
    }
    expected_validation_keys = {
        key.replace("train_", "val_")
        for key in expected_train_keys
        if key != "learning_rate"
    }
    if set(train_result) != expected_train_keys:
        raise RuntimeError(f"Métricas de train inesperadas: {sorted(train_result)}")
    if set(validation_result) != expected_validation_keys:
        raise RuntimeError(
            f"Métricas de validation inesperadas: {sorted(validation_result)}"
        )

    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max")
    checkpoint_report: dict[str, object]
    with tempfile.TemporaryDirectory(prefix="polysight-checkpoint-") as temporary_dir:
        checkpoint_directory = Path(temporary_dir)
        expected_weight = model.weight.detach().clone()
        first_save = save_epoch_checkpoints(
            directory=checkpoint_directory,
            last_filename="last.pt",
            best_filename="best.pt",
            epoch=1,
            current_metric=float(validation_result["val_dice"]),
            best_metric=None,
            selection_metric="val_dice",
            selection_mode="max",
            min_delta=1.0e-4,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            grad_scaler=None,
            metrics={**train_result, **validation_result},
            trainer_state={"global_step": 1, "epochs_without_improvement": 0},
            config_snapshot={"run": {"seed": 20260817}},
            code_commit="smoke-contract",
            dataset_hashes={"manifest_sha256": "0" * 64},
            architecture={"name": "conv2d-smoke"},
            threshold=0.5,
            slurm_job_id=None,
            mlflow_run_id=None,
        )
        if not first_save.improved or first_save.best_path is None:
            raise RuntimeError("La primera época no creó best.pt")
        initial_best_hash = verify_checkpoint_hash(first_save.best_path)

        with torch.no_grad():
            model.weight.add_(10.0)
        loaded = load_training_checkpoint(
            first_save.last_path,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            restore_rng=False,
        )
        if not torch.equal(expected_weight, model.weight.detach()):
            raise RuntimeError("La carga no restauró los pesos del modelo")
        if loaded["next_epoch"] != 2:
            raise RuntimeError("El checkpoint no indica la próxima época")

        second_save = save_epoch_checkpoints(
            directory=checkpoint_directory,
            last_filename="last.pt",
            best_filename="best.pt",
            epoch=2,
            current_metric=0.5,
            best_metric=first_save.best_metric,
            selection_metric="val_dice",
            selection_mode="max",
            min_delta=1.0e-4,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            grad_scaler=None,
            metrics={"val_dice": 0.5},
            trainer_state={"global_step": 2, "epochs_without_improvement": 1},
            config_snapshot={"run": {"seed": 20260817}},
            code_commit="smoke-contract",
            dataset_hashes={"manifest_sha256": "0" * 64},
            architecture={"name": "conv2d-smoke"},
            threshold=0.5,
        )
        if second_save.improved or second_save.best_path is not None:
            raise RuntimeError("Una métrica peor reemplazó indebidamente best.pt")
        if verify_checkpoint_hash(checkpoint_directory / "best.pt") != initial_best_hash:
            raise RuntimeError("best.pt cambió sin una mejora de validation")
        checkpoint_report = {
            "first_epoch_improved": first_save.improved,
            "second_epoch_improved": second_save.improved,
            "best_metric": second_save.best_metric,
            "last_sha256": second_save.last_sha256,
            "best_sha256": initial_best_hash,
            "restored_next_epoch": loaded["next_epoch"],
        }

    print(
        json.dumps(
            {
                "status": "ok",
                "torch": torch.__version__,
                "device": "cpu",
                "train": train_result,
                "validation": validation_result,
                "checkpoint": checkpoint_report,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
