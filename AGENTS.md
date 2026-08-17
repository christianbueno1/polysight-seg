# AGENTS.md — Agent Instructions

> Este archivo es el punto de entrada de cada sesión.
> Léelo primero, siempre, antes de hacer cualquier otra cosa.

---

## Qué es este proyecto


---

## Archivos de orquestación del proyecto — qué es cada uno

| Archivo | Propósito | Quién lo edita |
|---|---|---|
| `AGENTS.md` | Instrucciones del agente (este archivo) | Solo el humano |
| `NOTES.md` | Notas de contexto del proyecto | Humano (agente lee) |
| `BACKLOG.md` | Lista de fases del proyecto en orden — el mapa general | Agente agrega, humano aprueba |
| `PHASE_CURRENT.md` | Fase activa con tareas específicas y estado — una fase a la vez | Agente reescribe cada sesión |
| `CHANGELOG.md` | Log permanente de decisiones y acciones tomadas — con el porqué | Agente solo agrega, nunca edita entradas pasadas |

---

## Cómo leer el contexto al inicio de cada sesión

Leer los archivos en este orden exacto:

- `AGENTS.md` — entender las reglas (este archivo)
- `NOTES.md` — entender el contexto del proyecto y las convenciones
- `BACKLOG.md` — entender dónde está el proyecto globalmente (si existe)
- `PHASE_CURRENT.md` — entender en qué se está trabajando ahora (si existe)
- `CHANGELOG.md` — entender qué se ha hecho y por qué (si existe)

Si los archivos BACKLOG, PHASE_CURRENT y CHANGELOG no existen todavía o estan vacios, es la primera sesión.
En ese caso: confirmar el objetivo con el humano y crear `BACKLOG.md` primero.
Crear `PHASE_CURRENT.md` y `CHANGELOG.md` solo después de que la primera fase esté definida.

---

## Cómo funciona BACKLOG.md

`BACKLOG.md` es el mapa general del proyecto — equivalente a un Product Backlog.

- Cada entrada es una **Fase**: un área de trabajo con nombre e intención clara pero sin tareas detalladas.
- Las fases están ordenadas de primera a última.
- Las fases tienen estado: `[ ]` pendiente, `[~]` en progreso, `[x]` completada.
- Solo una fase puede estar `[~]` en cualquier momento.
- Se pueden agregar nuevas fases al final conforme el proyecto evoluciona — esto es esperado.
- Nunca eliminar una fase completada — el historial importa.

### Formato

```markdown
# BACKLOG

## Fases

- [x] Fase 1 — Estructura del repositorio y directorios
- [~] Fase 2 — OpenTofu: configuración base (Hetzner + Cloudflare)
- [ ] Fase 3 — Ansible: hardening y configuración del servidor
- [ ] Fase 4 — Ansible: instalación de Caddy, Firewalld, Podman
- [ ] Fase 5 — Despliegue de pods (API, Keycloak, Frontend)
- [ ] Fase 6 — DNS y validación TLS end-to-end
- [ ] Fase 7 — Monitoreo y alertas
```

---

## Cómo funciona PHASE_CURRENT.md

`PHASE_CURRENT.md` es el trabajo activo — equivalente al tablero Kanban "En progreso".

- Contiene las tareas de **una sola fase**.
- Las tareas son específicas y accionables (crear un archivo, escribir un bloque de config, ejecutar un comando).
- Las tareas tienen estado: `[ ]` pendiente, `[~]` en progreso, `[x]` hecha.
- Este archivo se **reescribe completamente** cuando empieza una nueva fase.
- Si durante la fase se descubren nuevas tareas, se agregan a la lista.
- La sección "Notas y decisiones" captura el **porqué** — alimenta el CHANGELOG.md.

### Formato

```markdown
# PHASE_CURRENT

## Fase 2 — OpenTofu: configuración base

**Objetivo:** Crear el directorio tofu/ con los archivos mínimos para definir el servidor
en Hetzner y los registros DNS en Cloudflare.

**Contexto:** Ver NOTES.md §Providers OpenTofu y §Dominio y DNS.

---

### Tareas

- [x] Crear directorio `tofu/`
- [x] Crear `tofu/providers.tf` con hcloud y cloudflare providers
- [~] Crear `tofu/variables.tf` con region, server_type, image, domain
- [ ] Crear `tofu/server.tf` con recurso hcloud_server + SSH key + firewall
- [ ] Crear `tofu/dns.tf` con registros Cloudflare para los 3 subdominios
- [ ] Crear `tofu/outputs.tf` con IP del servidor
- [ ] Validar con `tofu validate`

---

### Notas y decisiones

- Usando hcloud provider v~1.60 per NOTES.md.
- Usando cloudflare provider v~5.18 per NOTES.md.
- Cloudflare proxied=false para que Caddy maneje TLS directamente.
```

---

## Cómo funciona CHANGELOG.md

`CHANGELOG.md` es el audit trail permanente — equivalente al change log de ITIL o al git log en DevOps.

- Cada sesión que produce trabajo genera una entrada.
- Las entradas se **agregan al tope** (más reciente primero).
- Cada entrada registra: fecha, hora, fase, qué se hizo y **por qué** se tomaron las decisiones clave.
- Nunca editar ni eliminar entradas pasadas.
- Para obtener el timestamp usar: `date '+%Y-%m-%d %H:%M %z'`

### Formato

```markdown
# CHANGELOG

---

## 2026-04-13 21:30 -0500 — Fase 2: OpenTofu configuración base

**Hecho:**
- Creado `tofu/providers.tf` con hcloud ~>1.60 y cloudflare ~>5.18
- Creado `tofu/variables.tf` con region us-east, server_type cax11, image fedora-43

**Decisiones:**
- CAX11 Ampere ARM64: mejor relación precio/rendimiento en Hetzner para este workload.
- proxied=false en Cloudflare: Caddy gestiona TLS con Let's Encrypt directamente.

**Pendiente / carry-over:**
- `tofu/server.tf` y `tofu/dns.tf` — para la próxima sesión.

---

## 2026-04-12 18:00 -0500 — Fase 1: Estructura del repositorio

**Hecho:**
- Creados directorios: `tofu/`, `ansible/`, `ansible/inventory/`, `ansible/playbooks/`, `ansible/roles/`
- Creado `BACKLOG.md` con 7 fases

**Decisiones:**
- Separación tofu/ansible: concerns distintos, facilita trabajo independiente en cada capa.
```

---

## Flujo de trabajo con Git

Verificar que estoy en la rama dev antes de crear un branch nuevo para la fase actual.
Si no estoy en dev, hacer `git checkout dev` antes de crear el branch. Si no existe dev, crearla desde main: `git checkout main && git checkout -b dev`.

Cada fase del proyecto vive en su propio branch.
Este flujo es obligatorio:

```
1. Al INICIAR una fase:
   - Crear un branch nuevo desde dev: git checkout dev && git checkout -b <nombre>
   - Nombre del branch: chore/<descripcion-corta> (ej. chore/ansible-caddy)

2. DURANTE la fase:
   - Hacer commits atómicos y frecuentes después de cada tarea completada.
   - Nunca acumular muchos cambios sin commitear.
   - Mensaje de commit en español, conciso, con Co-Authored-By al final.

3. Al FINALIZAR una fase:
   - Commit de todos los cambios pendientes (PHASE_CURRENT, CHANGELOG, BACKLOG, archivos).
   - Merge a dev con --no-ff: git checkout dev && git merge <branch> --no-ff -m "chore: merge <branch> — <resumen>"
   - Eliminar el branch: git branch -d <branch>
   - Crear el branch de la siguiente fase antes de empezar a trabajar en ella.
```

### Reglas

- **Nunca trabajar en `main` directamente.** `main` es solo para releases estables.
- **`dev` es la rama de integración.** Todo se mergea aquí primero.
- **Un branch por fase.** No mezclar trabajo de dos fases en el mismo branch.
- **Siempre verificar el branch activo** antes de crear archivos o hacer cambios.
- **Working tree limpio al terminar.** Ningún archivo untracked o modificado sin commitear.

---

## Checklist de inicio de cada sesión

```
1. Leer los archivos de orquestación del proyecto (ver orden arriba).
2. Saludar al humano con un resumen de un párrafo:
   - Fase actual y su objetivo
   - Qué se completó en la sesión anterior (de CHANGELOG.md)
   - Qué está pendiente en PHASE_CURRENT.md
3. Preguntar: "¿Continuamos con la fase actual o hay algo nuevo?"
4. Trabajar las tareas en orden. Después de cada tarea completada:
   - Actualizar el estado en PHASE_CURRENT.md
   - Registrar cualquier decisión en la sección de notas
5. Al final de la sesión, agregar una entrada nueva al tope de CHANGELOG.md.
6. Si la fase está completa, marcarla [x] en BACKLOG.md
   y preparar PHASE_CURRENT.md para la siguiente fase.
```

---

## Qué hacer al crear archivos o directorios

- Siempre revisar `NOTES.md` para convenciones de nombres, rutas y detalles del entorno.


### Convenciones específicas de este proyecto



---

## Pendientes conocidos (de NOTES.md)

Estos ítems se convierten en fases del BACKLOG cuando el humano lo decida:

- [ ] Pipeline CI/CD para `deploy.yml` automático al mergear a `main`
- [ ] Backup de volúmenes (datos de SQL Server)

---

## Principios generales

- **Elaboración progresiva:** Es normal no tener todos los detalles al inicio.
  Las fases en BACKLOG.md pueden ser vagas. Las tareas en PHASE_CURRENT.md
  se detallan solo cuando la fase está activa.

- **Una fase a la vez:** No trabajar en fases futuras. Mantener el foco en PHASE_CURRENT.md.

- **Preguntar antes de asumir:** Si algo en NOTES.md o en otro archivo de orquestacion es ambiguo o falta,
  preguntar al humano antes de proceder. Documentar la respuesta en CHANGELOG.md.

- **Los cambios son trazables:** Cada decisión relevante va a CHANGELOG.md.
  Sesiones futuras (y otros humanos) deben poder entender por qué las cosas son como son.

---

## Referencia de metodología

| Práctica | Dónde aparece en este sistema |
|---|---|
| **Kanban** — visualizar y limitar WIP | Tareas en `PHASE_CURRENT.md` con estado; una sola fase activa |
| **ITIL Change Management** | `CHANGELOG.md` como audit trail; decisiones documentadas antes de actuar |
| **Elaboración progresiva** | Fases en `BACKLOG.md` intencionalmente vagas; detalle se agrega cuando la fase está activa |