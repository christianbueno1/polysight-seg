#!/usr/bin/env python3
"""Valida MLflow con un servidor y un run efímeros."""

from __future__ import annotations

import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen

import mlflow
from mlflow import MlflowClient


EXPECTED_MLFLOW_VERSION = "3.15.1"
SERVER_TIMEOUT_SECONDS = 30


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        return int(server_socket.getsockname()[1])


def _wait_until_ready(tracking_uri: str, process: subprocess.Popen[bytes]) -> None:
    deadline = time.monotonic() + SERVER_TIMEOUT_SECONDS
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"El servidor MLflow terminó antes de estar listo (código {process.returncode})"
            )
        try:
            with urlopen(f"{tracking_uri}/health", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception as error:  # El servidor puede estar iniciando o migrando SQLite.
            last_error = error
        time.sleep(0.5)

    raise TimeoutError(f"MLflow no respondió antes del timeout: {last_error}")


def main() -> int:
    if mlflow.__version__ != EXPECTED_MLFLOW_VERSION:
        raise RuntimeError(
            f"MLflow efectivo {mlflow.__version__}; se esperaba {EXPECTED_MLFLOW_VERSION}"
        )

    with tempfile.TemporaryDirectory(prefix="polysight-mlflow-") as temporary_dir:
        root = Path(temporary_dir)
        database = root / "mlflow.db"
        artifacts = root / "artifacts"
        server_log = root / "mlflow-server.log"
        sample_artifact = root / "validation.txt"
        port = _available_port()
        tracking_uri = f"http://127.0.0.1:{port}"
        command = [
            sys.executable,
            "-m",
            "mlflow",
            "server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--backend-store-uri",
            f"sqlite:///{database}",
            "--artifacts-destination",
            str(artifacts),
        ]

        with server_log.open("wb") as output:
            process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
            try:
                _wait_until_ready(tracking_uri, process)
                mlflow.set_tracking_uri(tracking_uri)
                mlflow.set_experiment("environment-validation")
                sample_artifact.write_text("MLflow operativo\n", encoding="utf-8")

                with mlflow.start_run(run_name="server-client-smoke") as active_run:
                    mlflow.log_param("python", f"{sys.version_info.major}.{sys.version_info.minor}")
                    mlflow.log_metric("validation_dice", 0.72, step=1)
                    mlflow.log_artifact(sample_artifact)
                    run_id = active_run.info.run_id

                run = MlflowClient().get_run(run_id)
                artifact_names = {
                    artifact.path for artifact in MlflowClient().list_artifacts(run_id)
                }
                if run.data.metrics.get("validation_dice") != 0.72:
                    raise RuntimeError("La métrica enviada no quedó persistida")
                if sample_artifact.name not in artifact_names:
                    raise RuntimeError("El artefacto enviado no quedó persistido")
                if not run.info.artifact_uri.startswith("mlflow-artifacts:/"):
                    raise RuntimeError(
                        f"URI de artefactos no portable: {run.info.artifact_uri}"
                    )
                if not database.is_file():
                    raise RuntimeError("MLflow no creó la base SQLite")

                print(f"mlflow={mlflow.__version__}")
                print(f"tracking_uri={tracking_uri}")
                print(f"artifact_uri={run.info.artifact_uri}")
                print("mlflow_server_client_validation=ok")
            except Exception:
                output.flush()
                print(server_log.read_text(encoding="utf-8", errors="replace"), file=sys.stderr)
                raise
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
