# Ejemplos de HyperKvasir

Este directorio contiene un conjunto pequeño para comprobar que los modelos aceptan
imágenes reales y producen una salida. No reemplaza los datasets, no sirve para medir
rendimiento y no debe incorporarse a un nuevo conjunto de `test`.

## Contenido

- `classification/`: 16 imágenes, una por cada clase del perfil `main16` del proyecto
  clasificador. La selección toma el UUID lexicográficamente menor de cada clase con al
  menos 100 imágenes.
- `segmentation/images/`: tres imágenes del split `validation`, una por estrato de
  tamaño de pólipo (`small`, `medium`, `large`).
- `segmentation/masks/`: máscaras de referencia correspondientes. En cada estrato se
  eligió el caso central al ordenar por fracción de primer plano.
- `manifest.csv`: fuente, etiqueta, rol y SHA-256 de cada archivo.

Para probar clasificación, se puede recorrer `classification/*.jpg` y comparar la
salida superior con la etiqueta situada antes de `__` en el nombre. Esto es solamente
una comprobación funcional: 16 aciertos o errores aislados no constituyen una métrica.

Para segmentación, se pasa cualquier archivo de `segmentation/images/` al modelo. La
máscara con el mismo UUID permite una inspección visual de referencia. Estos tres casos
pertenecen a `validation`; no se incluyó ninguna muestra de `test`.

## Procedencia y uso

Los archivos fueron extraídos sin recomprimir de
`hyper-kvasir-labeled-images.zip` y `hyper-kvasir-segmented-images.zip`. El manifest
permite verificar cada copia y reconstruirla desde el miembro exacto del ZIP.

HyperKvasir se distribuye bajo CC BY 4.0 para investigación y educación. Debe citarse:

> Borgli, H. et al. (2020). *HyperKvasir, a comprehensive multi-class image and video
> dataset for gastrointestinal endoscopy*. Scientific Data, 7, 283.
> <https://doi.org/10.1038/s41597-020-00622-y>

Antes de usar estos datos en competiciones, productos o contextos comerciales se deben
revisar las condiciones actuales del proveedor y obtener los permisos necesarios.
