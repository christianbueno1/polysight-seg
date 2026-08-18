# PHASE_CURRENT

## Fase 9 — Diseño de API piloto local con clasificación opcional

**Objetivo:** Definir una guía implementable para servir el modelo de segmentación en
una laptop y permitir integrar, sin acoplamiento obligatorio, un modelo de clasificación
mantenido en otro proyecto.

**Contexto:** El baseline versionado `model-unet-resnet34-v1.0.0` es el modelo oficial.
La primera prueba de la API será exclusivamente local y no constituye despliegue clínico
ni exposición a Internet.

---

### Tareas

- [x] Documentar arquitectura, contrato HTTP y preprocesamiento del segmentador
- [x] Diseñar clasificación opcional desacoplada mediante adaptadores
- [x] Definir configuración, seguridad, pruebas y criterios del piloto en laptop
- [ ] Revisar y aprobar con el responsable el alcance antes de implementar código

---

### Notas y decisiones

- Segmentación es obligatoria; clasificación puede estar deshabilitada, ejecutarse en
  proceso o consumirse como servicio HTTP local.
- El checkpoint se verifica por SHA-256 y metadatos antes de aceptar peticiones.
- El piloto escucha en `127.0.0.1`, procesa en memoria y no guarda imágenes por defecto.
- No se establecen cifras de latencia hasta medir la laptop seleccionada.
- La guía define el contrato objetivo; FastAPI y sus dependencias todavía no se agregan.
