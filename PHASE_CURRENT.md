# PHASE_CURRENT

## Fase 2 — Adquisición, validación y manifest de Kvasir-SEG

**Objetivo:** Incorporar Kvasir-SEG mediante un proceso seguro, idempotente y trazable,
validar cada par imagen–máscara y generar un manifest reproducible sin versionar los
datos binarios.

**Contexto:** El archivo fuente está disponible en
`/home/chris/Downloads/hyper-kvasir-segmented-images.zip`. Ver
`docs/segmentation-project-guide.md` para las reglas del dataset.

---

### Tareas

- [x] Registrar tamaño y SHA-256 del archivo fuente sin modificarlo
- [~] Confirmar estructura interna, procedencia, licencia y citas aplicables
- [ ] Implementar extracción segura e idempotente bajo `data/raw/`
- [ ] Validar archivos corruptos, nombres y correspondencia de los 1.000 pares
- [ ] Validar dimensiones y binarización explícita de máscaras JPEG
- [ ] Calcular hashes, duplicados exactos y porcentaje de píxeles de pólipo
- [ ] Generar manifest y resumen reproducibles bajo `data/processed/`
- [ ] Añadir pruebas ligeras para la lógica de validación de datos
- [ ] Documentar transferencia y reproducción del dataset en CEDIA
- [ ] Ejecutar la validación completa y registrar resultados

---

### Notas y decisiones

- El ZIP fuente y los datos extraídos permanecen fuera de Git.
- No se crearán splits durante esta fase; pertenecen a la Fase 3.
- El archivo descargado se tratará como inmutable y toda transformación se escribirá en
  rutas separadas.
- El ZIP contiene 1.000 imágenes, 1.000 máscaras, un JSON, ninguna ruta insegura y pasa
  la prueba de integridad.
- Falta confirmar la URL exacta desde la cual se descargó la copia local.
