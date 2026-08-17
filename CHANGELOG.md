# CHANGELOG

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
