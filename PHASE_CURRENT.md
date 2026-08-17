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
- [x] Confirmar estructura interna, procedencia, licencia y citas aplicables
- [x] Implementar extracción segura e idempotente bajo `data/raw/`
- [x] Validar archivos corruptos, nombres y correspondencia de los 1.000 pares
- [x] Validar dimensiones y binarización explícita de máscaras JPEG
- [x] Calcular hashes, duplicados exactos y porcentaje de píxeles de pólipo
- [x] Generar manifest y resumen reproducibles bajo `data/processed/`
- [x] Añadir pruebas ligeras para la lógica de validación de datos
- [x] Documentar transferencia y reproducción del dataset en CEDIA
- [ ] Ejecutar la validación completa y registrar resultados

---

### Notas y decisiones

- El ZIP fuente y los datos extraídos permanecen fuera de Git.
- No se crearán splits durante esta fase; pertenecen a la Fase 3.
- El archivo descargado se tratará como inmutable y toda transformación se escribirá en
  rutas separadas.
- El ZIP contiene 1.000 imágenes, 1.000 máscaras, un JSON, ninguna ruta insegura y pasa
  la prueba de integridad.
- El usuario confirmó que descargó la copia desde el portal oficial de Simula:
  `https://datasets.simula.no/hyper-kvasir/`.
- La extracción valida rutas, enlaces, duplicados y tamaño antes de publicar los datos
  atómicamente; un marcador con SHA-256 permite repetir el comando sin cambios.
- La validación decodifica los JPEG completos y exige 1.000 UUID compartidos entre
  imágenes, máscaras y bounding boxes con coordenadas válidas.
- Los límites `xmax` y `ymax` del JSON se interpretan como exclusivos porque el dataset
  contiene valores iguales al ancho o alto de la imagen.
- Las máscaras se convierten a escala de grises y se binarizan con `valor >= 128`; cada
  máscara debe conservar al menos un píxel de fondo y uno de pólipo.
- El manifest se ordena por UUID, usa rutas relativas y no incluye timestamps para que
  su contenido sea reproducible a partir del mismo archivo fuente.
- Los grupos de duplicados exactos se definen usando el SHA-256 del JPEG original.
- Las pruebas locales cubren el límite exacto de binarización, la idempotencia de la
  extracción y el rechazo de rutas ZIP con traversal.
- En CEDIA se transfiere el ZIP original y se reconstruyen los datos; los hashes del
  archivo fuente, manifest y resumen permiten comprobar que el resultado sea idéntico.
