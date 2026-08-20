"""Resolución ligera de configuración MLflow desde el entorno del job."""

from __future__ import annotations

import copy
import os
from typing import Any


MLFLOW_PORT_ENVIRONMENT_VARIABLE = "POLYSIGHT_MLFLOW_PORT"


def apply_mlflow_environment(config: dict[str, Any]) -> dict[str, Any]:
    """Aplica un puerto local por job sin modificar el YAML versionado."""

    port_value = os.environ.get(MLFLOW_PORT_ENVIRONMENT_VARIABLE)
    if port_value is None:
        return config
    try:
        port = int(port_value)
    except ValueError as error:
        raise ValueError(
            f"{MLFLOW_PORT_ENVIRONMENT_VARIABLE} debe ser un entero"
        ) from error
    if not 1024 <= port <= 65535:
        raise ValueError(
            f"{MLFLOW_PORT_ENVIRONMENT_VARIABLE} debe estar entre 1024 y 65535"
        )
    resolved = copy.deepcopy(config)
    host = str(resolved["server"]["host"])
    resolved["server"]["port"] = port
    resolved["server"]["tracking_uri"] = f"http://{host}:{port}"
    return resolved
