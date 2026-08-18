# Ficha del modelo — U-Net/ResNet-34 baseline

## Identificación

| Campo | Valor |
|---|---|
| Proyecto | PolySight Seg |
| Tarea | Segmentación binaria de pólipos en imágenes endoscópicas |
| Arquitectura | U-Net con encoder ResNet-34 preentrenado en ImageNet |
| Checkpoint | `best.pt`, época 22 |
| SHA-256 | `a3900c2db01e9e17fa7fedce12da94274d8995284f1c37f6e653df402919361b` |
| Run de entrenamiento | `5fdf1b9929ec443da426c6442d9e20f1` |
| Run de evaluación | `73876309ec7c45e09023574a02a47475` |

## Uso previsto

El modelo es un baseline experimental para estudiar y reproducir segmentación de
pólipos sobre Kvasir-SEG. Puede utilizarse para:

- investigación y aprendizaje sobre segmentación semántica;
- reproducir el protocolo documentado del proyecto;
- analizar errores, probabilidades y métricas del conjunto Kvasir-SEG;
- servir como punto de partida para experimentos posteriores debidamente validados.

No está aprobado para diagnóstico, tratamiento, priorización de pacientes ni ninguna
otra decisión clínica. Tampoco debe presentarse como un sistema clínicamente validado.

## Entrada y salida

La entrada es una imagen endoscópica RGB redimensionada a `256 × 256`, normalizada con
las estadísticas de ImageNet. La salida del modelo es un mapa de logits de un canal con
la misma resolución. Para obtener la máscara binaria se aplica sigmoid y el umbral fijo
`0.5`.

El modelo segmenta una sola clase de interés —pólipo— frente al fondo. No clasifica el
tipo de lesión, no estima malignidad y no entrega una medida clínica de incertidumbre.

## Datos de desarrollo

- Dataset: Kvasir-SEG, 1.000 pares imagen/máscara.
- Split fijo: 700 train, 150 validation y 150 test.
- Semilla: `20260817`.
- Selección: Dice de validation; mejor valor `0.8977634135250631` en la época 22.
- Evaluación final: una sola ejecución sobre las 150 imágenes de test.
- Separación garantizada: por archivo y grupo de duplicado exacto.
- Separación no garantizada: por paciente o procedimiento, debido a metadatos
  insuficientes en la fuente.

## Rendimiento en test

Las métricas siguientes son micro agregadas sobre todos los píxeles de las 150 imágenes
de test, usando umbral `0.5`:

| Métrica | Resultado |
|---|---:|
| Dice | `0.9183967352352693` |
| IoU | `0.8491068445832013` |
| Precisión | `0.9237401535043426` |
| Recall | `0.913114779938238` |

El Dice por imagen tuvo media `0.9090774776019991`, mediana
`0.954879509971524`, mínimo `0.07747857191064318` y máximo
`0.9890401607948728`. El mínimo demuestra que el buen desempeño agregado no garantiza
una segmentación correcta en cada imagen.

## Limitaciones y riesgos

- El entrenamiento y la evaluación usan un único dataset público de 1.000 imágenes.
- No existe validación externa, prospectiva, multicéntrica ni en datos clínicos locales.
- Se usó un solo split y una sola semilla; no se midió variabilidad mediante validación
  cruzada o múltiples inicializaciones.
- El redimensionamiento a `256 × 256` puede reducir detalles y lesiones pequeñas.
- Las imágenes alejadas del dominio de Kvasir-SEG pueden producir resultados no
  confiables por cambio de dominio.
- El modelo puede omitir gran parte de un pólipo o sobresegmentar regiones de fondo.
- No se calibró la probabilidad como medida de confianza clínica.
- No se ejecutó la comparación con EfficientNet-B0; no hay evidencia para afirmar que
  este encoder sea mejor o peor que alternativas.

Los falsos negativos son especialmente relevantes porque representan regiones reales
de pólipo no detectadas. La salida siempre requiere revisión humana experta en cualquier
demostración relacionada con el dominio médico.

## Usos no recomendados

- uso autónomo en endoscopia o atención de pacientes;
- sustitución de la interpretación de un profesional de salud;
- aplicación a modalidades, equipos o poblaciones no evaluadas;
- decisión clínica basada únicamente en la máscara o su probabilidad;
- comparación con otros modelos sin repetir el mismo protocolo experimental;
- ajuste del umbral utilizando las métricas de test ya observadas.

## Reproducibilidad y procedencia

La configuración de evaluación fija la procedencia, la época y el hash del checkpoint.
Antes de cargarlo debe verificarse su SHA-256. Las instrucciones están en
[`artifact-recovery.md`](artifact-recovery.md); el protocolo y el análisis completo se
encuentran en [`final-report.md`](final-report.md).

Las fuentes canónicas versionadas son:

- [`../configs/training/unet-resnet34-baseline.yaml`](../configs/training/unet-resnet34-baseline.yaml);
- [`../configs/evaluation/unet-resnet34-baseline.yaml`](../configs/evaluation/unet-resnet34-baseline.yaml);
- [`results/test/metrics.json`](results/test/metrics.json);
- [`results/test/per-image-metrics.csv`](results/test/per-image-metrics.csv).

`mlflow.db`, los checkpoints, los mapas de probabilidad y los artefactos completos no se
guardan en Git. Se conservan en el almacenamiento experimental y deben sincronizarse
juntos para reconstruir la interfaz MLflow.
