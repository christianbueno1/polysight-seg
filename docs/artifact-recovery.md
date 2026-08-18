# Recuperación de checkpoint, resultados y runs MLflow

Esta guía recupera la evidencia del baseline U-Net/ResNet-34 sin volver a entrenar ni
evaluar test. Los comandos se ejecutan desde la raíz local del repositorio y asumen que
el alias SSH `cedia` apunta al clúster.

## Identificadores canónicos

| Elemento | Identificador |
|---|---|
| Job de entrenamiento | `23312` |
| Run MLflow de entrenamiento | `5fdf1b9929ec443da426c6442d9e20f1` |
| Época seleccionada | `22` |
| SHA-256 de `best.pt` | `a3900c2db01e9e17fa7fedce12da94274d8995284f1c37f6e653df402919361b` |
| Job de evaluación final | `23325` |
| Run MLflow de evaluación | `73876309ec7c45e09023574a02a47475` |

## 1. Confirmar los jobs en el clúster

```bash
sacct -j 23312,23325 --format=JobID,JobName,State,ExitCode,Elapsed
```

Ambos jobs principales deben mostrar `COMPLETED` y `0:0`. Esto confirma el estado de
Slurm, pero las métricas y el modelo se verifican con los pasos siguientes.

## 2. Sincronizar el estado experimental

Esperar a que no exista ningún proceso escribiendo en MLflow. Luego ejecutar en local:

```bash
rsync -av --progress -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/mlflow.db ./
rsync -av --progress --exclude='*.log' -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/artifacts/ ./artifacts/
rsync -av --progress -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/evaluation/unet-resnet34-baseline/test/ \
  ./evaluation/unet-resnet34-baseline/test/
```

`mlflow.db` contiene metadatos y es pequeño; `artifacts/` incluye checkpoints, mapas de
probabilidad y demás archivos, por lo que su tamaño es mucho mayor. En la copia actual
son aproximadamente 1.3 MB y 1.2 GB, respectivamente.

## 3. Verificar el checkpoint ganador

La copia administrada por MLflow queda en:

```text
artifacts/1/5fdf1b9929ec443da426c6442d9e20f1/artifacts/checkpoints/best/best.pt
```

Verificarla con:

```bash
sha256sum artifacts/1/5fdf1b9929ec443da426c6442d9e20f1/artifacts/checkpoints/best/best.pt
```

El valor debe ser exactamente
`a3900c2db01e9e17fa7fedce12da94274d8995284f1c37f6e653df402919361b`.
No usar `last.pt`: el modelo seleccionado es `best.pt` de la época 22.

## 4. Abrir MLflow localmente

Si el puerto está libre:

```bash
uvx mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./artifacts
```

Abrir `http://127.0.0.1:5000`. Si aparece `Address already in use`, comprobar el
proceso existente:

```bash
ss -tulpn | grep ':5000'
```

Si ya es el servidor de este proyecto, no iniciar otro: abrir directamente la URL. En
la interfaz, buscar los runs por sus UUID. El run de entrenamiento contiene historial
y checkpoint; el run de evaluación contiene las métricas finales y artefactos de test.

## 5. Revisar resultados sin la interfaz

Los resultados completos sincronizados están en:

```text
evaluation/unet-resnet34-baseline/test/
```

Las copias pequeñas versionadas para auditoría están en:

```text
docs/results/test/
docs/assets/test/
```

Comprobaciones rápidas:

```bash
python -m json.tool docs/results/test/metrics.json
wc -l docs/results/test/per-image-metrics.csv
find evaluation/unet-resnet34-baseline/test/probability-maps -name '*.npz' | wc -l
```

Se esperan 151 líneas en el CSV —encabezado más 150 imágenes— y 150 mapas de
probabilidad. Las métricas oficiales deben coincidir con el run de evaluación y con
[`final-report.md`](final-report.md).

## Qué se conserva en Git

Git contiene configuraciones, métricas tabulares canónicas, figuras seleccionadas y
documentación. `mlflow.db`, `artifacts/`, `checkpoints/`, `evaluation/` y los datos se
ignoran por tamaño o por ser estado generado; deben conservarse en el almacenamiento
del clúster y en una copia local o respaldo controlado.
