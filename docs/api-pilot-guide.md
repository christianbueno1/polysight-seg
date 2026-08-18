# Guía para una API piloto local de PolySight

## Objetivo y alcance

La etapa piloto expondrá el modelo U-Net/ResNet-34 mediante una API ejecutada en una
laptop. Su función principal será recibir una imagen endoscópica y devolver la máscara
de segmentación del pólipo. Opcionalmente podrá solicitar una clasificación producida
por un modelo mantenido en otro proyecto.

El piloto es para desarrollo, demostración y pruebas controladas. No es un dispositivo
médico, no está validado para uso clínico y no debe publicarse directamente en Internet.

## Modelo que debe servir la API

| Campo | Valor |
|---|---|
| Versión | `model-unet-resnet34-v1.0.0` |
| Checkpoint | `best.pt`, época 22 |
| SHA-256 | `a3900c2db01e9e17fa7fedce12da94274d8995284f1c37f6e653df402919361b` |
| Entrada | Imagen RGB redimensionada a `256 × 256` |
| Salida | Logits de un canal; sigmoid y umbral fijo `0.5` |
| Run de entrenamiento | `5fdf1b9929ec443da426c6442d9e20f1` |

El servidor debe negarse a iniciar si el hash o los metadatos del checkpoint no
coinciden. Se debe reutilizar `load_selected_checkpoint()` y reconstruir la arquitectura
desde las configuraciones versionadas. Las instrucciones para recuperar el archivo están
en [`artifact-recovery.md`](artifact-recovery.md).

## Arquitectura propuesta

```text
Cliente local
     |
     | POST /v1/analyze (imagen + classify)
     v
API FastAPI
     |
     +--> validación y decodificación de imagen
     |
     +--> servicio de segmentación obligatorio
     |       +--> preprocesamiento
     |       +--> U-Net/ResNet-34
     |       +--> máscara y resumen
     |
     +--> adaptador de clasificación opcional
             +--> deshabilitado
             +--> modelo cargado en el mismo proceso
             +--> servicio HTTP local de otro proyecto
```

La segmentación es la capacidad principal. La clasificación se conecta mediante una
interfaz estable y no debe introducir imports directos del otro proyecto dentro de los
endpoints. Así se puede activar, reemplazar o retirar sin modificar la inferencia de
segmentación.

## Estructura sugerida

```text
src/polysight_seg/api/
├── app.py                 # creación de FastAPI y ciclo de vida
├── config.py              # variables de entorno y validación
├── schemas.py             # contratos de respuesta
├── image_io.py            # validación, decodificación y PNG/base64
├── segmentation.py        # carga única e inferencia
└── classification/
    ├── base.py            # protocolo común
    ├── disabled.py        # implementación nula
    ├── in_process.py      # adaptador opcional en el mismo entorno
    └── http_client.py     # cliente para servicio local independiente
tests/
├── test_api_contract.py
├── test_api_segmentation.py
└── test_api_classification_optional.py
```

## Dependencias de la API

El proyecto todavía no incluye un framework web. Para la implementación se propone
agregar un extra opcional, con versiones fijadas después de comprobar compatibilidad:

```toml
[project.optional-dependencies]
api = [
  "fastapi==<version-validada>",
  "uvicorn[standard]==<version-validada>",
  "python-multipart==<version-validada>",
]
```

No se deben escribir números de versión arbitrarios: primero se resuelven en un branch
de implementación, se prueban en Python 3.11 y luego se fijan en `pyproject.toml` y el
lockfile. PyTorch debe instalarse con una distribución compatible con el sistema de la
laptop: CPU para máxima portabilidad o CUDA cuando exista una GPU NVIDIA compatible.

## Preprocesamiento obligatorio

La API debe reproducir el camino de validation/test, sin aumentos aleatorios:

1. aceptar JPEG o PNG y limitar el tamaño del archivo;
2. decodificar y convertir explícitamente a RGB;
3. conservar las dimensiones originales para reconstruir la respuesta;
4. redimensionar a `256 × 256` con interpolación bilinear;
5. escalar y normalizar con media `[0.485, 0.456, 0.406]` y desviación
   `[0.229, 0.224, 0.225]`;
6. crear un batch `[1, 3, 256, 256]`;
7. ejecutar bajo `torch.inference_mode()` y con el modelo en `eval()`;
8. aplicar sigmoid y umbral `0.5`;
9. redimensionar la máscara binaria al tamaño original con interpolación nearest.

La API no debe aplicar flips, rotaciones ni cambios de brillo. El umbral no se expone
como parámetro del usuario durante el piloto porque fue fijado antes de evaluar test.

## Endpoints mínimos

### `GET /health/live`

Confirma que el proceso web responde. No ejecuta el modelo.

```json
{"status": "ok"}
```

### `GET /health/ready`

Confirma que el checkpoint fue verificado y cargado. También informa el estado del
clasificador opcional.

```json
{
  "status": "ready",
  "segmentation_model": "model-unet-resnet34-v1.0.0",
  "classification": {"enabled": false, "status": "disabled"}
}
```

### `GET /v1/models`

Devuelve versiones, hash del segmentador, umbral y datos del clasificador cuando esté
activo. No debe revelar rutas absolutas ni información sensible de la laptop.

### `POST /v1/analyze`

Entrada `multipart/form-data`:

- `image`: archivo JPEG o PNG obligatorio;
- `classify`: `auto`, `true` o `false`; valor predeterminado `auto`;
- `include_mask`: permite devolver la máscara PNG codificada en base64.

Semántica de `classify`:

- `false`: no llama al clasificador aunque esté disponible;
- `auto`: clasifica solo si el módulo está habilitado;
- `true`: exige clasificación y devuelve un error controlado si no está disponible.

Respuesta propuesta:

```json
{
  "request_id": "uuid",
  "model_version": "model-unet-resnet34-v1.0.0",
  "image": {"width": 1280, "height": 720},
  "segmentation": {
    "threshold": 0.5,
    "foreground_fraction": 0.1432,
    "mask_format": "image/png;base64",
    "mask": "..."
  },
  "classification": {
    "status": "disabled",
    "model_version": null,
    "label": null,
    "score": null
  },
  "timing_ms": {
    "segmentation": 185.4,
    "classification": null,
    "total": 193.1
  },
  "warnings": ["Uso experimental; no validado para decisión clínica"]
}
```

Los tiempos del ejemplo ilustran el contrato, no representan un benchmark real. Deben
medirse en la laptop elegida.

## Clasificación opcional

El contrato interno mínimo del adaptador puede ser:

```python
class ClassifierAdapter(Protocol):
    @property
    def model_version(self) -> str: ...

    def predict(self, image_rgb: np.ndarray) -> ClassificationResult: ...
```

El resultado debe incluir al menos `label`, `score` y `model_version`. También debe
definir qué imagen consume el clasificador:

- imagen original completa; o
- región delimitada por la máscara de segmentación.

Esa decisión pertenece al proyecto de clasificación y debe quedar en configuración,
no oculta dentro del endpoint. Si se usa un recorte, se debe definir qué ocurre cuando
la máscara está vacía y cuánto margen se agrega alrededor del pólipo.

### Opción A: clasificador en el mismo proceso

Adecuada si ambos proyectos usan versiones compatibles de Python, PyTorch y librerías.
Reduce latencia, pero aumenta memoria y acoplamiento. El adaptador debe cargar el modelo
una sola vez al iniciar la API.

### Opción B: clasificador como servicio local separado

Es la opción recomendada cuando los proyectos tienen dependencias distintas. La API de
segmentación llama a una URL como `http://127.0.0.1:8001/v1/classify`. Cada proyecto
conserva su entorno virtual, versión y ciclo de vida. Se deben fijar timeout corto,
límite de reintentos y contrato versionado.

Si la clasificación opcional falla con `auto`, la segmentación puede responder y marcar
`classification.status = "unavailable"`. Con `classify=true`, la petición debe fallar
de forma explícita. Nunca se debe fabricar una etiqueta o sustituirla silenciosamente.

## Configuración por entorno

Ejemplo para el piloto:

```dotenv
POLYSIGHT_HOST=127.0.0.1
POLYSIGHT_PORT=8000
POLYSIGHT_DEVICE=cpu
POLYSIGHT_CHECKPOINT=artifacts/1/5fdf1b9929ec443da426c6442d9e20f1/artifacts/checkpoints/best/best.pt
POLYSIGHT_MAX_UPLOAD_MB=10
POLYSIGHT_CLASSIFIER_MODE=disabled
POLYSIGHT_CLASSIFIER_URL=http://127.0.0.1:8001
POLYSIGHT_CLASSIFIER_TIMEOUT_SECONDS=5
```

Valores permitidos para `POLYSIGHT_CLASSIFIER_MODE`: `disabled`, `in_process` y
`http`. La configuración debe validarse al inicio y nunca registrar imágenes ni secretos.

## Ejecución local esperada

Una vez implementado el extra `api`, el flujo será equivalente a:

```bash
uv sync --extra api
uv run uvicorn polysight_seg.api.app:create_app \
  --factory \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1
```

Usar un solo worker durante el piloto evita cargar varias copias del modelo en memoria.
La interfaz OpenAPI quedaría en `http://127.0.0.1:8000/docs`.

Ejemplo de petición:

```bash
curl -X POST http://127.0.0.1:8000/v1/analyze \
  -F image=@sample.jpg \
  -F classify=auto \
  -F include_mask=true
```

Estos comandos son el contrato objetivo; funcionarán después de implementar los módulos
y agregar las dependencias. Esta guía por sí sola no crea aún el servidor.

## Seguridad y privacidad del piloto

- escuchar únicamente en `127.0.0.1`, no en `0.0.0.0`;
- aceptar solo MIME y extensiones explícitas, pero validar por decodificación real;
- limitar tamaño, dimensiones y tiempo de procesamiento;
- generar nombres internos y no confiar en el nombre enviado por el cliente;
- procesar en memoria y no conservar imágenes por defecto;
- no incluir imágenes, máscaras ni datos sensibles en logs;
- devolver errores genéricos al cliente y detalles solo en logs locales controlados;
- no habilitar CORS global; agregar orígenes concretos solo si una interfaz local lo
  necesita;
- no usar `reload` fuera del desarrollo interactivo.

Si más adelante se prueba desde otro equipo de la red, se requiere una decisión separada
sobre autenticación, TLS, firewall, consentimiento, retención y auditoría.

## Pruebas requeridas antes del piloto

1. **Carga:** hash incorrecto, checkpoint ausente y metadatos incompatibles impiden el
   inicio.
2. **Contrato:** health, models y analyze respetan esquemas y códigos HTTP.
3. **Imagen:** rechaza archivos vacíos, corruptos, demasiado grandes o no soportados.
4. **Preprocesamiento:** una imagen conocida produce el mismo tensor que evaluation.
5. **Inferencia:** la API produce la misma máscara que el runner para una muestra fija.
6. **Clasificación deshabilitada:** segmentación funciona sin instalar el otro proyecto.
7. **Clasificación activa:** versión, label y score se propagan sin modificar la máscara.
8. **Fallo opcional:** `auto` degrada de forma explícita y `true` devuelve error.
9. **Concurrencia:** varias peticiones pequeñas no mezclan resultados ni agotan memoria.
10. **Privacidad:** imágenes y contenido base64 no aparecen en logs.

No se debe volver a usar el conjunto test para ajustar la API. Las pruebas de integración
pueden usar imágenes sintéticas, archivos de demostración separados o muestras ya
destinadas a validation.

## Medición en la laptop

Antes de declarar viable el piloto se deben registrar:

- sistema operativo, CPU, RAM y GPU si existe;
- versión efectiva de Python y PyTorch;
- tiempo de arranque y memoria con modelos cargados;
- latencia p50, p95 y máxima para al menos 30 peticiones de calentamiento y medición;
- diferencia entre segmentación sola y segmentación más clasificación;
- tamaño medio y máximo de respuesta con y sin máscara base64;
- errores y temperatura sostenida durante una prueba corta.

No se fija aún un objetivo de latencia porque no se ha medido el hardware de la laptop.
Los resultados del benchmark deben documentarse antes de ampliar el alcance.

## Criterios de aceptación del piloto

- el servidor inicia solo con un checkpoint verificado;
- funciona en CPU, aunque una GPU compatible pueda acelerar la inferencia;
- segmentación funciona con clasificación habilitada o deshabilitada;
- el contrato permanece estable y muestra las versiones de ambos modelos;
- los resultados coinciden con el pipeline de evaluación para entradas conocidas;
- no se persisten imágenes por defecto;
- pruebas automáticas y benchmark local quedan registrados;
- la interfaz muestra de forma visible que el resultado es experimental.

## Orden recomendado de implementación

1. Configuración y carga única del segmentador.
2. Preprocesamiento y servicio de inferencia reutilizable.
3. Endpoints health, models y analyze sin clasificación.
4. Contratos y pruebas de paridad con evaluation.
5. Adaptador nulo y contrato común de clasificación.
6. Integración `in_process` o `http`, según compatibilidad del otro proyecto.
7. Pruebas de fallos, privacidad y límites de entrada.
8. Benchmark y demostración local en la laptop.
