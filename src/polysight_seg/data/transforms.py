"""Transformaciones sincronizadas para segmentación binaria."""

from __future__ import annotations

from typing import Any

import albumentations as A
import cv2


def build_transforms(config: dict[str, Any], split: str) -> A.Compose:
    """Construye transformaciones train o deterministas de evaluación."""
    if split not in {"train", "validation", "test"}:
        raise ValueError(f"Split no soportado: {split}")

    input_config = config["input"]
    normalization = config["normalization"]
    operations: list[A.BasicTransform] = [
        A.Resize(
            height=input_config["height"],
            width=input_config["width"],
            interpolation=cv2.INTER_LINEAR,
            p=1.0,
        )
    ]
    if split == "train":
        train = config["transforms"]["train"]
        operations.extend(
            [
                A.HorizontalFlip(p=train["horizontal_flip_probability"]),
                A.VerticalFlip(p=train["vertical_flip_probability"]),
                A.Rotate(
                    limit=train["rotate_limit_degrees"],
                    border_mode=cv2.BORDER_CONSTANT,
                    p=train["rotate_probability"],
                ),
                A.RandomBrightnessContrast(
                    p=train["brightness_contrast_probability"]
                ),
            ]
        )
    operations.append(
        A.Normalize(
            mean=normalization["mean"],
            std=normalization["std"],
            max_pixel_value=255.0,
            p=1.0,
        )
    )
    return A.Compose(operations)
