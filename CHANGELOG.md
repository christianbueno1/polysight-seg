# CHANGELOG

---

## 2026-08-17 19:31 -0500 — Fase 5: protocolo de entrenamiento versionado

**Hecho:**
- Creada `configs/training/unet-resnet34-baseline.yaml` con referencias a datos, modelo
  y tracking, además de runtime, optimizador, scheduler y checkpoints.
- Añadidos cinco contratos locales para validar referencias, presupuesto, selección y
  aislamiento de test sin importar PyTorch.
- Incorporada la nueva prueba al validador local y actualizados los índices de
  configuraciones y pruebas.

**Decisiones:**
- El baseline tendrá un máximo de 50 épocas con semilla `20260817`, AdamW con learning
  rate `1e-4` y weight decay `1e-4`.
- ReduceLROnPlateau reducirá el learning rate a la mitad después de tres épocas sin una
  mejora absoluta de `1e-4` en Dice de validation, con mínimo `1e-6`.
- Early stopping esperará diez épocas sin mejora para permitir reducciones del learning
  rate antes de detener el entrenamiento.
- La A100 usará AMP `float16` con gradient scaling y determinismo estricto; el mejor
  checkpoint se seleccionará únicamente por `val_dice`.
- Test queda deshabilitado declarativamente y reservado para la Fase 6.

**Pendiente / carry-over:**
- Implementar los loops de train y validation con agregación correcta por época.

---

## 2026-08-17 19:26 -0500 — Fase 5: MLflow instalado y validado en CEDIA

**Hecho:**
- Fijado `mlflow==3.15.1`, compatible con Python 3.11, en las dependencias del proyecto.
- Incorporados TP, FP, FN y TN de train y validation al contrato de métricas por época.
- Añadidos un smoke servidor-cliente efímero y su job Slurm para `cpu-dev`.
- Actualizado `.venv-cluster` mediante el job `23305` y ejecutado el smoke funcional
  mediante el job `23306`.
- Documentada en la guía general la estrategia reproducible de instalación en clústeres
  con módulos, virtualenv y Slurm.

**Decisiones:**
- La versión de MLflow se fija exactamente y se instala desde el proyecto, no mediante
  una modificación manual sin trazabilidad.
- El nodo de login se limita a sincronización, envío y consulta; instalación, imports y
  validación se ejecutan en nodos de cómputo CPU.
- El virtualenv reutiliza PyTorch del módulo del clúster y prioriza sus propios paquetes
  fijados mediante `PYTHONPATH`.
- La validación usa almacenamiento temporal para no crear runs ni artefactos en el
  experimento real.

**Resultados:**
- Job `23305`: `COMPLETED`, código `0:0`; Python 3.11.14, MLflow 3.15.1 y `pip check`
  sin conflictos.
- Job `23306`: `COMPLETED`, código `0:0`; servidor, SQLite, métrica y artefacto
  persistidos y URI `mlflow-artifacts:/` confirmada.

**Pendiente / carry-over:**
- Crear la configuración versionada del entrenamiento baseline.

---

## 2026-08-17 19:00 -0500 — Fase 5: separación de guías MLflow

**Hecho:**
- Eliminadas de `docs/mlflow-guide.md` las rutas, nombres y decisiones específicas de
  PolySight Seg.
- Añadido un ejemplo neutral de servidor y cliente MLflow con almacenamiento portable.
- Versionada `docs/mlflow-project-guide.md` como guía exclusiva de este proyecto.
- Añadido a la guía del proyecto el contrato de matrices, conteos, probabilidades y
  figuras regenerables para el checkpoint seleccionado.
- Actualizado el índice de documentación para enlazar ambas guías por separado.

**Decisiones:**
- La guía general contiene patrones reutilizables y no menciona infraestructura,
  datasets, modelos ni rutas de un proyecto concreto.
- La guía de proyecto es la fuente para CEDIA, U-Net/ResNet-34, splits, checkpoints y
  comandos de sincronización de PolySight Seg.

**Pendiente / carry-over:**
- Incorporar TP, FP, FN y TN a `configs/tracking/mlflow.yaml`.
- Fijar la dependencia de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:51 -0500 — Fase 5: referencia reutilizable de MLflow y matrices

**Hecho:**
- Ampliada `docs/mlflow-guide.md` como referencia general para futuros experimentos.
- Documentados datos fuente, matrices crudas/normalizadas, métricas por muestra,
  probabilidades, umbrales y formatos editables de figuras.
- Añadida una tabla de problemas frecuentes y medidas preventivas basada en incidentes
  experimentales ya observados.

**Decisiones:**
- Los conteos y archivos tabulares son la fuente canónica; las figuras son derivados
  regenerables y nunca la única evidencia.
- Ante desbalance, la vista principal de la matriz se normaliza por clase real y se
  acompaña siempre por conteos absolutos y métricas apropiadas al problema.
- SVG/PDF editables y PNG de alta resolución se generan desde una configuración visual
  versionada con contraste y layout adaptativos.
- Para cambiar umbrales sin repetir inferencia deben conservarse probabilidades o logits
  del checkpoint seleccionado, además del umbral aplicado.

**Pendiente / carry-over:**
- Incorporar TP, FP, FN y TN al contrato de tracking del entrenamiento actual.
- Fijar la dependencia de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:16 -0500 — Fase 5: diseño de tracking con MLflow

**Hecho:**
- Creada `configs/tracking/mlflow.yaml` con servidor, experimento, métricas, artefactos
  y archivos que deben sincronizarse.
- Adaptada `docs/mlflow-guide.md` al flujo real entre Slurm, CEDIA y el equipo local.
- Excluidos `mlflow.db` y sus archivos auxiliares de Git.
- Añadidos enlaces y referencias a la configuración y guía de tracking.

**Decisiones:**
- Cada job de entrenamiento usará un servidor MLflow en `127.0.0.1:5000` con backend
  SQLite y proxy hacia `./artifacts`.
- El proxy conserva URIs `mlflow-artifacts:/` que pueden resolverse después de copiar
  `mlflow.db` y `artifacts/` al equipo local.
- SQLite tendrá un solo escritor; no se ejecutarán entrenamientos concurrentes contra
  la misma base ni se copiará la base mientras el servidor esté activo.
- Test permanece fuera del tracking de esta fase para no contaminar la selección del
  mejor checkpoint por Dice de validation.

**Pendiente / carry-over:**
- Fijar una versión compatible de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:10 -0500 — Cierre de Fase 4 e inicio de Fase 5

**Hecho:**
- Completadas todas las tareas del baseline U-Net/ResNet-34.
- Marcada la Fase 4 como completada y activada la Fase 5 en el backlog.
- Preparada la Fase 5 con tareas de entrenamiento, checkpoints, MLflow, pruebas y
  ejecución completa en CEDIA.

**Decisiones:**
- MLflow se integrará antes del primer entrenamiento real para evitar migraciones o
  historiales parciales.
- Dice de validation seleccionará `best.pt`; test continuará aislado hasta la Fase 6.
- Los hiperparámetros de entrenamiento se fijarán de forma declarativa antes del run.

**Resultados de cierre:**
- Dataset y splits reproducibles, entorno CEDIA validado y contratos CPU correctos.
- Baseline de 24.436.369 parámetros con forward/backward real exitoso en A100.
- Pérdida, métricas, documentación y material de presentación completados.

**Pendiente / carry-over:**
- Iniciar el branch de Fase 5 y adaptar MLflow al repositorio antes de entrenar.

---

## 2026-08-17 18:09 -0500 — Fase 4: baseline documentado para exposición

**Hecho:**
- Añadida a `docs/presentacion.md` la explicación del encoder, decoder, conexiones de
  salto, logits y flujo de postprocesamiento.
- Documentados parámetros, pérdida, métricas y evidencia del smoke GPU real.
- Añadidas respuestas breves sobre U-Net, ResNet-34, pesos ImageNet y la interpretación
  correcta de las métricas previas al entrenamiento.

**Decisiones:**
- La presentación distingue explícitamente preparación técnica de rendimiento
  experimental para no presentar el smoke como resultado de entrenamiento.
- Se informa el pico observado de aproximadamente 908 MiB solo como referencia del
  batch diagnóstico, no como estimación definitiva del entrenamiento completo.

**Pendiente / carry-over:**
- Cerrar la Fase 4 e iniciar la Fase 5 de entrenamiento reproducible con MLflow.

---

## 2026-08-17 18:03 -0500 — Fase 4: smoke GPU del baseline real

**Hecho:**
- Añadidos `scripts/smoke_baseline.py` y `slurm/smoke_baseline.sbatch`.
- Ejecutado un batch real de train con U-Net/ResNet-34, pesos ImageNet, pérdida,
  métricas y backward en una A100-SXM4-40GB.
- Verificados forma de logits, valores finitos, gradientes, parámetros y memoria GPU.
- Registrados tamaño y SHA-256 del checkpoint ResNet-34 descargado.

**Decisiones:**
- El smoke usa el batch configurado de ocho muestras y no realiza un paso de optimizador;
  valida el grafo completo sin constituir entrenamiento.
- Las métricas del batch no entrenado se conservan como evidencia técnica, no como
  estimación de calidad ni resultado experimental.
- La instrumentación de memoria usa el dispositivo CUDA actual sin argumento para ser
  compatible con la versión efectiva de PyTorch instalada por CEDIA.

**Resultados:**
- Job `23304`: `COMPLETED`, código `0:0`, 27 segundos y `status=ok`.
- 24.436.369 parámetros entrenables; pico GPU 951.611.392 bytes; pérdida 1.3424215.
- Salida `[8,1,256,256]` para entrada `[8,3,256,256]`.
- Pesos ImageNet: 87.306.240 bytes, SHA-256
  `333f7ec4c6338da2cbed37f1fc0445f9624f1355633fa1d7eab79a91084c6cef`.

**Incidencia resuelta:**
- El job `23302` falló antes de construir el modelo porque PyTorch rechazó un objeto
  `torch.device` en `reset_peak_memory_stats`; se corrigió sin cambiar el cálculo.

**Pendiente / carry-over:**
- Documentar arquitectura, parámetros, resultados y preguntas para la presentación.

---

## 2026-08-17 17:44 -0500 — Fase 4: contratos CPU del baseline validados

**Hecho:**
- Añadidas cinco pruebas numéricas para modelo, pérdida y métricas.
- Separado el descubrimiento de pruebas locales ligeras de las pruebas que importan
  PyTorch en CEDIA.
- Añadido y ejecutado `slurm/test_baseline_cpu.sbatch` en `cpu-dev` como job `23300`.

**Decisiones:**
- La prueba de forma construye U-Net sin descargar pesos ImageNet; conserva y comprueba
  que la configuración real declara `imagenet`.
- Los contratos PyTorch se ejecutan en CPU y verifican que el job no reciba GPU.
- Se prueban backward finito, preferencia de pérdida, matriz de confusión conocida,
  métricas perfectas, reset y rechazo de formas incompatibles.

**Resultados:**
- Job `23300`: `COMPLETED`, código `0:0`, 15 segundos y cinco pruebas correctas.
- Dispositivo contractual: CPU; versión efectiva PyTorch 2.10.0+cu128.
- Las advertencias de deprecación de `torch.jit.script` proceden de dependencias de
  `segmentation_models_pytorch` y no afectaron los contratos.

**Pendiente / carry-over:**
- Preparar y ejecutar el smoke forward/backward del baseline con pesos ImageNet en GPU.

---

## 2026-08-17 17:26 -0500 — Fase 4: métricas binarias por píxel

**Hecho:**
- Implementado `BinarySegmentationMetrics` con acumulación de TP, FP, FN y TN.
- Implementados Dice, IoU, precisión y recall a partir de la matriz de confusión.
- Conectado el umbral inicial 0.5 desde la configuración versionada del baseline.
- Ejecutadas correctamente las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- Las métricas se calculan como agregación micro sobre todos los píxeles del split,
  evitando promediar batches con distinto número de muestras.
- Una unión vacía produce Dice/IoU 1.0; precision o recall sin denominador producen
  0.0. Kvasir-SEG no contiene máscaras reales vacías, pero el caso queda definido.
- Se conservan los conteos crudos para auditoría y para una matriz de confusión por
  píxel; Dice de validation continúa como criterio principal de selección.

**Pendiente / carry-over:**
- Añadir pruebas numéricas de contratos para modelo, pérdida y métricas sin GPU.

---

## 2026-08-17 17:03 -0500 — Fase 4: pérdida BCE + Dice implementada

**Hecho:**
- Implementadas `DiceLoss`, `BCEDiceLoss` y la factoría `build_loss`.
- Añadidos al YAML los pesos de BCE/Dice y el suavizado numérico.
- Validados sintaxis, configuración y las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- BCE y Dice se suman con pesos iniciales 1.0 y 1.0 para conservar una referencia
  simple y explícita antes de cualquier ajuste experimental.
- Dice aplica sigmoid a los logits, reduce por muestra sobre canal y espacio y luego
  promedia el batch.
- Se usa `smooth=1e-7` para evitar división por cero sin alterar materialmente el valor.
- Las formas de logits y targets deben coincidir; los targets se convierten al dtype de
  los logits antes del cálculo.

**Pendiente / carry-over:**
- Implementar Dice, IoU, precision y recall por píxel.
- Validar numéricamente pérdida y gradientes en las pruebas de contratos sin GPU.

---

## 2026-08-17 16:49 -0500 — Fase 4: pérdidas explicadas para la presentación

**Hecho:**
- Añadida a `docs/presentacion.md` una explicación breve de BCEWithLogitsLoss,
  Dice loss y el motivo de combinarlas.

**Decisiones:**
- La explicación diferencia clasificación por píxel y superposición global, vinculando
  Dice con el desbalance observado entre fondo y pólipo.
- No se documentan todavía pesos ni detalles numéricos: se fijarán al implementar y
  validar la pérdida.

**Pendiente / carry-over:**
- Implementar la pérdida combinada BCEWithLogits + Dice.

---

## 2026-08-17 15:37 -0500 — Fase 4: factoría del modelo

**Hecho:**
- Creado el paquete `polysight_seg.models` con carga de configuración y factoría.
- Implementada la construcción de `segmentation_models_pytorch.Unet` desde el YAML.
- Verificado localmente que cargar la configuración no importa PyTorch.
- Ejecutadas correctamente las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- La factoría solo acepta el contrato aprobado: U-Net, entrada RGB, una clase de salida
  y ausencia de activación interna.
- El import de `segmentation_models_pytorch` es diferido para mantener separadas las
  validaciones locales ligeras de la ejecución PyTorch en CEDIA.
- La descarga y construcción efectiva de los pesos ImageNet se comprobarán en el smoke
  forward/backward del baseline, no en el equipo local.

**Pendiente / carry-over:**
- Implementar la pérdida combinada BCEWithLogits + Dice.

---

## 2026-08-17 14:44 -0500 — Fase 4: configuración del baseline

**Hecho:**
- Creada `configs/models/unet-resnet34.yaml` como configuración canónica del modelo.
- Documentada la relación entre la configuración del modelo y la de Kvasir-SEG.
- Validado el YAML y ejecutadas las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- El baseline usa `segmentation_models_pytorch.Unet`, encoder ResNet-34 y pesos ImageNet.
- La red recibe tres canales y devuelve un canal de logits; no incorpora sigmoid para
  mantener compatibilidad numérica con BCEWithLogitsLoss.
- El umbral inicial 0.5 se aplica fuera del modelo y solo podrá ajustarse con validation.
- Los hiperparámetros de entrenamiento se mantienen fuera de esta configuración hasta
  la fase correspondiente.

**Pendiente / carry-over:**
- Implementar la factoría del modelo desde la configuración versionada.

---

## 2026-08-17 14:41 -0500 — Fase 4: evidencia CEDIA para la presentación

**Hecho:**
- Añadida a `docs/presentacion.md` una síntesis de entorno, GPU, datos y pipeline
  verificados mediante Slurm.
- Aclarado que los smoke tests validan preparación técnica, no calidad del modelo ni
  resultados de entrenamiento.

**Decisiones:**
- Se priorizan cifras breves y defendibles durante la exposición, junto con una respuesta
  directa sobre el uso obligatorio de Slurm para acceder a nodos de cómputo.

**Pendiente / carry-over:**
- Crear la configuración versionada del baseline U-Net/ResNet-34.

---

## 2026-08-17 14:30 -0500 — Fase 4: smoke tests GPU y datos completados

**Hecho:**
- Añadido un job `cpu-dev` para reconstruir y validar dataset, manifest y splits desde
  el ZIP original almacenado fuera de Git.
- Corregidos los jobs smoke para priorizar las dependencias fijadas del virtualenv sin
  ocultar el PyTorch suministrado por el módulo de CEDIA.
- Ejecutado el smoke GPU `23294` con una A100-SXM4-40GB y forward/backward real.
- Reproducidos los datos mediante el job `23295` y ejecutado el smoke del pipeline
  `23296` para train, validation y test.

**Decisiones:**
- La combinación efectiva PyTorch 2.10.0+cu128, driver 535.161.08 y A100 se acepta porque
  el smoke GPU verificó CUDA, cuDNN, asignación de dispositivo y cálculo real.
- `pin_memory=true` se mantiene para entrenamiento GPU; su advertencia en el smoke CPU
  es esperada y no representa un fallo del pipeline.
- No se actualiza Albumentations desde 1.4.24: la versión directa permanece fijada para
  conservar reproducibilidad aunque la librería anuncie una versión posterior.

**Resultados:**
- Job `23294`: `COMPLETED`, 9 s, A100-SXM4-40GB, `status=ok`, pérdida
  0.2901759743690491, PyTorch 2.10.0+cu128 y cuDNN 91002.
- Job `23295`: `COMPLETED`, 21 s, 1.000 pares y splits 700/150/150.
- Job `23296`: `COMPLETED`, 9 s, batches `[8,3,256,256]` y máscaras
  `[8,1,256,256]` para los tres splits.
- SHA-256 reproducidos: manifest `35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4`
  y splits `85fe68a5b241f880a80d1476fdffcff88ae5b5e51c0adbe690cce023cbfe13f9`.

**Pendiente / carry-over:**
- Crear la configuración versionada del baseline U-Net/ResNet-34.

---

## 2026-08-17 13:48 -0500 — Fase 4: entorno Python preparado mediante Slurm

**Hecho:**
- Añadido `slurm/setup_cluster_env.sbatch` para crear y auditar `.venv-cluster` desde
  un nodo `cpu-dev`, sin ejecutar cargas de cómputo en `login1`.
- Corregida la precedencia de paquetes entre el virtualenv y el `PYTHONPATH` del módulo.
- Ejecutado el job `23287` desde el commit `956b3583f093978d81a8b1a66e14dae7b4de2009`.
- Confirmados `pip check` sin errores, estado `COMPLETED`, salida `0:0` y working tree
  limpio en CEDIA.

**Decisiones:**
- Python se mantiene en 3.11; no fue la causa de los intentos fallidos de preparación.
- PyTorch debe proceder del módulo de CEDIA y no descargarse dentro del virtualenv.
- El `site-packages` del virtualenv precede al `PYTHONPATH` del módulo para respetar
  NumPy 1.26.4, Pillow 10.4.0 y las demás versiones directas fijadas.
- La compatibilidad de Torch 2.10.0+cu128 con el driver y la A100 se validará mediante
  Slurm; el nombre `pytorch/2.2` del módulo no coincide con su contenido efectivo.

**Resultados:**
- Python 3.11.14, PyTorch 2.10.0+cu128, CUDA build 12.8, cuDNN 91002,
  torchvision 0.25.0 y pip 26.2.1.
- Job `23287`: 47 segundos, `cpu-dev`, 4 CPU, 8 GB solicitados y 128868K MaxRSS.

**Pendiente / carry-over:**
- Ejecutar los smoke tests GPU y del pipeline de datos en CEDIA.
- Confirmar con el smoke GPU la compatibilidad efectiva entre Torch, driver y A100.

---

## 2026-08-17 12:51 -0500 — Fase 4: sincronización inicial en CEDIA

**Hecho:**
- Clonada la rama `chore/baseline-unet-resnet34` en
  `$HOME/projects/polysight-seg` en CEDIA.
- Transferido el ZIP original de Kvasir-SEG a `$HOME/datasets` mediante `rsync`.
- Verificados en CEDIA el commit, el working tree limpio, el tamaño y el SHA-256 del ZIP.

**Decisiones:**
- Se conserva el ZIP original fuera de Git y se reconstruirán los datos derivados con
  los scripts versionados después de preparar `.venv-cluster`.
- Se ejecuta la fase desde su branch dedicado y el commit aprobado
  `136d0310ee9faf43f95485f1f274881cade8e874`.

**Pendiente / carry-over:**
- Preparar `.venv-cluster` y registrar las versiones efectivas de dependencias.
- Reproducir los artefactos del dataset y ejecutar los smoke tests en CEDIA.

---

## 2026-08-17 12:46 -0500 — Cierre de sesión: publicación y preparación de Fase 4

**Hecho:**
- Cerrada la Fase 3 e integrada en `dev` con working tree limpio.
- Creado el repositorio público `christianbueno1/polysight-seg` mediante `gh` CLI.
- Publicadas las ramas `dev` y `chore/baseline-unet-resnet34`.
- Verificado acceso al nodo `login1` de CEDIA y disponibilidad de Python 3.11,
  PyTorch 2.2, CUDA 12.4, particiones CPU/GPU y GPUs A100.
- Preparada la Fase 4 con tareas para el baseline U-Net/ResNet-34.

**Decisiones:**
- `dev` es la rama predeterminada remota hasta que exista una release estable en `main`.
- El repositorio es público; datasets y artefactos continúan excluidos mediante
  `.gitignore`.
- Se usará `ssh -F ~/.ssh/config cedia` hasta corregir los permisos de la configuración
  SSH global local.

**Pendiente / carry-over:**
- Transferir el ZIP y reproducir dataset/manifests/splits en CEDIA.
- Ejecutar los smoke tests GPU y del pipeline de datos.
- Implementar y validar el baseline U-Net/ResNet-34.

---

## 2026-08-17 12:39 -0500 — Fase 3: Splits y pipeline de datos completados

**Hecho:**
- Confirmado que los folds oficiales corresponden al conjunto de clasificación y no a
  un protocolo train/validation/test específico de Kvasir-SEG.
- Generados splits deterministas 700/150/150 con semilla `20260817`.
- Estratificadas las muestras por tamaño pequeño, mediano y grande del pólipo.
- Validadas cobertura total, exclusividad, conteos y protección de grupos duplicados.
- Implementados configuración, Dataset, DataLoader y transformaciones sincronizadas.
- Preparado un smoke test Slurm del pipeline para `cpu-dev` en CEDIA.
- Añadidas pruebas locales y documentación técnica y de presentación.

**Decisiones:**
- Validation y test permanecen deterministas; solo train recibe augmentations aleatorias.
- Las entradas se redimensionan a 256 × 256 con bilinear para imágenes y nearest-neighbor
  para máscaras.
- Test queda aislado de toda selección de umbral, modelo e hiperparámetros.
- No puede garantizarse separación por paciente por falta de identificadores clínicos.

**Resultados:**
- Asignaciones SHA-256:
  `2d0f1f88380314f7d633b1d84b8f6d0e662eb98ff803b25140e8b48c305f7e34`.
- Splits CSV SHA-256:
  `85fe68a5b241f880a80d1476fdffcff88ae5b5e51c0adbe690cce023cbfe13f9`.
- Nueve pruebas locales finalizaron correctamente sin PyTorch.

**Pendiente / carry-over:**
- Ejecutar el smoke test del pipeline en CEDIA.
- Implementar el baseline U-Net con encoder ResNet-34 en la Fase 4.
- Crear el repositorio remoto cuando `gh` tenga una sesión autenticada válida.

---

## 2026-08-17 11:58 -0500 — Fase 2: Kvasir-SEG preparado y validado

**Hecho:**
- Registrados tamaño, SHA-256, procedencia oficial y condiciones de uso del ZIP.
- Implementada y ejecutada una extracción segura, atómica e idempotente.
- Validados los 1.000 pares, bounding boxes, UUID, JPEG y dimensiones.
- Definida la binarización reproducible de máscaras JPEG con umbral 128.
- Generado un manifest determinista con hashes, dimensiones y fracción de pólipo.
- Confirmada la ausencia de duplicados binarios exactos dentro del subconjunto.
- Añadidas pruebas ligeras y documentación para reproducir los datos en CEDIA.
- Creado material explicativo de binarización en `docs/presentacion.md`.

**Decisiones:**
- Los archivos originales permanecen inmutables y excluidos de Git.
- La binarización usa `valor >= 128` como pólipo y no materializa nuevas máscaras.
- Los bounding boxes usan límites máximos exclusivos.
- Los splits se construirán desde el manifest durante la Fase 3.

**Resultados:**
- Fuente SHA-256: `4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a`.
- Manifest SHA-256: `35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4`.
- 1.000 pares válidos, 0 corruptos y 0 grupos duplicados exactos.
- Las siete pruebas locales finalizaron correctamente sin PyTorch.

**Pendiente / carry-over:**
- Transferir el ZIP a CEDIA y comprobar allí los hashes reproducibles.
- Crear splits deterministas y el pipeline de datos en la Fase 3.

---

## 2026-08-17 11:19 -0500 — Fase 1: Base reproducible completada

**Hecho:**
- Fijados Python 3.11 y ocho dependencias directas para el entorno de CEDIA.
- Creada la estructura de código, configuraciones, scripts, Slurm y pruebas.
- Preparado un smoke test GPU con forward/backward real para PyTorch y CUDA.
- Añadidas cuatro pruebas y un comando de validación local sin PyTorch.
- Documentada la preparación, comprobación y evidencia requerida en CEDIA.
- Validada la estructura completa sin instalar dependencias de entrenamiento localmente.

**Decisiones:**
- PyTorch será suministrado por el módulo `pytorch/2.2` de CEDIA, no por una descarga
  local ni como dependencia directa del proyecto.
- El entorno local puede usar un Python posterior para comprobaciones ligeras, mientras
  el entorno ejecutable del proyecto permanece restringido a Python 3.11.
- Dataset, checkpoints, resultados, entornos virtuales y logs Slurm quedan fuera de Git.

**Pendiente / carry-over:**
- Ejecutar `slurm/smoke_gpu.sbatch` en CEDIA y conservar su evidencia.
- Incorporar y validar el archivo local de Kvasir-SEG durante la Fase 2.

---

## 2026-08-17 10:56 -0500 — Fase 1: Base reproducible del repositorio

**Hecho:**
- Confirmado el objetivo general de segmentación de pólipos con Kvasir-SEG.
- Creado el backlog inicial de ocho fases.
- Documentados los entornos local y CEDIA HPC y las características relevantes del
  equipo local.
- Creada la rama `dev` y el branch `chore/base-reproducible` para la Fase 1.
- Definidas las tareas concretas de la Fase 1.

**Decisiones:**
- PyTorch no se instalará ni ejecutará localmente debido a las limitaciones de hardware.
- CEDIA HPC será el entorno para PyTorch, GPU, entrenamiento y evaluación acelerada.
- El entorno local se limitará a desarrollo, Git, documentación y comprobaciones
  ligeras sin PyTorch.

**Pendiente / carry-over:**
- Configurar Python, dependencias, estructura, scripts Slurm y validaciones de la fase.
