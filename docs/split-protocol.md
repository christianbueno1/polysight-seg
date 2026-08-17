# Protocolo de splits de Kvasir-SEG

## Revisión de splits oficiales

El repositorio oficial de HyperKvasir publica dos archivos:

- `official_splits/2_fold_split.csv`;
- `official_splits/5_fold_split.csv`.

Cada archivo contiene 10.662 registros de datos etiquetados, además del encabezado. Esa
cifra coincide con el conjunto completo de clasificación descrito por HyperKvasir. No
se publica allí un split train/validation/test específico para los 1.000 pares de
segmentación ni un protocolo orientado a métricas píxel a píxel.

Fuentes revisadas:

- <https://github.com/simula/hyper-kvasir/tree/master/official_splits>;
- <https://github.com/simula/hyper-kvasir>.

Por tanto, los folds oficiales de clasificación no se usarán como si fueran un split
oficial de Kvasir-SEG. El proyecto generará y versionará su propio protocolo para
segmentación.

## Limitación de separación clínica

Los archivos disponibles no ofrecen identificadores suficientes de paciente o
procedimiento para garantizar independencia clínica entre splits. La partición propia
evitará solapamientos por archivo y mantendrá juntos los duplicados exactos, pero no
puede afirmar separación por paciente. Esta limitación debe acompañar todos los
resultados del estudio.

## Protocolo propuesto

La partición inicial tendrá:

```text
Train:      700 muestras (70 %)
Validation: 150 muestras (15 %)
Test:       150 muestras (15 %)
Semilla:    20260817
```

Reglas:

1. Usar exclusivamente el manifest validado de la Fase 2.
2. Agrupar duplicados exactos antes de asignar splits.
3. Estratificar por fracción de píxeles de pólipo en tres niveles: pequeño, mediano y
   grande.
4. Calcular los límites de tamaño de forma determinista y registrarlos junto al split.
5. Garantizar cobertura total y ausencia de UUID o grupos compartidos entre splits.
6. No modificar la partición después de observar métricas del modelo.
7. Usar validation para decisiones y evaluar test una sola vez con el modelo elegido.

El archivo resultante debe incluir por muestra el UUID, split, estrato y grupo de
duplicado. También debe registrar la semilla, hashes de entrada y salida, conteos y
distribución de tamaños.
