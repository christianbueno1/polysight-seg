# Guía de MLflow y artefactos reproducibles

Este documento combina criterios reutilizables para futuros experimentos con la
configuración concreta de PolySight Seg. La regla central es guardar primero los datos
que originan una figura y tratar PNG, SVG o PDF como productos derivados regenerables.

## Principios para cualquier experimento

### No guardar solamente las gráficas

Una imagen de una curva o matriz no permite cambiar normalización, etiquetas, colores,
fuentes o tamaño. Tampoco permite corregir un problema visual sin repetir evaluación.
Cada figura debe acompañarse de sus datos fuente y del código/configuración que la genera.

Para cada run conservar como mínimo:

- configuración completa, semilla, commit y versiones efectivas;
- identificadores y hashes de dataset y splits;
- historial de métricas por época en un formato tabular;
- checkpoint seleccionado y criterio exacto de selección;
- conteos crudos usados por métricas y matrices;
- datos fuente de cada figura y figuras exportadas en formatos editables.

### Matrices de confusión y clases desbalanceadas

Una matriz sin normalizar puede ser engañosa cuando una clase domina. La clase
mayoritaria produce conteos grandes y oculta errores importantes de las clases
minoritarias. La práctica recomendada es conservar siempre la matriz cruda y generar
varias vistas desde ella:

1. **Vista principal:** normalizada por clase real (`normalize="true"`); cada fila suma
   100 % y permite comparar recall entre clases aunque sus soportes sean distintos.
2. **Vista de auditoría:** conteos absolutos, acompañados por el soporte de cada clase.
3. **Vista opcional:** normalizada por clase predicha para analizar precision.

La matriz normalizada nunca reemplaza los conteos originales. Sin TP, FP, FN, TN o la
matriz multiclase cruda no es posible cambiar de normalización con fidelidad.

En segmentación binaria, la matriz se calcula por píxel:

```text
real/predicho, fondo, pólipo
fondo,         TN,    FP
pólipo,       FN,    TP
```

El fondo suele dominar, por lo que la matriz normalizada debe acompañarse con Dice e
IoU. En clasificación multiclase se aplica el mismo principio por muestra y clase.

### Datos que permiten reconstruir la evaluación

No depender de una figura ni de un único JSON agregado. Conservar, según el problema:

```text
metrics.json
history.csv
confusion-matrix-counts.csv
confusion-matrix-normalized-true.csv
per-sample-metrics.csv
threshold-curve.csv
```

Para segmentación, `per-sample-metrics.csv` debería incluir:

```text
sample_id, split, threshold, tp, fp, fn, tn,
dice, iou, precision, recall
```

Los conteos por muestra permiten reagrupar por tamaño de lesión, procedencia u otra
variable sin repetir inferencia. Para cambiar el umbral sin volver a ejecutar el modelo
se deben guardar probabilidades o logits, por ejemplo mapas `float16` comprimidos. No es
necesario guardarlos en todas las épocas: basta para el checkpoint seleccionado y los
splits que deban analizarse.

### Figuras editables y legibles

Los datos son canónicos; las figuras se regeneran. Toda visualización importante debe:

- exportarse como SVG o PDF editable y como PNG de al menos 300 DPI;
- usar layout automático para evitar títulos, ejes o valores recortados;
- adaptar el color del texto al fondo de cada celda para conservar contraste;
- abreviar conteos grandes o separar porcentaje y conteo en dos líneas;
- versionar etiquetas, orden de clases, paleta, tamaño y formato numérico;
- probarse con valores cortos, largos, cercanos a cero y cercanos a cien.

Una anotación recomendable para una celda es:

```text
92,4 %
(n=1,2 M)
```

### Umbrales y aislamiento de test

El umbral se elige exclusivamente con validation. Guardar el umbral junto con cada
matriz y archivo de métricas. Test se evalúa una vez con el umbral ya fijado; no se usa
para rediseñar clases, ajustar hiperparámetros ni escoger una visualización más favorable.

### Qué registrar en MLflow

MLflow debe conservar datos suficientes para auditar y reconstruir resultados:

- parámetros, configuración y tags de procedencia;
- métricas escalares por paso o época;
- conteos crudos de la matriz por época cuando sean relevantes;
- CSV/JSON fuente, scripts/configuraciones de plots y figuras derivadas;
- checkpoints, hashes y resúmenes del entorno.

En un problema binario conviene registrar `tp`, `fp`, `fn` y `tn` además de Dice, IoU,
precision y recall. Así se pueden reconstruir matrices sin repetir entrenamiento ni
evaluación.

### Problemas frecuentes que deben prevenirse

| Problema | Prevención |
|---|---|
| Solo se guardó un PNG | Guardar CSV/JSON crudo, configuración y script de la figura |
| Matriz engañosa por desbalance | Mostrar normalización por clase real y conservar conteos |
| No puede cambiarse el umbral | Guardar probabilidades/logits del checkpoint seleccionado |
| Texto blanco sobre celda clara | Elegir color de anotación según luminancia/valor |
| Valores salen de las celdas | Abreviar, ajustar fuente y usar layout automático |
| No se puede reproducir un run | Registrar commit, config, semilla, versiones y hashes |
| Artefactos apuntan a otra máquina | Usar URIs portables y sincronizar base más artefactos |
| Base SQLite inconsistente | Detener escritores antes de copiar y limitar concurrencia |
| Nombre de módulo no coincide con versión real | Registrar versiones importadas dentro del job |

## Aplicación en PolySight Seg

### Diseño

Cada job de entrenamiento inicia un servidor MLflow accesible solo desde el nodo
asignado. El cliente de entrenamiento usa `http://127.0.0.1:5000`; el servidor guarda:

- metadatos de experimentos y runs en `mlflow.db` mediante SQLite;
- checkpoints, configuraciones y demás artefactos bajo `artifacts/`;
- URIs portables con esquema `mlflow-artifacts:/`, sin rutas absolutas de CEDIA.

La configuración canónica está en `configs/tracking/mlflow.yaml`. La base y los
artefactos son estado experimental y no se agregan a Git.

### Servidor dentro del job de CEDIA

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

### Información de cada run

MLflow registrará:

- commit, job Slurm, configuraciones y versiones efectivas;
- hashes del dataset, manifest y splits;
- loss, Dice, IoU, precisión, recall y learning rate por época;
- `best.pt` seleccionado por Dice de validation y `last.pt` para reanudación;
- resúmenes de entorno y entrenamiento.

Test no se usará durante esta fase ni se registrará para seleccionar el modelo.

### Sincronización al equipo local

Esperar a que el job y el servidor hayan terminado. Desde la raíz local del proyecto:

```bash
rsync -av --progress -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/mlflow.db ./
rsync -av --progress --exclude='*.log' -e 'ssh -F /home/chris/.ssh/config' \
  cedia:projects/polysight-seg/artifacts/ ./artifacts/
```

No copiar `mlflow.db` mientras exista un proceso escribiendo en ella.

### Interfaz local

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
