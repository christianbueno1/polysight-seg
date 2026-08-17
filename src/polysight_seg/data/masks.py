"""Contrato de binarización para las máscaras JPEG de Kvasir-SEG."""

from __future__ import annotations

from PIL import Image


MASK_THRESHOLD = 128


def binarize_mask(mask: Image.Image) -> Image.Image:
    """Convierte una máscara a `L` con valores estrictamente 0 y 255."""
    grayscale = mask.convert("L")
    lookup = [0] * MASK_THRESHOLD + [255] * (256 - MASK_THRESHOLD)
    return grayscale.point(lookup, mode="L")
