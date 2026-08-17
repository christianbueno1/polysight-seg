# Informe de splits de Kvasir-SEG

## Ejecución

- Fecha: `2026-08-17 12:27 -0500`
- Semilla: `20260817`
- Manifest de entrada SHA-256:
  `35ddd003e5ec95817761c2e4de40c1c4274fc7ec43f7690d8b30aedee7019fd4`
- Asignaciones SHA-256:
  `2d0f1f88380314f7d633b1d84b8f6d0e662eb98ff803b25140e8b48c305f7e34`
- Resultado general: `ok`

## Distribución

| Split | Pequeño | Mediano | Grande | Total |
|---|---:|---:|---:|---:|
| Train | 234 | 233 | 233 | 700 |
| Validation | 50 | 50 | 50 | 150 |
| Test | 50 | 50 | 50 | 150 |
| Total | 334 | 333 | 333 | 1.000 |

Los límites deterministas de fracción de pólipo fueron:

- pequeño: `<= 0,0769584857`;
- mediano: `> 0,0769584857` y `<= 0,1668706762`;
- grande: `> 0,1668706762`.

## Comprobaciones

- Los 1.000 UUID aparecen exactamente una vez.
- No existen UUID inesperados ni faltantes respecto al manifest.
- Los conteos son exactamente 700/150/150.
- Cada split contiene los tres estratos de tamaño.
- Ningún grupo duplicado se reparte entre splits.
- Reordenar las filas del manifest no modifica las asignaciones.
- Regenerar los archivos con la misma semilla produce contenido idéntico.

La copia actual de Kvasir-SEG no contiene grupos duplicados exactos, pero la regla de
agrupación permanece implementada para futuras versiones del manifest.

## Artefactos reproducibles

```text
85fe68a5b241f880a80d1476fdffcff88ae5b5e51c0adbe690cce023cbfe13f9  splits.csv
b8f2872b5a0c524f94db92fc42455be0b788cd3c0d362337d183def2b7ed8929  splits-summary.json
```

Ambos archivos permanecen bajo `data/processed/kvasir-seg/` y se reconstruyen desde el
manifest usando código versionado.

## Limitación

HyperKvasir no proporciona identificadores suficientes de paciente o procedimiento para
esta partición. Se garantiza separación por UUID y duplicado exacto, pero no puede
afirmarse independencia clínica entre splits.
