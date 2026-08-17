# MLflow para PolySight Seg

## Diseño

Cada job de entrenamiento inicia un servidor MLflow accesible solo desde el nodo
asignado. El cliente de entrenamiento usa `http://127.0.0.1:5000`; el servidor guarda:

- metadatos de experimentos y runs en `mlflow.db` mediante SQLite;
- checkpoints, configuraciones y demás artefactos bajo `artifacts/`;
- URIs portables con esquema `mlflow-artifacts:/`, sin rutas absolutas de CEDIA.

La configuración canónica está en `configs/tracking/mlflow.yaml`. La base y los
artefactos son estado experimental y no se agregan a Git.

## Servidor dentro del job de CEDIA

El job de entrenamiento iniciará el servidor con el equivalente a:

```bash
mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./artifacts
```

Solo se ejecutará un escritor sobre esta base SQLite. No se deben lanzar dos jobs de
entrenamiento concurrentes contra el mismo `mlflow.db`.

## Información de cada run

MLflow registrará:

- commit, job Slurm, configuraciones y versiones efectivas;
- hashes del dataset, manifest y splits;
- loss, Dice, IoU, precisión, recall y learning rate por época;
- `best.pt` seleccionado por Dice de validation y `last.pt` para reanudación;
- resúmenes de entorno y entrenamiento.

Test no se usará durante esta fase ni se registrará para seleccionar el modelo.

## Sincronización al equipo local

Esperar a que el job y el servidor hayan terminado. Desde la raíz local del proyecto:

```bash
rsync -av --progress -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/mlflow.db ./
rsync -av --progress --exclude='*.log' -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/artifacts/ ./artifacts/
```

No copiar `mlflow.db` mientras exista un proceso escribiendo en ella.

## Interfaz local

Desde la carpeta que contiene `mlflow.db` y `artifacts/`:

```bash
uvx mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./artifacts
```

Abrir `http://127.0.0.1:5000`. Usar `127.0.0.1` evita exponer la interfaz a la red.

## Referencias oficiales

- <https://mlflow.org/docs/latest/self-hosting/architecture/overview/>;
- <https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/>.
