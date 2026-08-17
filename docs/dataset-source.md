# Fuente de Kvasir-SEG

## Archivo local registrado

Registro realizado el 17 de agosto de 2026 sin modificar ni extraer el archivo:

| Campo | Valor |
|---|---|
| Nombre | `hyper-kvasir-segmented-images.zip` |
| Ruta local | `/home/chris/Downloads/hyper-kvasir-segmented-images.zip` |
| Tamaño | 46.179.365 bytes |
| SHA-256 | `4463011f991dcdc74ec56399788b1a93822593f17ed18a662bdeb7392ffcdd9a` |
| Fecha de modificación local | `2026-08-17 11:06:32 -0500` |
| Prueba de integridad ZIP | Sin errores |

El hash identifica exactamente esta copia local; no se encontró un checksum oficial
publicado con el cual compararlo. El usuario confirmó que la copia se descargó desde
<https://datasets.simula.no/hyper-kvasir/>.

## Estructura observada

La inspección de solo lectura encontró:

- `segmented-images/bounding-boxes.json`;
- 1.000 archivos JPEG bajo `segmented-images/images/`;
- 1.000 archivos JPEG bajo `segmented-images/masks/`;
- cero rutas absolutas o con componentes `..`.

Esta estructura coincide con la descripción oficial: 1.000 imágenes de pólipos, cada
una con máscara JPEG y bounding box; imagen y máscara correspondientes comparten nombre.

## Procedencia y condiciones de uso

Fuentes oficiales:

- <https://datasets.simula.no/hyper-kvasir/>;
- <https://github.com/simula/hyper-kvasir>;
- <https://doi.org/10.1038/s41597-020-00622-y>.

Procedencia confirmada de la copia local:
<https://datasets.simula.no/hyper-kvasir/>.

El repositorio oficial identifica su licencia como CC BY 4.0 y permite el uso abierto
para investigación y educación. Competiciones y usos comerciales requieren permiso
previo por escrito. Todo documento, publicación o resultado basado en HyperKvasir debe
citar el artículo asociado.

Referencia principal:

> Borgli, H. et al. (2020). *HyperKvasir, a comprehensive multi-class image and video
> dataset for gastrointestinal endoscopy*. Scientific Data, 7, 283.
> <https://doi.org/10.1038/s41597-020-00622-y>

Estas condiciones deben revisarse nuevamente antes de redistribuir datos, publicar
modelos o cambiar el uso previsto del proyecto.

## Regla de binarización

Las máscaras están comprimidas como JPEG y contienen valores intermedios introducidos
por la compresión. El pipeline debe convertirlas a escala de grises y aplicar esta regla
determinista:

```text
valor < 128  -> fondo (0)
valor >= 128 -> pólipo (255)
```

No se deben interpretar los valores JPEG originales como clases adicionales. Cualquier
ajuste posterior de esta regla requiere una decisión documentada y una nueva versión
del manifest.
