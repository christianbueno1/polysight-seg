# CHANGELOG

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
