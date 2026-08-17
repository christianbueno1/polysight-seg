
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