# Presentación de PolySight Seg

Este documento reúne material explicativo para presentar el proyecto y responder
preguntas de la audiencia. Se ampliará conforme avancen las fases.

---

## Preparación de máscaras: binarización de Kvasir-SEG

### Cómo explicarlo durante la exposición

Kvasir-SEG contiene 1.000 imágenes endoscópicas y sus respectivas máscaras de
segmentación. En una máscara ideal, el fondo tendría valor `0` y el pólipo valor `255`.
Sin embargo, las máscaras del dataset están almacenadas como JPEG, un formato con
compresión con pérdida. Esa compresión introduce valores intermedios alrededor de los
bordes y evita que podamos tratar los píxeles originales como categorías exactas.

Por esta razón definimos una regla única y reproducible antes de entrenar:

```text
valor en escala de grises < 128  -> fondo (0)
valor en escala de grises >= 128 -> pólipo (255)
```

Primero convertimos cada máscara RGB a escala de grises y luego aplicamos el umbral. El
resultado contiene únicamente dos valores y representa una tarea de segmentación
binaria: fondo frente a pólipo.

### Por qué esta decisión es importante

Sin una regla explícita, distintas librerías o implementaciones podrían interpretar las
mismas máscaras de manera diferente. Eso afectaría la pérdida, las métricas Dice e IoU,
el tamaño aparente del pólipo y la comparación entre experimentos.

El umbral queda centralizado como parte del código y registrado en el manifest. De este
modo, entrenamiento, validación, test e inferencia usan exactamente la misma definición
de máscara.

### Resultados observados

- Se analizaron las 1.000 máscaras.
- Las 1.000 contienen valores intermedios causados por la compresión JPEG.
- Después del umbral, todas conservan al menos un píxel de fondo y uno de pólipo.
- La proporción global de píxeles de pólipo es aproximadamente `15,64 %`.
- Por imagen, la proporción promedio es `15,39 %` y la mediana es `11,40 %`.
- La máscara más pequeña ocupa aproximadamente `0,47 %` de su imagen.
- La máscara más grande ocupa aproximadamente `81,18 %` de su imagen.

Estos valores muestran un desbalance claro entre fondo y pólipo y también una variación
considerable en el tamaño de las lesiones. Esto justifica usar Dice e IoU como métricas
principales y considerar el tamaño del pólipo al construir los splits.

### Qué no hicimos

- No sobrescribimos las máscaras originales.
- No modificamos el ZIP descargado.
- No elegimos el umbral usando validation o test.
- No tratamos los valores intermedios de JPEG como clases adicionales.
- No ejecutamos PyTorch localmente; esta preparación usa únicamente Pillow.

Las máscaras originales permanecen como fuente inmutable. La binarización se aplica de
forma determinista cuando el pipeline la necesita.

### Preguntas de la audiencia y respuestas

#### ¿Por qué no usar directamente los valores 0 y 255?

Porque JPEG altera los valores durante la compresión. Aunque visualmente la máscara
parezca binaria, sus píxeles contienen muchos niveles intermedios. Exigir solamente `0`
y `255` descartaría información válida o produciría máscaras inconsistentes.

#### ¿Por qué se eligió el umbral 128?

Es el punto medio reproducible del rango de 8 bits entre fondo y primer plano. Se adoptó
como regla de preparación, no como hiperparámetro ajustado con resultados del modelo.
Cambiarlo requeriría versionar nuevamente el manifest y repetir los experimentos.

#### ¿El umbral 128 puede alterar el borde del pólipo?

Sí, cualquier binarización decide cómo clasificar los píxeles ambiguos del borde. Por
eso la regla se documenta y se mantiene idéntica en todos los experimentos. Así la
comparación entre modelos sigue siendo justa.

#### ¿Por qué no guardar nuevas máscaras PNG ya binarizadas?

No es necesario en esta etapa. Conservar la fuente original y aplicar una transformación
determinista evita duplicar datos y mantiene trazabilidad. Si más adelante se materializa
una versión PNG por rendimiento, deberá guardarse como artefacto derivado con su propia
versión y hashes.

#### ¿Por qué pixel accuracy no sería suficiente?

El fondo domina gran parte de las imágenes. Un modelo podría obtener accuracy alta
prediciendo principalmente fondo y aun así segmentar mal el pólipo. Dice e IoU miden
mejor la superposición de la región relevante.

#### ¿La binarización usa PyTorch?

No. Se realiza con Pillow y puede validarse localmente con bajo consumo. PyTorch queda
reservado para entrenamiento y evaluación en el clúster HPC de CEDIA.

#### ¿Se revisaron todas las máscaras o solo una muestra?

Se procesaron las 1.000 máscaras. También se comprobó que cada una coincide en nombre y
dimensiones con su imagen, que los JPEG pueden decodificarse y que el resultado binario
no queda vacío.

---

## División del dataset: train, validation y test

### Cómo explicarlo durante la exposición

Después de validar los 1.000 pares, los dividimos una sola vez en 700 muestras para
train, 150 para validation y 150 para test. La asignación usa la semilla fija `20260817`
y queda guardada por UUID, por lo que todos los modelos se compararán sobre exactamente
las mismas imágenes.

No usamos los folds oficiales de HyperKvasir porque fueron publicados para los 10.662
ejemplos del problema de clasificación, no como un protocolo train/validation/test
específico para segmentación.

### Estratificación por tamaño

Una lesión pequeña y una grande plantean dificultades distintas. Ordenamos las muestras
por la fracción de píxeles ocupada por el pólipo y formamos tres estratos:

- pequeño: hasta aproximadamente `7,70 %`;
- mediano: entre `7,70 %` y `16,69 %`;
- grande: más de `16,69 %`.

Validation y test contienen 50 muestras de cada estrato. Train contiene 234 pequeñas,
233 medianas y 233 grandes. Así evitamos que una partición resulte accidentalmente mucho
más fácil o difícil por el tamaño de sus pólipos.

### Preguntas de la audiencia y respuestas

#### ¿Por qué usar 70/15/15?

Con solo 1.000 pares necesitamos conservar suficientes ejemplos para aprender, pero
también reservar conjuntos independientes con tamaño útil. La proporción deja 700 para
entrenamiento y 150 para cada etapa de selección y evaluación final.

#### ¿Qué diferencia existe entre validation y test?

Validation permite elegir checkpoints, arquitectura e hiperparámetros. Test permanece
aislado y se evalúa una sola vez después de cerrar todas esas decisiones.

#### ¿Cómo se evita el data leakage?

Cada UUID aparece exactamente una vez y los duplicados exactos se asignan como grupo a
un solo split. Además, el pipeline recibe la partición ya creada y no puede reorganizarla
durante el entrenamiento.

#### ¿Existe separación por paciente?

No podemos garantizarla porque los datos publicados no incluyen identificadores
suficientes de paciente o procedimiento. Esta es una limitación explícita: garantizamos
separación por archivo y duplicado exacto, no independencia clínica.

#### ¿Por qué no cambiar el split si un resultado es malo?

Porque adaptar la partición después de observar métricas introduce sesgo y dificulta una
comparación justa. La semilla, asignaciones y hashes quedan fijados antes de entrenar.

---

## Validación del entorno en CEDIA

### Mensaje principal

Antes de entrenar verificamos el entorno, la GPU y el pipeline con trabajos cortos de
Slurm. Esto reduce el riesgo de descubrir errores durante un entrenamiento costoso.

### Evidencia obtenida

- Entorno: Python 3.11.14 y PyTorch 2.10.0+cu128 suministrado por CEDIA.
- Hardware: una NVIDIA A100-SXM4-40GB detectada correctamente.
- Smoke GPU: CUDA disponible y ciclo forward/backward completado.
- Datos: 1.000 pares reconstruidos con los mismos hashes que en local.
- Pipeline: batches de imágenes `[8, 3, 256, 256]` y máscaras `[8, 1, 256, 256]`.
- Splits verificados: 700 train, 150 validation y 150 test.

### Cómo interpretarlo

Estos resultados demuestran que la infraestructura y los datos están listos para
implementar el baseline. Todavía no son resultados de entrenamiento ni métricas de
calidad del modelo.

### Pregunta probable

#### ¿Por qué usar Slurm incluso para pruebas cortas?

Porque el nodo de acceso solo administra archivos y trabajos. Slurm asigna de forma
explícita CPU, memoria y GPU en los nodos de cómputo y deja evidencia reproducible de
cada ejecución.

---

## Funciones de pérdida: BCEWithLogits y Dice

### Cómo explicarlo durante la exposición

Usaremos dos funciones complementarias para enseñar al modelo a separar pólipo y fondo:

- **BCEWithLogitsLoss** evalúa cada píxel de forma individual. Penaliza si un píxel de
  pólipo se predice como fondo o viceversa. Recibe directamente los logits y combina la
  sigmoid internamente para mejorar la estabilidad numérica.
- **Dice loss** evalúa la superposición global entre la máscara predicha y la real. Da
  mayor importancia a la región del pólipo y ayuda cuando el fondo ocupa la mayor parte
  de la imagen.

### Por qué se combinan

BCE aporta aprendizaje preciso por píxel y Dice optimiza la forma y cobertura de la
lesión. Juntas equilibran clasificación local y calidad global de la segmentación.

#### ¿Por qué no usar solamente BCE?

Porque el desbalance favorece al fondo. Un modelo podría acertar muchos píxeles de
fondo y aun representar mal el pólipo; Dice compensa ese problema al medir solapamiento.

---
En el contexto de las redes neuronales y la segmentación de imágenes, el mejor valor para el Dice Loss es 0.
¿Qué significan los valores?
Valor cercano a 0: Es el valor ideal. Significa que la predicción del modelo y la etiqueta real se superponen casi por completo (hay un acierto perfecto).
Valor cercano a 1: Es un mal resultado. Indica que no hay coincidencia ni superposición entre el objeto predicho y el real.

---

## Baseline U-Net con encoder ResNet-34

### Cómo explicarlo durante la exposición

El baseline recibe una imagen RGB de `256 × 256` y produce un mapa de logits de un
canal con la misma resolución. U-Net combina dos recorridos:

1. **Encoder ResNet-34:** extrae características desde bordes y texturas hasta patrones
   de mayor nivel. Comienza con pesos aprendidos en ImageNet.
2. **Decoder U-Net:** recupera progresivamente la resolución y combina información del
   encoder mediante conexiones de salto para localizar mejor los bordes del pólipo.

La salida no incluye sigmoid. Durante la pérdida usamos los logits directamente y,
para calcular métricas o generar una máscara, aplicamos sigmoid y umbral inicial `0.5`.

### Parámetros principales

- Arquitectura: U-Net.
- Encoder: ResNet-34 preentrenado en ImageNet.
- Entrada: `[B, 3, 256, 256]`.
- Salida: `[B, 1, 256, 256]`.
- Parámetros entrenables: `24.436.369`.
- Pérdida: `BCEWithLogitsLoss + Dice loss`, con pesos `1.0 + 1.0`.
- Métricas: Dice, IoU, precisión y recall por píxel.

### Resultado de validación técnica

En una A100 de 40 GB se ejecutó un batch real de ocho imágenes con pesos ImageNet:

- forward y backward completados sin errores;
- logits y gradientes finitos;
- forma de salida correcta;
- pérdida inicial `1,3424`;
- memoria GPU pico aproximada: `908 MiB`.

Este resultado demuestra que el baseline puede entrenarse en CEDIA. La pérdida y las
métricas de este batch pertenecen a un modelo sin entrenar y no miden su calidad final.

### Preguntas de la audiencia y respuestas

#### ¿Por qué usar U-Net?

Porque fue diseñada para segmentación y combina contexto con localización precisa. Es
un baseline conocido, comprensible y adecuado para un dataset pequeño.

#### ¿Por qué usar ResNet-34?

Ofrece un equilibrio razonable entre capacidad y coste. Es suficientemente profunda
para extraer características útiles sin comenzar con un encoder excesivamente grande.

#### ¿Por qué comenzar con pesos ImageNet?

Porque transfieren características visuales generales y reducen la necesidad de
aprender todo desde cero con solo 700 imágenes de entrenamiento.

#### ¿Las métricas del smoke test son el resultado del modelo?

No. Solo verifican que datos, arquitectura, pérdida, métricas y gradientes funcionan
juntos. El rendimiento se medirá después del entrenamiento y la selección por validation.

---

## Entrenamiento del baseline

### Cómo explicarlo durante la exposición

Entrenamos el U-Net/ResNet-34 con 700 imágenes y usamos 150 imágenes de validation para
medir su capacidad de generalizar. El protocolo permitía hasta 50 épocas, pero el
entrenamiento se detuvo automáticamente en la época 32 porque validation dejó de mejorar.
Este mecanismo, llamado *early stopping*, evita continuar memorizando los datos de train.

El mejor resultado apareció en la época 22, con un Dice de validation de `0,8978`. Esto
indica una superposición alta entre los pólipos predichos y las máscaras reales de
validation. Conservamos ese estado como `best.pt`; el estado de la última época se guarda
por separado como `last.pt` y no se usa como el mejor modelo.

### Evidencia principal

- Hardware: una NVIDIA A100 de 40 GB con precisión mixta.
- Mejor Dice de validation: `0,8978` en la época 22.
- Parada: época 32 por *early stopping*.
- Trazabilidad: métricas por época, configuración y entorno registrados en MLflow.
- Integridad: `best.pt` y `last.pt` verificados mediante SHA-256.

![Curvas de pérdida y Dice del baseline](assets/unet-resnet34-training-curves.svg)

La pérdida de train continúa bajando y su Dice sigue subiendo, mientras validation se
estabiliza cerca de `0,89`. Esta separación indica que prolongar el entrenamiento ya no
mejoraba la generalización. Por eso se conserva la época 22 y se detiene el proceso en
la 32 después de diez épocas sin una mejora suficiente.

La figura se genera desde
[`results/unet-resnet34-baseline-history.csv`](results/unet-resnet34-baseline-history.csv)
con:

```bash
python scripts/plot_training_history.py \
  docs/results/unet-resnet34-baseline-history.csv \
  docs/assets/unet-resnet34-training-curves.svg
```

Este es un resultado de **validation**, utilizado para seleccionar el checkpoint. El
conjunto de test permaneció aislado durante esa selección y después se evaluó una sola
vez para obtener la medición final.

---

## Solución

### Cómo presentarla durante la sustentación

“Nuestra solución toma una imagen de colonoscopia y produce una máscara que señala,
píxel por píxel, dónde se encuentra el pólipo. No buscamos clasificar toda la imagen
con una sola etiqueta: queremos conservar la forma y la ubicación de la lesión para que
el resultado pueda inspeccionarse visualmente.”

### ¿Con qué datos construimos la solución?

Trabajamos con **Kvasir-SEG**, un dataset público compuesto por **1.000 imágenes
endoscópicas**, cada una acompañada por una máscara de referencia dibujada sobre el
pólipo. Esta correspondencia imagen–máscara permite enseñar al modelo no solo que hay
una lesión, sino exactamente qué región debe segmentar.

La división experimental fue:

- **700 imágenes de entrenamiento:** el modelo aprende sus parámetros.
- **150 imágenes de validation:** se selecciona la mejor época sin consultar test.
- **150 imágenes de test:** se realiza una única evaluación final.

Los tres conjuntos se estratificaron por el tamaño relativo del pólipo y contienen
casos pequeños, medianos y grandes. También se agruparon duplicados exactos antes de
dividir los datos para reducir el riesgo de *data leakage*. Las imágenes se ajustan a
`256 × 256` píxeles y las máscaras se convierten de forma reproducible a valores
binarios: fondo o pólipo.

### ¿Qué arquitectura utilizamos?

La solución combina dos componentes:

- **ResNet-34 como encoder:** analiza la imagen y aprende características visuales en
  distintos niveles, desde bordes y texturas hasta patrones más complejos.
- **U-Net como decoder:** recupera progresivamente la resolución espacial y construye
  la máscara final. Sus conexiones de salto reutilizan detalles del encoder para
  localizar mejor los bordes del pólipo.

El modelo recibe una imagen RGB y devuelve un mapa de probabilidad del mismo tamaño. Al
aplicar un umbral de `0,5`, cada píxel se convierte en fondo o pólipo. La arquitectura
contiene `24.436.369` parámetros entrenables y parte de pesos ImageNet para aprovechar
características visuales aprendidas previamente.

```text
Imagen RGB 256 × 256
        ↓
ResNet-34: extrae características
        ↓  conexiones de salto
U-Net: recupera forma y ubicación
        ↓
Probabilidad por píxel
        ↓  umbral 0,5
Máscara binaria del pólipo
```

### ¿Cómo aprende y cómo evitamos elegir el resultado a conveniencia?

Durante el entrenamiento combinamos **Binary Cross-Entropy**, que corrige cada píxel,
con **Dice loss**, que premia la superposición de la región completa. El entrenamiento
podía llegar a 50 épocas, pero se detuvo en la 32 mediante *early stopping*. El
checkpoint elegido fue el de la época 22 porque obtuvo el mejor Dice en validation.

Una forma sencilla de contarlo es esta:

“Imaginen que tenemos dos profesores corrigiendo al modelo. BCE revisa píxel por píxel:
‘aquí marcaste fondo, aquí marcaste pólipo’. Dice se aleja un poco y observa el dibujo
completo: ‘¿la región predicha realmente coincide con la lesión?’. Usamos ambos porque
necesitamos precisión local sin perder la forma global.”

El algoritmo que actualiza los pesos es **AdamW**, con *learning rate* inicial
`1 × 10⁻⁴` y *weight decay* `1 × 10⁻⁴`. AdamW adapta el tamaño de cada actualización y
separa la regularización de la actualización del gradiente. Cuando validation deja de
mejorar durante tres épocas, **ReduceLROnPlateau** reduce el *learning rate* a la mitad:
es como pasar de movimientos grandes a ajustes finos cuando ya estamos cerca de una
buena solución.

### ¿Por qué elegimos estos hiperparámetros?

“Los hiperparámetros no se eligieron para perseguir el mejor número en test. Definimos
un baseline conservador antes de la evaluación final y mantuvimos test fuera de todas
las decisiones. Cada valor cumple una función concreta dentro del experimento.”

| Elección | Valor | Razón de uso |
|---|---:|---|
| Resolución | `256 × 256` | Conserva suficiente estructura del pólipo con un coste manejable para entrenar y repetir el experimento. |
| Batch size | `8` | Mantiene batches reales completos y dejó un margen amplio en la A100; además evita depender de un batch excesivamente grande para un dataset pequeño. |
| Pesos iniciales | ImageNet | Aprovechan características visuales generales y reducen la necesidad de aprender desde cero con solo 700 imágenes de train. |
| Optimizador | AdamW | Ofrece actualizaciones adaptativas y separa el weight decay de la actualización del gradiente. Es una opción estable para establecer el baseline. |
| Learning rate | `1 × 10⁻⁴` | Es un inicio conservador para ajustar un encoder preentrenado sin modificar sus representaciones de forma demasiado brusca. |
| Weight decay | `1 × 10⁻⁴` | Introduce regularización moderada para limitar el sobreajuste sin dominar la optimización. |
| Pérdida | BCE + Dice, pesos `1,0 + 1,0` | BCE corrige píxeles individuales y Dice prioriza el solapamiento; pesos iguales evitan favorecer una componente sin evidencia previa. |
| Augmentations | flips, rotación `±15°`, brillo y contraste | Simulan variaciones plausibles de orientación e iluminación sin deformar agresivamente la anatomía. Solo se aplican en train. |
| Scheduler | ReduceLROnPlateau | Reduce el learning rate a la mitad tras tres épocas sin mejora y permite ajustes más finos cuando validation se estanca. |
| Máximo de épocas | `50` | Establece un presupuesto suficiente, mientras early stopping evita consumirlo si el modelo deja de mejorar. |
| Early stopping | paciencia `10` | Da margen para fluctuaciones de validation, pero detiene el entrenamiento antes de prolongar el sobreajuste. |
| Selección | mayor Dice de validation | Dice mide directamente el solapamiento y es más informativo que accuracy cuando el fondo domina los píxeles. |
| Umbral | `0,5` | Es el umbral binario inicial natural y quedó fijado antes de test para evitar ajustarlo sobre la evaluación final. |

Estas razones hacen que la configuración sea **defendible y reproducible**, pero no
demuestran que cada valor sea óptimo. No se ejecutó una búsqueda sistemática de
hiperparámetros. Por eso el resultado debe presentarse como el rendimiento de un baseline
bien controlado, no como el máximo rendimiento posible de U-Net/ResNet-34.

#### ¿Es correcto ejecutar dos semillas adicionales?

Sí. Ejecutamos dos semillas adicionales manteniendo todos los hiperparámetros y el mismo
split; únicamente cambió la semilla, que afecta la inicialización y el orden de los
batches. Reportamos las tres ejecuciones completas mediante media y desviación estándar,
sin seleccionar u ocultar la menos favorable. Como test ya había sido observado, este
trabajo se describe como un análisis posterior de estabilidad, no como una nueva
validación ciega ni como ajuste de hiperparámetros.

“En resumen, nuestra solución une datos trazables, una arquitectura diseñada para
segmentación y un protocolo que separa aprendizaje, selección y evaluación. Solo después
de congelar estas decisiones abrimos test para medir el resultado final.”

---

## Evaluación final sobre test

### Cómo explicarlo durante la exposición

Después de cerrar arquitectura, entrenamiento, checkpoint y umbral, evaluamos `best.pt`
una sola vez sobre las 150 imágenes de test. El modelo alcanzó:

- Dice: `0,9184`;
- IoU: `0,8491`;
- precisión: `0,9237`;
- recall: `0,9131`.

Esto significa que la predicción presenta una superposición alta con las máscaras reales
y mantiene un equilibrio razonable entre regiones detectadas incorrectamente y regiones
del pólipo omitidas. Son métricas micro calculadas sumando todos los píxeles de test.

La matriz de confusión contiene `1.390.325` verdaderos positivos, `114.779` falsos
positivos y `132.293` falsos negativos. Por clase real, el modelo reconoce correctamente
el `98,62 %` del fondo y el `91,31 %` de los píxeles de pólipo.

### El promedio no cuenta toda la historia

El Dice por imagen tuvo mediana `0,9549`, máximo `0,9890` y mínimo `0,0775`. La mayoría
de los casos obtiene una segmentación sólida, pero existen fallos severos que el valor
agregado puede ocultar. En el peor ejemplo, el modelo detecta solo una pequeña zona de
una lesión extensa; este caso debe analizarse y no descartarse como un simple outlier.

**Mejor caso — Dice `0,9890`:**

![Mejor caso de test](assets/test/best-case.png)

**Caso cercano a la mediana — Dice `0,9548`:**

![Caso mediano de test](assets/test/median-case.png)

**Peor caso — Dice `0,0775`:**

![Peor caso de test](assets/test/worst-case.png)

Los datos fuente permanecen en [`results/test/`](results/test/) y el run MLflow final es
`73876309ec7c45e09023574a02a47475`. Estos resultados describen el desempeño sobre
Kvasir-SEG; no constituyen por sí solos una validación clínica ni garantizan el mismo
rendimiento en otros equipos, hospitales o poblaciones.

---

## Estabilidad del resultado en tres ejecuciones

### Gancho para iniciar esta parte

“Hasta aquí tenemos un buen resultado, pero queda una pregunta incómoda: ¿fue mérito del
modelo o tuvimos suerte con una ejecución? Para comprobarlo hicimos algo parecido a
preparar tres veces la misma receta: conservamos los ingredientes, las cantidades y el
horno; solo cambió el orden inicial de la preparación.”

En el experimento, la “receta” fue la arquitectura U-Net/ResNet-34, el split
`700/150/150`, la resolución, las augmentations, la pérdida, el optimizador, el *early
stopping* y el umbral `0,5`. Lo único que cambió fue la semilla. Cada réplica eligió su
checkpoint usando exclusivamente validation y luego se evaluó sobre las mismas 150
imágenes de test.

### La evidencia que conviene mostrar

| Semilla | Dice test | Cómo decirlo |
|---:|---:|---|
| `20260817` | `0,9184` | Ejecución original |
| `20260818` | `0,9193` | Réplica con el resultado más alto |
| `20260819` | `0,9135` | Réplica con el resultado más bajo |
| **Resumen** | **`0,9171 ± 0,0031`** | Media ± desviación estándar muestral |

“Las tres preparaciones no salieron idénticas, porque una red neuronal siempre tiene
algo de azar. Sin embargo, quedaron muy cerca: entre el Dice más alto y el más bajo hay
solo `0,0058`. La cifra `0,9171 ± 0,0031` resume precisamente eso: el centro del resultado
y cuánto se movió entre las tres ejecuciones.”

La conclusión defendible es que el baseline muestra **estabilidad inicial ante el cambio
de semilla bajo este protocolo**. No conviene decir que “el modelo siempre obtendrá
0,9171” ni que ya está clínicamente validado. Las tres ejecuciones utilizaron las mismas
150 imágenes de test: siguen siendo 150 casos, no 450 casos independientes. Además,
`n=3` permite una primera comprobación de estabilidad, pero no reemplaza validación
cruzada ni evaluación externa.

### Guion breve para contarlo sin recitar una tabla

“Piensen en el primer Dice de `0,9184` como una fotografía. Se ve bien, pero una sola
fotografía no nos dice si el resultado se repetirá. Por eso tomamos dos fotografías más
con la misma cámara y bajo las mismas condiciones, cambiando únicamente la semilla.

¿Qué ocurrió? Obtuvimos `0,9184`, `0,9193` y `0,9135`. No elegimos la mejor para decorar
el póster; mostramos las tres. Al resumirlas, el Dice fue `0,9171 ± 0,0031`. La variación
es pequeña, así que el buen resultado no parece depender de una única ejecución
afortunada.

Ahora bien, estabilidad no es lo mismo que universalidad. Probamos tres veces el mismo
protocolo sobre los mismos 150 casos. Por eso el siguiente nivel de evidencia fue cambiar
los casos mediante validación cruzada; después todavía será necesario evaluar datos de
otros centros. Nuestro resultado no cierra la historia: nos dice que vale la pena
continuarla.”

### Respuestas rápidas para preguntas del público

#### ¿Qué es una semilla?

Es el punto de partida que controla componentes aleatorios, como la inicialización y el
orden de los batches. Cambiarla permite comprobar si el resultado era demasiado frágil.

#### ¿Qué significa el símbolo ±?

El `0,9171` es la media de las tres ejecuciones y el `0,0031` es su desviación estándar
muestral. No representa un margen de error clínico ni un intervalo de confianza.

#### ¿Por qué no reportar solo el mejor run?

Porque elegirlo después de ver test exageraría el rendimiento. La estabilidad se evalúa
mostrando también la réplica menos favorable.

#### ¿Tres runs equivalen a 450 imágenes de test?

No. Son tres evaluaciones de modelos entrenados con semillas distintas sobre las mismas
150 imágenes. Miden sensibilidad al entrenamiento aleatorio, no diversidad adicional de
pacientes o centros.

---

## Validación cruzada: cambiar los casos, no solo la suerte

### Gancho para conectar con el público

“Repetir la receta tres veces respondió una pregunta: el resultado no parecía depender
de una semilla afortunada. Pero todavía estábamos cocinando con la misma caja de
ingredientes. Entonces hicimos una prueba más exigente: cambiamos qué imágenes se usan
para aprender y cuáles se dejan fuera.”

Construimos **cinco folds externos**. En cada recorrido usamos 700 imágenes para train,
100 para validation y 200 como evaluación externa. Los folds externos no se solapan:
cada una de las 1.000 imágenes de Kvasir-SEG fue evaluada exactamente una vez por un
modelo que no la utilizó para entrenar. Mantuvimos fija la arquitectura U-Net/ResNet-34,
AdamW, BCE + Dice, augmentations, semilla y umbral `0,5`; de esta manera, la variable que
queríamos observar era la composición de los datos.

### Resultado que conviene revelar primero

> **Dice externo en cinco folds: `0,8972 ± 0,0047`.**

| Fold | Dice externo | Lectura para el presentador |
|---:|---:|---|
| 1 | `0,8961` | Cercano al promedio |
| 2 | `0,9001` | Ligeramente superior |
| 3 | `0,8961` | Prácticamente igual al fold 1 |
| 4 | `0,9031` | Resultado más alto |
| 5 | `0,8906` | Resultado más bajo |

“Lo interesante no es escoger el `0,9031` y esconder el resto. Lo importante es que los
cinco resultados permanecieron en una franja estrecha. Entre el mayor y el menor hay
aproximadamente `0,0125`. Eso nos dice que el baseline conserva un comportamiento
relativamente estable cuando cambiamos los casos que le toca aprender.”

Al agrupar los píxeles de las 1.000 predicciones *out of fold*, el Dice fue `0,8972`,
prácticamente igual a la media entre folds. Por imagen, la mediana fue `0,9463`: un caso
típico rindió mejor que el valor agregado. Sin embargo, el mínimo fue `0,0`, lo que
significa que al menos una imagen quedó completamente sin solapamiento.

### El giro de la historia

“Aquí aparece una lección importante: un modelo puede ser estable en promedio y aun
fallar por completo en un caso particular. Es parecido a un estudiante que mantiene una
buena calificación durante cinco exámenes, pero deja una pregunta en blanco. El promedio
nos habla de consistencia; la pregunta en blanco nos muestra dónde debemos investigar.”

El Dice `0,8972 ± 0,0047` de validación cruzada y el `0,9171 ± 0,0031` de las tres
semillas responden preguntas distintas y no deben tratarse como una competencia directa.
Las semillas repitieron el mismo split de 150 casos; los cinco folds cambiaron la
composición y cubrieron las 1.000 imágenes. La validación cruzada es una prueba interna
más amplia, aunque sigue usando un solo dataset público.

### Guion oral breve

“Primero comprobamos que el modelo no dependiera de una sola semilla. Después elevamos
la dificultad: construimos cinco particiones y conseguimos que cada imagen fuera
evaluada fuera de su propio entrenamiento. El Dice fue `0,8972 ± 0,0047`. En otras
palabras, el resultado se mantuvo cercano aunque cambiáramos los casos.

Pero no queremos contar solamente la parte cómoda. La mediana por imagen fue alta,
`0,9463`, mientras el peor caso obtuvo Dice `0`. Esa distancia entre el caso típico y el
fallo extremo marca nuestra siguiente tarea: no basta con mejorar el promedio; debemos
entender qué características hacen que una lesión desaparezca para el modelo.”

---

## Barreras que encontramos y cómo las resolvimos

### Cómo introducir esta parte

“Entrenar una red fue solo una parte del trabajo. La otra fue construir un experimento
en el que pudiéramos confiar. Las barreras no fueron adornos del proyecto: cada una podía
cambiar el resultado o impedir reproducirlo.”

#### 1. Las máscaras parecían binarias, pero no lo eran

Kvasir-SEG almacena las máscaras como JPEG. La compresión introduce valores intermedios
en los bordes. Definimos una binarización única con umbral `128`, conservamos los
originales y aplicamos la misma regla en train, validation y evaluación.

**Cómo decirlo:** “Antes de enseñar al modelo dónde estaba el pólipo, tuvimos que
asegurarnos de que todos habláramos el mismo idioma para definir sus bordes.”

#### 2. El fondo domina la imagen

Solo alrededor del `15,64 %` de los píxeles pertenece globalmente al pólipo. Accuracy
podría verse bien aunque el modelo ignorara parte de la lesión. Por eso usamos Dice e IoU
como métricas y combinamos BCE con Dice loss durante el aprendizaje.

#### 3. Un split conveniente podía engañarnos

Estratificamos por tamaño y mantuvimos juntos los duplicados exactos. Después repetimos
con tres semillas y finalmente usamos cinco folds externos. Cada paso atacó una fuente
distinta de incertidumbre: azar del entrenamiento y composición del dataset.

#### 4. MLflow podía competir consigo mismo

Una evaluación terminó la inferencia, pero falló al registrar artefactos porque el puerto
`5000` seguía ocupado. No repetimos la inferencia: verificamos los archivos y recuperamos
el registro de manera auditable. Para los experimentos posteriores encadenamos los jobs
y asignamos un puerto MLflow derivado de cada `SLURM_JOB_ID`, manteniendo un solo escritor
sobre SQLite.

**Analogía:** “Era como tener dos personas intentando escribir al mismo tiempo en el
mismo cuaderno. Organizamos una fila y dimos a cada conversación su propia puerta.”

#### 5. Un job recibió una terminación externa

El primer intento del fold 4 recibió `SIGKILL` a los 28 segundos. La memoria usada era
aproximadamente `1,7 GiB` de los `16 GiB` solicitados y no había timeout ni checkpoint;
por eso no lo etiquetamos como OOM sin evidencia. Conservamos los folds completos,
reenviamos únicamente el cuarto y redirigimos la dependencia del quinto. Ambos terminaron
correctamente.

**Mensaje clave:** “Reproducibilidad también significa saber recuperarse sin borrar la
historia, sin repetir lo que ya era válido y sin convertir una sospecha en una causa.”

---

## ¿Cuál es el siguiente paso para mejorar el modelo?

### Gancho de transición

“Ya respondimos si el baseline es repetible. La siguiente pregunta no es cómo decorar
el mismo número, sino qué cambio concreto puede mejorar la representación visual del
pólipo.”

El siguiente experimento recomendado es comparar el encoder actual **ResNet-34** con
**EfficientNet-B0**, manteniendo U-Net como decoder y congelando el resto del protocolo.
EfficientNet-B0 escala profundidad, anchura y resolución de forma equilibrada y puede
ofrecer características competitivas con un uso eficiente de parámetros. Esto es una
hipótesis que debemos probar, no una mejora que podamos afirmar por anticipado.

### Cómo hacer una comparación justa

- Mantener los mismos folds, resolución `256 × 256`, augmentations y máscaras.
- Conservar BCE + Dice, AdamW, scheduler, early stopping y umbral `0,5`.
- Inicializar ambos encoders con pesos ImageNet.
- Elegir cada checkpoint únicamente por validation.
- Evaluar ambos modelos sobre los mismos folds externos.
- Reportar los cinco pares de resultados, coste de entrenamiento, parámetros y memoria.
- Analizar especialmente los casos donde ResNet-34 obtuvo Dice bajo o `0`.

La comparación debe ser **pareada por fold**: para cada conjunto externo observamos si
EfficientNet-B0 mejora o empeora respecto a ResNet-34. Así evitamos atribuir al encoder
una diferencia causada por haber usado imágenes distintas.

### Cierre sugerido de la presentación

“Nuestro resultado no es solamente un Dice. Es una cadena de decisiones verificables:
datos preparados con una regla común, U-Net/ResNet-34 para conservar contexto y
localización, AdamW para optimizar, BCE + Dice para equilibrar píxeles y región, y cinco
folds para comprobar estabilidad.

El modelo es consistente, pero no infalible. El siguiente paso será enfrentar
ResNet-34 con EfficientNet-B0 bajo exactamente las mismas condiciones y preguntarnos no
solo quién obtiene el promedio más alto, sino quién rescata mejor los casos que hoy se
nos escapan. Ahí es donde una métrica deja de ser un número y se convierte en una pista
para construir una solución mejor.”

---

## Conclusiones

### Ideas clave para la diapositiva o el póster

- U-Net con encoder ResNet-34 logró segmentar pólipos con **Dice externo
  `0,8972 ± 0,0047`** en cinco folds.
- Cada una de las **1.000 imágenes** fue evaluada una vez fuera de su entrenamiento.
- Las tres semillas obtuvieron Dice `0,9171 ± 0,0031` sobre el split original, lo que
  muestra baja sensibilidad inicial al azar del entrenamiento.
- La mediana Dice por imagen fue `0,9463`, pero el mínimo fue `0`: un promedio estable
  no elimina fallos completos en casos individuales.
- El baseline es reproducible y consistente dentro de Kvasir-SEG, pero todavía no tiene
  validación externa ni clínica.

### Cómo contarlo al público

“¿Qué podemos concluir después de entrenar, repetir y cambiar los datos? Primero, que el
modelo aprendió algo útil: cuando una imagen se dejó fuera de su entrenamiento, la
superposición promedio se mantuvo cerca de `0,90`.

Segundo, que el resultado no parece una coincidencia. Cambiamos la semilla tres veces y
después cambiamos la composición de los datos en cinco folds. En ambos experimentos la
variación fue pequeña. Es como comprobar un puente primero haciendo pasar varias veces
el mismo vehículo y luego usando cargas distribuidas de otra manera: cada prueba responde
una duda diferente sobre su estabilidad.

Pero la tercera conclusión es la que nos obliga a ser responsables: estabilidad no
significa perfección. La imagen típica alcanzó un Dice cercano a `0,95`, mientras al
menos un caso no tuvo solapamiento. Por eso no presentamos este modelo como herramienta
clínica terminada. Lo presentamos como un baseline sólido, medido con transparencia y
con fallos concretos que ya sabemos dónde buscar.”

### Frase final de conclusión

> “El modelo es consistente en promedio; nuestro siguiente reto es convertir esa
> consistencia en seguridad también para los casos difíciles.”

---

## Nuestra contribución

### ¿Qué aportamos con este proyecto?

1. **Un pipeline reproducible de segmentación.** Construimos el recorrido completo desde
   Kvasir-SEG hasta la máscara predicha: validación de imágenes, binarización consistente,
   splits trazables, entrenamiento, selección de checkpoints, evaluación y artefactos.
2. **Un baseline técnico claramente definido.** Documentamos U-Net/ResNet-34, pesos
   ImageNet, AdamW, BCE + Dice, scheduler, early stopping y umbral `0,5`, evitando que el
   resultado dependa de decisiones implícitas.
3. **Evidencia de estabilidad en dos dimensiones.** Las tres semillas estudian el azar
   del entrenamiento; los cinco folds estudian la composición del dataset. Reportamos
   todas las ejecuciones, no solamente la más favorable.
4. **Trazabilidad experimental.** Cada run conserva configuración, métricas, entorno,
   checkpoint y SHA-256 en MLflow. Los jobs encadenados y los puertos por ejecución
   reducen conflictos operativos sin borrar el historial de incidentes.
5. **Una evaluación que no esconde los fallos.** Combinamos métricas globales,
   distribución por imagen y paneles cualitativos. El caso con Dice `0` permanece como
   evidencia y como objetivo de mejora.
6. **Una base justa para el siguiente experimento.** Los mismos cinco folds permiten
   comparar ResNet-34 con EfficientNet-B0 de manera pareada y atribuir mejor las
   diferencias al encoder.

### Cómo explicarla sin sonar como una lista de archivos

“Nuestra principal contribución no es afirmar que inventamos U-Net o ResNet-34. Estas
arquitecturas ya existen. Nuestro aporte está en convertirlas en un experimento completo,
trazable y honesto para este problema.

Construimos una línea de evidencia: definimos cómo interpretar las máscaras, evitamos
que duplicados cruzaran particiones, registramos cada entrenamiento, repetimos con
semillas distintas y finalmente hicimos que las 1.000 imágenes pasaran una vez por una
evaluación externa al entrenamiento.

En otras palabras, no entregamos solamente un modelo; entregamos una forma de saber de
dónde salió cada número, bajo qué condiciones puede repetirse y en qué casos todavía no
debemos confiar. Esa base nos permite hacer la siguiente comparación —ResNet-34 frente a
EfficientNet-B0— sin empezar de cero y sin mover las reglas después de ver el resultado.”

### Mensaje de contribución en una sola frase

> “Nuestra contribución es un baseline de segmentación reproducible, auditado y evaluado
> con estabilidad, que convierte un buen resultado en una base verificable para mejorar.”

---

## Texto recomendado para describir los resultados en el póster

### Resumen en viñetas

- Validación cruzada de **cinco folds**: cada una de las 1.000 imágenes fue evaluada una
  vez fuera de su entrenamiento.
- Rendimiento externo: **Dice `0,8972 ± 0,0047`**, con valores por fold entre `0,8906`
  y `0,9031`.
- Tres semillas sobre el split original obtuvieron **Dice `0,9171 ± 0,0031`**; este
  resultado complementa los folds al medir sensibilidad al azar del entrenamiento.
- Sobre las 1.000 predicciones *out of fold*: **precisión `0,9093`** y **recall
  `0,8855`** agrupados por píxel.
- El desempeño típico fue superior al agregado: **mediana Dice `0,9463`**, pero el
  mínimo de `0` revela al menos un fallo completo de solapamiento.
- En el análisis del split original, el tamaño no explicó por sí solo los errores: el
  peor caso perteneció al grupo de pólipos grandes.

### Explicación corta en tono de exposición

“La pregunta no era solamente si el modelo podía dibujar una máscara, sino si el buen
resultado sobreviviría al cambiar los casos. En cinco folds, cada una de las 1.000
imágenes fue evaluada fuera de su entrenamiento. Obtuvimos Dice `0,8972 ± 0,0047`: el
resultado cambió poco entre particiones y ofrece una señal de estabilidad interna.

Pero aquí aparece la parte más importante de la historia: un promedio alto no significa
que todos los casos sean fáciles. En las predicciones *out of fold*, la mediana por
imagen fue `0,9463`, pero el peor caso cayó a `0`: estabilidad global y ausencia total de
solapamiento pueden coexistir.

Entonces, ¿qué nos llevamos de este experimento? El baseline ofrece una primera señal de
estabilidad, pero todavía puede fallar de manera importante. Por eso mostramos tanto el
resultado consolidado como el caso típico y el peor caso: nuestro objetivo no es esconder
la variación ni el error detrás de un buen promedio, sino entenderlos antes de pensar en
una aplicación clínica.”

Para acompañar este texto se recomienda usar la
[comparación cualitativa preparada para el póster](assets/poster/01-qualitative-comparison.svg),
porque muestra simultáneamente un resultado típico y la principal limitación observada.
Su sello **“3 ejecuciones · Dice `0,9171 ± 0,0031`”** añade la evidencia de estabilidad
ante semillas sin obligar al público a interpretar otro gráfico. Como ahora existe
validación cruzada, el texto principal del póster debe destacar **“5 folds · Dice
`0,8972 ± 0,0047` · 1.000 predicciones out of fold”**; el sello de tres ejecuciones puede
quedar como evidencia secundaria.
