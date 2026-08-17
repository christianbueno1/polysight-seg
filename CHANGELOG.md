# CHANGELOG

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
