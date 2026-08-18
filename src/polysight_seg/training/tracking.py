"""Servidor y cliente MLflow para un único job de entrenamiento."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import mlflow


class ManagedMlflowServer:
    """Gestiona un servidor MLflow ligado a loopback durante el job."""

    def __init__(self, config: dict[str, Any], project_root: Path) -> None:
        self.config = config
        self.project_root = project_root
        self.process: subprocess.Popen[bytes] | None = None
        self._temporary_directory: tempfile.TemporaryDirectory[str] | None = None
        self._log_path: Path | None = None
        self._log_output: Any | None = None

    @property
    def tracking_uri(self) -> str:
        return str(self.config["tracking_uri"])

    def _assert_port_available(self) -> None:
        host = str(self.config["host"])
        port = int(self.config["port"])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            try:
                server_socket.bind((host, port))
            except OSError as error:
                raise RuntimeError(
                    f"El puerto MLflow {host}:{port} ya está ocupado; "
                    "no se iniciará otro escritor"
                ) from error

    def _read_log(self) -> str:
        if self._log_output is not None:
            self._log_output.flush()
        if self._log_path is None or not self._log_path.is_file():
            return ""
        return self._log_path.read_text(encoding="utf-8", errors="replace")

    def start(self) -> "ManagedMlflowServer":
        if self.process is not None:
            raise RuntimeError("El servidor MLflow ya fue iniciado")
        self._assert_port_available()
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="polysight-mlflow-server-"
        )
        self._log_path = Path(self._temporary_directory.name) / "server.log"
        self._log_output = self._log_path.open("wb")
        command = [
            sys.executable,
            "-m",
            "mlflow",
            "server",
            "--host",
            str(self.config["host"]),
            "--port",
            str(self.config["port"]),
            "--workers",
            str(self.config.get("workers", 1)),
            "--backend-store-uri",
            str(self.config["backend_store_uri"]),
            "--artifacts-destination",
            str(self.config["artifacts_destination"]),
        ]
        self.process = subprocess.Popen(
            command,
            cwd=self.project_root,
            stdout=self._log_output,
            stderr=subprocess.STDOUT,
        )

        deadline = time.monotonic() + float(self.config["startup_timeout_seconds"])
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                log = self._read_log()
                self.stop()
                raise RuntimeError(
                    f"El servidor MLflow terminó durante el arranque:\n{log}"
                )
            try:
                with urlopen(f"{self.tracking_uri}/health", timeout=2) as response:
                    if response.status == 200:
                        return self
            except Exception as error:
                last_error = error
            time.sleep(0.5)

        log = self._read_log()
        self.stop()
        raise TimeoutError(
            f"MLflow no respondió antes del timeout ({last_error}):\n{log}"
        )

    def stop(self) -> None:
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
            self.process = None
        if self._log_output is not None:
            self._log_output.close()
            self._log_output = None
        if self._temporary_directory is not None:
            self._temporary_directory.cleanup()
            self._temporary_directory = None
        self._log_path = None

    def __enter__(self) -> "ManagedMlflowServer":
        return self.start()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.stop()


def flatten_parameters(
    value: Any,
    *,
    prefix: str = "",
) -> dict[str, str | int | float | bool]:
    """Convierte configuración anidada en parámetros escalares para MLflow."""

    flattened: dict[str, str | int | float | bool] = {}
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            nested_prefix = f"{prefix}.{key}" if prefix else str(key)
            flattened.update(flatten_parameters(nested_value, prefix=nested_prefix))
    elif isinstance(value, (list, tuple)):
        flattened[prefix] = json.dumps(value, sort_keys=True)
    elif value is None:
        flattened[prefix] = "null"
    elif isinstance(value, (str, int, float, bool)):
        flattened[prefix] = value
    else:
        flattened[prefix] = str(value)
    return flattened


class ExperimentTracker:
    """Aplica el contrato de parámetros, métricas y artefactos del proyecto."""

    def __init__(self, config: dict[str, Any]) -> None:
        if config.get("schema_version") != 1:
            raise ValueError("Versión de configuración MLflow no soportada")
        self.config = config
        self.metric_names = set(config["logging"]["metrics_per_epoch"])

    def configure(self) -> None:
        mlflow.set_tracking_uri(self.config["server"]["tracking_uri"])
        mlflow.set_experiment(self.config["experiment"]["name"])

    def start_run(
        self,
        *,
        run_name: str,
        tags: dict[str, Any],
        run_id: str | None = None,
    ) -> Any:
        if run_id is not None:
            return mlflow.start_run(run_id=run_id)
        return mlflow.start_run(
            run_name=run_name,
            tags=tags,
            log_system_metrics=False,
        )

    def validate_artifact_uri(self, artifact_uri: str) -> None:
        if not artifact_uri.startswith("mlflow-artifacts:/"):
            raise RuntimeError(f"URI de artefactos no portable: {artifact_uri}")

    def log_initial_state(
        self,
        *,
        configs: dict[str, dict[str, Any]],
        config_paths: list[Path],
        dataset_hashes: dict[str, str],
        runtime: dict[str, Any],
        pip_freeze: str,
    ) -> None:
        parameters: dict[str, str | int | float | bool] = {}
        for config_name, config in configs.items():
            parameters.update(flatten_parameters(config, prefix=config_name))
        mlflow.log_params(parameters)
        for config_path in config_paths:
            mlflow.log_artifact(str(config_path), artifact_path="configs")
        mlflow.log_dict(dataset_hashes, "dataset/dataset-hashes.json")
        mlflow.log_dict(runtime, "environment/runtime.json")
        mlflow.log_text(pip_freeze, "environment/pip-freeze.txt")

    def log_epoch(self, metrics: dict[str, float | int], epoch: int) -> None:
        metric_names = set(metrics)
        if metric_names != self.metric_names:
            missing = sorted(self.metric_names - metric_names)
            unexpected = sorted(metric_names - self.metric_names)
            raise ValueError(
                f"Contrato de métricas incumplido; faltan={missing}, sobran={unexpected}"
            )
        mlflow.log_metrics(
            {name: float(value) for name, value in metrics.items()},
            step=epoch,
            synchronous=True,
        )

    def log_history(self, history_path: Path) -> None:
        mlflow.log_artifact(str(history_path), artifact_path="training")

    def log_checkpoint(self, checkpoint_path: Path, artifact_path: str) -> None:
        mlflow.log_artifact(str(checkpoint_path), artifact_path=artifact_path)
        sidecar = checkpoint_path.with_suffix(f"{checkpoint_path.suffix}.sha256")
        mlflow.log_artifact(str(sidecar), artifact_path=artifact_path)

    def log_summary(self, summary: dict[str, Any]) -> None:
        mlflow.log_dict(summary, "training/run-summary.json")
