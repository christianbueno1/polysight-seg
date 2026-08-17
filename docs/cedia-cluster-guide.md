# Guía general para usar el clúster HPC de CEDIA

## Alcance

Esta guía resume el acceso y el flujo de trabajo básico del clúster HPC de CEDIA para
cualquier proyecto. Los módulos, particiones y capacidades indicados fueron observados
entre julio y agosto de 2026 y deben verificarse antes de preparar un trabajo, porque la
configuración del clúster puede cambiar.

## Acceso por SSH

El host de acceso es:

```text
hpc.cedia.edu.ec
```

Cada persona debe usar el nombre de usuario asignado por CEDIA. Una conexión directa
puede hacerse con:

```bash
ssh USUARIO@hpc.cedia.edu.ec
```

Para simplificar comandos y transferencias, se recomienda configurar un alias en el
archivo local `~/.ssh/config`:

```sshconfig
Host cedia
    HostName hpc.cedia.edu.ec
    User USUARIO
    IdentityFile ~/.ssh/id_ed25519
```

Después se puede conectar o ejecutar una consulta remota con:

```bash
ssh cedia
ssh cedia 'hostname'
ssh cedia 'df -h'
```

El nodo observado al ingresar es `login1`. Es un nodo de acceso: allí se administran
archivos, repositorios y trabajos, pero no deben ejecutarse entrenamientos, análisis
pesados ni procesos prolongados. Las cargas de trabajo se envían a nodos de cómputo
mediante Slurm.

## Portal y soporte

- Portal: <https://hpc.cedia.edu.ec>
- Aplicaciones publicadas: Jupyter, RStudio, escritorio remoto con GPU y QGIS.
- Soporte: `noc@cedia.org.ec`

El portal puede ser útil para sesiones interactivas. Para ejecuciones reproducibles y
prolongadas se recomienda preparar scripts de Slurm.

## Transferencia de archivos

El código puede mantenerse en Git y clonarse en el clúster. Los datasets, checkpoints
y resultados grandes deben transferirse fuera de Git con `rsync` o, para casos simples,
con `scp`.

Ejemplos desde el equipo local:

```bash
rsync -av --progress dataset.tar.gz cedia:/home/USUARIO/datasets/
rsync -av --progress proyecto/ cedia:/home/USUARIO/projects/proyecto/
rsync -av --progress cedia:/home/USUARIO/projects/proyecto/results/ ./results/
scp archivo.txt cedia:/home/USUARIO/
```

Antes de transferir muchos datos, crear explícitamente los directorios remotos y
confirmar las políticas de almacenamiento aplicables a la cuenta.

## Almacenamiento

El directorio personal normalmente se encuentra en:

```text
/home/USUARIO
```

Observaciones realizadas el 29 y 30 de julio de 2026:

- `/home` está servido por NFS y es almacenamiento compartido;
- no se observaron variables `$SCRATCH` ni `$WORK`;
- `myquota` no estaba instalado y `quota -s` no produjo información;
- `/sw` contiene software compartido y no debe usarse para datos;
- `/tmp` pertenece al nodo donde se crea y no debe considerarse persistente ni
  necesariamente visible desde otros nodos.

La capacidad libre mostrada por `df -h` corresponde al sistema compartido, no a la
cuota garantizada de una cuenta. Para proyectos con datasets grandes se debe confirmar
con CEDIA la cuota, retención, respaldo y ubicación recomendada.

Consultas útiles:

```bash
df -h
du -sh /home/USUARIO/*
quota -s
```

## Módulos de software

El clúster utiliza módulos de entorno. Los comandos principales son:

```bash
module avail
module spider NOMBRE
module load NOMBRE/VERSION
module list
module purge
```

Módulos observados:

| Herramienta | Módulo observado |
|---|---|
| Python | `python/3.11` |
| PyTorch | `pytorch/2.2` |
| CUDA | `cuda/12.4` |
| OpenCV con GPU | `opencv/4.10.0/gpu` |

La tabla no es un inventario completo ni permanente. Siempre se debe ejecutar
`module avail` o `module spider` para conocer las versiones vigentes y comprobar que la
combinación cargada es compatible.

Un ejemplo para un proyecto PyTorch es:

```bash
module purge
module load pytorch/2.2
module load cuda/12.4

python --version
python -c 'import torch; print(torch.__version__, torch.version.cuda)'
```

Si el software requerido no está disponible como módulo, CEDIA informa que Enroot está
disponible para ejecutar contenedores. Su uso y las imágenes permitidas deben validarse
con la documentación o el soporte del clúster.

## Git y entornos Python

La versión de Git observada en el clúster es `1.8.3.1`. Es antigua, por lo que algunos
comandos o características modernas pueden no estar disponibles. Conviene usar comandos
Git básicos y validar cualquier automatización que dependa de opciones recientes.

Para Python puede crearse un entorno que reutilice las librerías del módulo cargado:

```bash
module purge
module load pytorch/2.2
module load cuda/12.4

python -m venv --system-site-packages .venv-cluster
source .venv-cluster/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Las versiones deben fijarse en el proyecto y validarse en un nodo de cómputo. Cargar un
módulo no garantiza por sí solo que CUDA esté disponible dentro de un trabajo.

## Slurm

Slurm administra las colas y asigna CPU, memoria, tiempo y GPU. Un trabajo se describe
en un archivo `.sbatch` y se envía desde el nodo de acceso.

Particiones publicadas:

| Tipo | Partición | Límite publicado |
|---|---|---|
| CPU | `cpu-dev` | 16 cores / 32 GB |
| CPU | `cpu` | 64 cores / 128 GB |
| CPU | `cpu-max` | 128 cores / 256 GB |
| GPU | `gpu-dev` | 1 GPU |
| GPU | `gpu` | 2 GPU |
| GPU | `gpu-max` | 4 GPU |

Tipos de GPU publicados:

- `a100_1g.5gb`;
- `a100_2g.10gb`;
- `a100_3g.20gb`;
- `a100-sxm4-40gb`.

Las particiones, límites y nombres de recursos deben confirmarse con:

```bash
sinfo
sinfo -o '%P %a %l %D %G'
scontrol show partition
```

## Ejemplo de trabajo CPU

```bash
#!/usr/bin/env bash
#SBATCH --job-name=mi-proyecto-cpu
#SBATCH --partition=cpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load python/3.11

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
srun python scripts/tarea.py
```

## Ejemplo de trabajo GPU

```bash
#!/usr/bin/env bash
#SBATCH --job-name=mi-proyecto-gpu
#SBATCH --partition=gpu-dev
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:a100-sxm4-40gb:1
#SBATCH --time=01:00:00
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

module purge
module load pytorch/2.2
module load cuda/12.4

cd "${SLURM_SUBMIT_DIR}"
source .venv-cluster/bin/activate
nvidia-smi
srun python scripts/train.py
```

No se deben copiar los recursos de estos ejemplos sin revisar el consumo real del
proyecto. Solicitar más CPU, RAM, GPU o tiempo del necesario puede aumentar la espera
en cola.

## Enviar y monitorear trabajos

```bash
sbatch slurm/train.sbatch
squeue -u "$USER"
scontrol show job JOB_ID
sacct -j JOB_ID --format=JobID,State,Elapsed,AllocTRES,MaxRSS,ExitCode
tail -f slurm-mi-proyecto-gpu-JOB_ID.out
scancel JOB_ID
```

Estados habituales:

| Estado | Significado |
|---|---|
| `PD` | pendiente en cola |
| `R` | ejecutándose |
| `CG` | finalizando |
| `CD` | completado |
| `F` | falló |
| `CA` | cancelado |
| `TO` | excedió el tiempo solicitado |
| `OOM` | excedió la memoria asignada |

Cancelar un trabajo con `scancel` es apropiado cuando se envió con parámetros
incorrectos o ya no es necesario.

## Diagnóstico mínimo de GPU

Antes de un entrenamiento largo, ejecutar un trabajo corto que verifique el entorno:

```bash
nvidia-smi
python - <<'PY'
import json
import torch

report = {
    "torch": torch.__version__,
    "cuda_build": torch.version.cuda,
    "cuda_available": torch.cuda.is_available(),
    "cudnn": torch.backends.cudnn.version(),
    "device_count": torch.cuda.device_count(),
    "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
}
print(json.dumps(report, indent=2))
if not report["cuda_available"]:
    raise SystemExit("CUDA no está disponible")
PY
```

Después conviene ejecutar las pruebas del proyecto y un smoke test de entrenamiento de
pocos pasos. Un `import torch` exitoso no demuestra que forward, backward, datos y
checkpoints funcionen correctamente.

## Flujo recomendado para cualquier proyecto

```text
1. Configurar y probar el acceso SSH
2. Consultar almacenamiento, módulos y particiones vigentes
3. Clonar el repositorio en /home/USUARIO/projects
4. Transferir datos fuera de Git y verificar sus hashes
5. Crear el entorno usando módulos compatibles
6. Enviar un diagnóstico corto mediante Slurm
7. Ejecutar pruebas y un smoke test
8. Enviar el trabajo completo con recursos explícitos
9. Monitorear estado, logs y consumo
10. Sincronizar resultados y checkpoints al almacenamiento definitivo
```

Cada ejecución importante debería registrar al menos:

- commit del código;
- configuración;
- versiones de Python y dependencias;
- módulos cargados;
- identificador del trabajo Slurm;
- recursos solicitados;
- semillas aleatorias, cuando correspondan;
- hashes del dataset, manifests y checkpoints;
- métricas y logs.

## Reglas esenciales

- El nodo de acceso no es un nodo de cómputo.
- Todo proceso pesado debe ejecutarse mediante Slurm.
- Los datasets y resultados grandes no deben guardarse en Git.
- No debe usarse `/sw` como almacenamiento de usuario.
- `/tmp` no es almacenamiento persistente ni compartido garantizado.
- Los módulos y particiones deben consultarse nuevamente antes de cada proyecto.
- Se debe comenzar con un diagnóstico y un smoke test, no con el entrenamiento completo.
- Los archivos importantes deben tener copias y hashes; no debe asumirse que `/home`
  cuenta con una política de respaldo determinada.
