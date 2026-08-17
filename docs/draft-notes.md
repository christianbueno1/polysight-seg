
### Dataset
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
