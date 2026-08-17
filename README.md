# PolySight Seg

Proyecto reproducible para entrenar y evaluar modelos de segmentación de pólipos sobre
Kvasir-SEG.

**Modelo:** U-Net CNN con encoder ResNet34 (pre-entrenado en ImageNet). Entrada RGB 256×256 → salida binaria.

PyTorch, CUDA, entrenamiento y evaluación acelerada se ejecutan en el clúster HPC de
CEDIA. El equipo local se usa únicamente para desarrollo y validaciones ligeras:

```bash
scripts/validate_local.sh
```

## Documentación

- [Entornos de ejecución](docs/execution-environments.md)
- [Preparación del proyecto en CEDIA](docs/cedia-project-setup.md)
- [Preparación y transferencia de Kvasir-SEG](docs/dataset-preparation.md)
- [Material para la presentación](docs/presentacion.md)
- [Guía general del clúster CEDIA](docs/cedia-cluster-guide.md)
- [Guía del proyecto de segmentación](docs/segmentation-project-guide.md)
