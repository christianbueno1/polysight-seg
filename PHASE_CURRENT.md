# PHASE_CURRENT

## Fase 9 — Notebooks reproducibles para Google Colab

**Objetivo:** Permitir que un revisor pruebe el código, verifique el checkpoint y repita
el entrenamiento desde notebooks delgados que reutilizan directamente el paquete.

**Contexto:** Colab usa Python 3.12 y recursos efímeros. Los notebooks deben fijar una
revisión, validar cada archivo grande por SHA-256 y distinguir verificación rápida de
reproducción completa. Las métricas deben ser comparables; no se exige igualdad binaria
entre hardware o kernels distintos.

---

### Tareas

- [x] Implementar inferencia reutilizable de una imagen en CPU o CUDA
- [x] Crear notebook de verificación del checkpoint e inferencia visual
- [x] Crear notebook de reconstrucción de datos y reproducción de training
- [x] Mantener evaluación de test desactivada por defecto
- [x] Añadir contratos estáticos de notebooks y compatibilidad Python 3.12
- [x] Ejecutar validaciones locales ligeras sin PyTorch
- [ ] Ejecutar contratos de inferencia con PyTorch en Google Colab
- [ ] Publicar el tag fijo consumido por los notebooks
- [ ] Validar manualmente ambos recorridos en Google Colab

---

### Notas y decisiones

- Los notebooks orquestan funciones y scripts existentes; no duplican el modelo.
- `best.pt` y el ZIP se reciben desde Drive o carga manual y siempre verifican SHA-256.
- El recorrido rápido funciona en CPU; smoke y training completo requieren CUDA.
- Test no participa en el notebook de reproducción y permanece desactivado por defecto.
- La clasificación y la API quedan fuera de esta fase después del cambio de alcance.
- La laptop no ejecutará pruebas pesadas; PyTorch, checkpoint real y smoke GPU se
  validarán dentro del runtime de Colab.
