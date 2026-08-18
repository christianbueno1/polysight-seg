# PHASE_CURRENT

## Fase 10 — Ejemplos trazables para clasificación y segmentación

**Objetivo:** Versionar un conjunto pequeño de imágenes que permita comprobar de forma
inmediata el clasificador `main16` y el segmentador sin descargar los datasets completos.

**Contexto:** Las imágenes proceden de los dos ZIP locales de HyperKvasir. Son fixtures
funcionales y visuales, no un conjunto para calcular métricas ni reemplazar los splits
experimentales.

---

### Tareas

- [x] Seleccionar una imagen representativa por cada clase de `main16`
- [x] Seleccionar tres imágenes de `validation` de segmentación con sus máscaras
- [x] Registrar etiquetas, procedencia y SHA-256 en un manifest
- [x] Documentar uso, alcance y atribución de los ejemplos
- [x] Validar formato, hashes, dimensiones y exclusión de `test`
- [x] Integrar un ejemplo como entrada predeterminada del notebook de inferencia

---

### Notas y decisiones

- Clasificación cubre las 16 salidas reales del perfil `main16`; una sola imagen por
  clase sirve como prueba funcional, no como estimación de calidad.
- Segmentación usa únicamente `validation`, nunca `test`, e incluye imagen y máscara.
- La selección es determinista para que pueda reconstruirse desde los ZIP originales.
- El conjunto completo ocupa 6,2 MiB y contiene 16 imágenes de clasificación y tres
  pares imagen–máscara de segmentación.
- Los notebooks fijan el commit `c46d252b174546782291d9970b87190ce1ab0da1`, que ya
  contiene la imagen de demostración usada como entrada predeterminada.
