"""Componentes reutilizables del entrenamiento supervisado."""

from polysight_seg.training.engine import train_one_epoch, validate_one_epoch

__all__ = ["train_one_epoch", "validate_one_epoch"]
