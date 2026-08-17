# Preparación de PolySight Seg en CEDIA

## Alcance

Este procedimiento prepara el proyecto con Python 3.11 y el PyTorch suministrado por
CEDIA. Debe ejecutarse en el nodo de acceso salvo el smoke test, que se envía a un nodo
GPU mediante Slurm.

Antes de copiar comandos, confirmar los módulos y recursos vigentes:

```bash
module spider python/3.11
module spider pytorch/2.2
module spider cuda/12.4
sinfo -o '%P %a %l %D %G'
```

Si alguno no existe o sus versiones son incompatibles, detener la preparación y
registrar la configuración observada antes de modificar el proyecto.

## Obtener el código

Clonar el repositorio o actualizar una copia existente con comandos Git compatibles con
la versión disponible en CEDIA. El entrenamiento debe ejecutarse desde el branch o
commit aprobado para el experimento.

```bash
git clone URL_DEL_REPOSITORIO polysight-seg
cd polysight-seg
git status
git rev-parse HEAD
```

## Crear el entorno

Cargar primero los módulos para que el entorno virtual reutilice el PyTorch de CEDIA:

```bash
module purge
module load pytorch/2.2
module load cuda/12.4

python --version
python -c 'import torch; print(torch.__version__, torch.version.cuda)'

python -m venv --system-site-packages .venv-cluster
source .venv-cluster/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip check
```

No ejecutar estos comandos de instalación en el equipo local. Si `pip` intenta sustituir
el PyTorch proporcionado por el módulo, cancelar la instalación y revisar el entorno
antes de continuar.

## Ejecutar el smoke test GPU

Desde la raíz del repositorio:

```bash
sbatch slurm/smoke_gpu.sbatch
squeue -u "$USER"
```

Cuando termine, consultar el archivo `slurm-polysight-smoke-JOB_ID.out`. El resultado
válido debe incluir `"status": "ok"`, el nombre de la GPU y las versiones de PyTorch y
CUDA. También puede verificarse el consumo y estado final con:

```bash
sacct -j JOB_ID --format=JobID,State,Elapsed,AllocTRES,MaxRSS,ExitCode
```

La ejecución se considera fallida si no recibió GPU, CUDA no está disponible, el ciclo
forward/backward no termina o Slurm devuelve un código distinto de cero.

## Evidencia que debe conservarse

Registrar para cada preparación:

- commit exacto del repositorio;
- salida de `module list`;
- versiones de Python, PyTorch, CUDA y cuDNN;
- salida de `python -m pip freeze`;
- identificador y estado final del trabajo Slurm;
- salida completa del smoke test.

Los logs, entornos virtuales y artefactos generados no deben agregarse a Git.
