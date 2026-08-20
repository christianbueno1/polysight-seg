# CHANGELOG

---

## 2026-08-20 01:00 -0500 — Fase 11: opciones autónomas para el póster

**Hecho:**
- Generadas tres figuras SVG listas para póster: comparación cualitativa, resumen
  cuantitativo y Dice frente al tamaño del pólipo.
- Incluidos títulos, definiciones, tamaño del test, umbral y conclusiones dentro de las
  propias figuras para que puedan interpretarse de manera autónoma.
- Documentados el orden recomendado, el generador reproducible y los nuevos artefactos.

**Decisiones:**
- Se recomienda primero la comparación cualitativa porque comunica tarea, resultado y
  limitación con menor carga de lectura para una audiencia general.
- El resumen cuantitativo ocupa el segundo lugar por su rigor y compacidad; el análisis
  por tamaño queda tercero porque exige interpretar ejes, puntos y estratos.
- Los paneles PNG se incrustan como datos en el SVG cualitativo para evitar dependencias
  externas al mover o exportar el póster.

**Pendiente / carry-over:**
- Elegir cuál de las tres figuras entra en el diseño definitivo del póster.
- Presentar la matriz de confusión explícitamente como matriz binaria por píxel.

---

## 2026-08-20 00:41 -0500 — Fase 11: Dice frente al tamaño del pólipo

**Hecho:**
- Creado un gráfico SVG reproducible con las 150 métricas individuales de test.
- Diferenciados los 50 casos pequeños, medianos y grandes mediante los splits canónicos.
- Integrados el gráfico, las medianas por estrato y su interpretación al reporte final.
- Documentado el generador y añadido el SVG al índice de artefactos.

**Decisiones:**
- El eje horizontal usa la fracción real de primer plano, una medida continua del tamaño.
- Se evita concluir que los pólipos pequeños explican todos los fallos: el estrato
  mediano tiene la mejor mediana, pero el peor caso observado pertenece al estrato grande.
- El SVG se genera solo con la biblioteca estándar para mantenerlo editable y reproducible.

**Pendiente / carry-over:**
- Presentar la matriz de confusión explícitamente como matriz binaria por píxel.

---

## 2026-08-19 22:51 -0500 — Fase 11: panel cualitativo para el reporte

**Hecho:**
- Añadida una sección de métricas complementarias y evidencia visual al reporte final.
- Integrados los paneles del mejor caso, caso cercano a la mediana y peor caso.
- Documentados Dice, IoU y la interpretación espacial de cada selección.

**Decisiones:**
- Se descarta el boxplot porque la tabla ya contiene mediana y P25–P75 y el espacio del
  póster se aprovecha mejor mostrando resultados espaciales.
- Se presentan tres niveles de rendimiento para evitar seleccionar solo evidencia
  favorable; el mapa de probabilidad se conserva como quinta vista informativa.

**Pendiente / carry-over:**
- Crear el gráfico de Dice frente al tamaño real del pólipo.
- Presentar la matriz de confusión explícitamente como matriz binaria por píxel.

---

## 2026-08-19 22:31 -0500 — Fase 11: consolidación de la tabla del reporte

**Hecho:**
- Eliminada del reporte final la tabla básica de métricas y conteos por píxel.
- Conservada la tabla comparativa con valores globales, distribución y peores casos.

**Decisiones:**
- Una sola tabla robusta evita duplicar Dice, IoU, precisión y recall en secciones
  consecutivas; la interpretación de la matriz por píxel permanece en el texto.

**Pendiente / carry-over:**
- Crear el boxplot de Dice e IoU por imagen.

---

## 2026-08-19 22:28 -0500 — Fase 11: tabla integrada al reporte final

**Hecho:**
- Añadida al reporte técnico una sección que compara métricas globales y por imagen.
- Incluidos mediana, P25–P75, mínimo y UUID del peor caso para las cuatro métricas.

**Decisiones:**
- Se explica explícitamente que la agregación global pondera píxeles y que las
  estadísticas distributivas otorgan el mismo peso a cada imagen.
- Se conserva el UUID del mínimo para que cada peor resultado pueda auditarse.

**Pendiente / carry-over:**
- Crear el boxplot de Dice e IoU por imagen.

---

## 2026-08-19 22:19 -0500 — Fase 11: tabla resumen de segmentación

**Hecho:**
- Registradas cinco métricas y visualizaciones recomendadas para comunicar el rendimiento.
- Creada la tabla resumen de Dice, IoU, precisión y recall sobre las 150 imágenes de test.
- Incluidos valor micro global, mediana, rango P25–P75, mínimo y UUID del peor caso.

**Decisiones:**
- Se separa el agregado por píxel de la distribución por imagen para no ocultar fallos
  individuales ni el efecto del tamaño de los pólipos.
- El peor caso se calcula independientemente para cada métrica y los percentiles usan
  interpolación lineal.
- `metrics.json` y `per-image-metrics.csv` permanecen como fuentes canónicas.

**Pendiente / carry-over:**
- Crear el boxplot de Dice e IoU por imagen como segunda visualización recomendada.

---

## 2026-08-18 05:39 -0500 — Fase 10: ejemplos para probar ambos modelos

**Hecho:**
- Extraídas sin recomprimir 16 imágenes, una por cada clase real de `main16`.
- Añadidos tres casos de segmentación de `validation`, uno por estrato, con sus máscaras.
- Registrados miembros fuente, etiquetas, roles y SHA-256 en `examples/manifest.csv`.
- Configurado el notebook de inferencia para usar un ejemplo incluido por defecto.
- Superadas 33 validaciones locales, incluidas apertura JPEG, hashes, cobertura de clases,
  dimensiones de los pares y pertenencia al split `validation`.

**Decisiones:**
- Los ejemplos son fixtures funcionales y visuales; no se reportan como evaluación ni
  deben incorporarse a `test`.
- Clasificación usa el UUID lexicográficamente menor de cada clase con al menos 100
  imágenes; segmentación usa el caso central por fracción de máscara en cada estrato.
- El notebook fija un commit que ya contiene su imagen predeterminada para que la ruta
  funcione después del clon inmutable en Colab.

**Pendiente / carry-over:**
- Ejecutar los checkpoints reales sobre estas imágenes en Colab o en la API cuando sus
  binarios estén disponibles.

---

## 2026-08-18 05:08 -0500 — Cierre de Fase 9: notebooks para Colab

**Hecho:**
- Entregados dos notebooks delgados, inferencia reutilizable y contratos estáticos.
- Superadas 29 validaciones locales sin PyTorch y comprobada la descarga HTTPS del
  commit inmutable consumido por los notebooks.
- Preparada la fusión de la fase en `dev`.

**Decisiones:**
- El responsable solicitó cerrar y fusionar sin ejecutar los notebooks en Colab.
- No se afirma validación de PyTorch, checkpoint real, GPU, smoke ni entrenamiento en
  Colab; esa ejecución queda registrada como pendiente externa en el backlog.
- Test continúa desactivado por defecto en el notebook de reproducción.

**Pendiente / carry-over:**
- Cuando exista acceso adecuado, ejecutar ambos notebooks en Colab y registrar sus
  resultados sin modificar los resultados oficiales del baseline.

---

## 2026-08-18 02:40 -0500 — Fase 9: notebooks de verificación y reproducción

**Hecho:**
- Reemplazado el alcance de API local por dos notebooks delgados para Google Colab.
- Implementada inferencia reutilizable de una imagen con carga estricta de `best.pt`.
- Añadidos contratos que impiden outputs guardados, secretos, rutas personales, código
  duplicado y activación accidental de test.
- Ampliado el rango declarado a Python 3.12 y actualizada la versión del paquete a 0.2.0.

**Decisiones:**
- Un notebook verifica el modelo y otro permite reconstruir datos, ejecutar smoke y
  repetir el entrenamiento completo.
- Colab no se usa como servidor; API y clasificación quedan fuera del alcance actual.
- Los notebooks fijan el commit `2bf2c5a874272ecd6ccd24b936af578f4e637c82` y verifican
  archivos grandes por SHA-256 antes de usarlos.

**Pendiente / carry-over:**
- Ejecutar en Colab los contratos PyTorch, la inferencia real y el smoke GPU.

---

## 2026-08-18 02:20 -0500 — Fase 9: diseño de API piloto local

**Hecho:**
- Creada `docs/api-pilot-guide.md` con arquitectura, endpoints, configuración,
  preprocesamiento, seguridad, pruebas y criterios de aceptación para una laptop.
- Diseñada la clasificación como capacidad opcional mediante adaptadores desacoplados.
- Activada la Fase 9 y actualizado el backlog de despliegue local.

**Decisiones:**
- La segmentación funciona por sí sola; el clasificador puede ejecutarse en proceso o
  como servicio HTTP local si existen conflictos de dependencias entre proyectos.
- El piloto queda limitado a `127.0.0.1`, un worker, procesamiento en memoria y uso
  experimental sin validez clínica.
- No se agregan todavía FastAPI ni dependencias web: primero se revisa esta guía y luego
  se implementa en tareas separadas.

**Pendiente / carry-over:**
- Aprobar el contrato y elegir el modo de integración del proyecto de clasificación.

---

## 2026-08-18 01:28 -0500 — Cierre de Fase 8: entrega del baseline

**Hecho:**
- Creado el checklist final de alcance, resultados, trazabilidad, documentación y
  validación técnica.
- Cerradas todas las tareas de empaquetado y marcada la Fase 8 como completada.
- Preparada la fusión del branch de fase en `dev` con el repositorio validado.

**Decisiones:**
- La entrega final se limita al U-Net/ResNet-34; la comparación EfficientNet-B0 sigue
  pendiente y requiere una decisión futura antes de iniciar trabajo.
- Se conserva `PHASE_CURRENT.md` como registro de la fase recién cerrada hasta que el
  responsable confirme cuál será la siguiente fase activa.

**Resultados:**
- 24 contratos locales correctos, enlaces internos válidos y documentación consistente.
- Dice test `0.9183967352352693` e IoU `0.8491068445832013` sobre 150 imágenes.

**Pendiente / carry-over:**
- Definir si el siguiente trabajo será la Fase 7 u otro pendiente del backlog.

---

## 2026-08-18 01:26 -0500 — Fase 8: validación final del repositorio

**Hecho:**
- Añadida una prueba que recorre los archivos Markdown versionados y verifica todos sus
  enlaces locales, incluyendo imágenes y directorios.
- Integrada la prueba al validador local sin dependencias de PyTorch.
- Ejecutadas comprobaciones finales de formato, contratos, documentación y estructura.

**Decisiones:**
- Los enlaces externos no se consultan durante la validación local; los destinos internos
  sí deben existir en el checkout para que la entrega sea navegable sin red.
- La comprobación de enlaces queda permanente para futuras ediciones documentales.

**Pendiente / carry-over:**
- Preparar el checklist de entrega, cerrar la Fase 8 y fusionarla en `dev`.

---

## 2026-08-18 01:21 -0500 — Fase 8: índice de artefactos

**Hecho:**
- Creado `docs/artifact-index.md` con fuentes canónicas, derivados, documentos y estado
  experimental no versionado.
- Relacionados los artefactos con los jobs, runs MLflow y preguntas que permiten
  responder durante una revisión técnica.
- Enlazado el índice desde el README.

**Decisiones:**
- YAML, JSON y CSV tienen prioridad sobre figuras y resúmenes si surge una discrepancia.
- Los binarios grandes se referencian por ruta y procedencia, pero permanecen fuera de
  Git y se recuperan mediante la guía de sincronización.

**Pendiente / carry-over:**
- Ejecutar la validación final del repositorio y de todos los enlaces documentales.

---

## 2026-08-18 01:17 -0500 — Fase 8: consistencia documental

**Hecho:**
- Auditadas las métricas, la época seleccionada, los runs, el umbral y los tamaños de
  splits entre README, reporte, ficha y presentación.
- Corregida una frase obsoleta que anunciaba la evaluación de test como trabajo futuro.
- Añadido un contrato local que compara JSON/CSV canónicos con valores exactos y
  redondeados publicados en los documentos finales.

**Decisiones:**
- Reporte y ficha conservan precisión completa; README y presentación usan cuatro
  decimales para facilitar lectura sin cambiar el valor representado.
- Los resultados canónicos siguen procediendo de `docs/results/test/`.

**Pendiente / carry-over:**
- Añadir un índice de artefactos y fuentes canónicas.

---

## 2026-08-18 01:14 -0500 — Fase 8: ficha del modelo

**Hecho:**
- Creada `docs/model-card.md` con identificación, uso previsto, interfaz, rendimiento,
  procedencia, limitaciones, riesgos y usos no recomendados.
- Enlazada la ficha desde el README y actualizada la tarea correspondiente de la fase.

**Decisiones:**
- El modelo se limita a investigación reproducible sobre Kvasir-SEG y no se presenta
  como herramienta de decisión clínica.
- La ficha destaca el peor Dice individual y los riesgos de falsos negativos, cambio de
  dominio y falta de validación externa.
- No se atribuye superioridad frente a EfficientNet-B0 porque esa comparación no fue
  ejecutada.

**Pendiente / carry-over:**
- Auditar la consistencia de cifras entre README, reporte, ficha y presentación.

---

## 2026-08-18 00:57 -0500 — Fase 8: recuperación de artefactos

**Hecho:**
- Creada una guía para sincronizar `mlflow.db`, artefactos y resultados desde CEDIA.
- Documentadas las rutas y los identificadores canónicos de entrenamiento y evaluación.
- Verificados localmente el SHA-256 de `best.pt`, 150 métricas por imagen y 150 mapas de
  probabilidad.

**Decisiones:**
- La recuperación valida explícitamente el checkpoint ganador y no requiere repetir
  entrenamiento ni evaluación de test.
- Se diferencia el pequeño backend SQLite del directorio de artefactos, que concentra
  aproximadamente 1.2 GB en la copia actual.

**Pendiente / carry-over:**
- Crear la ficha del modelo con uso previsto, límites y riesgos.

---

## 2026-08-18 00:55 -0500 — Fase 8: reporte técnico final

**Hecho:**
- Creado `docs/final-report.md` con protocolo, entrenamiento, evaluación, análisis de
  errores, trazabilidad y límites del baseline.
- Enlazado el reporte desde el README y verificadas sus fuentes documentales.

**Decisiones:**
- Se reportan métricas micro agregadas junto con la distribución por imagen para evitar
  ocultar fallos severos detrás del promedio.
- Las conclusiones se limitan a Kvasir-SEG y excluyen la comparación no ejecutada.

**Pendiente / carry-over:**
- Documentar la recuperación del checkpoint, los resultados y los runs MLflow.

---

## 2026-08-18 00:53 -0500 — Fase 8: README consolidado

**Hecho:**
- Reorganizado el README para presentar el objetivo, la arquitectura, el protocolo y
  los resultados oficiales del baseline U-Net/ResNet-34.
- Añadidos los runs MLflow principales y enlaces directos a configuraciones, métricas,
  curvas y material de presentación.
- Registrada la primera tarea de empaquetado como completada.

**Decisiones:**
- La portada prioriza resultados de test y advierte sobre la variabilidad por imagen y
  la ausencia de validación clínica externa.
- La comparación con EfficientNet-B0 permanece fuera del alcance de esta entrega.

**Pendiente / carry-over:**
- Crear el reporte técnico final y documentar la recuperación de artefactos y runs.

---

## 2026-08-18 00:51 -0500 — Repriorización: comparación diferida

**Hecho:**
- Devuelta la Fase 7 de comparación con EfficientNet-B0 a estado pendiente.
- Activada la Fase 8 para consolidar la entrega del baseline ya entrenado y evaluado.
- Preparado un tablero de documentación, ficha del modelo, artefactos y validación final.

**Decisiones:**
- La comparación de encoders no es necesaria para la entrega actual y podrá retomarse
  posteriormente sin eliminarse del backlog.
- El empaquetado se limitará al U-Net/ResNet-34 y a sus resultados ya cerrados; no se
  inferirán comparaciones que no fueron ejecutadas.

**Pendiente / carry-over:**
- Fusionar el cierre de Fase 6 en `dev` y comenzar el branch de empaquetado.

---

## 2026-08-18 00:45 -0500 — Cierre de Fase 6 e inicio de Fase 7

**Hecho:**
- Ejecutado `best.pt` una sola vez sobre las 150 imágenes de test mediante el job `23325`.
- Auditados 150 registros por imagen, 150 mapas de probabilidad, nueve umbrales, ambas
  matrices y 15 paneles cualitativos.
- Registrada la evaluación final en MLflow y sincronizados base, artefactos y resultados
  al equipo local.
- Versionados métricas, conteos, métricas por imagen, curva descriptiva y ejemplos
  cualitativos para la presentación.
- Cerrada la Fase 6 y preparado el protocolo comparable de EfficientNet-B0 para Fase 7.

**Decisiones:**
- El resultado oficial usa umbral `0.5`; la curva de test no se utiliza para reajustarlo.
- Se reportan métricas agregadas y distribución por imagen porque el promedio oculta
  fallos severos como el caso mínimo de Dice `0.07747857191064318`.
- La presentación limita las conclusiones a Kvasir-SEG y no interpreta el estudio como
  validación clínica externa.

**Resultados:**
- Dice test `0.9183967352352693`, IoU `0.8491068445832013`, precisión
  `0.9237401535043426` y recall `0.913114779938238`.
- Mediana Dice por imagen `0.954879509971524`; máximo `0.9890401607948728`.
- Run MLflow final: `73876309ec7c45e09023574a02a47475`, estado `FINISHED`.

**Pendiente / carry-over:**
- Iniciar la comparación U-Net/ResNet-34 frente a U-Net/EfficientNet-B0 sin modificar
  el protocolo ni los resultados ya cerrados del baseline.

---

## 2026-08-18 00:36 -0500 — Fase 6: gates cerrados para evaluación de test

**Hecho:**
- Implementados paneles cualitativos deterministas para mejores, medianos y peores casos
  con imagen, máscara, probabilidad, predicción y overlay.
- Inspeccionada y corregida la compatibilidad de etiquetas de los paneles generados.
- Integrado un run MLflow separado para cada evaluación con tags de checkpoint, run de
  training, split, métricas y directorio completo de artefactos.
- Preparado el job definitivo que ejecuta el evaluador sin límites sobre test.

**Decisiones:**
- La evaluación final escribe bajo `evaluation/.../test` y se niega a comenzar si ese
  directorio ya existe, como protección contra repeticiones accidentales.
- El run de evaluación conserva un vínculo explícito al run que produjo `best.pt`.
- Las etiquetas raster usan caracteres compatibles con OpenCV para evitar texto ilegible.

**Resultados:**
- Job CPU `23321`: `COMPLETED`, 5/5 contratos cualitativos correctos.
- Jobs GPU `23322` y `23323`: paneles reales generados y verificados visualmente.
- Job GPU `23324`: `COMPLETED`, run MLflow
  `04ade91887f84f71a2b6004af1ca7f5c` con métricas y artefactos portables.

**Pendiente / carry-over:**
- Ejecutar ahora la evaluación única de las 150 imágenes de test.

---

## 2026-08-18 00:11 -0500 — Fase 6: smoke GPU del evaluador real

**Hecho:**
- Integrado un runner que conecta configuración, checkpoint verificado, DataLoader,
  inferencia y escritura de artefactos.
- Añadidas protecciones que prohíben test parcial y exigen límite de batches para un
  smoke sobre validation.
- Ejecutado el evaluador real con `best.pt`, AMP y dos batches de validation en A100.
- Verificados métricas, 16 registros por imagen, 16 mapas de probabilidad, nueve puntos
  de umbral y matrices cruda y normalizada.

**Decisiones:**
- La arquitectura se reconstruye sin volver a cargar pesos ImageNet; `best.pt` es la
  única fuente de pesos durante evaluación.
- Los resultados del smoke se separan por job bajo `evaluation/.../smoke/` y no se
  confunden con la evaluación final.
- Test no admite `--max-batches`; su futura ejecución debe cubrir las 150 muestras.

**Resultados:**
- Job `23320`: `COMPLETED`, código `0:0`, 19 segundos y 16 muestras de validation.
- Dice del smoke: `0.8990412835061632`; se reporta solo como evidencia técnica.

**Pendiente / carry-over:**
- Generar visualizaciones cualitativas y registrar la evaluación mediante MLflow antes
  de ejecutar test completo una sola vez.

---

## 2026-08-17 23:44 -0500 — Fase 6: motor y artefactos de evaluación

**Hecho:**
- Implementada una sola pasada de inferencia que calcula métricas micro agregadas y por
  imagen, además de conteos para múltiples umbrales.
- Conservados mapas de probabilidad comprimidos en `float16` y datos tabulares para
  métricas, curva de umbral y matrices de confusión.
- Implementada escritura atómica de JSON, CSV y NPZ, con validación de identificadores
  antes de construir rutas de artefactos.
- Añadidos contratos CPU con resultados exactos y persistencia reconstruible.

**Decisiones:**
- Las métricas agregadas se calculan desde la suma de TP, FP, FN y TN de todas las
  imágenes, no promediando métricas por batch.
- La matriz usa filas de clase real y columnas de predicción; se conserva en conteos y
  normalizada por clase real.
- Cada mapa de probabilidad se guarda por `sample_id` para permitir nuevos análisis sin
  repetir inferencia.

**Resultados:**
- Job `23318`: `COMPLETED`, código `0:0`, 3/3 contratos del motor correctos.
- Job `23319`: `COMPLETED`, código `0:0`, 4/4 contratos de motor y artefactos correctos.
- Ninguna imagen del split test fue consumida.

**Pendiente / carry-over:**
- Implementar visualizaciones cualitativas de mejores, medianos y peores casos.

---

## 2026-08-17 23:27 -0500 — Fase 6: carga verificada del checkpoint ganador

**Hecho:**
- Implementada una carga específica de evaluación que verifica el hash externo fijado,
  el sidecar y los metadatos de selección antes de restaurar pesos.
- Validada la coincidencia de run MLflow, época, métrica, mejor valor y marca `is_best`;
  el modelo queda en modo `eval()` tras una carga correcta.
- Ampliados los contratos CPU para cubrir carga válida y rechazo de hash o procedencia
  incorrectos.

**Decisiones:**
- La identidad del checkpoint no dependerá solo del sidecar copiado junto al archivo; el
  hash versionado en la configuración funciona como segunda fuente independiente.
- Ningún dato de test debe consumirse si la identidad o selección del checkpoint difiere
  del protocolo aprobado.

**Resultados:**
- Job `23317`: `COMPLETED`, código `0:0`, 12/12 pruebas y validación MLflow correctas.

**Pendiente / carry-over:**
- Implementar evaluación agregada y métricas por imagen sobre test.

---

## 2026-08-17 23:21 -0500 — Fase 6: protocolo de evaluación versionado

**Hecho:**
- Creada la configuración de evaluación final del U-Net/ResNet-34 con checkpoint, hash,
  run de origen, split, umbral, métricas y artefactos explícitos.
- Añadidos cuatro contratos locales que impiden usar `last.pt`, cambiar el umbral con
  test u omitir evidencia necesaria para reconstruir resultados.
- Incorporada la configuración a los índices y al validador local.

**Decisiones:**
- `best.pt` queda fijado por su SHA-256 y por el run de entrenamiento que lo produjo.
- La evaluación se registrará como un run MLflow separado enlazado al run de training.
- La curva de umbral sobre test será únicamente descriptiva; el umbral operativo `0.5`
  no cambiará después de observar test.
- Se conservarán mapas de probabilidad comprimidos en `float16`, métricas por imagen,
  matrices y casos cualitativos para permitir análisis posteriores sin repetir inferencia.

**Pendiente / carry-over:**
- Implementar carga verificada del checkpoint ganador.

---

## 2026-08-17 22:36 -0500 — Cierre de Fase 5 e inicio de Fase 6

**Hecho:**
- Sincronizados localmente `mlflow.db` y los artefactos de los runs smoke y full; los
  cuatro checkpoints pasaron su verificación SHA-256.
- Verificada la interfaz local MLflow y el acceso al run completo, métricas, historial,
  configuraciones y checkpoint ganador.
- Versionado el historial de 32 épocas y creado un generador de curvas SVG sin
  dependencias externas, además de exportaciones SVG editable y PNG de alta resolución.
- Incorporadas las curvas y su interpretación breve a la presentación.
- Cerrada la Fase 5 y preparado el tablero de evaluación, inferencia y análisis de errores
  de la Fase 6.

**Decisiones:**
- El CSV es la fuente canónica de las curvas; SVG y PNG son derivados regenerables.
- La línea de selección identifica la época 22 y evita confundir el último valor con el
  mejor Dice de validation.
- La Fase 6 evaluará una sola vez `best.pt` sobre test y conservará métricas por imagen,
  conteos, probabilidades y figuras auditables.

**Resultados:**
- Run completo accesible localmente: `5fdf1b9929ec443da426c6442d9e20f1`.
- Mejor Dice de validation: `0.8977634135250631` en la época 22.
- Curvas regeneradas de forma determinista desde el historial sincronizado.

**Pendiente / carry-over:**
- Iniciar la implementación de la evaluación sin consumir todavía el conjunto de test.

---

## 2026-08-17 22:27 -0500 — Fase 5: modelo seleccionado visible en MLflow

**Hecho:**
- Ampliada la guía general de MLflow con un patrón para mostrar directamente el mejor
  valor, paso, criterio, checkpoint y motivo de parada de cada run.
- Documentada la diferencia entre un checkpoint registrado como artefacto, un Logged
  Model con flavor y la promoción opcional mediante Model Registry.
- Añadidas medidas preventivas para evitar que el ganador quede oculto en una curva o
  aparezca únicamente como archivo genérico.

**Decisiones:**
- Los próximos proyectos registrarán tags `selection.*`, una métrica escalar final del
  mejor resultado y un resumen JSON portable.
- Checkpoint y MLflow Model se conservarán como productos complementarios: el primero
  para reanudación/auditoría y el segundo para carga estandarizada e inferencia.
- Test no participará en la selección ni en la promoción inicial del modelo.

**Pendiente / carry-over:**
- Aplicar este patrón en runners futuros; el run actual conserva correctamente su
  checkpoint ganador como artefacto.

---

## 2026-08-17 21:19 -0500 — Fase 5: entrenamiento completo del baseline

**Hecho:**
- Ejecutado el entrenamiento completo U-Net/ResNet-34 mediante el job `23312` en una
  A100; terminó correctamente en 32 épocas y 2.816 pasos.
- Verificados `best.pt`, `last.pt`, ambos sidecars SHA-256, el historial de 32 épocas y
  los artefactos del run MLflow `5fdf1b9929ec443da426c6442d9e20f1`.
- Añadido a `docs/presentacion.md` un resumen breve y explicativo del resultado.

**Decisiones:**
- Se conserva como modelo seleccionado `best.pt`, correspondiente a la época 22 y Dice
  de validation `0.8977634135250631`; `last.pt` no lo reemplaza.
- La parada en la época 32 se considera correcta porque fue activada por early stopping,
  no por error ni por límite de recursos.
- El resultado se presenta explícitamente como validation; test sigue aislado hasta la
  Fase 6 para evitar sesgo en la medición final.

**Pendiente / carry-over:**
- Sincronizar la base y los artefactos MLflow, verificar la interfaz local y preparar
  las curvas de entrenamiento y validation.

---

## 2026-08-17 20:45 -0500 — Fase 5: handoff de contexto antes de `/clear`

**Hecho:**
- Consolidado en `PHASE_CURRENT.md` el estado exacto de la fase, la última evidencia
  válida y la secuencia para reanudar sin depender del historial de conversación.
- Documentado el comando del próximo smoke integrado, el entorno Slurm requerido y las
  comprobaciones que deben cumplirse antes del entrenamiento completo.

**Decisiones:**
- La próxima sesión comenzará por el smoke del runner con dos batches de train y dos de
  validation en una A100.
- El entrenamiento completo no se enviará hasta verificar en el mismo smoke AMP, MLflow,
  historial, ambos checkpoints y sus hashes.
- `BACKLOG.md` no cambia: la Fase 5 continúa activa y es la única fase en progreso.

**Estado para reanudación:**
- Branch: `chore/training-mlflow`; repositorios local, GitHub y CEDIA sincronizados al
  preparar este handoff.
- Último resultado experimental: job CPU `23310`, 10/10 pruebas y MLflow correcto.
- Próxima tarea pendiente: smoke integrado de pocos batches en GPU.

---

## 2026-08-17 20:40 -0500 — Fase 5: contratos CPU integrales

**Hecho:**
- Añadidas diez pruebas unitarias para loops, acumulación de gradientes, checkpoints,
  RNG, tracking y utilidades del runner.
- Creado `slurm/test_training_cpu.sbatch` para ejecutar la suite sin GPU y continuar con
  una integración real de servidor y cliente MLflow.
- Verificados el contrato completo de métricas, el historial CSV atómico y los hashes
  efectivos del dataset.

**Decisiones:**
- Los contratos usan modelos escalares mínimos para probar la lógica sin construir el
  U-Net ni consumir GPU.
- La suite comprueba explícitamente que train actualiza parámetros y validation usa
  `eval()` sin modificarlos.
- La manipulación de un checkpoint debe detectarse mediante SHA-256 antes de intentar
  cargar su contenido.
- La restauración de RNG cubre Python, NumPy y PyTorch CPU; CUDA se comprobará dentro
  del smoke GPU integrado.

**Resultados:**
- Job `23310`: `COMPLETED`, código `0:0`, 33 segundos en `cpu-dev`.
- Diez de diez pruebas correctas en PyTorch 2.10.0+cu128.
- La validación MLflow posterior creó SQLite, registró el run y confirmó una URI
  `mlflow-artifacts:/` portable.

**Pendiente / carry-over:**
- Ejecutar el runner completo con pocos batches en una A100 antes del entrenamiento de
  hasta 50 épocas.

---

## 2026-08-17 20:30 -0500 — Fase 5: runner integrado con MLflow

**Hecho:**
- Implementado el runner que construye datos, modelo, pérdida, AdamW, scheduler, AMP y
  ejecuta train/validation con early stopping y checkpoints.
- Implementado un servidor MLflow administrado por el proceso de entrenamiento y un
  tracker que aplica el contrato de parámetros, tags, métricas y artefactos.
- Añadido `scripts/train.py` como CLI para entrenamiento completo y smokes limitados.
- Registrados configuración, hashes, entorno, `pip freeze`, historial por época,
  checkpoints y resumen final de cada run.
- Refactorizada y ejecutada la validación MLflow usando los componentes reales.

**Decisiones:**
- El servidor escucha solo en `127.0.0.1` y usa un worker para mantener un único flujo
  de escritura sobre SQLite.
- Cada run nuevo recibe un subdirectorio de checkpoints basado en su UUID de MLflow para
  evitar sobrescrituras; una reanudación conserva el run y directorio originales.
- Los registros por época son síncronos y deben coincidir exactamente con el contrato
  de métricas versionado.
- `run_mode=smoke` distingue cualquier ejecución limitada por batches; el entrenamiento
  completo omite ambos límites.
- Test no se construye ni evalúa dentro del runner de la Fase 5.

**Resultados:**
- Job `23309`: `COMPLETED`, código `0:0`, 44 segundos en `cpu-dev`.
- Servidor, SQLite, parámetros, métrica, historial y resumen persistidos con URI
  `mlflow-artifacts:/`; el CLI real cargó correctamente.

**Pendiente / carry-over:**
- Añadir pruebas CPU integrales de loops, checkpoints, tracking y utilidades del runner.

---

## 2026-08-17 20:18 -0500 — Fase 5: checkpoints auditables y reanudables

**Hecho:**
- Implementado guardado atómico de `last.pt` en cada época y `best.pt` únicamente ante
  mejora suficiente de la métrica de selección.
- Añadidos sidecars `.sha256` y verificación de integridad previa a toda carga.
- Conservados estados de modelo, optimizador, scheduler, GradScaler y generadores
  aleatorios, además de métricas, configuración, versiones y procedencia.
- Implementada restauración segura mediante `torch.load(..., weights_only=True)`.
- Ampliado y ejecutado el smoke CPU para cubrir guardado, selección, hash y carga.

**Decisiones:**
- `last.pt` permite continuar desde `next_epoch`; `best.pt` representa exclusivamente el
  mayor Dice de validation según `min_delta` y nunca se selecciona con test.
- Los temporales se crean en el mismo directorio y se reemplazan atómicamente para no
  exponer un checkpoint parcialmente escrito si el job se interrumpe.
- Cada checkpoint incluye schema y tipo explícitos; la carga rechaza otros formatos o
  versiones antes de restaurar estados.
- Los RNG de Python, NumPy, CPU y CUDA se almacenan con tipos compatibles con la carga
  restringida de PyTorch.

**Resultados:**
- Job `23308`: `COMPLETED`, código `0:0`, diez segundos y `status=ok` en CPU.
- La primera época creó `best.pt`; una segunda métrica inferior no lo reemplazó y su
  SHA-256 permaneció intacto.
- La carga restauró los pesos guardados y confirmó `next_epoch=2`.

**Pendiente / carry-over:**
- Integrar configuración, métricas y artefactos del entrenamiento con MLflow.

---

## 2026-08-17 20:01 -0500 — Fase 5: loops de train y validation

**Hecho:**
- Implementados `train_one_epoch` y `validate_one_epoch` como motor reutilizable de
  segmentación binaria.
- Añadidos AMP, gradient scaling, acumulación de gradientes, clipping, límite opcional
  de batches y transferencia no bloqueante hacia CUDA.
- Agregadas pérdida, Dice, IoU, precision, recall y TP/FP/FN/TN sobre cada época.
- Creado y ejecutado un smoke contractual mediante `cpu-dev` con un modelo diminuto.

**Decisiones:**
- La pérdida se promedia ponderando cada batch por su número de muestras; las métricas
  se calculan desde conteos de píxeles acumulados, no promediando métricas por batch.
- La última agrupación incompleta de gradient accumulation usa su tamaño real para no
  reducir artificialmente su contribución.
- Validation usa `torch.inference_mode()`, activa `eval()` y nunca recibe optimizador.
- Los loops rechazan logits o pérdidas no finitos antes de continuar el entrenamiento.

**Resultados:**
- Job `23307`: `COMPLETED`, código `0:0`, nueve segundos y `status=ok` en CPU.
- Train modificó los parámetros; validation los conservó; se procesaron 12 píxeles y
  la pérdida ponderada coincidió con el valor esperado.

**Pendiente / carry-over:**
- Implementar `last.pt` y `best.pt` con estado y metadatos suficientes para reanudar y
  auditar el entrenamiento.

---

## 2026-08-17 19:31 -0500 — Fase 5: protocolo de entrenamiento versionado

**Hecho:**
- Creada `configs/training/unet-resnet34-baseline.yaml` con referencias a datos, modelo
  y tracking, además de runtime, optimizador, scheduler y checkpoints.
- Añadidos cinco contratos locales para validar referencias, presupuesto, selección y
  aislamiento de test sin importar PyTorch.
- Incorporada la nueva prueba al validador local y actualizados los índices de
  configuraciones y pruebas.

**Decisiones:**
- El baseline tendrá un máximo de 50 épocas con semilla `20260817`, AdamW con learning
  rate `1e-4` y weight decay `1e-4`.
- ReduceLROnPlateau reducirá el learning rate a la mitad después de tres épocas sin una
  mejora absoluta de `1e-4` en Dice de validation, con mínimo `1e-6`.
- Early stopping esperará diez épocas sin mejora para permitir reducciones del learning
  rate antes de detener el entrenamiento.
- La A100 usará AMP `float16` con gradient scaling y determinismo estricto; el mejor
  checkpoint se seleccionará únicamente por `val_dice`.
- Test queda deshabilitado declarativamente y reservado para la Fase 6.

**Pendiente / carry-over:**
- Implementar los loops de train y validation con agregación correcta por época.

---

## 2026-08-17 19:26 -0500 — Fase 5: MLflow instalado y validado en CEDIA

**Hecho:**
- Fijado `mlflow==3.15.1`, compatible con Python 3.11, en las dependencias del proyecto.
- Incorporados TP, FP, FN y TN de train y validation al contrato de métricas por época.
- Añadidos un smoke servidor-cliente efímero y su job Slurm para `cpu-dev`.
- Actualizado `.venv-cluster` mediante el job `23305` y ejecutado el smoke funcional
  mediante el job `23306`.
- Documentada en la guía general la estrategia reproducible de instalación en clústeres
  con módulos, virtualenv y Slurm.

**Decisiones:**
- La versión de MLflow se fija exactamente y se instala desde el proyecto, no mediante
  una modificación manual sin trazabilidad.
- El nodo de login se limita a sincronización, envío y consulta; instalación, imports y
  validación se ejecutan en nodos de cómputo CPU.
- El virtualenv reutiliza PyTorch del módulo del clúster y prioriza sus propios paquetes
  fijados mediante `PYTHONPATH`.
- La validación usa almacenamiento temporal para no crear runs ni artefactos en el
  experimento real.

**Resultados:**
- Job `23305`: `COMPLETED`, código `0:0`; Python 3.11.14, MLflow 3.15.1 y `pip check`
  sin conflictos.
- Job `23306`: `COMPLETED`, código `0:0`; servidor, SQLite, métrica y artefacto
  persistidos y URI `mlflow-artifacts:/` confirmada.

**Pendiente / carry-over:**
- Crear la configuración versionada del entrenamiento baseline.

---

## 2026-08-17 19:00 -0500 — Fase 5: separación de guías MLflow

**Hecho:**
- Eliminadas de `docs/mlflow-guide.md` las rutas, nombres y decisiones específicas de
  PolySight Seg.
- Añadido un ejemplo neutral de servidor y cliente MLflow con almacenamiento portable.
- Versionada `docs/mlflow-project-guide.md` como guía exclusiva de este proyecto.
- Añadido a la guía del proyecto el contrato de matrices, conteos, probabilidades y
  figuras regenerables para el checkpoint seleccionado.
- Actualizado el índice de documentación para enlazar ambas guías por separado.

**Decisiones:**
- La guía general contiene patrones reutilizables y no menciona infraestructura,
  datasets, modelos ni rutas de un proyecto concreto.
- La guía de proyecto es la fuente para CEDIA, U-Net/ResNet-34, splits, checkpoints y
  comandos de sincronización de PolySight Seg.

**Pendiente / carry-over:**
- Incorporar TP, FP, FN y TN a `configs/tracking/mlflow.yaml`.
- Fijar la dependencia de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:51 -0500 — Fase 5: referencia reutilizable de MLflow y matrices

**Hecho:**
- Ampliada `docs/mlflow-guide.md` como referencia general para futuros experimentos.
- Documentados datos fuente, matrices crudas/normalizadas, métricas por muestra,
  probabilidades, umbrales y formatos editables de figuras.
- Añadida una tabla de problemas frecuentes y medidas preventivas basada en incidentes
  experimentales ya observados.

**Decisiones:**
- Los conteos y archivos tabulares son la fuente canónica; las figuras son derivados
  regenerables y nunca la única evidencia.
- Ante desbalance, la vista principal de la matriz se normaliza por clase real y se
  acompaña siempre por conteos absolutos y métricas apropiadas al problema.
- SVG/PDF editables y PNG de alta resolución se generan desde una configuración visual
  versionada con contraste y layout adaptativos.
- Para cambiar umbrales sin repetir inferencia deben conservarse probabilidades o logits
  del checkpoint seleccionado, además del umbral aplicado.

**Pendiente / carry-over:**
- Incorporar TP, FP, FN y TN al contrato de tracking del entrenamiento actual.
- Fijar la dependencia de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:16 -0500 — Fase 5: diseño de tracking con MLflow

**Hecho:**
- Creada `configs/tracking/mlflow.yaml` con servidor, experimento, métricas, artefactos
  y archivos que deben sincronizarse.
- Adaptada `docs/mlflow-guide.md` al flujo real entre Slurm, CEDIA y el equipo local.
- Excluidos `mlflow.db` y sus archivos auxiliares de Git.
- Añadidos enlaces y referencias a la configuración y guía de tracking.

**Decisiones:**
- Cada job de entrenamiento usará un servidor MLflow en `127.0.0.1:5000` con backend
  SQLite y proxy hacia `./artifacts`.
- El proxy conserva URIs `mlflow-artifacts:/` que pueden resolverse después de copiar
  `mlflow.db` y `artifacts/` al equipo local.
- SQLite tendrá un solo escritor; no se ejecutarán entrenamientos concurrentes contra
  la misma base ni se copiará la base mientras el servidor esté activo.
- Test permanece fuera del tracking de esta fase para no contaminar la selección del
  mejor checkpoint por Dice de validation.

**Pendiente / carry-over:**
- Fijar una versión compatible de MLflow y validar `.venv-cluster` en CEDIA.

---

## 2026-08-17 18:10 -0500 — Cierre de Fase 4 e inicio de Fase 5

**Hecho:**
- Completadas todas las tareas del baseline U-Net/ResNet-34.
- Marcada la Fase 4 como completada y activada la Fase 5 en el backlog.
- Preparada la Fase 5 con tareas de entrenamiento, checkpoints, MLflow, pruebas y
  ejecución completa en CEDIA.

**Decisiones:**
- MLflow se integrará antes del primer entrenamiento real para evitar migraciones o
  historiales parciales.
- Dice de validation seleccionará `best.pt`; test continuará aislado hasta la Fase 6.
- Los hiperparámetros de entrenamiento se fijarán de forma declarativa antes del run.

**Resultados de cierre:**
- Dataset y splits reproducibles, entorno CEDIA validado y contratos CPU correctos.
- Baseline de 24.436.369 parámetros con forward/backward real exitoso en A100.
- Pérdida, métricas, documentación y material de presentación completados.

**Pendiente / carry-over:**
- Iniciar el branch de Fase 5 y adaptar MLflow al repositorio antes de entrenar.

---

## 2026-08-17 18:09 -0500 — Fase 4: baseline documentado para exposición

**Hecho:**
- Añadida a `docs/presentacion.md` la explicación del encoder, decoder, conexiones de
  salto, logits y flujo de postprocesamiento.
- Documentados parámetros, pérdida, métricas y evidencia del smoke GPU real.
- Añadidas respuestas breves sobre U-Net, ResNet-34, pesos ImageNet y la interpretación
  correcta de las métricas previas al entrenamiento.

**Decisiones:**
- La presentación distingue explícitamente preparación técnica de rendimiento
  experimental para no presentar el smoke como resultado de entrenamiento.
- Se informa el pico observado de aproximadamente 908 MiB solo como referencia del
  batch diagnóstico, no como estimación definitiva del entrenamiento completo.

**Pendiente / carry-over:**
- Cerrar la Fase 4 e iniciar la Fase 5 de entrenamiento reproducible con MLflow.

---

## 2026-08-17 18:03 -0500 — Fase 4: smoke GPU del baseline real

**Hecho:**
- Añadidos `scripts/smoke_baseline.py` y `slurm/smoke_baseline.sbatch`.
- Ejecutado un batch real de train con U-Net/ResNet-34, pesos ImageNet, pérdida,
  métricas y backward en una A100-SXM4-40GB.
- Verificados forma de logits, valores finitos, gradientes, parámetros y memoria GPU.
- Registrados tamaño y SHA-256 del checkpoint ResNet-34 descargado.

**Decisiones:**
- El smoke usa el batch configurado de ocho muestras y no realiza un paso de optimizador;
  valida el grafo completo sin constituir entrenamiento.
- Las métricas del batch no entrenado se conservan como evidencia técnica, no como
  estimación de calidad ni resultado experimental.
- La instrumentación de memoria usa el dispositivo CUDA actual sin argumento para ser
  compatible con la versión efectiva de PyTorch instalada por CEDIA.

**Resultados:**
- Job `23304`: `COMPLETED`, código `0:0`, 27 segundos y `status=ok`.
- 24.436.369 parámetros entrenables; pico GPU 951.611.392 bytes; pérdida 1.3424215.
- Salida `[8,1,256,256]` para entrada `[8,3,256,256]`.
- Pesos ImageNet: 87.306.240 bytes, SHA-256
  `333f7ec4c6338da2cbed37f1fc0445f9624f1355633fa1d7eab79a91084c6cef`.

**Incidencia resuelta:**
- El job `23302` falló antes de construir el modelo porque PyTorch rechazó un objeto
  `torch.device` en `reset_peak_memory_stats`; se corrigió sin cambiar el cálculo.

**Pendiente / carry-over:**
- Documentar arquitectura, parámetros, resultados y preguntas para la presentación.

---

## 2026-08-17 17:44 -0500 — Fase 4: contratos CPU del baseline validados

**Hecho:**
- Añadidas cinco pruebas numéricas para modelo, pérdida y métricas.
- Separado el descubrimiento de pruebas locales ligeras de las pruebas que importan
  PyTorch en CEDIA.
- Añadido y ejecutado `slurm/test_baseline_cpu.sbatch` en `cpu-dev` como job `23300`.

**Decisiones:**
- La prueba de forma construye U-Net sin descargar pesos ImageNet; conserva y comprueba
  que la configuración real declara `imagenet`.
- Los contratos PyTorch se ejecutan en CPU y verifican que el job no reciba GPU.
- Se prueban backward finito, preferencia de pérdida, matriz de confusión conocida,
  métricas perfectas, reset y rechazo de formas incompatibles.

**Resultados:**
- Job `23300`: `COMPLETED`, código `0:0`, 15 segundos y cinco pruebas correctas.
- Dispositivo contractual: CPU; versión efectiva PyTorch 2.10.0+cu128.
- Las advertencias de deprecación de `torch.jit.script` proceden de dependencias de
  `segmentation_models_pytorch` y no afectaron los contratos.

**Pendiente / carry-over:**
- Preparar y ejecutar el smoke forward/backward del baseline con pesos ImageNet en GPU.

---

## 2026-08-17 17:26 -0500 — Fase 4: métricas binarias por píxel

**Hecho:**
- Implementado `BinarySegmentationMetrics` con acumulación de TP, FP, FN y TN.
- Implementados Dice, IoU, precisión y recall a partir de la matriz de confusión.
- Conectado el umbral inicial 0.5 desde la configuración versionada del baseline.
- Ejecutadas correctamente las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- Las métricas se calculan como agregación micro sobre todos los píxeles del split,
  evitando promediar batches con distinto número de muestras.
- Una unión vacía produce Dice/IoU 1.0; precision o recall sin denominador producen
  0.0. Kvasir-SEG no contiene máscaras reales vacías, pero el caso queda definido.
- Se conservan los conteos crudos para auditoría y para una matriz de confusión por
  píxel; Dice de validation continúa como criterio principal de selección.

**Pendiente / carry-over:**
- Añadir pruebas numéricas de contratos para modelo, pérdida y métricas sin GPU.

---

## 2026-08-17 17:03 -0500 — Fase 4: pérdida BCE + Dice implementada

**Hecho:**
- Implementadas `DiceLoss`, `BCEDiceLoss` y la factoría `build_loss`.
- Añadidos al YAML los pesos de BCE/Dice y el suavizado numérico.
- Validados sintaxis, configuración y las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- BCE y Dice se suman con pesos iniciales 1.0 y 1.0 para conservar una referencia
  simple y explícita antes de cualquier ajuste experimental.
- Dice aplica sigmoid a los logits, reduce por muestra sobre canal y espacio y luego
  promedia el batch.
- Se usa `smooth=1e-7` para evitar división por cero sin alterar materialmente el valor.
- Las formas de logits y targets deben coincidir; los targets se convierten al dtype de
  los logits antes del cálculo.

**Pendiente / carry-over:**
- Implementar Dice, IoU, precision y recall por píxel.
- Validar numéricamente pérdida y gradientes en las pruebas de contratos sin GPU.

---

## 2026-08-17 16:49 -0500 — Fase 4: pérdidas explicadas para la presentación

**Hecho:**
- Añadida a `docs/presentacion.md` una explicación breve de BCEWithLogitsLoss,
  Dice loss y el motivo de combinarlas.

**Decisiones:**
- La explicación diferencia clasificación por píxel y superposición global, vinculando
  Dice con el desbalance observado entre fondo y pólipo.
- No se documentan todavía pesos ni detalles numéricos: se fijarán al implementar y
  validar la pérdida.

**Pendiente / carry-over:**
- Implementar la pérdida combinada BCEWithLogits + Dice.

---

## 2026-08-17 15:37 -0500 — Fase 4: factoría del modelo

**Hecho:**
- Creado el paquete `polysight_seg.models` con carga de configuración y factoría.
- Implementada la construcción de `segmentation_models_pytorch.Unet` desde el YAML.
- Verificado localmente que cargar la configuración no importa PyTorch.
- Ejecutadas correctamente las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- La factoría solo acepta el contrato aprobado: U-Net, entrada RGB, una clase de salida
  y ausencia de activación interna.
- El import de `segmentation_models_pytorch` es diferido para mantener separadas las
  validaciones locales ligeras de la ejecución PyTorch en CEDIA.
- La descarga y construcción efectiva de los pesos ImageNet se comprobarán en el smoke
  forward/backward del baseline, no en el equipo local.

**Pendiente / carry-over:**
- Implementar la pérdida combinada BCEWithLogits + Dice.

---

## 2026-08-17 14:44 -0500 — Fase 4: configuración del baseline

**Hecho:**
- Creada `configs/models/unet-resnet34.yaml` como configuración canónica del modelo.
- Documentada la relación entre la configuración del modelo y la de Kvasir-SEG.
- Validado el YAML y ejecutadas las nueve comprobaciones locales sin PyTorch.

**Decisiones:**
- El baseline usa `segmentation_models_pytorch.Unet`, encoder ResNet-34 y pesos ImageNet.
- La red recibe tres canales y devuelve un canal de logits; no incorpora sigmoid para
  mantener compatibilidad numérica con BCEWithLogitsLoss.
- El umbral inicial 0.5 se aplica fuera del modelo y solo podrá ajustarse con validation.
- Los hiperparámetros de entrenamiento se mantienen fuera de esta configuración hasta
  la fase correspondiente.

**Pendiente / carry-over:**
- Implementar la factoría del modelo desde la configuración versionada.

---

## 2026-08-17 14:41 -0500 — Fase 4: evidencia CEDIA para la presentación

**Hecho:**
- Añadida a `docs/presentacion.md` una síntesis de entorno, GPU, datos y pipeline
  verificados mediante Slurm.
- Aclarado que los smoke tests validan preparación técnica, no calidad del modelo ni
  resultados de entrenamiento.

**Decisiones:**
- Se priorizan cifras breves y defendibles durante la exposición, junto con una respuesta
  directa sobre el uso obligatorio de Slurm para acceder a nodos de cómputo.

**Pendiente / carry-over:**
- Crear la configuración versionada del baseline U-Net/ResNet-34.

---

## 2026-08-17 14:30 -0500 — Fase 4: smoke tests GPU y datos completados

**Hecho:**
- Añadido un job `cpu-dev` para reconstruir y validar dataset, manifest y splits desde
  el ZIP original almacenado fuera de Git.
- Corregidos los jobs smoke para priorizar las dependencias fijadas del virtualenv sin
  ocultar el PyTorch suministrado por el módulo de CEDIA.
- Ejecutado el smoke GPU `23294` con una A100-SXM4-40GB y forward/backward real.
- Reproducidos los datos mediante el job `23295` y ejecutado el smoke del pipeline
  `23296` para train, validation y test.

**Decisiones:**
- La combinación efectiva PyTorch 2.10.0+cu128, driver 535.161.08 y A100 se acepta porque
  el smoke GPU verificó CUDA, cuDNN, asignación de dispositivo y cálculo real.
- `pin_memory=true` se mantiene para entrenamiento GPU; su advertencia en el smoke CPU
  es esperada y no representa un fallo del pipeline.
- No se actualiza Albumentations desde 1.4.24: la versión directa permanece fijada para
  conservar reproducibilidad aunque la librería anuncie una versión posterior.

**Resultados:**
- Job `23294`: `COMPLETED`, 9 s, A100-SXM4-40GB, `status=ok`, pérdida
  0.2901759743690491, PyTorch 2.10.0+cu128 y cuDNN 91002.
- Job `23295`: `COMPLETED`, 21 s, 1.000 pares y splits 700/150/150.
- Job `23296`: `COMPLETED`, 9 s, batches `[8,3,256,256]` y máscaras
  `[8,1,256,256]` para los tres splits.
- SHA-256 reproducidos: manifest `35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4`
  y splits `85fe68a5b241f880a80d1476fdffcff88ae5b5e51c0adbe690cce023cbfe13f9`.

**Pendiente / carry-over:**
- Crear la configuración versionada del baseline U-Net/ResNet-34.

---

## 2026-08-17 13:48 -0500 — Fase 4: entorno Python preparado mediante Slurm

**Hecho:**
- Añadido `slurm/setup_cluster_env.sbatch` para crear y auditar `.venv-cluster` desde
  un nodo `cpu-dev`, sin ejecutar cargas de cómputo en `login1`.
- Corregida la precedencia de paquetes entre el virtualenv y el `PYTHONPATH` del módulo.
- Ejecutado el job `23287` desde el commit `956b3583f093978d81a8b1a66e14dae7b4de2009`.
- Confirmados `pip check` sin errores, estado `COMPLETED`, salida `0:0` y working tree
  limpio en CEDIA.

**Decisiones:**
- Python se mantiene en 3.11; no fue la causa de los intentos fallidos de preparación.
- PyTorch debe proceder del módulo de CEDIA y no descargarse dentro del virtualenv.
- El `site-packages` del virtualenv precede al `PYTHONPATH` del módulo para respetar
  NumPy 1.26.4, Pillow 10.4.0 y las demás versiones directas fijadas.
- La compatibilidad de Torch 2.10.0+cu128 con el driver y la A100 se validará mediante
  Slurm; el nombre `pytorch/2.2` del módulo no coincide con su contenido efectivo.

**Resultados:**
- Python 3.11.14, PyTorch 2.10.0+cu128, CUDA build 12.8, cuDNN 91002,
  torchvision 0.25.0 y pip 26.2.1.
- Job `23287`: 47 segundos, `cpu-dev`, 4 CPU, 8 GB solicitados y 128868K MaxRSS.

**Pendiente / carry-over:**
- Ejecutar los smoke tests GPU y del pipeline de datos en CEDIA.
- Confirmar con el smoke GPU la compatibilidad efectiva entre Torch, driver y A100.

---

## 2026-08-17 12:51 -0500 — Fase 4: sincronización inicial en CEDIA

**Hecho:**
- Clonada la rama `chore/baseline-unet-resnet34` en
  `$HOME/projects/polysight-seg` en CEDIA.
- Transferido el ZIP original de Kvasir-SEG a `$HOME/datasets` mediante `rsync`.
- Verificados en CEDIA el commit, el working tree limpio, el tamaño y el SHA-256 del ZIP.

**Decisiones:**
- Se conserva el ZIP original fuera de Git y se reconstruirán los datos derivados con
  los scripts versionados después de preparar `.venv-cluster`.
- Se ejecuta la fase desde su branch dedicado y el commit aprobado
  `136d0310ee9faf43f95485f1f274881cade8e874`.

**Pendiente / carry-over:**
- Preparar `.venv-cluster` y registrar las versiones efectivas de dependencias.
- Reproducir los artefactos del dataset y ejecutar los smoke tests en CEDIA.

---

## 2026-08-17 12:46 -0500 — Cierre de sesión: publicación y preparación de Fase 4

**Hecho:**
- Cerrada la Fase 3 e integrada en `dev` con working tree limpio.
- Creado el repositorio público `christianbueno1/polysight-seg` mediante `gh` CLI.
- Publicadas las ramas `dev` y `chore/baseline-unet-resnet34`.
- Verificado acceso al nodo `login1` de CEDIA y disponibilidad de Python 3.11,
  PyTorch 2.2, CUDA 12.4, particiones CPU/GPU y GPUs A100.
- Preparada la Fase 4 con tareas para el baseline U-Net/ResNet-34.

**Decisiones:**
- `dev` es la rama predeterminada remota hasta que exista una release estable en `main`.
- El repositorio es público; datasets y artefactos continúan excluidos mediante
  `.gitignore`.
- Se usará `ssh -F ~/.ssh/config cedia` hasta corregir los permisos de la configuración
  SSH global local.

**Pendiente / carry-over:**
- Transferir el ZIP y reproducir dataset/manifests/splits en CEDIA.
- Ejecutar los smoke tests GPU y del pipeline de datos.
- Implementar y validar el baseline U-Net/ResNet-34.

---

## 2026-08-17 12:39 -0500 — Fase 3: Splits y pipeline de datos completados

**Hecho:**
- Confirmado que los folds oficiales corresponden al conjunto de clasificación y no a
  un protocolo train/validation/test específico de Kvasir-SEG.
- Generados splits deterministas 700/150/150 con semilla `20260817`.
- Estratificadas las muestras por tamaño pequeño, mediano y grande del pólipo.
- Validadas cobertura total, exclusividad, conteos y protección de grupos duplicados.
- Implementados configuración, Dataset, DataLoader y transformaciones sincronizadas.
- Preparado un smoke test Slurm del pipeline para `cpu-dev` en CEDIA.
- Añadidas pruebas locales y documentación técnica y de presentación.

**Decisiones:**
- Validation y test permanecen deterministas; solo train recibe augmentations aleatorias.
- Las entradas se redimensionan a 256 × 256 con bilinear para imágenes y nearest-neighbor
  para máscaras.
- Test queda aislado de toda selección de umbral, modelo e hiperparámetros.
- No puede garantizarse separación por paciente por falta de identificadores clínicos.

**Resultados:**
- Asignaciones SHA-256:
  `2d0f1f88380314f7d633b1d84b8f6d0e662eb98ff803b25140e8b48c305f7e34`.
- Splits CSV SHA-256:
  `85fe68a5b241f880a80d1476fdffcff88ae5b5e51c0adbe690cce023cbfe13f9`.
- Nueve pruebas locales finalizaron correctamente sin PyTorch.

**Pendiente / carry-over:**
- Ejecutar el smoke test del pipeline en CEDIA.
- Implementar el baseline U-Net con encoder ResNet-34 en la Fase 4.
- Crear el repositorio remoto cuando `gh` tenga una sesión autenticada válida.

---

## 2026-08-17 11:58 -0500 — Fase 2: Kvasir-SEG preparado y validado

**Hecho:**
- Registrados tamaño, SHA-256, procedencia oficial y condiciones de uso del ZIP.
- Implementada y ejecutada una extracción segura, atómica e idempotente.
- Validados los 1.000 pares, bounding boxes, UUID, JPEG y dimensiones.
- Definida la binarización reproducible de máscaras JPEG con umbral 128.
- Generado un manifest determinista con hashes, dimensiones y fracción de pólipo.
- Confirmada la ausencia de duplicados binarios exactos dentro del subconjunto.
- Añadidas pruebas ligeras y documentación para reproducir los datos en CEDIA.
- Creado material explicativo de binarización en `docs/presentacion.md`.

**Decisiones:**
- Los archivos originales permanecen inmutables y excluidos de Git.
- La binarización usa `valor >= 128` como pólipo y no materializa nuevas máscaras.
- Los bounding boxes usan límites máximos exclusivos.
- Los splits se construirán desde el manifest durante la Fase 3.

**Resultados:**
- Fuente SHA-256: `4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a`.
- Manifest SHA-256: `35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4`.
- 1.000 pares válidos, 0 corruptos y 0 grupos duplicados exactos.
- Las siete pruebas locales finalizaron correctamente sin PyTorch.

**Pendiente / carry-over:**
- Transferir el ZIP a CEDIA y comprobar allí los hashes reproducibles.
- Crear splits deterministas y el pipeline de datos en la Fase 3.

---

## 2026-08-17 11:19 -0500 — Fase 1: Base reproducible completada

**Hecho:**
- Fijados Python 3.11 y ocho dependencias directas para el entorno de CEDIA.
- Creada la estructura de código, configuraciones, scripts, Slurm y pruebas.
- Preparado un smoke test GPU con forward/backward real para PyTorch y CUDA.
- Añadidas cuatro pruebas y un comando de validación local sin PyTorch.
- Documentada la preparación, comprobación y evidencia requerida en CEDIA.
- Validada la estructura completa sin instalar dependencias de entrenamiento localmente.

**Decisiones:**
- PyTorch será suministrado por el módulo `pytorch/2.2` de CEDIA, no por una descarga
  local ni como dependencia directa del proyecto.
- El entorno local puede usar un Python posterior para comprobaciones ligeras, mientras
  el entorno ejecutable del proyecto permanece restringido a Python 3.11.
- Dataset, checkpoints, resultados, entornos virtuales y logs Slurm quedan fuera de Git.

**Pendiente / carry-over:**
- Ejecutar `slurm/smoke_gpu.sbatch` en CEDIA y conservar su evidencia.
- Incorporar y validar el archivo local de Kvasir-SEG durante la Fase 2.

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
