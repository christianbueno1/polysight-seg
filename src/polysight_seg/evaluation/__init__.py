"""Evaluación reproducible de checkpoints seleccionados."""

from polysight_seg.evaluation.checkpoint import load_selected_checkpoint
from polysight_seg.evaluation.engine import EvaluationResult, evaluate_segmentation
from polysight_seg.evaluation.runner import run_evaluation
from polysight_seg.evaluation.qualitative import generate_qualitative_panels
from polysight_seg.evaluation.artifacts import (
    EvaluationArtifactPaths,
    write_evaluation_artifacts,
)

__all__ = [
    "EvaluationArtifactPaths",
    "EvaluationResult",
    "evaluate_segmentation",
    "load_selected_checkpoint",
    "generate_qualitative_panels",
    "run_evaluation",
    "write_evaluation_artifacts",
]
