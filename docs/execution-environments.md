# Entornos de ejecución

## Decisión

El equipo local no se utilizará para instalar ni ejecutar PyTorch, entrenar modelos o
realizar otras cargas pesadas. Sus recursos son insuficientes para el entrenamiento de
los modelos de segmentación previstos.

El entrenamiento, la evaluación acelerada y las pruebas que requieran PyTorch se
ejecutarán preferentemente en el clúster HPC de CEDIA mediante Slurm. El entorno local
se reservará para Git, edición de código, documentación y validaciones ligeras que no
dependan de PyTorch.

La configuración operativa de CEDIA se describe en
[`cedia-cluster-guide.md`](cedia-cluster-guide.md).

## Sistema local de desarrollo

Información registrada el 17 de agosto de 2026:

| Componente | Especificación |
|---|---|
| Sistema operativo | Fedora Linux 44 Workstation, x86_64 |
| Kernel | Linux 7.1.8-200.fc44.x86_64 |
| Shell | zsh 5.9 |
| Entorno de escritorio | GNOME 50.4 sobre Mutter/Wayland |
| Terminal | Ptyxis 50.1 |
| Fuente de terminal | JetBrainsMono Nerd Font 14 pt |
| CPU | Intel Core i5-4430, 4 núcleos, hasta 3.20 GHz |
| GPU | NVIDIA GeForce GT 610 dedicada |
| Memoria | 15.40 GiB |
| Swap | 8.00 GiB |
| Disco raíz | 220.98 GiB, Btrfs |
| Pantalla | 1920 × 1080, 23 pulgadas, 60 Hz |
| Locale | en_US.UTF-8 |

No se registran la IP local, el tiempo de actividad ni el uso instantáneo de memoria y
disco, porque son datos transitorios y no describen las capacidades reproducibles del
entorno.
