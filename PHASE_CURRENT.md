# PHASE_CURRENT

## Fase 8 — Empaquetado de resultados y documentación del estudio

**Objetivo:** Consolidar el baseline entrenado, su evaluación final y la evidencia
reproducible en una entrega comprensible para revisión técnica y presentación.

**Contexto:** U-Net/ResNet-34 obtuvo Dice test `0.9183967352352693` e IoU
`0.8491068445832013` sobre 150 imágenes. Configuraciones, checkpoints, métricas,
probabilidades, paneles y runs MLflow están auditados. La comparación EfficientNet-B0
queda diferida y no forma parte de la entrega actual.

---

### Tareas

- [x] Consolidar en README el objetivo, arquitectura, datos y resultados principales
- [x] Crear un reporte técnico final con protocolo, métricas y análisis de errores
- [ ] Documentar cómo recuperar checkpoint, resultados y runs MLflow
- [ ] Crear una ficha del modelo con uso previsto, límites y riesgos
- [ ] Revisar que presentación y documentación usen cifras consistentes
- [ ] Añadir un índice de artefactos y fuentes canónicas
- [ ] Ejecutar validaciones finales del repositorio y enlaces documentales
- [ ] Preparar checklist de entrega y cierre de la fase

---

### Notas y decisiones

- La entrega actual contiene únicamente el baseline U-Net/ResNet-34 cerrado.
- La Fase 7 permanece pendiente para retomarla posteriormente; no se elimina del backlog.
- Las métricas oficiales proceden del run MLflow
  `73876309ec7c45e09023574a02a47475` con umbral fijo `0.5`.
- Los CSV/JSON son fuentes canónicas; las figuras y resúmenes son derivados.
- La documentación distinguirá resultados de validation, test y smokes técnicos.
- El README presenta primero resultados test, protocolo, runs y evidencia versionada,
  con una advertencia explícita sobre alcance y variabilidad por imagen.
- El reporte técnico separa protocolo, resultados agregados, variabilidad por imagen y
  límites; no presenta como comparación ningún experimento no ejecutado.
