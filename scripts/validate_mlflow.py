#!/usr/bin/env python3
"""Valida servidor y contrato de tracking MLflow con un run efímero."""

from __future__ import annotations

import socket
import tempfile
from pathlib import Path

import mlflow
from mlflow import MlflowClient

from polysight_seg.training.tracking import ExperimentTracker, ManagedMlflowServer


EXPECTED_MLFLOW_VERSION = "3.15.1"


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        return int(server_socket.getsockname()[1])


def main() -> int:
    if mlflow.__version__ != EXPECTED_MLFLOW_VERSION:
        raise RuntimeError(
            f"MLflow efectivo {mlflow.__version__}; se esperaba {EXPECTED_MLFLOW_VERSION}"
        )

    with tempfile.TemporaryDirectory(prefix="polysight-mlflow-") as temporary_dir:
        root = Path(temporary_dir)
        port = _available_port()
        tracking_config = {
            "schema_version": 1,
            "server": {
                "host": "127.0.0.1",
                "port": port,
                "workers": 1,
                "tracking_uri": f"http://127.0.0.1:{port}",
                "backend_store_uri": f"sqlite:///{root / 'mlflow.db'}",
                "artifacts_destination": str(root / "artifacts"),
                "startup_timeout_seconds": 30,
            },
            "experiment": {
                "name": "environment-validation",
                "run_name_prefix": "validation",
            },
            "logging": {"metrics_per_epoch": ["validation_dice"]},
        }
        sample_config = root / "sample-config.yaml"
        sample_config.write_text("schema_version: 1\n", encoding="utf-8")
        history = root / "history.csv"
        history.write_text("epoch,validation_dice\n1,0.72\n", encoding="utf-8")
        tracker = ExperimentTracker(tracking_config)

        with ManagedMlflowServer(tracking_config["server"], root):
            tracker.configure()
            with tracker.start_run(
                run_name="server-client-smoke",
                tags={"purpose": "environment-validation"},
            ) as active_run:
                tracker.validate_artifact_uri(active_run.info.artifact_uri)
                tracker.log_initial_state(
                    configs={"validation": {"schema_version": 1}},
                    config_paths=[sample_config],
                    dataset_hashes={"manifest_sha256": "0" * 64},
                    runtime={"mlflow": mlflow.__version__},
                    pip_freeze=f"mlflow=={mlflow.__version__}\n",
                )
                tracker.log_epoch({"validation_dice": 0.72}, epoch=1)
                tracker.log_history(history)
                tracker.log_summary({"status": "ok"})
                run_id = active_run.info.run_id

            client = MlflowClient()
            run = client.get_run(run_id)
            training_artifacts = {
                artifact.path for artifact in client.list_artifacts(run_id, "training")
            }
            if run.data.metrics.get("validation_dice") != 0.72:
                raise RuntimeError("La métrica enviada no quedó persistida")
            if "training/history.csv" not in training_artifacts:
                raise RuntimeError("El historial enviado no quedó persistido")
            if not run.info.artifact_uri.startswith("mlflow-artifacts:/"):
                raise RuntimeError(f"URI de artefactos no portable: {run.info.artifact_uri}")
            if not (root / "mlflow.db").is_file():
                raise RuntimeError("MLflow no creó la base SQLite")

            print(f"mlflow={mlflow.__version__}")
            print(f"tracking_uri={tracking_config['server']['tracking_uri']}")
            print(f"artifact_uri={run.info.artifact_uri}")
            print("mlflow_server_client_validation=ok")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
