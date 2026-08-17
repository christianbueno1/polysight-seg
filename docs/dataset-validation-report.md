# Informe de validación de Kvasir-SEG

## Ejecución

- Fecha: `2026-08-17 11:53 -0500`
- Archivo fuente: `hyper-kvasir-segmented-images.zip`
- SHA-256 fuente: `4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a`
- Estado de extracción repetida: `unchanged`
- Resultado general: `ok`

## Integridad estructural

| Comprobación | Resultado |
|---|---:|
| Pares imagen–máscara | 1.000 |
| Registros de bounding boxes | 1.000 |
| Imágenes JPEG RGB | 1.000 |
| Máscaras JPEG RGB | 1.000 |
| Archivos corruptos | 0 |
| Pares con nombres diferentes | 0 |
| Pares con dimensiones diferentes | 0 |
| Bounding boxes inválidos | 0 |

Los límites máximos de los bounding boxes se interpretaron como exclusivos, permitiendo
`xmax == width` y `ymax == height`, según los valores observados en el JSON oficial.

## Máscaras

| Métrica | Resultado |
|---|---:|
| Umbral de binarización | 128 |
| Máscaras con valores JPEG intermedios | 1.000 |
| Fracción global de píxeles de pólipo | 0,1564208100 |
| Fracción media por imagen | 0,1539098941 |
| Mediana por imagen | 0,1140072416 |
| Mínimo por imagen | 0,0047392690 |
| Máximo por imagen | 0,8118197138 |

Todas las máscaras conservaron píxeles de fondo y pólipo después de aplicar el umbral.

## Duplicados exactos

- Grupos de imágenes con el mismo SHA-256: `0`.
- Muestras dentro de grupos duplicados: `0`.

Este resultado descarta duplicados binarios exactos dentro del subconjunto segmentado.
No descarta imágenes visualmente similares ni la presencia de estas mismas imágenes en
otras partes de HyperKvasir.

## Artefactos reproducibles

```text
35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4  manifest.csv
964f4d97e04eb2687694a5e44452d2cff4bb409920364e4aca44b75025c30a7f  summary.json
```

Los artefactos se generaron dos veces con contenido idéntico. Permanecen bajo
`data/processed/kvasir-seg/` y están excluidos de Git porque pueden reconstruirse desde
el ZIP y el código versionado.

## Pruebas del proyecto

Las siete pruebas locales finalizaron correctamente sin importar PyTorch. Cubren
metadatos, estructura, exclusión de PyTorch local, umbral de binarización, extracción
idempotente y rechazo de path traversal.
