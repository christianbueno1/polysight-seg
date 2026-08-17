# Ideas y propuestas del proyecto

Este documento registra ideas, alternativas y propuestas para el proyecto de
segmentación de pólipos. Su contenido sirve como base para la discusión y no representa
necesariamente decisiones definitivas hasta que las alternativas sean validadas
experimentalmente.

## Comparación inicial de arquitecturas

Se propone comparar dos variantes de U-Net:

1. Usar **U-Net con encoder ResNet-34** como baseline de referencia.
2. Probar **U-Net con encoder EfficientNet-B0** como segundo experimento.
3. Comparar ambas variantes usando exactamente el mismo split, las mismas
   transformaciones y el mismo protocolo de entrenamiento y evaluación.
4. Elegir la alternativa considerando Dice de validación, coste de inferencia y
   estabilidad entre épocas, no solamente el mejor resultado de una única época.

No se propone comenzar con EfficientNet-B3, B4 o B5. Debido a que Kvasir-SEG contiene
solo 1.000 pares de imagen y máscara, EfficientNet-B0 ofrece un punto de partida más
razonable por su menor coste computacional y menor riesgo de sobreajuste.

