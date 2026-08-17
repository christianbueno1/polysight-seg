"""Dataset y DataLoader de Kvasir-SEG para ejecución en CEDIA."""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
import yaml
from torch.utils.data import DataLoader, Dataset

from polysight_seg.data.transforms import build_transforms


VALID_SPLITS = {"train", "validation", "test"}


def load_data_config(path: Path) -> dict[str, Any]:
    """Carga la configuración YAML y comprueba sus campos esenciales."""
    with path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file)
    if config.get("schema_version") != 1:
        raise ValueError("Versión de configuración de datos no soportada")
    if config["dataset"]["mask_threshold"] != 128:
        raise ValueError("El umbral de máscara debe coincidir con el manifest")
    return config


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


class KvasirSegDataset(Dataset[dict[str, Any]]):
    """Carga pares RGB/máscara seleccionados por un split inmutable."""

    def __init__(self, config: dict[str, Any], split: str) -> None:
        if split not in VALID_SPLITS:
            raise ValueError(f"Split no soportado: {split}")
        dataset_config = config["dataset"]
        self.root = Path(dataset_config["root"]).resolve(strict=True)
        self.threshold = dataset_config["mask_threshold"]
        manifest_rows = _read_csv(Path(dataset_config["manifest"]))
        split_rows = _read_csv(Path(dataset_config["splits"]))
        selected_ids = {
            row["sample_id"] for row in split_rows if row["split"] == split
        }
        self.samples = sorted(
            (row for row in manifest_rows if row["sample_id"] in selected_ids),
            key=lambda row: row["sample_id"],
        )
        if len(self.samples) != len(selected_ids):
            raise ValueError(f"El manifest no cubre todos los UUID de {split}")
        self.transform = build_transforms(config, split)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        sample = self.samples[index]
        image_path = self.root / sample["image_path"]
        mask_path = self.root / sample["mask_path"]
        image_bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        mask_gray = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if image_bgr is None or mask_gray is None:
            raise OSError(f"No se pudo decodificar el par {sample['sample_id']}")

        image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mask = (mask_gray >= self.threshold).astype(np.uint8)
        transformed = self.transform(image=image, mask=mask)
        transformed_image = np.ascontiguousarray(
            transformed["image"].transpose(2, 0, 1)
        )
        transformed_mask = np.ascontiguousarray(transformed["mask"][None, ...])
        image_tensor = torch.from_numpy(transformed_image).float()
        mask_tensor = torch.from_numpy(transformed_mask).float()
        if not torch.all((mask_tensor == 0) | (mask_tensor == 1)):
            raise ValueError(f"Máscara no binaria después de transformar: {sample['sample_id']}")
        return {
            "image": image_tensor,
            "mask": mask_tensor,
            "sample_id": sample["sample_id"],
        }


def _seed_worker(worker_id: int) -> None:
    del worker_id
    worker_seed = torch.initial_seed() % 2**32
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def build_dataloader(
    config: dict[str, Any], split: str, seed: int
) -> DataLoader[dict[str, Any]]:
    """Crea un DataLoader con semillas reproducibles por worker."""
    dataset = KvasirSegDataset(config, split)
    loader = config["loader"]
    generator = torch.Generator()
    generator.manual_seed(seed)
    workers = loader["num_workers"]
    return DataLoader(
        dataset,
        batch_size=loader["batch_size"],
        shuffle=split == "train",
        num_workers=workers,
        pin_memory=loader["pin_memory"],
        persistent_workers=loader["persistent_workers"] and workers > 0,
        worker_init_fn=_seed_worker,
        generator=generator,
        drop_last=False,
    )
