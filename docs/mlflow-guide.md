## MLflow local

- Estos archivos son los que debemos sincronizar en local: `mlflow.db` y `artifacts/`; los archivos `.log` se excluyen durante la sincronización.
- La interfaz local puede iniciarse desde la carpeta copiada con:
  `uvx mlflow ui --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./artifacts --port 5000`.
- Los experimentos, runs y modelos guardan ubicaciones portables con el esquema `mlflow-artifacts:/`; no contienen rutas absolutas de artefactos de CEDIA.