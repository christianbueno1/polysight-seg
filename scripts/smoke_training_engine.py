#!/usr/bin/env python3
"""Smoke CPU de los loops de train y validation."""

from __future__ import annotations

import json

import torch
from torch import nn

from polysight_seg.training import train_one_epoch, validate_one_epoch


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

    print(
        json.dumps(
            {
                "status": "ok",
                "torch": torch.__version__,
                "device": "cpu",
                "train": train_result,
                "validation": validation_result,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
