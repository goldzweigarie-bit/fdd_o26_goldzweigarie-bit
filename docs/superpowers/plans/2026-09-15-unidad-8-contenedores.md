# Unidad 8 — Contenedores · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publicar la unidad 8 del curso —tres sesiones sobre contenedores, 26 páginas de lección, 30 figuras generadas y cinco entregas— en `https://rayalucaria.org/fdd_o26/`.

**Architecture:** Repositorio de contenido, no de aplicación. El Markdown de `course/` lo consume el CLI `raya`, que vive en el repo hermano `~/itam/raya_lucaria`. Las figuras salen de dos generadores de Python que son su única fuente de verdad, protegidos por una guarda que compara disco contra generador. El orden de construcción existe para romper tres ciclos de dependencias: las páginas necesitan que sus figuras existan, las figuras necesitan estar referenciadas desde alguna página, y el calendario necesita que los índices de sección ya resuelvan.

**Tech Stack:** Markdown + YAML frontmatter, Python 3 (sólo biblioteca estándar), pytest, el CLI `raya`.

**Spec:** `docs/superpowers/specs/2026-09-15-unidad-8-contenedores-design.md`

**Plan hermano:** `docs/superpowers/plans/2026-09-15-revision-entrega-reglas-5-y-6.md` — las reglas 5 y 6 de la revisión de entregas. Es independiente y puede correr antes, después o en paralelo.

## Global Constraints

Todo esto sale del spec y aplica a **cada** task. Un fallo aquí no se ve hasta el build, o no se ve nunca.

- **Todo `$` va dentro de un code span o de un fence.** El renderizador carga `dollarmath`: dos `$` en una línea de prosa se convierten en MathJax **sin error y sin warning**. `$(pwd)`, `$USER`, `$GHUSER`, `$HOME` aparecen por todas partes en esta unidad.
- **Todo `@` suelto va en code span.** `@reboot` tumba el build con `Unknown numbered object reference`. `ubuntu@sha256:` y los correos son seguros.
- **Nada de HTML crudo.** No rompe el build: se escapa en silencio y sale visible en la página.
- **Nada de mermaid.** El renderizador lo rechaza; los diagramas son SVG propio.
- **Cita cualquier valor de frontmatter que lleve dos puntos.** `summary: Datalake, warehouse: dos respuestas` es YAML inválido y tumba el build entero.
- **Tope de 160 líneas** por página de lección. Exentas a 260: `instalar-docker-y-podman`, `planes-b-de-instalacion`, `cuando-se-rompe-el-aislamiento`, `B_prompts`, `C_anidar`, `D_entregas`. `A_chuleta` a 320.
- **Forma de página**, sólo en las 26 de lección: línea de posición → `Meta:` de una línea → `::: figure` → `## En corto` con **máximo tres viñetas** → cuerpo → **exactamente un `::: problem` con `hint` y `answer`** → cierre en dos líneas (`> [!NOTE]` y, en la siguiente, `> **Si sólo recuerdas una cosa:** …`) — en una sola línea no renderiza. Prohibido `::: note`.
- **`**Haz:** → **Deberías ver:**`** — toda página con bloques ejecutables lleva al menos tres tramos, ninguno de más de 15 líneas.
- **Ids de objeto numerado únicos en TODO el curso**: prefijo `cont-` sin excepción. Una figura sólo se numera **una vez**; sus reapariciones van como imagen suelta `![alt](../_assets/x.svg)` sin directiva.
- **Español en la prosa, inglés en los identificadores.** Se dice "contenedor", "imagen", "chuleta".
- **Los generadores sólo usan biblioteca estándar.** CI instala `pytest pillow pyyaml` y la guarda **importa** el generador.
- **No tocar `tools/svg_base.py`**: modificarla regenera y revalida los 32 SVG de las unidades 6 y 7.
- Validar con `cd ~/itam/raya_lucaria && UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26`.
- Probar con `cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q` (≈ 2 min 40 s).
- Commits con `feat(unidad-8): ...`, `docs(unidad-8): ...`, `test(unidad-8): ...`, y la línea `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>` al final.

---

## Fase 0 — Lo que raya no mira

Nada de `codigo/` lo recorre raya ni ninguna prueba, y un asset que ninguna página enlaza es invisible para la validación. Por eso esta fase se puede hacer entera antes de tocar `course/`, y cada task valida sola.

### Task 1: El espejo de la unidad

**Files:**
- Create: `codigo/08_contenedores/README.md`, `bitacora.md`, `mi-imagen.md`
- Create: `codigo/08_contenedores/info/info.sh`, `info/Dockerfile`
- Create: `codigo/08_contenedores/roto/Dockerfile`, `roto/requirements.txt`, `roto/app.py`
- Create: `codigo/08_contenedores/volumenes/app.py`, `volumenes/predicciones.md`
- Create: `codigo/08_contenedores/donde_vive/app.py`, `donde_vive/Dockerfile`
- Create: `codigo/08_contenedores/dev/main.py`, `dev/requirements.txt`, `dev/Dockerfile`
- Create: `codigo/docker/certificaciones.md`
- Modify: `codigo/README.md`

**Interfaces:**
- Produces: el contenido exacto de `roto/Dockerfile`, que la guarda de la Task 16 asserta por ruta exacta; y los tres archivos de laboratorio que las páginas 2/9, 2/10 y 2/12 referencian por nombre.

- [ ] **Step 1: Copia y limpia lo que viene del semestre pasado**

```bash
cd ~/itam/fdd_o26
mkdir -p codigo/08_contenedores/{info,roto,volumenes,donde_vive,dev} codigo/docker
cp ~/itam/fdd_p26/clase/08_containers/example/info.sh        codigo/08_contenedores/info/
cp ~/itam/fdd_p26/clase/08_containers/example/Dockerfile     codigo/08_contenedores/info/
cp ~/itam/fdd_p26/clase/08_containers/exercises/lab1_bind_mounts/app.py       codigo/08_contenedores/volumenes/
cp ~/itam/fdd_p26/clase/08_containers/exercises/lab4_donde_vive/app.py        codigo/08_contenedores/donde_vive/
cp ~/itam/fdd_p26/clase/08_containers/exercises/lab4_donde_vive/Dockerfile    codigo/08_contenedores/donde_vive/
cp ~/itam/fdd_p26/clase/08_containers/exercises/lab3_dev_workflow/{main.py,requirements.txt,Dockerfile} codigo/08_contenedores/dev/
```

Después borra del `info.sh` copiado la línea de depuración que quedó commiteada
en el original:

```bash
cd ~/itam/fdd_o26
sed -i '/Discooooooooooo/d' codigo/08_contenedores/info/info.sh
grep -c Disco codigo/08_contenedores/info/info.sh   # debe imprimir 0
```

`output.txt` **no se copia**: el laboratorio lo tiene que generar el alumno, y
en el original venía con el ejercicio ya resuelto.

- [ ] **Step 2: Escribe el Dockerfile roto y sus dos acompañantes**

`roto/Dockerfile` — los tres defectos son el orden del `COPY`, correr como root
y la base sin pinear. **No puede existir solo**: sin `requirements.txt` el
primer defecto no tiene nada que mover.

```dockerfile
FROM python:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

`roto/requirements.txt`:

```
requests==2.32.3
```

`roto/app.py`:

```python
"""Lo de menos es lo que hace: el ejercicio es el Dockerfile."""
import getpass
import requests

print(f"Corriendo como: {getpass.getuser()}")
print("requests", requests.__version__)
```

- [ ] **Step 3: Escribe `predicciones.md` con la tabla ya armada**

Sin la tabla escrita, el ejercicio de la página 2/10 es incomparable entre
alumnos y no se puede calificar.

```markdown
# Los ocho casos

Llena la columna **Predicción** **antes** de correr nada. Después corre cada
caso y llena **Resultado**. Si acertaste las ocho, entendiste volúmenes.

| # | El código está | Editas en | ¿Rebuild? | Predicción | Resultado |
|---|---|---|---|---|---|
| 1 | en la imagen | el host | no | | |
| 2 | en la imagen | el host | sí | | |
| 3 | en la imagen | el contenedor | no | | |
| 4 | en la imagen | el contenedor | sí | | |
| 5 | por volumen | el host | no | | |
| 6 | por volumen | el host | sí | | |
| 7 | por volumen | el contenedor | no | | |
| 8 | por volumen | el contenedor | sí | | |

Este archivo **no se entrega**. Es tuyo, para pensar antes de teclear.
```

- [ ] **Step 4: Escribe `bitacora.md` y `mi-imagen.md`**

`bitacora.md`, con el mismo esqueleto que la de la unidad 7:

```markdown
# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre:
- Usuario de GitHub:
- Usuario de Docker Hub:

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version


docker images


docker history <tu-usuario>/<tu-imagen>


```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1.
2.
3.

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.
```

`mi-imagen.md`:

```markdown
# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub:
- Usuario de Docker Hub:

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL:

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>


```

## Cómo la corro yo

Comando exacto:

```text

```

Salida que debo esperar:

```text

```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
docker rmi -f <tu-usuario>/<tu-imagen>
docker run --rm <tu-usuario>/<tu-imagen>


```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>


```
```

- [ ] **Step 5: Escribe `codigo/docker/certificaciones.md`**

Tres secciones, una por entrega, calcado de `codigo/github/certificaciones.md`:

```markdown
# Certificaciones de Docker

Llena este archivo en **tu copia**, dentro de `estudiantes/<tu-login>/docker/`.

Son **dos** cursos de Docker en DataCamp, no tres. El segundo se entrega en dos
partes, por eso hay tres secciones.

## Quién soy

- Nombre:
- Usuario de GitHub:
- Correo con el que entraste a DataCamp:

## Introduction to Docker

Se llena en la **primera** entrega.

Fecha en que lo terminaste:

URL del Statement of Accomplishment:

![Captura del curso Introduction to Docker terminado](./introduccion-a-docker.png)

## Intermediate Docker · capítulos 1 y 2

Se llena en la **segunda** entrega. El curso no está terminado todavía, así que
**no hay certificado**: la captura que sirve es la página del curso con sus
cuatro capítulos, donde se vean los dos primeros al 100 % y tu nombre.

Fecha:

![Captura de los capítulos 1 y 2 de Intermediate Docker](./intermedio-1-2.png)

## Intermediate Docker · capítulos 3 y 4

Se llena en la **tercera** entrega, cuando el curso ya está completo.

Fecha:

URL del Statement of Accomplishment:

![Captura del curso Intermediate Docker terminado](./intermedio-3-4.png)

## Una cosa que aprendiste y no sabías

Se llena en la **tercera** entrega. Dos o tres líneas. Algo concreto de alguno
de los dos cursos que no habías visto en clase, o que en clase entendiste a
medias y ahí se te acomodó.
```

- [ ] **Step 6: Escribe el `README.md` del espejo y actualiza el de `codigo/`**

`codigo/08_contenedores/README.md` dice qué es cada carpeta, que
`predicciones.md` no se entrega, y el comando de copia con su barra y su punto:

```bash
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
cp -r codigo/docker/.          estudiantes/$GHUSER/docker/
```

Con la advertencia que la unidad 7 dedicó un párrafo entero a explicar: sin la
barra y el punto, la segunda vez acabas con `08_contenedores` dentro de
`08_contenedores`; y no se copia arrastrando en el Finder ni en el Explorador,
porque produce nombres con la palabra «copia». Y la trampa nueva de esta
unidad: **la carpeta lleva el cero adelante** aunque la unidad se vea como «8»
en el sitio.

En `codigo/README.md`, agrega las dos carpetas nuevas a la lista.

- [ ] **Step 7: Comprueba que nada se rompió**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Esperado: verde. Nada de `codigo/` lo mira ninguna prueba, así que esto sólo
confirma que no tocaste otra cosa por accidente.

- [ ] **Step 8: Commit**

```bash
cd ~/itam/fdd_o26
git add codigo/
git commit -m "feat(unidad-8): el espejo de la unidad, con el Dockerfile roto

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Los benchmarks como assets publicables

**Files:**
- Create: `course/8_contenedores/_assets/benchmarks/` — 5 scripts, `requirements.txt`, 13 CSV
- Create: `course/8_contenedores/code/analyze.py`

`REFERENCE_EXTENSIONS` del esquema es exactamente `{".py": "code", ".ipynb": "notebook"}`. Un enlace a un `.sh` o un `.csv` bajo `code/` **hace fallar `raya validate`**, y con ella el build y el despliegue. Los assets, en cambio, no tienen lista blanca de extensiones.

- [ ] **Step 1: Copia los scripts y los datos**

```bash
cd ~/itam/fdd_o26
mkdir -p course/8_contenedores/_assets/benchmarks/results course/8_contenedores/code
cp ~/itam/fdd_p26/clase/08_containers/scripts/*.sh              course/8_contenedores/_assets/benchmarks/
cp ~/itam/fdd_p26/clase/08_containers/scripts/requirements.txt  course/8_contenedores/_assets/benchmarks/
cp ~/itam/fdd_p26/clase/08_containers/scripts/results/*.csv     course/8_contenedores/_assets/benchmarks/results/
cp ~/itam/fdd_p26/clase/08_containers/scripts/analyze.py        course/8_contenedores/code/
ls course/8_contenedores/_assets/benchmarks/results/*.csv | wc -l   # debe imprimir 13
```

- [ ] **Step 2: Pinea la imagen en `bench_runtime.sh`**

`ubuntu:latest` hoy es 26.04 con coreutils en Rust, y con eso el resultado del
experimento de hash **invierte el signo**. Los scripts se publican para que los
alumnos los repitan, así que sin el pin la lección de reproducibilidad se
vuelve su propio contraejemplo.

```bash
cd ~/itam/fdd_o26/course/8_contenedores/_assets/benchmarks
grep -n "ubuntu" bench_runtime.sh
```

Sustituye cada `ubuntu` suelto por `ubuntu:24.04` y agrega arriba del script un
comentario de dos líneas explicando por qué está pineado.

- [ ] **Step 3: Arregla el `images/` de `analyze.py`**

El script escribe en un directorio `images/` que en el layout nuevo no existe,
y se publica justamente para que lo corran.

```bash
cd ~/itam/fdd_o26 && grep -n "images" course/8_contenedores/code/analyze.py
```

Cambia el destino a `Path(csv).parent` —junto al CSV que acaba de leer— y quita
el `mkdir` de `images`. Comprueba que ya no queda ninguna referencia:

```bash
grep -c "images" course/8_contenedores/code/analyze.py   # debe imprimir 0
```

- [ ] **Step 4: Valida**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Esperado: sin errores. Todavía no hay páginas, así que nada enlaza estos
archivos y son invisibles para la validación — que es justo lo que permite
hacer esta fase primero.

- [ ] **Step 5: Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/
git commit -m "feat(unidad-8): los scripts y los datos de los benchmarks

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Fase 1 — El esqueleto navegable

### Task 3: El índice de la unidad y los tres de sección

**Files:**
- Create: `course/8_contenedores/0_index.md`
- Create: `course/8_contenedores/1_la_idea/0_index.md`
- Create: `course/8_contenedores/2_manos_a_la_obra/0_index.md`
- Create: `course/8_contenedores/3_diseno_y_seguridad/0_index.md`

**Interfaces:**
- Produces: los cuatro ids `contenedores`, `la-idea-del-contenedor`,
  `contenedores-con-las-manos`, `disenar-con-contenedores`. El calendario de la
  Task 19 apunta a los tres últimos; todas las páginas cuelgan de ellos.

Los índices **no** están sujetos a la forma de página: sólo al tope de líneas y
a las reglas de `$`, `@` y HTML crudo.

- [ ] **Step 1: Escribe el índice de la unidad**

`course/8_contenedores/0_index.md`, con este frontmatter exacto:

```yaml
---
id: contenedores
title: "Contenedores"
nav_title: "Contenedores"
summary: "Tres clases. Qué es un contenedor, cómo se usa en tu máquina, y cómo se reparte un sistema en servicios."
status: ready
estimated_time: 399m
tags: [docker, podman, contenedor, imagen, volumen, namespace, cgroup, kata, seguridad, diseno]
prerequisites: [git-y-github]
---
```

El cuerpo lleva: la ilustración de portada (que todavía no existe — se agrega
en la Task 8), un `## En corto` de tres viñetas, la tabla de las tres secciones
**en texto plano, sin wikilinks** (se enlazan en la Task 18, porque un `[[id]]`
hacia una página que no existe tumba la validación entera), el enlace a
`code/analyze.py` —desde este directorio, que es el precedente exacto de la
unidad 3— y **el total de trabajo fuera de clase**: ≈ 300 minutos de lectura
más 8 h 27 de DataCamp, o sea unas 13 horas en doce días. Ese número va aquí
porque es donde un alumno decide cómo reparte su semana.

- [ ] **Step 2: Escribe los tres índices de sección**

Mismo patrón, con estos frontmatter:

```yaml
---
id: la-idea-del-contenedor
title: "La idea"
nav_title: "1. La idea"
summary: "Qué es un contenedor, qué pasa cuando escribes docker run, y por qué el mundo se movió a esto."
status: ready
tags: [contenedor, namespace, cgroup, imagen, orquestacion]
---
```

```yaml
---
id: contenedores-con-las-manos
title: "Manos a la obra"
nav_title: "2. Manos a la obra"
summary: "Instalar, construir, montar y limpiar. Dónde vive cada byte de tu contenedor."
status: ready
tags: [docker, podman, volumen, bind-mount, dockerfile, registro]
---
```

```yaml
---
id: disenar-con-contenedores
title: "Diseño y seguridad"
nav_title: "3. Diseño y seguridad"
summary: "Cómo se reparte una aplicación en servicios, por dónde se rompe el aislamiento, y qué hay más allá del contenedor."
status: ready
tags: [diseno, microservicio, red, seguridad, kata, gvisor]
---
```

El índice de la sección 2 distingue explícitamente `~/fdd/docker-lab` —carpeta
local y desechable, **no** un repositorio— de `estudiantes/<login>/08_contenedores/`,
que sí lo es, y **pone primero las tres páginas de lectura previa**, porque sus
entregas vencen el mismo día de la clase.

- [ ] **Step 3: Valida**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Esperado: sin errores. Cuatro directorios renderizados, cada uno con su
`0_index.md`, sin hijos todavía — eso valida.

Si sale `Missing local asset reference` por la portada, coméntala hasta la
Task 8.

- [ ] **Step 4: Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/
git commit -m "feat(unidad-8): el esqueleto de la unidad y sus tres secciones

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Fase 2 — Figuras

Las tres piezas de esta fase van **en el mismo commit**: un SVG sin su fila de
`CREDITOS.md` pone rojo `test_creditos.py`, y una fila sin su SVG también.

### Task 4: Las 31 filas de CREDITOS como especificación

**Files:**
- Create: `course/8_contenedores/_assets/CREDITOS.md`

Esto va **antes** del generador, y es el paso que más retrabajo ahorra: sin una
descripción concreta por figura, dos personas dibujan dos cosas distintas y
cada figura arrastra unas 55 líneas de Python.

- [ ] **Step 1: Escribe el encabezado y la tabla**

Una sola tabla — `test_creditos.py` toma **la última** del archivo y compara el
resto de las filas contra su encabezado, así que una segunda tabla rompe las
filas de la primera. Columnas: `Archivo | Descripción y prompt resumido | Autor / origen | Fecha | Licencia`.

El texto en minúsculas debe contener las cadenas `generada`, `ninguna` y
`personas reales`, que `test_ilustraciones.py` exige literalmente.

- [ ] **Step 2: Escribe una oración concreta por figura**

Al nivel de detalle de la unidad 7 — elementos y etiquetas, no el tema. Ejemplo
del registro que hay que alcanzar, para `cont-anatomia-run`:

> Cadena de cinco cajas de izquierda a derecha —`docker` CLI, `dockerd`,
> `containerd`, `containerd-shim-runc-v2` y `runc`— con el proceso del
> contenedor colgando del shim y una flecha punteada que sube del shim a
> `PID 1`; `runc` aparece en gris y con una marca de salida, porque crea y sale.

Las 30, con su id: `cont-intermodal`, `cont-ns-cgroups`,
`cont-tres-abstracciones`, `cont-anatomia-run`, `cont-escalamiento`,
`cont-vm-vs-contenedor`, `cont-espectro`, `cont-docker-vs-podman`,
`cont-capas-cache`, `cont-sin-sudo`, `cont-planes-b`, `cont-registro`,
`cont-ciclo-de-vida`, `cont-build-contexto`, `cont-dockerfile-roto`,
`cont-overlay-volumen`, `cont-rutas`, `cont-uid-plataformas`,
`cont-matriz-volumen`, `cont-tapar`, `cont-estado-postgres`, `cont-prune`,
`cont-red-y-pod`, `cont-contrato`, `cont-pipeline-servicios`,
`cont-superficie-ataque`, `cont-bench-arranque`, `cont-bench-escala`,
`cont-bench-overhead`, `cont-bench-anidado`. Más `ilus-contenedores-portada.jpg`,
que son 31 filas.

- [ ] **Step 3: Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/_assets/CREDITOS.md
git commit -m "docs(unidad-8): las 31 figuras, descritas antes de dibujarlas

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: El generador de las cuatro gráficas

**Files:**
- Create: `tools/gen_contenedores_bench.py`

**Interfaces:**
- Produces: `DIAGRAMAS: dict[str, Callable[[], str]]` con las cuatro entradas
  `cont-bench-arranque`, `cont-bench-escala`, `cont-bench-overhead`,
  `cont-bench-anidado`; `ESTADISTICO = statistics.median`; y
  `CSV_DE: dict[str, tuple[str, tuple[str, ...]]]` — figura → (archivo,
  columnas exigidas). La Task 6 importa `DIAGRAMAS` y la Task 15 lee `CSV_DE`.

Va primero que las conceptuales porque es la parte con riesgo real: no hay
primitiva de gráfica en el repo.

- [ ] **Step 1: Copia la única función reutilizable**

De las cinco funciones de la unidad 3 que parecían aprovechables, **sólo una lo
es**: `log_position()` en `tools/gen_ai_hardware_costs.py:61` — pura, 18
líneas, sólo `math`. Cópiala textual (no la importes: ese módulo hace
`import yaml` a nivel de módulo). `_log_axis()` hay que reescribirlo, y
`_plot_log_row()`, `_log_ticks()` y `_axes()` no sirven — además usan una
paleta ajena al skin que la guarda de colores rechazaría.

- [ ] **Step 2: Declara el mapa de datos y el estadístico**

```python
import statistics

ESTADISTICO = statistics.median

# Los tres numeros que la unidad cita son MEDIANAS. Quien use mean() por
# reflejo publicara 3.1 / 423 / 222 y contradira la prosa sin que ninguna
# guarda lo note: el baseline tiene un ramp-up de frecuencia en las primeras
# cinco repeticiones.
CSV_DE = {
    "cont-bench-arranque": ("exp1_startup.csv",
        ("runtime", "image", "rep", "startup_ms")),
    "cont-bench-escala": ("exp2_scale.csv",
        ("runtime", "count", "launch_time_s", "per_container_kb",
         "total_container_kb", "daemon_rss_kb")),
    "cont-bench-overhead": ("exp3_runtime.csv",
        ("runtime", "workload", "rep", "time_s")),
    "cont-bench-anidado": ("exp4_nested.csv",
        ("method", "metric", "rep", "value")),
}
```

Lee los CSV con el módulo `csv` de la biblioteca estándar. **Nada de pandas ni
matplotlib**: CI instala `pytest pillow pyyaml` y la guarda importa este
archivo.

- [ ] **Step 3: Escribe la infraestructura de gráfica**

Unas 150 líneas: ejes, ticks, escala —logarítmica para el arranque, que va de
1.8 ms a 428 ms—, barras y etiquetas. Reglas que no se negocian:

- **Usa `svg_base.marco()`** para la raíz y emite strings, no `ElementTree`.
  `test_svg_tamano_intrinseco.py` exige `width` y `height` numéricos **sin
  unidades**, `viewBox` empezando literalmente en `0 0`, y la proporción
  cuadrando con menos de 0.01 de error. `marco()` lo cumple gratis; construir
  la raíz a mano es lo que produce el SVG deformado.
- **Todo `<text>` lleva `fill` explícito** y los colores salen de
  `skins/fdd-eva.yaml`.
- **Cada etiqueta nombra un valor que la gráfica alcanza**, y nada se sale del
  `viewBox`.

- [ ] **Step 4: Dibuja las cuatro y pon el pie**

Cada gráfica lleva su pie con máquina, kernel y versiones de runtime **y de las
herramientas medidas** — para el hash, GNU coreutils 8.32 contra 9.4, que es lo
que el experimento midió de verdad.

- [ ] **Step 5: Genera y mira**

```bash
cd ~/itam/fdd_o26 && python3 tools/gen_contenedores_bench.py
ls course/8_contenedores/_assets/cont-bench-*.svg
```

Ábrelas. Es el único punto del plan donde mirar el resultado no es opcional:
una gráfica con una etiqueta encimada o fuera del lienzo pasa cualquier prueba
automática.

- [ ] **Step 6: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/gen_contenedores_bench.py course/8_contenedores/_assets/cont-bench-*.svg
git commit -m "feat(unidad-8): las cuatro graficas de benchmark, desde los CSV medidos

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: El generador de las 26 figuras conceptuales

**Files:**
- Create: `tools/gen_contenedores.py`

**Interfaces:**
- Consumes: `DIAGRAMAS` de `gen_contenedores_bench.py`.
- Produces: el catálogo fusionado `DIAGRAMAS` —30 entradas— y un `main(argv)`
  que acepta nombres sueltos y sale con código distinto de cero ante uno
  desconocido. La Task 15 importa el catálogo.

- [ ] **Step 1: Escribe el esqueleto y el catálogo**

Patrón de `tools/gen_regex.py`: paleta en constantes desde
`skins/fdd-eva.yaml`, una función por diagrama que devuelve una cadena SVG
completa, y un `DIAGRAMAS` que el generador y su prueba comparten como única
fuente de «qué figuras existen». Al final, fusiona el catálogo de las gráficas:

```python
from gen_contenedores_bench import DIAGRAMAS as DIAGRAMAS_BENCH

DIAGRAMAS = {**DIAGRAMAS_CONCEPTUALES, **DIAGRAMAS_BENCH}
```

- [ ] **Step 2: Dibuja las 26, contra las descripciones de la Task 4**

Cada una con `aria-label` de **80 caracteres o más**, fondo horneado, `fill`
explícito en todo `<text>`, y ningún texto fuera del lienzo — son las
aserciones que `test_gen_regex.py` y `test_gen_git.py` ya hacen y que la guarda
de la Task 15 va a replicar.

- [ ] **Step 3: Genera todo y cuenta**

```bash
cd ~/itam/fdd_o26 && python3 tools/gen_contenedores.py
ls course/8_contenedores/_assets/cont-*.svg | wc -l   # debe imprimir 30
python3 -m pytest tools/test_svg_tamano_intrinseco.py -q
```

Esperado: 30 archivos y la prueba de tamaño intrínseco en verde — aplica sola,
sin registrar nada.

- [ ] **Step 4: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/gen_contenedores.py course/8_contenedores/_assets/cont-*.svg
git commit -m "feat(unidad-8): las 26 figuras conceptuales de la unidad

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: La portada

**Files:**
- Modify: `tools/ilustraciones.json`
- Create: `course/8_contenedores/_assets/ilus-contenedores-portada.jpg`

- [ ] **Step 1: Agrega la entrada al catálogo**

Cuatro trampas verificadas de `test_ilustraciones.py`:

1. **`PROHIBIDOS_EN_PROMPT` compara subcadenas** e incluye `logotipo`. Escribir
   «sin logotipos» **falla la prueba**; los prompts existentes dicen **«sin
   logos»**. Copia esa formulación exacta.
2. La lista `PROHIBIDOS` se aplica al JSON entero: nada de `evangelion`,
   `ghibli`, `akira`, `lain`, `mario`.
3. El prompt no pide personas reales ni personajes con derechos ni texto
   legible.
4. La cadena `_assets/ilus-contenedores-portada.jpg` tiene que aparecer en
   alguna página — por eso esta task va después de la Task 3.

- [ ] **Step 2: Genera**

```bash
cd ~/itam/fdd_o26
set -a && . ./.env && set +a
python3 tools/gen_ilustraciones.py contenedores-portada
```

Es no determinista y no se regenera en CI: se genera una vez, se revisa a ojo y
se commitea.

- [ ] **Step 3: Referencia la portada desde el índice de la unidad**

En `course/8_contenedores/0_index.md`, con alt text descriptivo y largo.

- [ ] **Step 4: Comprueba las tres guardas de imagen**

```bash
cd ~/itam/fdd_o26
python3 -m pytest tools/test_creditos.py tools/test_ilustraciones.py tools/test_svg_tamano_intrinseco.py -q
```

Esperado: verde. Si `test_creditos.py` falla, es que un archivo no tiene fila o
una fila no tiene archivo — falla en los dos sentidos.

- [ ] **Step 5: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/ilustraciones.json course/8_contenedores/
git commit -m "feat(unidad-8): la portada de la unidad

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Fase 3 — Las páginas

### Procedimiento de página

**Las 26 tasks de esta fase siguen este procedimiento. No hay atajo ni
variante: lo que cambia entre una página y otra es el contrato de su tabla.**

> **Para quien ejecute el plan:** en las Fases 3, cada **fila de tabla es una
> task**, con su número en la primera columna. No llevan encabezado `### Task N`
> propio a propósito — los cinco pasos son idénticos para las 31 y repetirlos
> treinta veces haría el plan ilegible sin agregar una sola instrucción. Trata
> cada fila como una task completa: sus pasos son los cinco de aquí abajo, sus
> datos son los de la fila, y su gate de revisión es el Paso D más el Paso C.
> Lo mismo aplica a las Tasks 36 a 39, los anexos.

- [ ] **Paso A — Escribe la página** en la ruta que dice su fila, con el
  frontmatter que dice su fila y la forma de las Global Constraints: línea de
  posición (`**Página N de M · sección S de 3**`, numerada **por sección**),
  `Meta:` de una línea, `::: figure` con su id, `## En corto` de tres viñetas,
  el cuerpo, **un** `::: problem` con `hint` y `answer`, y el cierre
  `> [!NOTE]` y, en la línea siguiente, `> **Si sólo recuerdas una cosa:**` — en una sola línea no renderiza. La sustancia está en la sección
  homónima del spec; esta tabla sólo fija lo verificable.

- [ ] **Paso B — Agrega a la chuleta** todo comando `docker` o `podman` nuevo
  que la página cite, **en este mismo commit**. Reconstruir `A_chuleta.md` al
  final a partir de 26 páginas son horas de trabajo mecánico y con huecos.

- [ ] **Paso C — Valida**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Esperado: sin errores. Un `[[id]]` hacia una página que todavía no existe tumba
la validación entera, así que los enlaces hacia adelante se agregan cuando el
destino existe.

- [ ] **Paso D — Corre la guarda de la unidad**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_contenedores_curriculum.py -q
```

La guarda se escribe en la Task 8, antes que la primera página, y su lista
`LECCIONES` crece página a página. Eso convierte la forma en TDD; escribirla al
final significa descubrir que 26 páginas la violan.

- [ ] **Paso E — Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/ && git commit -m "feat(unidad-8): <id de la pagina>

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: La guarda de currículum, antes que la primera página

**Files:**
- Create: `tools/test_contenedores_curriculum.py`

**Interfaces:**
- Produces: `LECCIONES: list[Path]` —la lista que crece con cada página—,
  `bloques_bash(texto) -> list[str]`, y `normaliza(linea) -> Iterator[str]`,
  que la comprobación de la chuleta usa.

Es **reescritura, no adaptación**: de las 421 líneas de
`test_regex_curriculum.py` sólo se reaprovechan unas 120 de forma de página. La
mitad ejecutable —correr los bloques bash exigiendo stderr vacío— no se puede
usar sin Docker.

- [ ] **Step 1: Copia la forma de página del molde**

De `tools/test_regex_curriculum.py`: el orden `Meta:` → `::: figure` →
`## En corto`, el máximo de tres viñetas, exactamente un `::: problem` con
`hint` y `answer`, el cierre con callout y la prohibición de `::: note`. Dos
detalles que hay que cambiar al copiar:

- **`rglob`, no `glob`**: la unidad tiene subsecciones y con `glob` la
  comprobación de figuras daría cero.
- **Excluir `_assets/` completo** del barrido de páginas, no sólo
  `CREDITOS.md`.

- [ ] **Step 2: Escribe la regla del `$`**

La que evita que `dollarmath` se coma un `$(pwd)` en silencio:

```python
def test_ningun_dolar_suelto_en_prosa(pagina):
    """Dos $ en una linea de prosa se vuelven MathJax sin error ni warning."""
    for n, linea in enumerate(prosa_sin_fences_ni_code_spans(pagina), 1):
        assert linea.count("$") < 2, (
            f"{pagina.name}:{n} tiene dos $ fuera de un code span: "
            "el renderizador lo va a convertir en MathJax."
        )
```

`prosa_sin_fences_ni_code_spans` tiene que quitar **las dos cosas**: la página
2/9 escribe `--user "$(id -u):$(id -g)"`, que son dos `$` en un solo code span,
y un filtro que sólo quite fences reprueba media unidad.

- [ ] **Step 3: Escribe la regla del `@` y la del HTML crudo**

El regex del `@` se **copia literal** de
`packages/static/src/raya_static/numbered_objects.py:21`, no se escribe a ojo:

```python
REFERENCE_RE = re.compile(
    r"(?<![\\A-Za-z0-9._%+-])@(?P<object_id>[A-Za-z][A-Za-z0-9_-]*)")
```

Escrito a mano genera falsos positivos con `ubuntu@sha256:`. La de HTML crudo
tiene que permitir los placeholders `<tu-login>`, `<usuario>`, `<tu-imagen>` y
compañía **dentro de code span**, que la unidad usa por todas partes.

- [ ] **Step 4: Escribe la normalización de comandos**

Sin ella, la aserción «todo comando citado aparece en la chuleta» exigiría que
la chuleta liste `docker stop mi-postgres-16`:

```python
GRUPOS = {"image", "container", "volume", "network", "system", "context",
          "builder", "buildx", "compose", "config", "manifest", "plugin", "trust"}


def normaliza(linea):
    """`docker stop mi-postgres-16` -> `docker stop`; `docker volume rm x` ->
    `docker volume rm`. Baja de ~60 instancias a ~28 entradas, que es lo que
    una chuleta debe listar."""
    patron = r"\b(docker|podman)\s+(?!-)([a-z]+)(?:\s+(?!-)([a-z]+))?"
    for m in re.finditer(patron, linea):
        binario, a, b = m.groups()
        yield f"{binario} {a} {b}" if a in GRUPOS and b else f"{binario} {a}"
```

El barrido ignora los fences que muestran **salida** —`Unable to find image
locally`, la salida de `docker ps`—, no sólo los de entrada. Y
`docker --version` se casa aparte de `docker version`.

- [ ] **Step 5: Escribe `bash -n` sobre los bloques**

Lo que sí se puede automatizar sin Docker, y atrapa la mitad de los errores
reales:

```python
def test_los_bloques_bash_son_sintacticamente_validos(pagina):
    for i, bloque in enumerate(bloques_bash(lee(pagina))):
        r = subprocess.run(["bash", "-n"], input=bloque, text=True,
                           capture_output=True)
        assert r.returncode == 0, f"{pagina.name} bloque {i}: {r.stderr}"
```

- [ ] **Step 6: Escribe la regla de `roto/Dockerfile`**

**Por ruta exacta.** Si barriera por patrón o recorriera `estudiantes/`, el
primer alumno que entregue su copia arreglada pondría el CI del curso en rojo y
el sitio dejaría de publicarse.

```python
ROTO = RAIZ / "codigo/08_contenedores/roto/Dockerfile"


def test_el_dockerfile_roto_sigue_roto():
    """Si alguien lo arregla aqui, la entrega 2 deja de tener sentido."""
    texto = ROTO.read_text(encoding="utf-8")
    assert "python:latest" in texto, "le pinearon la version"
    assert "USER " not in texto, "le agregaron el USER"
    assert texto.index("COPY . .") < texto.index("pip install"), \
        "le arreglaron el orden del COPY"
```

- [ ] **Step 7: Escribe la cobertura de la lista de verificación**

```python
VERIFICACION = RAIZ / "tools/data/verificacion_contenedores.csv"
```

Columnas `pagina,bloque,comando,runtime,version,fecha,resultado`, **una fila por
fence bash** identificado por página e índice. La guarda comprueba que para cada
página el número de filas iguale el número de bloques. Es lo único decidible sin
parsear shell, y es lo que hace la disciplina real: alguien corrió ese bloque y
anotó la fecha. Crea el CSV con su encabezado y nada más; crece con las páginas.

- [ ] **Step 8: Corre la guarda en vacío**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_contenedores_curriculum.py -q
```

Esperado: verde con cero páginas parametrizadas. `LECCIONES` está vacía todavía.

- [ ] **Step 9: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/test_contenedores_curriculum.py tools/data/verificacion_contenedores.csv
git commit -m "test(unidad-8): la guarda de forma, antes de escribir las paginas

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Tasks 9 a 17: Sección 1 — La idea

Cada fila es una task. Aplica el **Procedimiento de página** con este contrato.
Frontmatter común: `status: ready`, y `prerequisites` encadenando con la página
anterior.

| Task | Archivo | `id` · `estimated_time` | Figura | El `::: problem` |
|---|---|---|---|---|
| 9 | `1_la_idea/1_en_mi_maquina.md` | `en-mi-maquina-si-funciona` · 8m | `cont-intermodal` | Tres fallas del curso: a cuál le sirve un contenedor y a cuál no. Se resuelve en parejas, con manos levantadas antes de la respuesta |
| 10 | `1_la_idea/2_que_es_un_contenedor.md` | `que-es-un-contenedor` · 12m | `cont-ns-cgroups` | Con la salida impresa de `ls -la /proc/1/ns/`, cuántos de los **diez** difieren y cuál no. Respuesta: difieren nueve, coincide `user` |
| 11 | `1_la_idea/3_receta_imagen_contenedor.md` | `receta-imagen-contenedor` · 10m | `cont-tres-abstracciones` | Recortar con tijeras un Dockerfile impreso en dos montones, `build` y `run` |
| 12 | `1_la_idea/4_anatomia_de_docker_run.md` | `anatomia-de-docker-run` · 12m | `cont-anatomia-run` | La escenificación de pie: cinco alumnos son la cadena; se sientan `runc`, `dockerd`, `containerd` y por último el shim, que es el único que tira el proceso |
| 13 | `1_la_idea/5_escalamiento_y_orquestacion.md` | `escalamiento-y-orquestacion` · 10m | `cont-escalamiento` | Un servicio guarda las sesiones en un archivo interno: qué se rompe con tres copias y dónde debería vivir |
| 14 | `1_la_idea/6_vm_contra_contenedor.md` | `vm-contra-contenedor` · 10m | `cont-vm-vs-contenedor` numerada, `cont-espectro` **suelta** | Dado un `docker run`, qué cambiaría si eso fuera una VM: arranque, tamaño, kernel, qué ve del host |
| 15 | `1_la_idea/7_docker_y_podman.md` | `docker-y-podman` · 14m | `cont-docker-vs-podman` numerada, `cont-bench-escala` **suelta** | Corrige el script —no mide los shims, y suma RSS en vez de PSS— y vuelve a contestar quién usa menos memoria. Respuesta: **no hay cruce** |
| 16 | `1_la_idea/8_capas_y_cache.md` | `capas-y-cache` · 15m | `cont-capas-cache` | Dockerfile mal ordenado: qué capas se invalidan al tocar una línea de código, y reescribirlo |
| 17 | `1_la_idea/9_lo_que_cuesta.md` | `lo-que-cuesta` · 15m | `cont-bench-arranque` numerada, `cont-bench-overhead` **suelta** | Con esos números, cuánto cuesta un pipeline de 500 contenedores de 2 s contra uno de un contenedor de 1000 s |

Cuatro cosas de esta sección que se pierden si no se escriben a propósito:

- **Task 9** lleva la objeción que va a hacer la sala: «¿y esto en qué se
  diferencia de un `venv` o de conda?». Tres filas la desarman.
- **Task 10** define `PID` y `/proc`, dice que son ocho tipos pero **diez
  enlaces**, y su fila `USER` dice que Docker no activa user namespaces por
  defecto. Ahí se nombra Kata por primera vez.
- **Task 12** define `daemon` y `socket`, y reparte responsabilidades como las
  midió la revisión: el overlay lo monta el shim o `dockerd`, el cgroup lo crea
  **systemd**, y el orden es **proceso → cgroup → namespaces**.
- **Task 17** define `syscall`, lleva el pie de versiones completo de la unidad,
  y publica los dos resultados de ejecución **diciendo qué miden**: el hash
  compara coreutils 8.32 contra 9.4, y el `sort` es casi todo el `docker exec`.

Al terminar la Task 17, escribe la tabla de deudas de la sección al final de
`1_la_idea/0_index.md`, con su columna `Estado`: doce filas, once que se pagan y
Kubernetes que **no se paga a propósito**.

---

### Tasks 18 a 30: Sección 2 — Manos a la obra

| Task | Archivo | `id` · `estimated_time` | Figura | El `::: problem` |
|---|---|---|---|---|
| 18 | `2_manos_a_la_obra/1_instalar.md` | `instalar-docker-y-podman` · 25m | `cont-sin-sudo` | El bloque de comprobación que sirve en las tres plataformas: `whoami`, `id -u`, `type -a docker`, `docker context ls`, `docker version`, `docker run --rm hello-world` |
| 19 | `2_manos_a_la_obra/2_planes_b.md` | `planes-b-de-instalacion` · 12m | `cont-planes-b` | Diagnosticar tres síntomas reales y decir la causa |
| 20 | `2_manos_a_la_obra/3_a_docker_hub.md` | `a-docker-hub` · 12m | `cont-registro` | Qué se descarga con `docker run ubuntu` y de dónde; y por qué la URL de administración da 404 a los demás |
| 21 | `2_manos_a_la_obra/4_ciclo_de_vida.md` | `ciclo-de-vida-de-un-contenedor` · 12m | `cont-ciclo-de-vida` | Recorrer el ciclo **prediciendo `ps -a`** en cada paso, y por qué `exec` falla en uno detenido |
| 22 | `2_manos_a_la_obra/5_el_dockerfile_por_dentro.md` | `el-dockerfile-por-dentro` · 15m | `cont-build-contexto` | Antes de correr `hola.sh` de tres formas, escribir qué imprime cada una |
| 23 | `2_manos_a_la_obra/6_arreglar_un_dockerfile.md` | `arreglar-un-dockerfile` · 12m | `cont-dockerfile-roto` | Los tres defectos, su consecuencia y su arreglo. El `answer` es la rúbrica de la entrega 2 |
| 24 | `2_manos_a_la_obra/7_donde_vive_cada_byte.md` | `donde-vive-cada-byte` · 10m | `cont-overlay-volumen` | **Una sola** fila: dado un archivo, en cuál de las cuatro cae y por qué |
| 25 | `2_manos_a_la_obra/8_rutas.md` | `rutas-en-docker` · 10m | `cont-rutas` | Montar mal a propósito, cuatro casos. Uno es el `./` olvidado, que crea un named volume vacío sin error |
| 26 | `2_manos_a_la_obra/9_el_archivo_compartido.md` | `el-archivo-compartido` · 15m | `cont-uid-plataformas` | **Predecir el dueño del archivo en tu plataforma** y verificarlo; el `answer` trae las cuatro |
| 27 | `2_manos_a_la_obra/10_los_ocho_casos.md` | `los-ocho-casos` · 15m | `cont-matriz-volumen` | La matriz de `predicciones.md`. Si acertaste las ocho, entendiste volúmenes |
| 28 | `2_manos_a_la_obra/11_las_cuatro_trampas.md` | `las-cuatro-trampas` · 15m | `cont-tapar` | Bind mount contra named volume sobre un path con contenido, con los dos comandos y el `wc -l` |
| 29 | `2_manos_a_la_obra/12_named_volumes_y_postgres.md` | `named-volumes-y-postgres` · 15m | `cont-estado-postgres` | `postgres:17` sobre el volumen de `16`: predecir si funciona. El `answer` trae el mensaje literal del fallo |
| 30 | `2_manos_a_la_obra/13_limpieza.md` | `limpieza-de-docker` · 12m | `cont-prune` | Crear `lab-1`…`lab-5` y borrarlas con un solo pipeline de regex. Enlaza `[[grep-awk-en-serio]]` |

Cinco cosas que esta sección no puede perder:

- **Task 18** cierra con el **prepull**, y eso salva la clase del 22: treinta
  alumnos tras el NAT del ITAM son una sola IP y la sesión baja seis imágenes.
  Como ya hicieron `docker login` en la Task 20, los pulls autenticados cuentan
  contra la cuenta. Y la Task 20 termina recordando volver a `docker login`
  después de su comprobación, porque su propio ejercicio los deja deslogueados.
- **Task 18** también fija dónde se trabaja: Linux nativo o la ruta **ext4** de
  WSL2, nunca `/mnt/c/`.
- **Task 21** tiene **una sola idea**: un contenedor vive lo que vive su proceso
  principal. La tabla de los doce comandos se va a la chuleta.
- **Task 26** lleva la tabla de cuatro plataformas. En Docker Desktop el archivo
  queda de **tu** usuario, no de `root`: la explicación es que ahí el bind mount
  no es tu disco, es un puente.
- **Task 29** dice que ahí **no se publica puerto** —se entra por `exec`— y
  enlaza `[[la-red-y-el-nombre]]` para el porqué.

Al terminar la Task 30, escribe la tabla de deudas de la sección 2 en su índice:
seis filas, cinco que se pagan y `docker cp` que **se delega a DataCamp**,
declarado.

---

### Tasks 31 a 35: Sección 3 — Diseño y seguridad

| Task | Archivo | `id` · `estimated_time` | Figura | El `::: problem` |
|---|---|---|---|---|
| 31 | `3_diseno_y_seguridad/1_la_red_y_el_nombre.md` | `la-red-y-el-nombre` · 12m | `cont-red-y-pod` | **Predecir** si el `ping` al nombre funciona, si el `psql` funciona y si desde el host funciona; después correrlo |
| 32 | `3_diseno_y_seguridad/2_el_contrato.md` | `el-contrato-de-un-servicio` · 15m | `cont-contrato` | Un contenedor con un cron, una API y una base: qué se rompe al escalarlo y cómo se parte |
| 33 | `3_diseno_y_seguridad/3_disenar_un_sistema.md` | `disenar-un-sistema` · 15m | `cont-pipeline-servicios` | Diseñar un scraper diario más un tablero. El `answer` trae **cuatro comprobaciones cerradas** |
| 34 | `3_diseno_y_seguridad/4_cuando_se_rompe.md` | `cuando-se-rompe-el-aislamiento` · 15m | `cont-superficie-ataque` | Un `docker run` con cuatro banderas peligrosas: señalarlas, y **correr** la versión con `--cap-drop ALL` para ver qué falla |
| 35 | `3_diseno_y_seguridad/5_kata_y_el_espectro.md` | `kata-y-el-espectro` · 12m | `cont-espectro` **numerada aquí** | Cuatro escenarios → runtime. Cierra el que la Task 14 dejó abierto, y el `answer` lo dice con esas palabras |

- **Task 31** define `puerto`, y dice que en la red bridge por omisión **no hay
  resolución por nombre**.
- **Task 34** está exenta a 260 líneas. La fila de CVE-2022-0492 es la que mejor
  sostiene la tesis: el bug existía y la configuración por defecto lo tapaba,
  porque el seccomp de Docker bloquea `unshare` sin `CAP_SYS_ADMIN`.
- **Task 35** presenta **dos ejes, no un espectro**: dónde aterriza la syscall
  (rootful y rootless caen en el mismo punto) y qué privilegio tiene quien se
  escapa. Rootless mueve sólo el segundo.

---

### Tasks 36 a 39: Los anexos

| Task | Archivo | `id` | Tope | Qué lleva |
|---|---|---|---|---|
| 36 | `A_chuleta.md` | `chuleta-contenedores` | 320 | Los ~28 comandos normalizados, Docker y Podman lado a lado, por tarea. Absorbe las tablas que las páginas le mandaron. Tabla de errores frecuentes con los de instalación **y los de ejecución**: `exited (127)`, el `no such file or directory` del script con CRLF, `port is already allocated`. Más una fila de `docker cp` |
| 37 | `B_prompts.md` | `prompts-contenedores` | 260 | Los ocho prompts del material viejo, reescritos, con los enlaces oficiales de Docker, Podman y Kata |
| 38 | `C_anidar.md` | `contenedores-anidados` | 260 | El capítulo 6 completo, con `cont-bench-anidado`. Abre reconociendo la contradicción con la Task 34. **Sus comandos entran a la chuleta** |
| 39 | `D_entregas.md` | `entregas-contenedores` | 260 | Los cinco bloques del tablero, con la forma literal que fija el spec: tabla de cuatro filas —fecha, puntos, **branch**, carpeta—, qué archivos, el ritual con la branch escrita, y una línea de criterio de término |

Los cuatro quedan **fuera de la forma de página**: sólo les aplican el tope de
líneas y las reglas de `$`, `@` y HTML crudo.

Al terminar la Task 36, **mide la chuleta**:

```bash
cd ~/itam/fdd_o26 && wc -l course/8_contenedores/A_chuleta.md
```

Si pasa de 320, parte la tabla de errores a su propio anexo antes que recortar
comandos: la aserción de la guarda exige que **todo** comando citado esté ahí.

---

## Fase 4 — Cerrar los índices

### Task 40: Los wikilinks de las cuatro tablas de contenido

**Files:**
- Modify: los cuatro `0_index.md`

- [ ] **Step 1: Sustituye el texto plano por wikilinks**

Ahora que las 35 páginas existen, las tablas de contenido de la Task 3 pasan de
texto plano a `[[id|etiqueta]]`. **La barra va sin escapar**, incluso dentro de
una tabla: `[[id\|etiqueta]]` produce un id con una barra invertida pegada y
rompe el build con `Broken wikilink reference`. Ese error ya tumbó el build de
este repo dos veces.

- [ ] **Step 2: Valida y corre la guarda de wikilinks**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_wikilinks.py -q
```

- [ ] **Step 3: Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/
git commit -m "feat(unidad-8): los indices enlazan las 35 paginas

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Fase 5 — Entregas y calendario

### Task 41: Los cinco objetos oficiales

**Files:**
- Create: `course/8_contenedores/_official/tasks/1_instalar_docker.yaml`
- Create: `course/8_contenedores/_official/assignments/1_datacamp_intro_docker.yaml`
- Create: `course/8_contenedores/_official/assignments/2_imagen_en_docker_hub.yaml`
- Create: `course/8_contenedores/_official/assignments/3_datacamp_intermedio_1_2.yaml`
- Create: `course/8_contenedores/_official/assignments/4_datacamp_intermedio_3_4.yaml`

**Interfaces:**
- Produces: los ids `setup-docker`, `datacamp-introduccion-docker`,
  `imagen-en-docker-hub`, `datacamp-docker-intermedio-1`,
  `datacamp-docker-intermedio-2`. Sus `content.due` y `content.available`
  generan ocurrencias de calendario automáticamente: **no se escriben a mano**
  en el YAML del calendario.

- [ ] **Step 1: Escribe los cinco, con el molde de la unidad 7**

Campos: `id`, `type`, `authority`, y dentro de `content`: `title`,
`instructions`, `resources[]` con `title`/`url`/`note`, `due`, `available`,
`points`, `status: published`, `tags[]`. Omiten `scope.quantum` porque están
colocados junto a la unidad.

Tres hechos del esquema que cambian cómo se escriben:

1. **`content.instructions` no es Markdown.** El builder hace `html.escape()` y
   lo mete en un solo `<p>`: sin tablas, sin listas, sin bloques de código, sin
   saltos de línea. Por eso los objetos de la unidad 7 deletrean todo
   («certificaciones punto md», «cp guion r»). Sigue esa convención, y manda la
   versión legible a `[[entregas-contenedores]]`, que va **primero** en
   `resources`.
2. **`branch` como llave de `content` sería invisible**: el builder sólo lee
   `title`, `summary`/`prompt`/`instructions`/`body`/`question`, `due`,
   `available`, `points`, `weight`, `status` y `tags`. El nombre de la branch va
   **dentro de `instructions`**.
3. **`content.points` se omite en la task**, no se pone en `0`: un `0` se
   renderiza como «0 puntos», que no es lo mismo que «no vale puntos».

Fechas: `available: "2026-09-17"` para los tres primeros, `"2026-09-22"` y
`"2026-09-24"` para los otros dos. `due`: `"2026-09-22"`, `"2026-09-22"`,
`"2026-09-22"`, `"2026-09-24"`, `"2026-09-29"`.

- [ ] **Step 2: Mete las frases que cierran los agujeros**

Cada objeto tiene que decir, en su `instructions`, lo que los revisores
encontraron faltando: que las dos entregas del 22 son dos branches y dos pull
requests nacidas **las dos de `main`**; qué significa el check verde y qué
revisa el profesor; que la carpeta es `08_contenedores` **con el cero**; que la
de certificaciones es `docker/` y **no `github/`**; que se copia con la barra y
el punto desde la terminal; que `__pycache__/` va a aparecer al correr los
`app.py` y la revisión lo rechaza con razón; que la contraseña de Postgres va
en la línea de comandos y no en un `.env`; que los cursos son premium y quien
perdió el acceso lo dice **antes del viernes 18**; y que son **dos** cursos de
Docker, no tres.

La comprobación de `setup-docker` **no puede ser `id -nG | grep docker`**: en
macOS, en Windows y en rootless no existe grupo `docker` ni debe existir.

- [ ] **Step 3: Valida e inspecciona**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya build ~/itam/fdd_o26
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya artifacts inspect ~/itam/fdd_o26/artifact
```

Esperado: los cinco objetos aparecen en `data/official.json` y sus diez
ocurrencias —cinco `available` y cinco `due`— en el calendario.

- [ ] **Step 4: Commit**

```bash
cd ~/itam/fdd_o26
git add course/8_contenedores/_official/
git commit -m "feat(unidad-8): las cinco entregas, con su branch y su carpeta

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 42: Las tres sesiones en el calendario

**Files:**
- Modify: `course/_official/calendar/1_2026-o26.yaml`

Va **después** de los objetos oficiales y de los índices: un `page:` que no
resuelve falla la validación, y en CI no falla en el job `checks` sino dentro
del workflow reusable, donde el mensaje es mucho menos obvio.

- [ ] **Step 1: Agrega las tres entradas**

Después de `session-09`, antes del asueto del 15 de septiembre:

```yaml
  - id: session-10
    kind: session
    date: "2026-09-17"
    start_time: "19:00"
    end_time: "20:00"
    title: "Contenedores: la idea"
    page: la-idea-del-contenedor

  - id: session-11
    kind: session
    date: "2026-09-22"
    start_time: "19:00"
    end_time: "20:30"
    title: "Contenedores: manos a la obra"
    page: contenedores-con-las-manos

  - id: session-12
    kind: session
    date: "2026-09-24"
    start_time: "19:00"
    end_time: "20:30"
    title: "Contenedores: diseño y seguridad"
    page: disenar-con-contenedores
```

`session-10` termina a las **20:00**: es la excepción al horario del semestre, y
el esquema lo permite porque sólo exige `end_time > start_time`. El jueves
2026-09-10 **se queda sin entrada**: esa sesión es de la unidad 7 y ya pasó.

No escribas ninguna fecha de entrega aquí: cada objeto con `content.due` genera
su propia ocurrencia.

- [ ] **Step 2: Valida**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Esperado: sin errores. Si sale un fallo de `page`, es que el id de sección no
coincide con el del `0_index.md`.

- [ ] **Step 3: Commit**

```bash
cd ~/itam/fdd_o26
git add course/_official/calendar/1_2026-o26.yaml
git commit -m "feat(unidad-8): las sesiones 10, 11 y 12 en el calendario

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Fase 6 — Cerrar

### Task 43: La guarda del generador

**Files:**
- Create: `tools/test_gen_contenedores.py`

Va al final porque contiene «cada SVG referenciado desde alguna página», que
sólo puede pasar cuando las 35 páginas existen.

- [ ] **Step 1: Escribe la comparación disco contra generador**

**Sin el fixture que regenera antes de comparar.** `test_gen_git.py` y
`test_gen_regex.py` lo tienen, y por eso **no detectan una edición a mano**: el
generador sobrescribe el archivo y el assert pasa siempre. Sólo
`test_diagramas.py` la atrapa de verdad, y es el comportamiento que esta guarda
promete.

- [ ] **Step 2: Replica las aserciones de los generadores existentes**

`aria-label` de 80 caracteres o más, `fill` explícito en todo `<text>`, fondo
horneado, colores contenidos en `skins/fdd-eva.yaml`, ningún texto fuera del
lienzo, cada SVG referenciado desde alguna página (**con `rglob`**), y el
generador saliendo con código distinto de cero ante un nombre desconocido.

- [ ] **Step 3: Comprueba el mapa figura→CSV**

Que los cuatro CSV de `CSV_DE` existan y traigan sus columnas, y que
`len(DIAGRAMAS)` iguale los archivos `cont-*.svg` del disco: 30.

- [ ] **Step 4: Corre la suite completa**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Esperado: las 736 anteriores más las de la unidad 8, todas en verde. Tarda unos
dos minutos y medio. Localmente esto corre además un `raya build` completo por
los tests del dashboard de la unidad 3, así que un curso roto se ve aquí como
falla de pytest.

- [ ] **Step 5: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/test_gen_contenedores.py
git commit -m "test(unidad-8): la guarda del generador de figuras

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 44: Los archivos de fuera que quedan desactualizados

**Files:**
- Modify: `CLAUDE.md`, `AGENTS.md`, `README.md`
- Modify: `course/0_index.md`
- Modify: `course/1_introduccion/1_el_curso/0_index.md`

- [ ] **Step 1: `CLAUDE.md`**

Tres cosas dejan de ser ciertas: «currently `session-01` through `session-09`,
ending at 2026-09-08», la lista cerrada de `page` válidos, y la franja
Tue/Thu 19:00–20:30, que ahora tiene **una excepción declarada**. Agrega
también la unidad 8 a la descripción de la estructura.

- [ ] **Step 2: `AGENTS.md`**

El `CLAUDE.md` raíz obliga a mantenerlos consistentes: cualquier cambio en uno
se refleja en el otro.

- [ ] **Step 3: `README.md` y `course/0_index.md`**

Sólo el horario: dejar dicho que la sesión del 17 de septiembre termina a las
20:00.

- [ ] **Step 4: `course/1_introduccion/1_el_curso/0_index.md`**

La Fase 2 anuncia «9 Docker I» y «10 Docker II» como dos unidades. Se combinan
en **una sola de tres sesiones**. Ese cambio es la intención, no un efecto
secundario.

- [ ] **Step 5: Valida y corre todo**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

- [ ] **Step 6: Commit**

```bash
cd ~/itam/fdd_o26
git add CLAUDE.md AGENTS.md README.md course/0_index.md course/1_introduccion/
git commit -m "docs: la unidad 8 entra al calendario, al plan y al horario

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 45: Las verificaciones que necesitan una máquina

Ninguna se puede hacer con el teclado, y dos pueden arruinar una clase en vivo.

- [ ] **Step 1: El laboratorio de permisos en un Mac real**

Es lo único del informe técnico que se apoya en issues oficiales y no en
medición. Corre el laboratorio de `el-archivo-compartido` en un Mac con Docker
Desktop y comprueba de quién queda el archivo. Si no es del usuario del Mac,
corrige la tabla de cuatro plataformas de la Task 26. **Antes del 22 de
septiembre.**

- [ ] **Step 2: Los comandos de Kata**

En una máquina con KVM. Comprueba el contraste de `uname -r` entre un
contenedor normal y uno de Kata. Si no corren, la Task 35 se queda con la
explicación y sin demostración — y hay que quitar la promesa de la
demostración, no dejarla escrita.

- [ ] **Step 3: La salida de `ls /proc/1/ns/`**

Captúrala en la **versión exacta de Docker** que se vaya a usar en clase: el
comportamiento de `time` cambia entre runtimes y entre versiones, y si la
página imprime una salida y la máquina da otra, el ejercicio de la Task 10 se
cae solo.

- [ ] **Step 4: Los dos datos que caducan**

Confirma que *Intermediate Docker* sigue teniendo cuatro capítulos en ese orden
—las entregas 3 y 4 los parten— y revisa los límites de pull de Docker Hub, que
cambiaron en 2025 y que son de lo que depende el prepull de la Task 18.

- [ ] **Step 5: Llena la lista de verificación**

Cada bloque de comandos que corriste va a
`tools/data/verificacion_contenedores.csv` con su runtime, su versión y su
fecha. La guarda de la Task 8 comprueba la cobertura.

- [ ] **Step 6: Commit**

```bash
cd ~/itam/fdd_o26
git add tools/data/verificacion_contenedores.csv course/8_contenedores/
git commit -m "test(unidad-8): los comandos de la unidad, corridos y anotados

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

## Self-review

**Cobertura del spec.** Recorrí sus secciones: estructura (Task 3 y Fase 3),
las 26 páginas (Tasks 9-35), los cuatro anexos (Tasks 36-39), los objetos
oficiales (Task 41), el espejo (Task 1), el código publicado y los datos
(Task 2), las figuras (Tasks 4-7), las guardas (Tasks 8 y 43), el orden de
construcción (las seis fases), fuera de la unidad (Task 44) y los riesgos
(Task 45). Las dos reglas de CI están en el plan hermano. Las diecinueve
correcciones técnicas viajan dentro de las páginas que las aplican, y las que
más fácil se pierden están llamadas por su nombre bajo cada tabla de sección.

**Placeholders.** Los pasos de código traen el código. Las tasks de página
traen su contrato verificable —ruta, id, minutos, figura, ejercicio— y la
sustancia vive en la sección homónima del spec, que el encabezado declara como
documento acompañante. El Procedimiento de página está escrito una vez y
completo, no diferido.

**Consistencia de tipos.** `DIAGRAMAS` se define en la Task 5 y se fusiona en la
Task 6; `CSV_DE` se define en la Task 5 y se consume en la Task 43;
`ESTADISTICO` en la Task 5; `LECCIONES`, `bloques_bash()` y `normaliza()` en la
Task 8 y se usan en la Fase 3; `ROTO` y `VERIFICACION` en la Task 8 y la
Task 45. Los 30 ids de figura de la Task 4 son exactamente los que citan las
tablas de las Fases 3.

**Una omisión que dejo a propósito.** El plan no fija el texto de las 26
páginas: son ~3,900 líneas de prosa en español y su lugar es el spec, no el
plan. Lo que el plan sí fija es todo lo que una guarda o el validador pueden
comprobar.
