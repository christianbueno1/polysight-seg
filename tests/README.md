# Pruebas

Las pruebas locales se limitarán a componentes ligeros que no importen PyTorch. Las
pruebas de modelo, CUDA y entrenamiento se ejecutarán en CEDIA HPC.

`test_training_config.py` valida localmente el protocolo declarativo sin importar
PyTorch ni solicitar recursos de cómputo.

`test_training_components.py` se ejecuta en `cpu-dev` y cubre loops, checkpoints,
tracking y utilidades del runner; no construye el U-Net ni solicita GPU.
