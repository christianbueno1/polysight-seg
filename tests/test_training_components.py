"""Contratos CPU del motor, checkpoints, tracking y runner."""

from __future__ import annotations

import csv
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch
import yaml
from torch import nn

from polysight_seg.data.dataset import load_data_config
from polysight_seg.evaluation.checkpoint import load_selected_checkpoint
from polysight_seg.training.checkpointing import (
    load_training_checkpoint,
    save_epoch_checkpoints,
    verify_checkpoint_hash,
)
from polysight_seg.training.engine import train_one_epoch, validate_one_epoch
from polysight_seg.training.runner import (
    _dataset_hashes,
    _metric_improved,
    _write_history,
)
from polysight_seg.training.tracking import ExperimentTracker, flatten_parameters


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ScalarModel(nn.Module):
    """Modelo mínimo con un único peso y registro de modo."""

    def __init__(self, initial_weight: float = 0.0) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.tensor(initial_weight))
        self.training_modes: list[bool] = []

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        self.training_modes.append(self.training)
        return inputs * self.weight


def _batches() -> list[dict[str, torch.Tensor]]:
    return [
        {
            "image": torch.zeros(2, 1, 2, 2),
            "mask": torch.ones(2, 1, 2, 2),
        },
        {
            "image": torch.ones(1, 1, 2, 2),
            "mask": torch.ones(1, 1, 2, 2),
        },
    ]


class TrainingEngineTest(unittest.TestCase):
    def test_train_and_validation_respect_modes_and_sample_weighting(self) -> None:
        model = ScalarModel(initial_weight=0.2)
        batches = _batches()
        loss_function = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with torch.no_grad():
            losses = [
                loss_function(model(batch["image"]), batch["mask"]).item()
                for batch in batches
            ]
        model.training_modes.clear()
        expected_loss = (2 * losses[0] + losses[1]) / 3

        weight_before_train = model.weight.detach().clone()
        train_result = train_one_epoch(
            model,
            batches,
            loss_function,
            optimizer,
            torch.device("cpu"),
            threshold=0.5,
            gradient_accumulation_steps=2,
        )
        self.assertTrue(all(model.training_modes))
        self.assertAlmostEqual(train_result["train_loss"], expected_loss)
        self.assertFalse(torch.equal(weight_before_train, model.weight.detach()))
        self.assertEqual(train_result["train_tp"], 12)

        model.training_modes.clear()
        weight_before_validation = model.weight.detach().clone()
        validation_result = validate_one_epoch(
            model,
            batches,
            loss_function,
            torch.device("cpu"),
            threshold=0.5,
        )
        self.assertTrue(not mode for mode in model.training_modes)
        self.assertTrue(torch.equal(weight_before_validation, model.weight.detach()))
        self.assertEqual(validation_result["val_tp"], 12)

    def test_incomplete_accumulation_group_uses_its_real_size(self) -> None:
        model = ScalarModel(initial_weight=0.0)
        batches = [
            {"image": torch.ones(1, 1, 1, 1), "mask": torch.ones(1, 1, 1, 1)}
            for _ in range(3)
        ]
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        train_one_epoch(
            model,
            batches,
            nn.MSELoss(),
            optimizer,
            torch.device("cpu"),
            threshold=0.5,
            gradient_accumulation_steps=2,
        )
        self.assertAlmostEqual(model.weight.item(), 0.36, places=6)

    def test_invalid_runtime_options_are_rejected(self) -> None:
        model = ScalarModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with self.assertRaises(ValueError):
            train_one_epoch(
                model,
                _batches(),
                nn.BCEWithLogitsLoss(),
                optimizer,
                torch.device("cpu"),
                threshold=0.5,
                gradient_accumulation_steps=0,
            )
        with self.assertRaises(ValueError):
            validate_one_epoch(
                model,
                _batches(),
                nn.BCEWithLogitsLoss(),
                torch.device("cpu"),
                threshold=0.5,
                amp_enabled=True,
            )


class CheckpointingTest(unittest.TestCase):
    def _save(
        self,
        directory: Path,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        *,
        epoch: int = 1,
        current_metric: float = 0.8,
        best_metric: float | None = None,
        mlflow_run_id: str | None = None,
    ):
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max")
        return save_epoch_checkpoints(
            directory=directory,
            last_filename="last.pt",
            best_filename="best.pt",
            epoch=epoch,
            current_metric=current_metric,
            best_metric=best_metric,
            selection_metric="val_dice",
            selection_mode="max",
            min_delta=1.0e-4,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            grad_scaler=None,
            metrics={"val_dice": current_metric},
            trainer_state={"global_step": epoch, "epochs_without_improvement": 0},
            config_snapshot={"schema_version": 1},
            code_commit="test-commit",
            dataset_hashes={"manifest_sha256": "0" * 64},
            architecture={"name": "scalar"},
            threshold=0.5,
            mlflow_run_id=mlflow_run_id,
        )

    def test_best_selection_hash_and_state_restoration(self) -> None:
        model = ScalarModel(initial_weight=0.25)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with tempfile.TemporaryDirectory() as temporary_dir:
            directory = Path(temporary_dir)
            first = self._save(directory, model, optimizer)
            self.assertTrue(first.improved)
            self.assertIsNotNone(first.best_path)
            best_hash = verify_checkpoint_hash(directory / "best.pt")
            expected_weight = model.weight.detach().clone()

            with torch.no_grad():
                model.weight.add_(5.0)
            payload = load_training_checkpoint(
                directory / "last.pt",
                model=model,
                optimizer=optimizer,
                restore_rng=False,
            )
            self.assertTrue(torch.equal(expected_weight, model.weight.detach()))
            self.assertEqual(payload["next_epoch"], 2)

            second = self._save(
                directory,
                model,
                optimizer,
                epoch=2,
                current_metric=0.7,
                best_metric=first.best_metric,
            )
            self.assertFalse(second.improved)
            self.assertIsNone(second.best_path)
            self.assertEqual(verify_checkpoint_hash(directory / "best.pt"), best_hash)

    def test_hash_tampering_is_rejected(self) -> None:
        model = ScalarModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self._save(Path(temporary_dir), model, optimizer)
            with result.last_path.open("ab") as file:
                file.write(b"tampered")
            with self.assertRaises(ValueError):
                verify_checkpoint_hash(result.last_path)

    def test_rng_state_is_restored(self) -> None:
        random.seed(7)
        np.random.seed(7)
        torch.manual_seed(7)
        model = ScalarModel()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self._save(Path(temporary_dir), model, optimizer)
            expected = (random.random(), float(np.random.rand()), torch.rand(1))
            random.random()
            np.random.rand()
            torch.rand(1)
            load_training_checkpoint(
                result.last_path,
                model=model,
                optimizer=optimizer,
                restore_rng=True,
            )
            actual = (random.random(), float(np.random.rand()), torch.rand(1))
            self.assertEqual(actual[0], expected[0])
            self.assertEqual(actual[1], expected[1])
            self.assertTrue(torch.equal(actual[2], expected[2]))

    def test_selected_checkpoint_validates_identity_before_loading(self) -> None:
        source_model = ScalarModel(initial_weight=0.25)
        optimizer = torch.optim.SGD(source_model.parameters(), lr=0.1)
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self._save(
                Path(temporary_dir),
                source_model,
                optimizer,
                mlflow_run_id="source-run",
            )
            target_model = ScalarModel(initial_weight=9.0)
            payload = load_selected_checkpoint(
                result.best_path,
                expected_sha256=result.best_sha256,
                expected_run_id="source-run",
                expected_epoch=1,
                expected_selection_metric="val_dice",
                expected_selection_value=0.8,
                model=target_model,
            )
            self.assertEqual(payload["epoch"], 1)
            self.assertTrue(torch.equal(source_model.weight, target_model.weight))
            self.assertFalse(target_model.training)

    def test_selected_checkpoint_rejects_hash_or_metadata_mismatch(self) -> None:
        model = ScalarModel(initial_weight=0.25)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
        with tempfile.TemporaryDirectory() as temporary_dir:
            result = self._save(
                Path(temporary_dir),
                model,
                optimizer,
                mlflow_run_id="source-run",
            )
            with self.assertRaisesRegex(ValueError, "fijado en configuración"):
                load_selected_checkpoint(
                    result.best_path,
                    expected_sha256="0" * 64,
                    expected_run_id="source-run",
                    expected_epoch=1,
                    expected_selection_metric="val_dice",
                    expected_selection_value=0.8,
                    model=ScalarModel(),
                )
            with self.assertRaisesRegex(ValueError, "run MLflow"):
                load_selected_checkpoint(
                    result.best_path,
                    expected_sha256=result.best_sha256,
                    expected_run_id="wrong-run",
                    expected_epoch=1,
                    expected_selection_metric="val_dice",
                    expected_selection_value=0.8,
                    model=ScalarModel(),
                )


class TrackingAndRunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (PROJECT_ROOT / "configs/tracking/mlflow.yaml").open(encoding="utf-8") as file:
            cls.tracking_config = yaml.safe_load(file)

    def test_flatten_parameters_is_stable(self) -> None:
        self.assertEqual(
            flatten_parameters(
                {"optimizer": {"lr": 1.0e-4}, "shape": [3, 256, 256], "resume": None}
            ),
            {
                "optimizer.lr": 1.0e-4,
                "shape": "[3, 256, 256]",
                "resume": "null",
            },
        )

    def test_epoch_metrics_must_match_tracking_contract(self) -> None:
        tracker = ExperimentTracker(self.tracking_config)
        metrics = {name: 0.0 for name in tracker.metric_names}
        with patch("polysight_seg.training.tracking.mlflow.log_metrics") as log_metrics:
            tracker.log_epoch(metrics, epoch=3)
        log_metrics.assert_called_once_with(metrics, step=3, synchronous=True)
        metrics.pop("val_dice")
        with self.assertRaises(ValueError):
            tracker.log_epoch(metrics, epoch=4)

    def test_runner_selection_and_dataset_hashes(self) -> None:
        self.assertTrue(_metric_improved(0.8, None, "max", 1.0e-4))
        self.assertFalse(_metric_improved(0.80005, 0.8, "max", 1.0e-4))
        self.assertTrue(_metric_improved(0.81, 0.8, "max", 1.0e-4))
        data_config = load_data_config(PROJECT_ROOT / "configs/data/kvasir-seg.yaml")
        hashes = _dataset_hashes(data_config)
        self.assertEqual(
            hashes["manifest_sha256"],
            "35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4",
        )

    def test_history_is_written_atomically_as_csv(self) -> None:
        history = [
            {"epoch": 1, "val_dice": 0.7, "is_best": True},
            {"epoch": 2, "val_dice": 0.8, "is_best": True},
        ]
        with tempfile.TemporaryDirectory() as temporary_dir:
            path = Path(temporary_dir) / "history.csv"
            _write_history(path, history)
            with path.open(newline="", encoding="utf-8") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([row["epoch"] for row in rows], ["1", "2"])
            self.assertEqual([row["val_dice"] for row in rows], ["0.7", "0.8"])
            self.assertEqual(list(path.parent.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
