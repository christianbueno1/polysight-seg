# PHASE_CURRENT

## Fase 7 — Comparación U-Net ResNet-34 frente a EfficientNet-B0

**Objetivo:** Entrenar y evaluar una variante U-Net/EfficientNet-B0 bajo el mismo
protocolo del baseline para comparar calidad, coste y estabilidad de forma justa.

**Contexto:** El baseline U-Net/ResNet-34 quedó cerrado con Dice test `0.9183967352352693`
e IoU `0.8491068445832013`. Sus splits, resolución, pérdida, semilla, umbral y protocolo
de selección permanecen fijados y deben reutilizarse en la comparación.

---

### Tareas

- [ ] Definir y versionar la configuración U-Net/EfficientNet-B0
- [ ] Añadir contratos de arquitectura y presupuesto de parámetros
- [ ] Ejecutar smoke CPU/GPU de construcción y forward/backward
- [ ] Crear configuración de entrenamiento comparable al baseline
- [ ] Ejecutar entrenamiento reproducible con MLflow en CEDIA
- [ ] Seleccionar `best.pt` exclusivamente mediante Dice de validation
- [ ] Adaptar y validar la configuración de evaluación sin consumir test
- [ ] Ejecutar una sola evaluación final sobre el mismo split test
- [ ] Comparar métricas, parámetros, tiempo y artefactos cualitativos
- [ ] Documentar conclusiones y limitaciones para la presentación

---

### Notas y decisiones

- Solo cambia el encoder; datos, splits, resolución, augmentations, pérdida, optimizador,
  semilla, máximo de épocas, early stopping y umbral se mantienen comparables.
- Validation seleccionará el checkpoint de EfficientNet-B0; test se conservará aislado
  hasta cerrar su entrenamiento y evaluador.
- La comparación reportará Dice e IoU junto con parámetros, tiempo y memoria; una sola
  métrica no determinará por sí misma la recomendación final.
- Los resultados del baseline son inmutables y no se reajustarán después de observar la
  segunda arquitectura.
