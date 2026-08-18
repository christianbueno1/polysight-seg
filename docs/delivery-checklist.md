# Checklist de entrega — baseline U-Net/ResNet-34

## Alcance

- [x] La entrega contiene únicamente el baseline U-Net/ResNet-34 entrenado y evaluado.
- [x] La comparación con EfficientNet-B0 se declara pendiente y no se presenta como
  experimento ejecutado.
- [x] Las conclusiones se limitan a Kvasir-SEG y no afirman validación clínica.

## Resultados y trazabilidad

- [x] El checkpoint oficial es `best.pt` de la época 22.
- [x] El SHA-256 oficial del checkpoint está fijado y fue verificado.
- [x] El run de entrenamiento `5fdf1b9929ec443da426c6442d9e20f1` está documentado.
- [x] El run de evaluación `73876309ec7c45e09023574a02a47475` está documentado.
- [x] Las métricas oficiales proceden de `docs/results/test/metrics.json`.
- [x] Las métricas por imagen, matrices y curva descriptiva están versionadas.
- [x] Los mejores, medianos y peores casos tienen evidencia visual versionada.

## Documentación

- [x] El README resume objetivo, protocolo, resultados y evidencia.
- [x] El reporte técnico incluye protocolo, análisis de errores y límites.
- [x] La ficha del modelo define uso previsto, riesgos y usos no recomendados.
- [x] La presentación distingue smoke, validation y evaluación final de test.
- [x] La guía de recuperación explica cómo sincronizar y verificar artefactos.
- [x] El índice identifica fuentes canónicas, derivados y archivos externos.
- [x] Las cifras exactas y redondeadas son consistentes entre documentos.

## Validación técnica

- [x] `scripts/validate_local.sh` termina correctamente sin PyTorch ni GPU.
- [x] Los 24 contratos locales pasan.
- [x] Todos los enlaces Markdown locales versionados apuntan a destinos existentes.
- [x] `git diff --check` no reporta errores de formato.
- [x] No existen marcadores de conflicto en archivos versionados.
- [x] No hay archivos ignorados accidentalmente incorporados a Git.
- [x] Los datos, checkpoints, MLflow y resultados completos permanecen fuera de Git.

## Entrega y continuidad

- [x] El branch `chore/empaquetado-resultados` contiene commits atómicos y está
  sincronizado con su remoto antes del cierre.
- [x] La Fase 8 está lista para fusionarse en `dev` mediante `--no-ff`.
- [x] La Fase 7 permanece en el backlog para una decisión futura del responsable.
- [x] No se inicia una nueva fase sin confirmación del alcance.
