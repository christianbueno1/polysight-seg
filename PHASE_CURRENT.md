# PHASE_CURRENT

## Fase 3 — Splits reproducibles y pipeline de datos

**Objetivo:** Crear particiones deterministas de train, validation y test, y preparar un
pipeline de carga y transformaciones sincronizadas para ejecutarse con PyTorch en CEDIA.

**Contexto:** La Fase 2 produjo un manifest validado de 1.000 pares bajo
`data/processed/kvasir-seg/manifest.csv`. Ver `docs/dataset-validation-report.md`.

---

### Tareas

- [x] Verificar si existe un split oficial aplicable específicamente a Kvasir-SEG
- [x] Definir semilla, proporciones, estratos de tamaño y reglas contra leakage
- [x] Implementar generación determinista de splits desde el manifest
- [x] Validar conteos, exclusividad, cobertura y distribución de los splits
- [ ] Definir configuración versionada de datos y transformaciones
- [ ] Implementar Dataset y DataLoader de segmentación para CEDIA
- [ ] Implementar transformaciones sincronizadas de imagen y máscara
- [ ] Añadir pruebas locales para la lógica independiente de PyTorch
- [ ] Preparar un smoke test del pipeline de datos para Slurm
- [ ] Documentar y registrar los resultados reproducibles de la fase

---

### Notas y decisiones

- Test permanecerá aislado y no se usará para elegir umbral, transformaciones ni
  hiperparámetros.
- Los grupos de duplicados, si aparecen en futuras versiones del manifest, deberán
  permanecer completos dentro de un único split.
- El split se generará localmente sin PyTorch; Dataset, DataLoader y augmentations se
  ejecutarán y validarán en CEDIA.
- Los folds oficiales cubren los 10.662 ejemplos etiquetados de clasificación y no
  constituyen un split train/validation/test específico para Kvasir-SEG.
- Se adopta una partición 70/15/15 con semilla `20260817` y estratificación determinista
  por tamaño relativo del pólipo.
- La falta de identificadores de paciente o procedimiento impide garantizar separación
  clínica y se documentará como limitación del estudio.
- La creación y publicación del repositorio en GitHub mediante `gh` CLI se realizará en
  una fase posterior; no forma parte del pipeline de datos actual.
- La asignación ordena los grupos mediante SHA-256 de semilla e identificador, por lo
  que no depende del orden de las filas del manifest.
- La validación exige cobertura de los 1.000 UUID, conteos 700/150/150, los tres estratos
  en cada split y ausencia de grupos duplicados repartidos entre particiones.
