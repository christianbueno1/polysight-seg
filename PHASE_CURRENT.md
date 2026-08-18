# PHASE_CURRENT

## Fase 5 — Entrenamiento reproducible y seguimiento de experimentos

**Objetivo:** Entrenar el baseline U-Net/ResNet-34 en CEDIA con un protocolo versionado,
checkpoints auditables y seguimiento completo mediante MLflow.

**Contexto:** La Fase 4 validó datos, arquitectura, pérdida, métricas, contratos CPU y
un forward/backward real en una A100. El entrenamiento seleccionará el mejor checkpoint
usando exclusivamente Dice de validation; test permanece aislado para la Fase 6.

---

### Tareas

- [x] Adaptar y versionar la configuración de MLflow para este proyecto
- [x] Fijar la dependencia de MLflow y validar `.venv-cluster` en CEDIA
- [x] Crear configuración versionada de entrenamiento
- [x] Implementar loops de train y validation con métricas por época
- [x] Implementar checkpoints `last.pt` y `best.pt` con metadatos de trazabilidad
- [ ] Integrar parámetros, métricas y artefactos del entrenamiento en MLflow
- [ ] Añadir pruebas CPU del entrenamiento, checkpoints y tracking
- [ ] Ejecutar un smoke de entrenamiento de pocos batches en GPU
- [ ] Ejecutar el entrenamiento completo del baseline en CEDIA
- [ ] Sincronizar `mlflow.db` y `artifacts/` y verificar la interfaz local
- [ ] Documentar configuración, curvas y resultados de validation para la presentación

---

### Notas y decisiones

- MLflow se incorpora antes del primer entrenamiento completo; no existen ejecuciones
  históricas que migrar.
- Registrar por época: loss, Dice, IoU, precisión, recall y learning rate para train y
  validation cuando corresponda.
- Registrar también commit, configuraciones, versiones efectivas y hashes del dataset.
- `best.pt` se selecciona por Dice de validation; test no participa en selección ni
  ajuste de hiperparámetros.
- `mlflow.db`, artefactos, checkpoints y logs permanecen fuera de Git.
- Los hiperparámetros concretos se decidirán y documentarán al crear la configuración
  de entrenamiento, antes de ejecutar el primer run.
- El tracking usa un servidor limitado a `127.0.0.1`, SQLite como backend y proxy de
  artefactos local para conservar URIs `mlflow-artifacts:/` portables.
- `mlflow.db` tendrá un solo escritor y se sincronizará solo después de terminar el job.
- MLflow se fija en `3.15.1`, versión estable compatible con Python 3.11; la validación
  se ejecuta mediante Slurm en `cpu-dev`, nunca en el nodo de login.
- Se conservan TP, FP, FN y TN de train y validation por época para reconstruir métricas
  y matrices sin repetir el entrenamiento.
- El baseline usa 50 épocas máximas, semilla `20260817`, AdamW con learning rate y
  weight decay `1e-4`, y ReduceLROnPlateau guiado por Dice de validation.
- Se habilita AMP `float16` con escalado de gradiente en la A100 y determinismo estricto;
  early stopping espera 10 épocas sin mejora y test permanece deshabilitado.
- Los loops agregan la pérdida ponderada por número de muestras y calculan las métricas
  micro desde TP, FP, FN y TN acumulados sobre la época completa.
- Validation usa `inference_mode`, no calcula gradientes ni modifica el optimizador.
- `last.pt` se actualiza cada época y `best.pt` solo ante una mejora superior al
  `min_delta` configurado sobre Dice de validation.
- Cada checkpoint usa escritura atómica, sidecar SHA-256 y conserva estados de modelo,
  optimizador, scheduler, scaler y RNG, además de configuración y procedencia.
