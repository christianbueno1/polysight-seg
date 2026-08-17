
### GPU de CEDIA
El generador produjo exactamente 700/150/150. Cada validation y test contiene 50 pólipos pequeños, 50 medianos y 50 grandes; train contiene 234/233/233. Registraré esta
  implementación y después añadiré validaciones explícitas de cobertura, exclusividad y leakage.

Generación y validación de splits completadas:

  - Train: 700.
  - Validation: 150.
  - Test: 150.
  - Estratos equilibrados por tamaño.
  - Cobertura: 1.000 UUID.
  - Sin muestras solapadas.
  - Generación reproducible con semilla 20260817.
  - Hash de asignación: 2d0f1f88380314f7d633b1d84b8f6d0e662eb98ff803b25140e8b48c305f7e34.
  - Commits: c3e395c y 5480ec8.

### Cluster
`A100-SXM4-40GB` es el modelo de GPU que CEDIA te asignó para ese job.

En concreto:

* **A100** = NVIDIA A100 Tensor Core GPU, una GPU de centro de datos orientada a IA y HPC.
* **SXM4** = el formato/módulo físico de esa A100 dentro del servidor; no es una tarjeta PCIe común.
* **40GB** = tiene **40 GB de memoria HBM2** en la GPU.

Para tu proyecto, eso significa que el job `23294` realmente corrió sobre una GPU muy potente y pudo usar CUDA correctamente. El hecho de que el `forward/backward` haya funcionado confirma que PyTorch pudo mover tensores y modelo a la GPU y ejecutar tanto la pasada hacia adelante como el cálculo de gradientes.

En términos prácticos:

```text
CPU RAM          !=      GPU VRAM

memoria del nodo         40 GB HBM2 de la A100
                             ↑
                    aquí viven durante training:
                    - modelo
                    - activaciones
                    - gradientes
                    - parte del batch
```

Los **40 GB** son bastante útiles para segmentación, porque U-Net suele consumir bastante VRAM, especialmente por las activaciones intermedias del encoder y decoder.

Para el baseline que mencionas, algo como:

```text
U-Net
  +
ResNet-34 encoder
  +
256x256
  +
batch_size 8
```

debería ser una carga bastante razonable para una A100 de 40 GB. Más adelante incluso podrías medir el consumo real y decidir si aumentar el `batch_size`.

Y una diferencia importante: `A100-SXM4-40GB` **no significa que CUDA tenga 40 GB**. CUDA es la plataforma/software; los 40 GB corresponden a la memoria física de esa GPU.

### Clases
❯ cat configs/models/unet-resnet34.yaml
¿Qué probabilidad hay de que este píxel pertenezca al pólipo?

### BCE
agrragar formula en linea $\text{BCE} = -[y \log(\hat{y}) + (1 - y) \log(1 - \hat{y})]$, formula en linea.

The Binary Cross-Entropy (BCE) formula, also known as log loss, measures the performance of a machine learning model whose output is a probability value between 0 and 1. For a single data point, the formula is 
$$
\text{BCE} = -[y \log(\hat{y}) + (1 - y) \log(1 - \hat{y})]
$$
where y is the true label (0 or 1) and ŷ is the predicted probability.

# Loss functions
## Funciones de pérdida: BCEWithLogits + Dice

Para tu tarea siguiente (rama `chore/baseline-unet-resnet34`), vas a combinar dos losses que se complementan.

---

### 1. BCEWithLogitsLoss — error píxel por píxel

```
BCE = -[ y·log(σ(x)) + (1-y)·log(1-σ(x)) ]
```
donde `x` = logit crudo del modelo, `y` = etiqueta real (0 o 1), `σ` = sigmoid.

- Compara cada píxel de forma **independiente**: ¿este píxel es pólipo o fondo?
- Ya la discutimos: numéricamente estable porque nunca calcula `sigmoid()` y `log()` por separado (evita el `log(0)` que vimos antes).
- **Problema:** en tus imágenes, el pólipo suele ocupar una fracción pequeña del frame (recuerda `foreground_fraction` en `validate.py`). Con desbalance de clases, el modelo puede lograr BCE bajo simplemente prediciendo "todo fondo" y aun así fallar en capturar la forma real del pólipo.

---

### 2. Dice Loss — error de superposición global

```
Dice = 2·|A∩B| / (|A|+|B|)
DiceLoss = 1 - Dice
```
donde `A` = máscara predicha (tras sigmoid), `B` = máscara real.

- No mira píxeles aislados, mira **qué tan bien coincide la forma completa** de la región predicha contra la real.
- Es robusta al desbalance de clases — no le "premia" con score alto por acertar el fondo abrumador, mide directamente la calidad del solapamiento en la región de interés.
- **Requiere probabilidades (0 a 1)**, no logits crudos, así que hay que aplicarle `sigmoid()` explícitamente antes de calcular Dice.

---

### 3. La combinación

```
loss_total = α · BCEWithLogitsLoss(logits, target) + β · DiceLoss(sigmoid(logits), target)
```

Típicamente `α = β = 0.5` o ambos en `1.0` (pesos configurables vía YAML, siguiendo tu mismo patrón declarativo).

| | BCE | Dice |
|---|---|---|
| Qué mide | error por píxel | superposición de región |
| Sensible a desbalance | sí (débil) | no |
| Gradientes al inicio del training | estables | pueden ser ruidosos si la predicción inicial no solapa nada |
| Necesita | logits | probabilidades (sigmoid aplicado) |

Se combinan porque **BCE da estabilidad temprana** en el entrenamiento, y **Dice empuja la forma final** a parecerse a la máscara real — juntas compensan las debilidades de cada una.

---

### Contrato de formas (según tus YAMLs)

```
logits: [B, 1, 256, 256]   ← salida cruda del modelo
target: [B, 1, 256, 256]   ← máscara binaria (0/1), ya limpia por mask_threshold=128 + nearest interpolation
```

Ambas losses reciben el mismo `target`; solo la rama de Dice necesita el `sigmoid(logits)` intermedio.

¿Armamos ahora el esqueleto de `losses.py` con la clase `CombinedLoss`, siguiendo el mismo patrón de validación estricta que ya tienes en `factory.py` (con pesos `alpha`/`beta` configurables por YAML)?