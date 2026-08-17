# Pipeline de datos

## Configuración canónica

El contrato del pipeline se mantiene en `configs/data/kvasir-seg.yaml`. La configuración
centraliza rutas reproducibles, umbral de máscara, parámetros del DataLoader, resolución,
interpolaciones, normalización y augmentations.

## Resolución e interpolación

Las imágenes y máscaras se redimensionarán a `256 × 256`:

- imagen RGB: interpolación bilinear;
- máscara binaria: nearest-neighbor.

Nearest-neighbor evita crear clases nuevas en la máscara. Después de cualquier
transformación, la máscara debe conservar únicamente `0` y `1` al convertirse en tensor.

## Normalización

Se utilizan media y desviación estándar de ImageNet porque los encoders iniciales serán
preentrenados en ImageNet:

```text
mean = [0.485, 0.456, 0.406]
std  = [0.229, 0.224, 0.225]
```

## Transformaciones de train

Las transformaciones geométricas se aplicarán conjuntamente a imagen y máscara:

- flip horizontal con probabilidad 0,5;
- flip vertical con probabilidad 0,5;
- rotación de hasta ±15 grados con probabilidad 0,5;
- resize final a `256 × 256`.

Brillo y contraste se aplicarán únicamente a la imagen con probabilidad 0,3. Validation
y test no tendrán transformaciones aleatorias: solo resize, binarización, conversión a
tensor y normalización de la imagen.

## DataLoader inicial

La configuración inicial solicita batches de 8, cuatro workers, memoria fijada y workers
persistentes. Estos valores son operativos y podrán reducirse si el smoke test en CEDIA
muestra límites de RAM, VRAM o procesos. Cualquier cambio usado en un experimento debe
quedar registrado con el checkpoint y las métricas.

## Prevención de leakage

El pipeline recibe el nombre del split y selecciona únicamente los UUID asignados en
`splits.csv`. No calcula ni modifica particiones durante el entrenamiento. Test no puede
usarse para ajustar augmentations, umbral, arquitectura o hiperparámetros.

## Smoke test en CEDIA

Después de reproducir el dataset y preparar `.venv-cluster`, enviar:

```bash
sbatch slurm/smoke_data_pipeline.sbatch
```

El trabajo usa `cpu-dev` y comprueba un batch de cada split, formas `[B,3,256,256]` y
`[B,1,256,256]`, valores finitos, máscaras binarias y determinismo de validation/test.
