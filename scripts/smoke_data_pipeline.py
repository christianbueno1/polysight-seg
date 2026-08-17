"""Smoke test del pipeline PyTorch destinado a CEDIA HPC."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch

from polysight_seg.data.dataset import KvasirSegDataset, build_dataloader, load_data_config


EXPECTED_COUNTS = {"train": 700, "validation": 150, "test": 150}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/data/kvasir-seg.yaml"),
    )
    parser.add_argument("--seed", type=int, default=20260817)
    args = parser.parse_args()
    config = load_data_config(args.config)
    results = {"status": "ok", "splits": {}}

    for split, expected_count in EXPECTED_COUNTS.items():
        dataset = KvasirSegDataset(config, split)
        if len(dataset) != expected_count:
            raise ValueError(f"Conteo inesperado para {split}: {len(dataset)}")
        loader = build_dataloader(config, split, args.seed)
        batch = next(iter(loader))
        images = batch["image"]
        masks = batch["mask"]
        if images.ndim != 4 or images.shape[1:] != (3, 256, 256):
            raise ValueError(f"Forma de imágenes inválida en {split}: {images.shape}")
        if masks.ndim != 4 or masks.shape[1:] != (1, 256, 256):
            raise ValueError(f"Forma de máscaras inválida en {split}: {masks.shape}")
        if not torch.isfinite(images).all():
            raise ValueError(f"Valores no finitos en imágenes de {split}")
        if not torch.all((masks == 0) | (masks == 1)):
            raise ValueError(f"Máscaras no binarias en {split}")
        if split != "train":
            first = dataset[0]
            second = dataset[0]
            if not torch.equal(first["image"], second["image"]):
                raise ValueError(f"Transformación no determinista en {split}")
            if not torch.equal(first["mask"], second["mask"]):
                raise ValueError(f"Máscara no determinista en {split}")

        results["splits"][split] = {
            "samples": len(dataset),
            "batches": math.ceil(len(dataset) / config["loader"]["batch_size"]),
            "batch_image_shape": list(images.shape),
            "batch_mask_shape": list(masks.shape),
        }

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
