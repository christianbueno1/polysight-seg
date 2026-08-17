# PHASE_CURRENT

## Fase 3 — Splits reproducibles y pipeline de datos

**Objetivo:** Crear particiones deterministas de train, validation y test, y preparar un
pipeline de carga y transformaciones sincronizadas para ejecutarse con PyTorch en CEDIA.

**Contexto:** La Fase 2 produjo un manifest validado de 1.000 pares bajo
`data/processed/kvasir-seg/manifest.csv`. Ver `docs/dataset-validation-report.md`.

---

### Tareas

- [~] Verificar si existe un split oficial aplicable específicamente a Kvasir-SEG
- [ ] Definir semilla, proporciones, estratos de tamaño y reglas contra leakage
- [ ] Implementar generación determinista de splits desde el manifest
- [ ] Validar conteos, exclusividad, cobertura y distribución de los splits
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
