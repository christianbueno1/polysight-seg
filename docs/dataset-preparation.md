# Preparación y transferencia de Kvasir-SEG

## Principio de reproducción

Se transfiere a CEDIA el ZIP original, no el directorio extraído. Esto reduce la cantidad
de archivos durante la transferencia y permite reconstruir el mismo dataset usando el
SHA-256 y los scripts versionados del proyecto.

El archivo esperado es:

```text
hyper-kvasir-segmented-images.zip
SHA-256: 4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a
Tamaño: 46179365 bytes
```

## Transferir desde el equipo local

Crear primero un directorio personal para datasets en CEDIA:

```bash
ssh cedia 'mkdir -p "$HOME/datasets"'
rsync -av --progress \
  /home/chris/Downloads/hyper-kvasir-segmented-images.zip \
  cedia:/home/USUARIO/datasets/
```

Sustituir `USUARIO` por la cuenta asignada. No subir el ZIP a Git.

## Comprobar la copia remota

En el nodo de acceso de CEDIA:

```bash
sha256sum /home/USUARIO/datasets/hyper-kvasir-segmented-images.zip
stat --printf='%s bytes\n' /home/USUARIO/datasets/hyper-kvasir-segmented-images.zip
```

El hash y tamaño deben coincidir exactamente con los valores registrados. Si no
coinciden, descartar esa copia remota y repetir la transferencia antes de extraer.

## Reproducir el dataset en CEDIA

Desde la raíz del repositorio y con el entorno de CEDIA ya preparado:

```bash
source .venv-cluster/bin/activate
export PYTHONPATH=src

python scripts/prepare_dataset.py \
  /home/USUARIO/datasets/hyper-kvasir-segmented-images.zip
python scripts/validate_dataset.py
python scripts/generate_manifest.py
```

El primer comando escribe bajo `data/raw/kvasir-seg/`. Si se repite con el mismo ZIP,
debe responder `dataset_status=unchanged`. Los dos archivos derivados se escriben bajo
`data/processed/kvasir-seg/`:

```text
manifest.csv
summary.json
```

## Verificar reproducibilidad

Para la copia registrada en esta fase, los resultados esperados son:

```text
manifest.csv  35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4
summary.json  964f4d97e04eb2687694a5e44452d2cff4bb409920364e4aca44b75025c30a7f
```

Comprobarlos en CEDIA:

```bash
sha256sum data/processed/kvasir-seg/manifest.csv \
  data/processed/kvasir-seg/summary.json
```

Una diferencia indica un cambio de código, dependencias, fuente o regla de preparación;
no debe continuarse con los splits hasta identificarla.

## Resultados esperados de validación

- 1.000 pares imagen–máscara;
- 1.000 registros de bounding boxes;
- todos los archivos decodificables como JPEG RGB;
- dimensiones coincidentes dentro de cada par;
- umbral de máscara igual a 128;
- cero grupos de imágenes exactamente duplicadas dentro de Kvasir-SEG.

Los datos extraídos, manifests y resúmenes se consideran artefactos reproducibles y
permanecen excluidos de Git.
