# Guía para iniciar el proyecto de segmentación de pólipos

## Decisión de organización

La segmentación no tiene que implementarse dentro del repositorio PolySight. Puede y,
si se desea mantener responsabilidades claras, conviene desarrollarse en un repositorio
independiente.

La separación propuesta es:

```text
PolySight
└── clasificación multiclase de hallazgos gastrointestinales

Nuevo proyecto de segmentación
└── localización píxel a píxel de pólipos
```

Aunque ambos proyectos usan imágenes endoscópicas y PyTorch, resuelven problemas
diferentes:

| Aspecto | Clasificación | Segmentación |
|---|---|---|
| Pregunta | ¿Qué hallazgo aparece? | ¿Qué píxeles pertenecen al pólipo? |
| Entrada | Imagen RGB | Imagen RGB |
| Salida | Probabilidades por clase | Máscara de probabilidad por píxel |
| Ground truth | Etiqueta de clase | Máscara binaria |
| Arquitectura inicial | EfficientNet-B0 | U-Net u otra red de segmentación |
| Métricas principales | Macro-F1, accuracy | Dice, IoU |

Separar los repositorios evita mezclar dependencias, configuraciones, manifests,
checkpoints, métricas, comandos y releases. También permite desplegar posteriormente
clasificación y segmentación como servicios independientes.

## Qué debe permanecer en PolySight

PolySight puede conservar:

- la documentación que explica la relación entre ambos estudios;
- la procedencia general de HyperKvasir;
- enlaces al nuevo repositorio;
- decisiones compartidas de trazabilidad y uso del dataset.

El nuevo proyecto debe contener:

- descarga y validación de Kvasir-SEG;
- pares imagen–máscara y manifests;
- splits de train, validation y test;
- transformaciones sincronizadas;
- modelos y funciones de pérdida de segmentación;
- entrenamiento, evaluación e inferencia;
- artefactos, MLflow y checkpoints propios;
- documentación y release del estudio de segmentación.

No se debe hacer que el nuevo proyecto importe directamente módulos internos de este
repositorio. Si posteriormente aparece código verdaderamente compartido, debe extraerse
a una librería pequeña y versionada, no copiarse informalmente entre repositorios.

## Entorno Python recomendado para CEDIA

Para el piloto de segmentación se recomienda mantener **Python 3.11**. Es la versión ya
validada en CEDIA con los módulos `pytorch/2.2` y `cuda/12.4`, reduce incompatibilidades
y facilita la integración posterior con la API de clasificación.

El nuevo proyecto puede tener un entorno y repositorio independientes, pero conviene
fijar inicialmente `requires-python = ">=3.11,<3.12"`. Solo se debe actualizar Python
después de comprobar en CEDIA la compatibilidad de PyTorch, CUDA y todas las dependencias,
incluido un smoke test de entrenamiento sobre GPU. No se recomienda usar automáticamente
la versión más reciente de Python solo por ser nueva.

## Dataset

La parte necesaria es el conjunto de segmentación de HyperKvasir, conocido como
Kvasir-SEG:

```text
Archivo: hyper-kvasir-segmented-images.zip
Tamaño publicado: aproximadamente 46 MB
Contenido: 1.000 imágenes, 1.000 máscaras y bounding boxes
```

Fuentes oficiales:

- https://datasets.simula.no/hyper-kvasir/
- https://datasets.simula.no/downloads/hyper-kvasir/
- https://github.com/simula/hyper-kvasir
- https://www.nature.com/articles/s41597-020-00622-y

Para cada ejemplo:

- la imagen original es RGB;
- la máscara representa el pólipo en blanco y el fondo en negro;
- la imagen y la máscara tienen el mismo nombre;
- el bounding box correspondiente está disponible en JSON.

Las 1.000 imágenes proceden de la clase de pólipos del conjunto etiquetado de
HyperKvasir. Por eso existen también dentro de los datos usados en el estudio de
clasificación. Los dos experimentos deben tratarse como estudios separados y no deben
combinarse sus resultados o splits como si fueran una sola evaluación.

El repositorio oficial indica que los datos están abiertos para investigación y
educación, que deben citarse los trabajos correspondientes y que competiciones o usos
comerciales requieren permiso previo por escrito. El nuevo proyecto debe revisar y
documentar estas condiciones antes de redistribuir datos o modelos.

## Objetivo del modelo

El modelo debe recibir una imagen endoscópica y producir una probabilidad para cada
píxel:

```text
Imagen RGB
  -> red de segmentación
  -> logits de un canal
  -> sigmoid
  -> mapa de probabilidades
  -> umbral
  -> máscara binaria del pólipo
```

El umbral inicial puede ser `0.5`, pero cualquier ajuste posterior debe hacerse usando
exclusivamente validation. Test no debe utilizarse para elegir el umbral.

## Arquitectura inicial recomendada

Usar U-Net como baseline, con un encoder preentrenado en ImageNet, por ejemplo
ResNet-34:

```text
Arquitectura: U-Net
Encoder: ResNet-34 preentrenado
Canales de entrada: 3
Canales de salida: 1
Tarea: segmentación binaria
```

U-Net es una referencia inicial comprensible y adecuada para un dataset pequeño. No
debe asumirse que será la arquitectura óptima. U-Net++, DeepLabV3+, SegFormer u otras
alternativas pueden evaluarse en fases posteriores, usando el mismo split y protocolo.

## Preparación reproducible

Antes de entrenar:

1. descargar solamente el archivo de segmentación;
2. registrar URL, tamaño exacto y SHA-256;
3. implementar extracción segura e idempotente;
4. comprobar que existen exactamente 1.000 pares;
5. validar correspondencia de nombres;
6. comprobar dimensiones iguales entre imagen y máscara;
7. detectar archivos corruptos;
8. binarizar las máscaras explícitamente;
9. calcular el porcentaje de píxeles de pólipo por imagen;
10. detectar y agrupar duplicados exactos;
11. generar manifest y resumen con hashes.

Las máscaras publicadas usan compresión JPEG. No debe suponerse que sus píxeles son
solamente `0` y `255`; el pipeline debe aplicar una regla de binarización documentada y
probarla.

## Splits

Como punto de partida:

```text
Train:      70%
Validation: 15%
Test:       15%
```

La asignación debe ser determinista y conservar grupos de duplicados en un único
split. También conviene distribuir ejemplos según el porcentaje de la imagen ocupado
por el pólipo, usando bins como pequeño, mediano y grande.

HyperKvasir no ofrece identificadores suficientes para garantizar separación por
paciente o procedimiento. Esta limitación debe aparecer en los reportes. Antes de
generar una partición propia, el nuevo proyecto debe verificar si existe un split
oficial aplicable específicamente a Kvasir-SEG; no debe asumir que los splits oficiales
de clasificación cubren segmentación.

Debido a que solo hay 1.000 pares, también puede considerarse validación cruzada en una
fase posterior. Para el primer baseline, un split fijo facilita reproducibilidad y
comparación operativa.

## Transformaciones

Las transformaciones geométricas deben aplicarse de forma sincronizada:

```text
Rotación de imagen  = misma rotación de máscara
Flip de imagen      = mismo flip de máscara
Crop de imagen      = mismo crop de máscara
Resize de imagen    = resize correspondiente de máscara
```

Reglas importantes:

- usar interpolación apropiada para fotografías al redimensionar la imagen;
- usar nearest-neighbor para la máscara y preservar sus clases;
- aplicar brillo, contraste o color solamente a la imagen;
- convertir la máscara final a valores binarios;
- no aplicar augmentations aleatorias en validation ni test.

## Pérdida y métricas

Una combinación inicial razonable es:

```text
BCEWithLogitsLoss + Dice loss
```

Métricas principales:

- Dice coefficient;
- IoU o Jaccard;
- precision por píxel;
- recall por píxel.

Pixel accuracy puede registrarse, pero no debe ser el criterio principal porque el
fondo suele ocupar gran parte de la imagen.

Dice de validation puede utilizarse para:

- guardar `best.pt`;
- aplicar early stopping;
- comparar configuraciones;
- seleccionar el modelo que se evaluará una sola vez sobre test.

## Checkpoint: `.pt` frente a `.pth`

El resultado del entrenamiento también será un modelo de PyTorch. Puede guardarse con
extensión `.pt` o `.pth`:

```text
best.pt
best.pth
```

Para PyTorch, ambas extensiones son convenciones de nombre; no representan dos
formatos intrínsecamente diferentes. El contenido depende de lo que se entregue a
`torch.save()`.

Para mantener consistencia con PolySight se recomienda:

```text
best.pt
```

El checkpoint debería almacenar como mínimo:

```python
{
    "model_state": model.state_dict(),
    "optimizer_state": optimizer.state_dict(),
    "scheduler_state": scheduler.state_dict(),
    "epoch": epoch,
    "best_val_dice": best_val_dice,
    "threshold": threshold,
    "architecture": architecture,
    "config": config,
    "manifest_sha256": manifest_sha256,
    "code_commit": code_commit,
}
```

Para inferencia, el servicio debe reconstruir la misma arquitectura y cargar
`model_state`. Guardar solamente `state_dict` es preferible a serializar el objeto
Python completo porque reduce el acoplamiento a rutas de importación, aunque sigue
siendo obligatorio versionar la arquitectura y sus dependencias.

La extensión no garantiza compatibilidad ni seguridad. Cada checkpoint debe tener:

- SHA-256;
- versión de PyTorch y librerías relevantes;
- commit del código;
- configuración;
- hash del manifest;
- métricas de validation y test;
- procedencia del dataset.

Nunca debe cargarse con `torch.load()` un checkpoint de origen no confiable.

## Otros formatos de despliegue

El checkpoint `.pt` es el artefacto principal de entrenamiento. Posteriormente pueden
derivarse formatos de inferencia:

```text
best.pt       -> reanudación, auditoría e inferencia PyTorch
model.pt2     -> programa exportado con torch.export, si es compatible
model.onnx    -> interoperabilidad con ONNX Runtime
```

Estos formatos no reemplazan automáticamente el checkpoint auditable. Cada exportación
debe comprobar paridad numérica y visual con `best.pt` antes de utilizarse.

## Artefactos de evaluación

Cada evaluación debe guardar:

```text
metrics.json
per-image-metrics.csv
predictions/
├── original.png
├── ground-truth.png
├── probability-map.png
├── predicted-mask.png
└── overlay.png
```

El reporte debe incluir ejemplos mejores, medianos y peores según Dice, además de
analizar falsos positivos, falsos negativos y rendimiento según tamaño del pólipo.

## Fases sugeridas para el nuevo repositorio

```markdown
- [ ] Fase 1 — Estructura, gobierno y entorno del proyecto
- [ ] Fase 2 — Preparación reproducible de Kvasir-SEG y splits
- [ ] Fase 3 — Pipeline PyTorch de segmentación
- [ ] Fase 4 — Integración con MLflow y entorno de cómputo
- [ ] Fase 5 — Ejecución experimental y selección por validation
- [ ] Fase 6 — Evaluación final, análisis y release
- [ ] Fase 7 — Servicio de inferencia o integración con API
```

Solo una fase debe estar activa. La primera sesión debe confirmar el objetivo y crear
el backlog antes de implementar el dataset o el modelo.

## Relación futura con una API

El servicio de segmentación podría exponer:

```text
POST /segment
  entrada: imagen
  salida: máscara, overlay y metadatos del modelo
```

Clasificación y segmentación pueden mantenerse como dos servicios o combinarse detrás
de un gateway. No es necesario decidirlo durante la primera fase experimental.

La API debe cargar el modelo una sola vez, verificar su hash y devolver la identidad
exacta del modelo usado. Las máscaras pueden entregarse como PNG binario, no como JPEG,
para evitar artefactos de compresión.

## Alcance de las conclusiones

Un modelo entrenado y evaluado en Kvasir-SEG demuestra rendimiento experimental sobre
ese conjunto y split. No constituye validación clínica ni garantiza generalización a
otros hospitales, dispositivos, poblaciones, videos o condiciones de captura.

La evaluación externa con otros datasets de segmentación de pólipos puede plantearse
después del baseline, manteniendo esos datos completamente fuera del entrenamiento y
selección del modelo.
