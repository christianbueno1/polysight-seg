# Pruebas

Las pruebas locales se limitarán a componentes ligeros que no importen PyTorch. Las
pruebas de modelo, CUDA y entrenamiento se ejecutarán en CEDIA HPC.

`test_training_config.py` valida localmente el protocolo declarativo sin importar
PyTorch ni solicitar recursos de cómputo.
