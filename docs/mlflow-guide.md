# Guía de MLflow y artefactos reproducibles

Este documento reúne criterios reutilizables para futuros experimentos. La regla central
es guardar primero los datos que originan una figura y tratar PNG, SVG o PDF como
productos derivados regenerables.

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
real/predicho, fondo, objeto
fondo,         TN,    FP
objeto,        FN,    TP
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

### Hacer visible el modelo seleccionado

La vista general de MLflow muestra el último valor de cada serie, que no necesariamente
es el mejor. No debe obligarse a la audiencia a recorrer una curva para descubrir qué
época ganó. Al cerrar el run, registrar explícitamente:

- métrica y regla de selección, por ejemplo maximizar `validation_score`;
- mejor valor y paso o época donde ocurrió;
- ruta del checkpoint seleccionado y su hash;
- motivo y paso final de parada;
- un `run-summary.json` con los mismos datos como evidencia portable.

Conviene exponer estos campos como tags con nombres estables, por ejemplo
`selection.metric`, `selection.best_value`, `selection.best_step` y
`selection.checkpoint_artifact`. Registrar además una métrica escalar final como
`best_validation_score` permite verla directamente en Overview sin confundirla con el
último punto de `validation_score`.

Un checkpoint de entrenamiento guardado mediante `log_artifact` sigue siendo un archivo
genérico: conserva pesos, optimizador y estado para auditoría o reanudación, pero no
aparece como **Logged model**. Para que el ganador sea consumible desde MLflow, también
debe registrarse con el flavor correspondiente, por ejemplo `mlflow.pytorch.log_model`,
incluyendo firma e input example cuando sea posible. Son dos artefactos complementarios:

- **checkpoint:** reanudación y trazabilidad completa del entrenamiento;
- **MLflow Model:** carga estandarizada, inferencia, comparación y despliegue.

El Model Registry es un paso adicional, útil cuando existe un flujo de promoción. Solo
debe registrarse el modelo seleccionado después de cerrar el criterio de validation; test
no participa en esa selección. Usar alias con significado operativo, como `candidate` o
`champion`, es preferible a depender únicamente de números de versión.

### Problemas frecuentes que deben prevenirse

| Problema | Prevención |
|---|---|
| Solo se guardó un PNG | Guardar CSV/JSON crudo, configuración y script de la figura |
| Matriz engañosa por desbalance | Mostrar normalización por clase real y conservar conteos |
| No puede cambiarse el umbral | Guardar probabilidades/logits del checkpoint seleccionado |
| Texto blanco sobre celda clara | Elegir color de anotación según luminancia/valor |
| Valores salen de las celdas | Abreviar, ajustar fuente y usar layout automático |
| No se puede reproducir un run | Registrar commit, config, semilla, versiones y hashes |
| El mejor resultado queda oculto en la curva | Registrar mejor valor, paso, criterio y ruta como resumen y tags |
| El ganador no aparece como Logged model | Registrar además el modelo con su flavor; el checkpoint solo es un artefacto |
| Artefactos apuntan a otra máquina | Usar URIs portables y sincronizar base más artefactos |
| Base SQLite inconsistente | Detener escritores antes de copiar y limitar concurrencia |
| Nombre de módulo no coincide con versión real | Registrar versiones importadas dentro del job |

## Instalación reproducible en clústeres con Slurm

La instalación debe probarse en el mismo tipo de nodo y con los mismos módulos que
usará el experimento. El nodo de login se limita a sincronizar código, enviar jobs y
consultar resultados; la instalación y los imports se ejecutan dentro de un job CPU.

### Elegir y fijar la versión

Antes de instalar:

1. consultar el metadato oficial `Requires-Python` de la versión candidata;
2. confirmar que admite la versión de Python del clúster;
3. fijarla exactamente en el archivo de dependencias, por ejemplo
   `mlflow==X.Y.Z`;
4. instalar desde ese archivo, no mediante un comando manual que no quede versionado.

Fijar la versión evita que dos ejecuciones obtengan releases distintas. La versión
efectivamente importada debe registrarse dentro del job, porque el nombre de un módulo
del clúster no garantiza por sí solo qué paquete termina resolviendo Python.

### Reutilizar el framework provisto por el clúster

Si PyTorch, CUDA u otro framework pesado proviene de módulos, se puede crear el entorno
con acceso a sus paquetes y mantener el resto de dependencias dentro del virtualenv:

```bash
module purge
module load MODULO_DEL_FRAMEWORK

python -m venv --system-site-packages .venv
source .venv/bin/activate

venv_site_packages="$VIRTUAL_ENV/lib/pythonX.Y/site-packages"
export PYTHONPATH="${venv_site_packages}:${PYTHONPATH:-}"

python -m pip install -e .
python -m pip check
```

Se reemplaza `pythonX.Y` por la versión real del job. Anteponer el `site-packages` del
virtualenv hace que se respeten las versiones fijadas allí, mientras
`--system-site-packages` permite reutilizar el framework administrado por el clúster.
Si no se necesita ningún paquete del sistema, es preferible crear un virtualenv normal.

### Validar más que el import

Después de instalar, una prueba efímera debe:

- comprobar las versiones reales de Python, MLflow y el framework;
- ejecutar `pip check` para detectar dependencias incompatibles;
- iniciar un servidor MLflow limitado a `127.0.0.1` con una base SQLite temporal;
- crear un run, persistir una métrica y un artefacto y volver a leerlos con el cliente;
- comprobar que la URI del artefacto sea portable;
- detener el servidor y descartar los archivos temporales.

Este smoke separa los errores de instalación de los del entrenamiento y no contamina la
base ni los artefactos del experimento real.

## Ejemplo general: tracking local y portable

Para un experimento individual puede usarse un servidor limitado a loopback, SQLite
como backend y un directorio local de artefactos:

```bash
cd DIRECTORIO_DEL_EXPERIMENTO
mlflow server \
  --host 127.0.0.1 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --artifacts-destination ./artifacts
```

El cliente se conecta al servidor y registra datos con nombres propios de su problema:

```python
import mlflow

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("nombre-del-experimento")

with mlflow.start_run(run_name="modelo-configuracion-semilla"):
    mlflow.log_params({"learning_rate": 1e-3, "seed": 1234})
    mlflow.log_metric("validation_score", 0.81, step=1)
    mlflow.log_artifact("history.csv", artifact_path="evaluation")
```

Para trasladar el experimento se copian juntos `mlflow.db` y `artifacts/`, siempre con
el servidor detenido. Al iniciar la misma configuración en el destino, las URIs
`mlflow-artifacts:/` vuelven a resolverse contra el directorio de artefactos copiado.

## Referencias oficiales

- <https://mlflow.org/docs/latest/self-hosting/architecture/overview/>;
- <https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/>.
