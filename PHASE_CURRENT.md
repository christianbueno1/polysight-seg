# PHASE_CURRENT

## Fase 4 — Baseline U-Net con encoder ResNet-34

**Objetivo:** Implementar y validar en CEDIA un baseline de segmentación binaria U-Net
con encoder ResNet-34 preentrenado en ImageNet, junto con su pérdida y métricas.

**Contexto:** La Fase 3 dejó splits 700/150/150, configuración de entradas 256 × 256 y
un pipeline de datos reproducible. PyTorch se ejecuta exclusivamente en CEDIA.

---

### Tareas

- [x] Sincronizar repositorio y dataset en CEDIA
- [x] Preparar `.venv-cluster` y registrar versiones efectivas de dependencias
- [x] Ejecutar los smoke tests GPU y del pipeline de datos en CEDIA
- [x] Crear configuración versionada del baseline U-Net/ResNet-34
- [x] Implementar la factoría del modelo con entrada RGB y salida de un canal
- [x] Implementar pérdida combinada BCEWithLogits + Dice
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
- `.venv-cluster` fue preparado por Slurm en `cpu-dev` con el job `23287`; `pip check`
  finalizó sin dependencias rotas y el job terminó `COMPLETED` con código `0:0`.
- Versiones efectivas observadas: Python 3.11.14, PyTorch 2.10.0+cu128, CUDA build
  12.8, cuDNN 91002, torchvision 0.25.0 y pip 26.2.1.
- El módulo etiquetado `pytorch/2.2` contiene PyTorch 2.10.0; esta discrepancia con el
  nombre del módulo debe validarse contra el driver y la GPU mediante el smoke test.
- El `PYTHONPATH` exportado por el módulo debe conservarse detrás del `site-packages`
  del virtualenv para usar PyTorch de CEDIA sin eclipsar las dependencias fijadas.
- Smoke GPU `23294`: `COMPLETED` con A100-SXM4-40GB, CUDA disponible, forward/backward
  correcto y pérdida 0.2901759743690491.
- El driver NVIDIA 535.161.08 reporta CUDA 12.2, pero PyTorch 2.10.0+cu128 completó el
  smoke GPU; la combinación efectiva funciona en el nodo asignado.
- Preparación de datos `23295`: 1.000 pares y hashes de manifest/splits idénticos a
  los locales; smoke del pipeline `23296`: `status=ok` para 700/150/150 muestras.
- En jobs CPU, la advertencia de `pin_memory` sin acelerador es esperada y no afecta el
  contrato del pipeline; en entrenamiento GPU sí podrá fijar memoria para transferencias.
- Configuración canónica del modelo: `configs/models/unet-resnet34.yaml`; no incluye
  hiperparámetros de entrenamiento y mantiene la activación fuera de la red.
- La factoría valida el contrato antes de construir y realiza el import pesado de
  `segmentation_models_pytorch` de forma diferida para no requerir PyTorch localmente.
- La pérdida suma BCEWithLogits y Dice con pesos 1.0/1.0; Dice se calcula por muestra
  desde sigmoid y usa suavizado `1e-7` para estabilidad numérica.
