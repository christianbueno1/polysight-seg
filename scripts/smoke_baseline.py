"""Smoke forward/backward del baseline real destinado a CEDIA GPU."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from polysight_seg.data.dataset import build_dataloader, load_data_config
from polysight_seg.losses import build_loss
from polysight_seg.metrics import build_metrics
from polysight_seg.models import build_model, load_model_config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-config",
        type=Path,
        default=Path("configs/models/unet-resnet34.yaml"),
    )
    parser.add_argument(
        "--data-config",
        type=Path,
        default=Path("configs/data/kvasir-seg.yaml"),
    )
    parser.add_argument("--seed", type=int, default=20260817)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA no está disponible dentro del trabajo Slurm")

    torch.manual_seed(args.seed)
    device = torch.device("cuda:0")
    torch.cuda.manual_seed_all(args.seed)
    torch.cuda.reset_peak_memory_stats(device)

    model_config = load_model_config(args.model_config)
    data_config = load_data_config(args.data_config)
    loader = build_dataloader(data_config, "train", args.seed)
    batch = next(iter(loader))
    images = batch["image"].to(device, non_blocking=True)
    masks = batch["mask"].to(device, non_blocking=True)

    model = build_model(model_config).to(device).train()
    loss_function = build_loss(model_config).to(device)
    metrics = build_metrics(model_config)

    model.zero_grad(set_to_none=True)
    logits = model(images)
    if logits.shape != masks.shape:
        raise ValueError(f"Forma de salida inválida: {logits.shape} != {masks.shape}")
    if not torch.isfinite(logits).all():
        raise ValueError("El forward produjo logits no finitos")

    loss = loss_function(logits, masks)
    loss.backward()
    gradients = [
        parameter.grad
        for parameter in model.parameters()
        if parameter.grad is not None
    ]
    if not gradients or not all(torch.isfinite(gradient).all() for gradient in gradients):
        raise ValueError("El backward produjo gradientes ausentes o no finitos")

    metrics.update(logits.detach(), masks)
    torch.cuda.synchronize(device)
    report = {
        "status": "ok",
        "device": torch.cuda.get_device_name(device),
        "torch": torch.__version__,
        "cuda_build": torch.version.cuda,
        "batch_image_shape": list(images.shape),
        "batch_mask_shape": list(masks.shape),
        "logits_shape": list(logits.shape),
        "loss": loss.item(),
        "metrics": metrics.compute(),
        "confusion_counts": metrics.confusion_counts(),
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "trainable_parameters": sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        "peak_gpu_memory_bytes": torch.cuda.max_memory_allocated(device),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
