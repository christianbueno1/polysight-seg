# PHASE_CURRENT

## Fase 6 — Evaluación, inferencia y análisis de errores del baseline

**Objetivo:** Evaluar una sola vez el checkpoint seleccionado U-Net/ResNet-34 sobre test,
conservar resultados reproducibles por imagen y analizar de forma cuantitativa y visual
los aciertos y errores del baseline.

**Contexto:** La Fase 5 seleccionó `best.pt` exclusivamente mediante Dice de validation.
El checkpoint ganador corresponde a la época 22 con Dice de validation `0.8977634135250631`
y run MLflow `5fdf1b9929ec443da426c6442d9e20f1`. Test ha permanecido aislado.

---

### Tareas

- [x] Crear una configuración versionada de evaluación e inferencia
- [x] Implementar carga verificada del checkpoint ganador
- [ ] Implementar evaluación agregada y métricas por imagen sobre test
- [ ] Conservar conteos, probabilidades y curva de umbral como datos regenerables
- [ ] Generar matrices de confusión cruda y normalizada por clase real
- [ ] Implementar inferencia y visualizaciones cualitativas de mejores y peores casos
- [ ] Añadir pruebas CPU para contratos de evaluación y artefactos
- [ ] Ejecutar un smoke GPU de evaluación sin consumir test completo
- [ ] Ejecutar una sola evaluación completa del checkpoint sobre test en CEDIA
- [ ] Registrar métricas y artefactos de evaluación en MLflow
- [ ] Sincronizar resultados y verificar integridad local
- [ ] Documentar resultados finales y análisis de errores para la presentación

---

### Notas y decisiones

- La evaluación usará `best.pt`, nunca `last.pt`.
- Test se ejecutará una sola vez después de fijar código, configuración y umbral.
- El umbral inicial permanece en `0.5`; cualquier análisis de sensibilidad se reportará
  sin usar test para reajustar el modelo o seleccionar otro checkpoint.
- Se conservarán TP, FP, FN y TN agregados y por imagen, además de Dice, IoU, precisión
  y recall, para reconstruir métricas y matrices.
- Las figuras serán derivados de CSV/JSON versionados o registrados en MLflow; los datos
  tabulares seguirán siendo la evidencia canónica.
- Las visualizaciones cualitativas distinguirán imagen, máscara real, probabilidad y
  predicción binaria, con identificadores suficientes para auditoría.
- La configuración enlaza el run de entrenamiento y fija `best.pt` por ruta y SHA-256;
  una evaluación crea un run MLflow separado para no alterar el historial de training.
- La carga valida sidecar, hash fijado, run MLflow, época, métrica y valor de selección
  antes de restaurar pesos; el job CPU `23317` verificó los contratos con 12/12 pruebas.
