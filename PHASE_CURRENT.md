# PHASE_CURRENT

## Fase 4 — Baseline U-Net con encoder ResNet-34

**Objetivo:** Implementar y validar en CEDIA un baseline de segmentación binaria U-Net
con encoder ResNet-34 preentrenado en ImageNet, junto con su pérdida y métricas.

**Contexto:** La Fase 3 dejó splits 700/150/150, configuración de entradas 256 × 256 y
un pipeline de datos reproducible. PyTorch se ejecuta exclusivamente en CEDIA.

---

### Tareas

- [x] Sincronizar repositorio y dataset en CEDIA
- [ ] Preparar `.venv-cluster` y registrar versiones efectivas de dependencias
- [ ] Ejecutar los smoke tests GPU y del pipeline de datos en CEDIA
- [ ] Crear configuración versionada del baseline U-Net/ResNet-34
- [ ] Implementar la factoría del modelo con entrada RGB y salida de un canal
- [ ] Implementar pérdida combinada BCEWithLogits + Dice
- [ ] Implementar métricas Dice, IoU, precisión y recall por píxel
- [ ] Añadir pruebas de contratos que puedan ejecutarse sin GPU
- [ ] Preparar y ejecutar smoke test forward/backward del baseline en CEDIA
- [ ] Documentar arquitectura, parámetros, resultados y preguntas para la presentación

---

### Notas y decisiones

- Arquitectura baseline: U-Net con encoder ResNet-34 preentrenado en ImageNet.
- Entrada: tensor RGB `[B, 3, 256, 256]`.
- Salida: logits `[B, 1, 256, 256]`; sigmoid y umbral se aplican fuera del modelo.
- Pérdida inicial: BCEWithLogitsLoss + Dice loss.
- PyTorch, CUDA y pruebas del modelo no se ejecutarán en el equipo local.
- Acceso temporal a CEDIA: `ssh -F ~/.ssh/config cedia`, porque un archivo de la
  configuración SSH global local tiene permisos inseguros.
- Repositorio público: `https://github.com/christianbueno1/polysight-seg`, con `dev`
  como rama de integración predeterminada.
- Copia de trabajo en CEDIA: `$HOME/projects/polysight-seg`, rama
  `chore/baseline-unet-resnet34`, commit `136d0310ee9faf43f95485f1f274881cade8e874`.
- ZIP fuente en CEDIA: `$HOME/datasets/hyper-kvasir-segmented-images.zip`, verificado
  con 46.179.365 bytes y SHA-256 `4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a`.
