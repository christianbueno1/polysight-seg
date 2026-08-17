# PHASE_CURRENT

## Fase 1 — Base reproducible del repositorio y entorno Python

**Objetivo:** Establecer una estructura reproducible para desarrollar localmente y
ejecutar PyTorch exclusivamente en el clúster HPC de CEDIA.

**Contexto:** Ver `docs/execution-environments.md`,
`docs/cedia-cluster-guide.md` y `docs/segmentation-project-guide.md`.

---

### Tareas

- [x] Documentar la separación entre el entorno local y CEDIA HPC
- [x] Fijar la versión compatible de Python en la configuración del proyecto
- [x] Definir dependencias reproducibles sin instalarlas en el equipo local
- [x] Crear la estructura inicial de código, configuración, scripts Slurm y pruebas
- [ ] Preparar un smoke test de PyTorch y CUDA para un nodo GPU de CEDIA
- [ ] Añadir comandos de validación local que no dependan de PyTorch
- [ ] Documentar la preparación y verificación del entorno en CEDIA
- [ ] Validar la estructura y los archivos de configuración de la fase

---

### Notas y decisiones

- El equipo local se reserva para Git, edición, documentación y validaciones ligeras.
- PyTorch no se instalará ni ejecutará localmente.
- Entrenamiento, evaluación acelerada y smoke tests de PyTorch se ejecutarán mediante
  Slurm en CEDIA HPC.
- Se mantiene Python 3.11 por compatibilidad con los módulos observados en CEDIA.
- PyTorch 2.2 será provisto por el módulo de CEDIA y no se declara para descarga desde
  PyPI.
- Las dependencias directas quedan fijadas; sus versiones transitivas se registrarán
  después de validar la instalación dentro de CEDIA.
- El archivo `hyper-kvasir-segmented-images.zip` ya está disponible localmente en
  `/home/chris/Downloads/`; su incorporación y validación corresponden a la Fase 2.
- Los directorios de datos y artefactos generados se excluyen de Git.
