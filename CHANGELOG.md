# CHANGELOG

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
