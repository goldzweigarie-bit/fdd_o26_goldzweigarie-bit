# Unidad 8 — Contenedores

Diseño de la unidad. Tres sesiones de clase, una sola unidad publicada.

**Versión 3.** Dos rondas de revisión adversarial, cuatro revisores cada una:
pedagogía para lector con ADHD, exactitud técnica, un estudiante torpe contra
las entregas, y el contrato técnico del repositorio. La segunda ronda **midió en
la máquina de referencia** en vez de leer documentación, y tumbó cuatro
afirmaciones de la v2 — una de ellas peor que el error que pretendía corregir.
El patrón de fallo de la v2 fue enunciar la corrección en la tabla y dejar la
versión vieja en el cuerpo de la página; la v3 corrige las dos puntas.

Se reescribe sobre `fdd_p26/clase/08_containers/`: 2,879 líneas de Markdown,
cuatro laboratorios, cinco scripts de benchmark con sus mediciones, y trece
imágenes de las que sólo cuatro se usan. Nada se tira. **Trazabilidad** dice
dónde quedó cada pieza; **Qué corregimos** dice qué estaba mal.

## Qué es

Una unidad de tres clases que lleva a alguien que nunca ha corrido un contenedor
desde "¿qué es eso?" hasta publicar su propia imagen en un registro público y
saber decidir cómo se reparte un sistema en servicios.

| Sesión | Fecha | Horario | Sección |
|---|---|---|---|
| `session-10` | jueves 2026-09-17 | 19:00–**20:00** | 1 · La idea |
| `session-11` | martes 2026-09-22 | 19:00–20:30 | 2 · Manos a la obra |
| `session-12` | jueves 2026-09-24 | 19:00–20:30 | 3 · Diseño y seguridad |

La primera es **corta y sin computadora**. Su horario rompe la franja de 90
minutos del resto del semestre, así que hay que anunciarlo en clase y actualizar
los tres archivos que documentan el horario.

**El presupuesto se cuenta en trabajo, no en lectura.** Una página práctica no
cuesta lo que se tarda en leerla: cuesta teclear, esperar el `pull`,
equivocarse y arreglar. Por eso las clases llevan **pocas páginas en clase y
muchas de lectura**, y el reparto está calculado sobre el trabajo real:

| Sesión | Páginas en clase | Lectura en clase | Ejercicios | Total | Franja |
|---|---:|---:|---:|---:|---:|
| 1 | 4 | 42 min | ~20 min | ~62 | 60 |
| 2 | 4 | 52 min | ~35 min | ~87 | 90 |
| 3 | 5 | 69 min | ~20 min | ~89 | 90 |

Fuera de clase: ≈ 236 min de lectura —las páginas de lectura y previa, más los
cinco anexos de referencia— **más 8 h 27 de DataCamp**, o sea unas **12 horas y
media en doce días**. Ese número va escrito en `0_index.md` de la unidad,
porque es donde un alumno decide cómo reparte su semana.

## Idea que sostiene toda la unidad

**Un contenedor no es una máquina pequeña: es un proceso de Linux con la vista
recortada y la despensa medida.**

Si es un proceso, arranca en milisegundos y **vive exactamente lo que vive ese
proceso**. Si comparte el kernel, un bug del kernel es un bug de todos. Si es
desechable, se pueden correr mil copias idénticas — y entonces el estado no
puede vivir adentro. Si el estado vive afuera, hay que decidir dónde, y eso ya
es diseño de sistemas.

Registro heredado de las unidades 5, 6 y 7: el concepto llega **después** de la
falla concreta. Español para la prosa, inglés para los términos técnicos. Se
dice "contenedor", no "container". Se dice "chuleta", como en la unidad 6.

## El hilo de arquitectura: un nivel por clase

| Clase | Nivel | Pregunta que contesta |
|---|---|---|
| 1 | **El runtime** | ¿Qué pasa exactamente cuando escribo `docker run`? |
| 2 | **La imagen y el almacenamiento** | ¿Dónde vive cada byte, y quién lo borra? |
| 3 | **El sistema** | ¿Cómo se reparte una aplicación en contenedores? |

Tres conceptos se **nombran temprano y se desarrollan tarde**: **Kata** (se
nombra en 1/2, se paga en 3/5), **orquestación** (se planta en 1/1, se paga en
1/5) y **gVisor** (aparece en la figura del espectro de 1/6, se paga en 3/5).
Toda deuda que se abre está tabulada al final de su sección, con una columna que
dice si se paga o si se deja abierta a propósito.

## El reparto con DataCamp

Temarios verificados el 2026-09-15 en `datacamp.com`.

**Introduction to Docker** — 4 h 11. Cap. 1 `run`, detached, interactivo,
`stop`/`rm`, limpiar, `pull`, tags · Cap. 2 registros, `build`, Dockerfile,
`COPY`, `CMD` · Cap. 3 caché y orden, `WORKDIR`, `USER`, `ARG`/`ENV`, no root.

**Intermediate Docker** — 4 h 16. Cap. 1 `docker help`, `--rm`, montar el
filesystem del host, `docker cp`, volúmenes · Cap. 2 puertos, `EXPOSE`, redes ·
Cap. 3 capas, multi-stage, multi-platform · Cap. 4 Docker Compose.

El ciclo: **la clase da la idea, la tarea la teclea, y la clase siguiente da por
tecleado lo que la tarea entrenó.**

| Se da en clase porque DataCamp no puede | Se le deja a DataCamp |
|---|---|
| Instalación, post-install, sin `sudo`, `podman machine`, arquitectura de CPU | `run`, `stop`, `rm`, `pull`, tags |
| Podman, rootless, subuid, sin daemon | `build`, `COPY`, `CMD`, `ARG`/`ENV`, `USER` |
| Namespaces, cgroups, VMs, el costo medido | `push` y `pull` a un registro |
| Rutas del host, permisos UID, bind mounts sobre tu disco | Volúmenes y redes como comandos |
| Diseño, contratos de servicio, seguridad, Kata | Multi-stage, multi-platform, Compose |

DataCamp corre en un sandbox del navegador: no tiene máquina, no tiene rutas del
host, no tiene arquitectura de CPU, no tiene Podman y no tiene seguridad más
allá de "no uses root".

## Qué corregimos del curso pasado

### Defectos de estructura

1. **La instalación vivía en otra unidad**, enterrada como tarea 7.0 en
   `07_regex/00_index.md`, sin puntos. Aquí es página propia, tarea oficial con
   fecha, y **con planes B**, como la unidad 4.
2. **Páginas imposibles de leer**: 774 líneas la de volúmenes, 575 la de Docker.
3. **Los volúmenes se enseñaban dos veces.** Aquí cada idea vive en una página, y
   `CMD`/`ENTRYPOINT` sólo aparece donde se puede correr.
4. **Los benchmarks eran un capítulo suelto** que no sostenía ninguna decisión.
5. **No había hilo de arquitectura.**
6. **Faltaba el porqué del mundo**: Kubernetes mencionado tres veces sin decir
   qué es.
7. **Cero seguridad.**
8. **El módulo terminaba en un callejón**: sin entrega, sin artefacto propio.
9. **Ejercicios sin criterio de término.**
10. **Basura commiteada**: un `echo "=== Discooooooooooo ==="` en `info.sh`, y
    `output.txt` con el laboratorio ya resuelto.
11. **Trece PNG, cuatro usados**, con fondo blanco ilegible sobre el tema.
12. **Los prompts para LLM partían la lectura.**
13. **Ejercicios que escriben en `/tmp` del host**, uno con `rm -rf`.

### Errores técnicos que el material viejo enseñaba mal

Diecinueve correcciones. Las marcadas **(v3)** son correcciones *a la v2*: la
primera ronda las arregló a medias o las empeoró, y la segunda las midió.

| # | Lo que decía | Lo que es |
|---|---|---|
| 14 | `dockerd → containerd → runc` | Falta **`containerd-shim-runc-v2`**, uno por contenedor. `runc` corre dos veces (`create` y `start`) y **sale las dos**; en estado estable no queda ningún `runc`. El padre del PID 1 es el shim, reparentado a systemd por un doble fork explícito |
| 15 | "Matar el daemon mata los contenedores" | `kill -9 dockerd` **no** los mata. **(v3)** Pero "el daemon los re-adopta" también es falso: con el default `live-restore: false`, `daemon.restore()` llama a `shutdownContainer()` y **el daemon reiniciado los mata**. Y hay una tercera pieza: **matar el shim sí mata el contenedor** |
| 16 | "Ya no hay nada de Docker en medio" | No hay nada en el **camino de ejecución**; el shim conserva stdio, código de salida y reaping. Se prueba imprimiendo el árbol: el contenedor cuelga del shim, que cuelga de PID 1 — ni `dockerd` ni `containerd` aparecen |
| 17 | "root en el contenedor no es root en el host" | **Docker no activa user namespaces por defecto.** `user` es el **único** de los diez enlaces de `/proc/1/ns/` que coincide con el host. **(v3)** Sólo vale en **Linux nativo**: en Docker Desktop de macOS y en rutas de Windows el archivo sale de **tu** usuario, porque el filesystem compartido inventa la propiedad |
| 18 | "Un volumen vacío reemplaza lo de la imagen" | Cierto para **bind mount**. Un **named volume vacío copia** el contenido de la imagen. **(v3)** La opción que lo apaga es **`:nocopy`** en `-v` y `volume-nocopy` en `--mount`; **Podman se comporta idéntico** |
| 19 | Seis namespaces | Son **ocho tipos**. **(v3)** Pero `ls /proc/<pid>/ns/` imprime **diez enlaces**: `pid` y `time` aparecen también como `_for_children`. Nueve difieren del host; el que no, es `user` |
| 20 | `runc` "monta el overlay" y "crea el cgroup" | **(v3) Las dos son falsas.** El overlay lo monta **el shim** (`mount.All`), o **`dockerd` mismo** con el graphdriver `overlay2`, que es lo que tendrán instalado. Y el cgroup lo crea **systemd** vía `StartTransientUnit`, porque el cgroup driver por defecto en cgroups v2 es `systemd`; `runc` sólo escribe los knobs que systemd no expone. El orden real es **proceso → cgroup → namespaces** |
| 21 | Podman "se salta media cadena" | Se salta el **daemon**, no el runtime: `podman → conmon → crun/runc`. **(v3)** Y el 2× de arranque **no lo explica el daemon**: fijando todo menos el runtime, `podman --runtime crun` da 193 ms, `podman --runtime runc` 363 ms y `docker` 330 ms. Con `runc`, **Podman rootless es ~10 % más lento** |
| 22 | Podman rootless "no necesita nada" | Necesita rango en `/etc/subuid`/`subgid` y `newuidmap`/`newgidmap` del paquete `uidmap`, que en Debian y Ubuntu es **Recommends**: falta con `--no-install-recommends` y en imágenes base |
| 23 | Rootless "no tiene el problema de UID" | Mapea el **UID 0 a tu UID, y sólo ése**; los demás caen en tu rango de subuid. **(v3)** Para el caso común la respuesta no es `podman unshare` —que **no existe en macOS**, donde el cliente es remoto— sino **`--userns=keep-id`** o el sufijo **`:U`** del volumen |
| 24 | git "guarda los diffs" | git guarda **snapshots direccionados por contenido**; lo enseña nuestra propia `[[que-guarda-un-commit]]` |
| 25 | CVE-2022-0492 = contenedor privilegiado | Al revés: funcionaba **sin privilegios**. Dos filas: la mala configuración de siempre y el CVE. **(v3)** Y con `docker run` por defecto **nunca fue explotable**: el perfil seccomp bloquea `unshare` sin `CAP_SYS_ADMIN`, y AppArmor bloquea montar cgroupfs. Se abría con `--privileged`, con `seccomp=unconfined`, o en Kubernetes, donde los pods vienen sin seccomp |
| 26 | Leaky Vessels: "no corras como root" | Mitigación: **runc ≥ 1.1.12** (rango afectado **1.0.0-rc93 – 1.1.11**) y BuildKit ≥ 0.12.5. Son cuatro CVE. **(v3)** `USER` no mitiga el vector pero **sí estorba la sobrescritura**: es defensa en profundidad, y decir "no mitiga" a secas invita a concluir que `USER` no sirve |
| 27 | "`docker run -v ./x:/app` falla siempre" | Funciona **desde Docker CLI 23**, y también en Podman. **(v3)** La trampa real no es la versión: es que **`-v dir:/app` sin `./` crea un named volume vacío** y lo monta, sin error |
| 28 | Kata fuera de macOS "por Apple Silicon" | **Kata es un runtime de Linux**: no hay binarios para macOS. **(v3)** Y la virtualización anidada en Apple Silicon **existe desde M3** con macOS 15; lo que falta es que Docker Desktop exponga `/dev/kvm` |
| 29 | "El overlay escribe ~20 % más lento" | Sale de un CSV que reporta a Podman **3.7×** más rápido que bare metal: midió page cache. Queda el **copy-up** cualitativo |
| 30 | Baseline "1.8 ms a pelo" | **(v3)** No es "el piso del cronómetro": el intervalo va de un `date` al siguiente, así que **mide el `fork`+`execve` de `/usr/bin/date`**. Es el costo de arrancar un programa — el programa equivocado. Y es **mediana**: la media es 3.1 ms por el ramp-up de frecuencia |
| 31 | "El hash es más rápido dentro" (teoría del VFS) | El experimento compara **binarios distintos**. **(v3)** El mecanismo no es SHA-NI —esta CPU no lo tiene y ninguno de los dos enlaza `libcrypto`—: es **GNU coreutils 8.32 del host contra 9.4 de la imagen**, 3.4× sobre el mismo archivo. Y con `ubuntu:latest`, que hoy es 26.04 con coreutils en Rust, **el signo se invierte** |
| 32 | "El cruce está en ~100 contenedores" | **(v3) No hay cruce.** El script mide el RSS de `dockerd` y **suma el de todos los `conmon`**: cuenta el supervisor por contenedor de Podman e ignora el de Docker. Medido: shim **11.0 MB/contenedor**, `conmon` **2.02 MB**. Podman gana en todo N. Y sumar RSS **doble-cuenta páginas compartidas**: 12 `conmon` son 25 MB de RSS y 4 MB de PSS |

Dos errores de definición que sobreviven en el material viejo y hay que matar:
`04_benchmarks.md` afirma que el RSS "no incluye páginas compartidas con otros
procesos" —falso, y es justo lo que hace parecer legítimo sumarlos— y llama
"ruido" a lo que es un confound.

Lo que se agrega: la anatomía de `docker run`, **el contenedor vive lo que vive
su proceso principal**, la comparación con `venv` y conda, la tabla de dónde vive
cada byte, un `Dockerfile` roto para arreglar, la limpieza por regex, Docker Hub,
la arquitectura de CPU, la red y el nombre, el contrato de un servicio, el diseño
de un sistema, los exploits con sus cierres, Kata y los dos ejes del aislamiento,
la chuleta, los planes B y el tablero de entregas.

## Reglas de escritura de esta unidad

Verificadas contra el framework. Las tres primeras rompen el sitio en silencio o
en ruidoso; la guarda las comprueba.

1. **Todo `$` va dentro de code span o fence.** El renderizador carga
   `dollarmath`: dos `$` en una línea de prosa se vuelven MathJax **sin error y
   sin warning**. `$(pwd)`, `$USER`, `$GHUSER` están por todas partes.
2. **Todo `@` suelto va en code span.** `@reboot` tumba el build.
   `ubuntu@sha256:` y los correos son seguros.
3. **Nada de HTML crudo.** No rompe el build: se escapa en silencio y sale
   visible. Ninguna guarda existente lo detecta.
4. **Llaves dobles son inertes**: `--format '{{.State.Pid}}'` sale literal.
5. **Tope de 160 líneas** por página de lección. **Exentas a 260**:
   `instalar-docker-y-podman`, `planes-b`, `cuando-se-rompe-el-aislamiento`,
   `B_prompts`, `C_anidar`, `D_entregas`. **`A_chuleta` a 320**: la de Git usa
   207 con un solo runtime y sin tabla de errores; ésta lleva dos runtimes y ~28
   comandos normalizados. El tope de 160 viene de la unidad 6; la unidad 7 lo
   excede en once de sus dieciséis páginas, así que no es "la norma del curso".
   **Exentas a 215 — las tres páginas estructuradas de la sección 1**:
   `docker-y-podman`, `capas-y-cache`, `lo-que-cuesta`. El motivo es distinto al
   de las de 260 y conviene no confundirlos: el techo cuenta **líneas de
   fuente**, y aquí un párrafo ocupa una sola por largo que sea — el de 314
   palabras de `lo-que-cuesta` costaba **1 línea**. Partir esos muros en tablas,
   viñetas y avisos para lectores con ADHD **baja las palabras y sube las
   líneas**: ese párrafo quedó en 90 palabras y 14 líneas. Medido en líneas la
   mejora parece un empeoramiento, así que en estas tres el techo se subió en
   vez de borrar contenido. Eso vale para `lo-que-cuesta` (144→205 líneas,
   3613→3264 palabras) y `docker-y-podman` (158→187, 2930→2905); en
   `capas-y-cache` (152→185, 1745→**1814**) el techo subió por otra razón y hay
   que decirla: **se le añadió material**, no es reflow. Las otras **seis**
   lecciones de la sección **siguen bajo 160** tras la misma reescritura, y
   `anatomia-de-docker-run` cupo en 155.
   **2026-09-22 — se suman los dos laboratorios de la sección 2**,
   `lab-sin-volumen` y `lab-con-volumen`, también a 215. No crecieron por
   reflow sino por aire: cada experimento lleva «Predice / Haz / Deberías ver /
   Por qué» en líneas propias. A 160 hubo que pegar el «Haz» a la pregunta y
   quitar los blancos antes de los encabezados, y la página dejó de escanearse.
   **Mismo día, más tarde — las ocho páginas de la clase 2 pasan a un techo
   propio de 260** (`CLASE` en la guarda). El profesor pidió que cada bandera y
   cada subcomando se explique donde se usa; cada bloque lleva su «Qué hace cada
   pieza», una línea por pieza, y eso sube las líneas sin subir la prosa.
6. **Forma de página**: `Meta:` de una línea → `::: figure` → `## En corto` con
   **máximo tres viñetas** → cuerpo → **exactamente un `::: problem` con `hint` y
   `answer`** → cierre en **dos líneas** (`> [!NOTE]`, y en la siguiente `> **Si sólo recuerdas una cosa:** …`): con el cuerpo en la misma línea el marcador no casa `_CALLOUT_MARKER_RE` y **sale impreso como texto**, sin fallar el build. Lo vigila `tools/test_callouts.py`. Prohibido
   `::: note`. **Aplica a las 26 páginas de lección y a ninguna otra**: los
   cuatro índices y los cinco anexos sólo están sujetos al tope de líneas y a las
   reglas 1 a 4, como en la unidad 6.
7. **Cada página de lección tiene su propia figura numerada.** Sin excepciones y
   sin lista de exentas: la guarda hace `index("::: figure")` y revienta si
   falta. Por eso el inventario subió a 29 SVG.
8. **Marcador de posición**: `**Página N de M · sección S de 3**`, numerado **por
   sección**. Índices y anexos no lo llevan.
9. **Toda cifra de benchmark lleva su pie** con máquina, kernel y versiones de
   runtime **y de las herramientas medidas** (coreutils, en el caso del hash).
   El pie completo vive una sola vez, en `lo-que-cuesta`; las cifras citadas en
   otras páginas llevan una línea con enlace a ella.
10. **`**Haz:** → **Deberías ver:**`** — toda página con bloques ejecutables
    lleva al menos tres tramos, ninguno de más de 15 líneas. Es el dispositivo
    que hace legible a la unidad 6, donde aparece entre 9 y 15 veces por página,
    y sin él el marco de la regla 6 envuelve 160 líneas de prosa corrida.
11. **Nueve palabras que el curso nunca definió** — `daemon`, `socket`, `puerto`,
    `syscall`, `PID`, `/proc`, `réplica`, `estado`, `psql` — llevan definición de
    una línea **en su primera aparición y sólo ahí**; después se enlaza.

## Estructura

```
course/8_contenedores/
  0_index.md
  1_la_idea/               9 páginas   (4 en clase · 5 de lectura)
  2_manos_a_la_obra/      13 páginas   (4 en clase · 9 de lectura)
  3_diseno_y_seguridad/    5 páginas
  A_chuleta.md  B_prompts.md  C_anidar.md  D_entregas.md
  _assets/                30 SVG + portada + CREDITOS.md
  _assets/benchmarks/     5 scripts + requirements.txt + 13 CSV
  _official/              1 task · 4 assignments
  code/analyze.py
```

> **Nota 2026-09-22 — la sección 2 pasa de 13 a 16 páginas (reparto 9 · 16 · 5,
> 30 lecciones, 38 páginas).** La clase perdía tiempo en instalar, planes B y
> Docker Hub, que el grupo ya traía de DataCamp. Ahora las páginas 1–8 son la
> clase (repaso Dockerfile → imagen → contenedor, ciclo de vida, Dockerfile,
> dónde vive cada byte, dos laboratorios nuevos —`lab-sin-volumen` y
> `lab-con-volumen`—, Postgres y limpieza), la 9 es la entrega
> (`arreglar-un-dockerfile`) y la 10–16 quedan como **referencia**: instalar,
> planes B, Docker Hub, rutas, el archivo compartido, los ocho casos y las
> cuatro trampas. Ninguna página vieja se borró y ningún objeto oficial cambió.
> Lo que sigue en este spec describe el reparto original y no se reescribió.

Los prefijos `10_`…`13_` **ordenan numéricamente**: `parse_ordered_name()`
convierte el prefijo a `int`. Comprobado con una sección de prueba. No rellenar
con ceros: un `01_` obligaría a rellenar a todos los hermanos.

| Archivo | id | Min | Dónde |
|---|---|---:|---|
| `0_index.md` | `contenedores` | — | — |
| `1_la_idea/0_index.md` | `la-idea-del-contenedor` | — | — |
| `1_la_idea/1_en_mi_maquina.md` | `en-mi-maquina-si-funciona` | 8 | clase |
| `1_la_idea/2_que_es_un_contenedor.md` | `que-es-un-contenedor` | 12 | clase |
| `1_la_idea/3_receta_imagen_contenedor.md` | `receta-imagen-contenedor` | 10 | clase |
| `1_la_idea/4_anatomia_de_docker_run.md` | `anatomia-de-docker-run` | 12 | clase |
| `1_la_idea/5_escalamiento_y_orquestacion.md` | `escalamiento-y-orquestacion` | 10 | lectura |
| `1_la_idea/6_vm_contra_contenedor.md` | `vm-contra-contenedor` | 10 | lectura |
| `1_la_idea/7_docker_y_podman.md` | `docker-y-podman` | 14 | lectura |
| `1_la_idea/8_capas_y_cache.md` | `capas-y-cache` | 15 | lectura |
| `1_la_idea/9_lo_que_cuesta.md` | `lo-que-cuesta` | 15 | lectura |
| `2_manos_a_la_obra/0_index.md` | `contenedores-con-las-manos` | — | — |
| `2_manos_a_la_obra/1_instalar.md` | `instalar-docker-y-podman` | 25 | previa |
| `2_manos_a_la_obra/2_planes_b.md` | `planes-b-de-instalacion` | 12 | previa |
| `2_manos_a_la_obra/3_a_docker_hub.md` | `a-docker-hub` | 12 | previa |
| `2_manos_a_la_obra/4_ciclo_de_vida.md` | `ciclo-de-vida-de-un-contenedor` | 12 | clase |
| `2_manos_a_la_obra/5_el_dockerfile_por_dentro.md` | `el-dockerfile-por-dentro` | 15 | lectura |
| `2_manos_a_la_obra/6_arreglar_un_dockerfile.md` | `arreglar-un-dockerfile` | 12 | lectura |
| `2_manos_a_la_obra/7_donde_vive_cada_byte.md` | `donde-vive-cada-byte` | 10 | clase |
| `2_manos_a_la_obra/8_rutas.md` | `rutas-en-docker` | 10 | lectura |
| `2_manos_a_la_obra/9_el_archivo_compartido.md` | `el-archivo-compartido` | 15 | clase |
| `2_manos_a_la_obra/10_los_ocho_casos.md` | `los-ocho-casos` | 15 | clase |
| `2_manos_a_la_obra/11_las_cuatro_trampas.md` | `las-cuatro-trampas` | 15 | lectura |
| `2_manos_a_la_obra/12_named_volumes_y_postgres.md` | `named-volumes-y-postgres` | 15 | lectura |
| `2_manos_a_la_obra/13_limpieza.md` | `limpieza-de-docker` | 12 | lectura |
| `3_diseno_y_seguridad/0_index.md` | `disenar-con-contenedores` | — | — |
| `3_diseno_y_seguridad/1_la_red_y_el_nombre.md` | `la-red-y-el-nombre` | 12 | clase |
| `3_diseno_y_seguridad/2_el_contrato.md` | `el-contrato-de-un-servicio` | 15 | clase |
| `3_diseno_y_seguridad/3_disenar_un_sistema.md` | `disenar-un-sistema` | 15 | clase |
| `3_diseno_y_seguridad/4_cuando_se_rompe.md` | `cuando-se-rompe-el-aislamiento` | 15 | clase |
| `3_diseno_y_seguridad/5_kata_y_el_espectro.md` | `kata-y-el-espectro` | 12 | clase |
| `A_chuleta.md` | `chuleta-contenedores` | 8 | referencia |
| `B_prompts.md` | `prompts-contenedores` | 8 | referencia |
| `C_anidar.md` | `contenedores-anidados` | 18 | anexo |
| `D_entregas.md` | `entregas-contenedores` | 10 | referencia |

Treinta y cinco archivos `.md`: 26 de lección, 4 índices, 5 anexos. ≈ 399 min.
`prerequisites` de la unidad: `git-y-github`.

**Ningún id choca**, verificado por grep y ejecutando el resolvedor del
framework contra los 63 ids de página, 155 objetos numerados y 59 objetos
oficiales existentes. `cuando-se-rompe-el-aislamiento` no choca con
`cuando-se-rompe` de la unidad 2. Las ocurrencias del calendario viven en su
propio namespace (`official:<id>:due`). Ambigüedad menor conocida: el resolvedor
indexa el stem sin despojar prefijos de letra, así que `[[A_chuleta]]` sería
ambiguo entre la unidad 6 y la 8 — se usa `[[chuleta-contenedores]]`.

---

# Sección 1 — La idea · `session-10` · jueves 2026-09-17 · 60 min

Sin computadora. **Cuatro páginas en clase, cinco de lectura.** Las páginas se
proyectan; sólo se imprime la salida del ejercicio de la página 2.

`receta-imagen-contenedor` va **antes** que `anatomia-de-docker-run`, porque la
anatomía explica el arranque de una imagen y hay que saber qué es una imagen
primero. Es la misma corrección que la unidad 7 hizo al mover "qué guarda un
commit" después de "tu primer repositorio".

### 1 · En mi máquina sí funciona — `en-mi-maquina-si-funciona` · 8 min · clase

Meta: entender qué problema resolvieron los contenedores y por qué el mundo se
movió a ellos.

El problema primero, con fallas del propio curso: el script de bash de la unidad
5 que no corre en la máquina del compañero, la versión de `grep` que cambia el
resultado de un patrón de la unidad 6, el pipeline de la unidad 2 que vive en la
laptop y muere en el servidor. Después McLean y el contenedor intermodal de
1956, con la tabla carga↔software.

**Y la objeción que va a hacer la sala entera**, porque son alumnos de ciencia de
datos que ya usan entornos virtuales: *"¿y esto en qué se diferencia de un `venv`
o de conda?"*. Tres filas la desarman —un `venv` aísla paquetes de Python; el
contenedor aísla además el intérprete, las librerías del sistema, los binarios
(`grep`, la falla de la unidad 6) y el sistema de archivos— y de paso explican
por qué la tercera falla de la lista no la arregla un `requirements.txt`.

Cierra plantando lo que desarrolla la página 5: el contenedor no sólo hace que
corra igual en otra máquina, hace que corra **igual mil veces a la vez**.

- Figura `cont-intermodal`.
- `::: problem` — tres fallas del curso, a cuál le sirve un contenedor y a cuál
  no. **Se resuelve en parejas y se levanta la mano por opción** antes de dar la
  respuesta.

### 2 · Qué es un contenedor — `que-es-un-contenedor` · 12 min · clase

Meta: que "proceso aislado" deje de ser una frase hecha.

Un proceso de Linux que **comparte el kernel del host** y tiene su propia vista
de archivos, procesos, red, usuarios y recursos. Namespaces = qué puede **ver**;
cgroups = cuánto puede **usar**. Aquí se definen `PID` y `/proc`.

**Ocho tipos de namespace, diez enlaces.** La tabla lista los seis que importan
(PID, NET, MNT, USER, UTS, IPC) y el cuerpo dice la verdad completa: existen
también `cgroup` —que Docker activa por defecto en cgroups v2 desde 20.10— y
`time`; y `ls /proc/<pid>/ns/` imprime **diez** entradas, porque `pid` y `time`
aparecen además en su variante `_for_children`, que es el namespace que heredarán
los hijos. Sin esto, un alumno cuenta líneas, obtiene diez, y la página le dijo
ocho.

La fila USER dice la verdad: **Docker no activa user namespaces por defecto**, así
que root adentro es root en el host salvo que configures `userns-remap`; Podman
rootless sí lo hace siempre. Y ahí se nombra **Kata** por primera vez: si el
kernel es compartido, ¿qué haces cuando no quieres compartirlo? Se paga en 3/5.

- Figura `cont-ns-cgroups`.
- `::: problem` — con la salida impresa de `ls -la /proc/1/ns/` del host y del
  contenedor, decir cuántos de los diez difieren y cuál no. La respuesta:
  **difieren nueve; el único que coincide es `user`**, y ésa es toda la
  explicación de por qué el archivo del laboratorio de la clase 2 sale de `root`.
- Nota de laboratorio: la salida se captura con `docker exec <nombre> ls -la
  /proc/1/ns/` —leerla desde el host requiere root— y **en la versión exacta de
  Docker que se use en clase**, porque el comportamiento de `time` cambia entre
  runtimes.

### 3 · Receta, congelado, servido — `receta-imagen-contenedor` · 10 min · clase

Meta: separar las tres cosas que todo el mundo confunde.

Dockerfile es la receta, imagen es el platillo congelado, contenedor es el
platillo servido. De una imagen salen muchos contenedores; los contenedores son
efímeros; las imágenes son inmutables. La tabla de los ocho comandos del
Dockerfile **se va a la chuleta**: aquí vive la analogía, no la referencia. Y
`CMD` contra `ENTRYPOINT` tampoco va aquí — vive en 2/5, donde se puede correr.

- Figura `cont-tres-abstracciones`.
- `::: problem` — se reparte impreso un Dockerfile de cinco líneas y **se recorta
  con tijeras en dos montones**, `build` y `run`. El mismo ejercicio, con las
  manos, que es lo único que se puede hacer sin computadora.

### 4 · Qué pasa cuando escribes `docker run` — `anatomia-de-docker-run` · 12 min · clase

Meta: que `docker run` deje de ser magia. Aquí se definen `daemon` y `socket`.

La cadena, con el reparto **medido**:

```
docker CLI  →  dockerd  →  containerd  →  containerd-shim-runc-v2  →  runc
```

Quién hace qué, corregido respecto de la v2:

- **El rootfs ya está desplegado en disco desde el `pull`.** Quien lo monta es
  **`dockerd` mismo** con el graphdriver `overlay2` —que es lo que tendrán
  instalado— o **el shim** cuando se usa el image store de containerd. **Nunca
  `runc`**, que lo recibe montado y sólo lo bind-montea sobre sí mismo para poder
  pivotar.
- **El cgroup lo crea systemd**, no `runc`: el cgroup driver por defecto en
  cgroups v2 es `systemd`, y `runc` le pide una unidad scope transitoria por
  D-Bus. Se ve con `systemctl list-units --type=scope`, donde la descripción dice
  literalmente `libcontainer container <id>`. `runc` sí escribe los knobs que
  systemd no expone.
- **El orden es proceso → cgroup → namespaces.** `runc` hace `fork`/`exec` de
  `runc init`, después mete ese PID al cgroup —el comentario del código dice
  *"antes de sincronizar con el hijo, para que ningún hijo escape del cgroup"*— y
  sólo entonces `nsexec.c` hace el `clone`/`unshare` que crea los namespaces.
- **`runc` corre dos veces y sale las dos.** En estado estable no queda ningún
  `runc` en el árbol.
- **El shim se desacopla con un doble fork** y queda reparentado a systemd,
  aunque se mantiene en el cgroup de `containerd.service`.

De ahí salen tres cosas: la cadena de Podman (`podman → conmon → crun/runc`),
que se salta **el daemon** y no el runtime; qué pasa de verdad cuando matas cada
pieza; y dónde entra Kata. El cierre, matizado: no queda nada de Docker en el
**camino de ejecución** —cada syscall va directo al kernel— pero sí queda un
supervisor sosteniendo la salida estándar y el código de salida. Se prueba
imprimiendo el árbol de procesos, donde ni `dockerd` ni `containerd` aparecen.

- Figura `cont-anatomia-run`.
- `::: problem` — **se hace de pie**, y es lo único de la sesión que la gente va a
  recordar el martes. Cinco alumnos son `docker CLI`, `dockerd`, `containerd`,
  el shim y `runc`, cada uno con su hoja. Se pasa un papelito ("corre `ubuntu`")
  por la cadena; `runc` se lo entrega al sexto, que es el proceso, **y se
  sienta** — que es la corrección #14 hecha con el cuerpo. Después se sienta
  `dockerd`: el proceso sigue de pie, sostenido por el shim. Después se sienta
  `containerd`: sigue de pie. Y al final se sienta el shim: **ahí sí se cae el
  proceso**, porque containerd corre `cleanupAfterDeadShim`, que termina en un
  `runc delete --force`.
  El `answer` completa la cuarta línea, la del daemon que vuelve: con el default
  `live-restore: false`, cuando `dockerd` reinicia **mata** lo que quedaba vivo.
  Y la tabla de `systemctl stop` contra `systemctl restart` en las dos
  configuraciones.
- Dos avisos para la demo en vivo: `systemctl stop docker` **no apaga Docker**,
  porque `docker.socket` sigue escuchando y el siguiente `docker ps` lo
  reactiva; hace falta `systemctl stop docker.socket docker.service`. Y parar
  `docker.service` **no para `containerd`**: la relación es `Wants=`.

### 5 · De uno a mil: escalamiento y orquestación — `escalamiento-y-orquestacion` · 10 min · lectura

Meta: entender por qué el mundo se movió, más allá de la reproducibilidad. Aquí
se definen `estado` y `réplica`.

| Idea | Qué se dice |
|---|---|
| **Estado** | lo que el proceso escribió y espera volver a leer: una base, un archivo subido, la sesión de un usuario |
| La unidad desechable | un contenedor es idéntico a sus hermanos y se puede matar sin pensarlo |
| Escalar es horizontal | se corren N copias —**réplicas**, en la jerga— de la misma imagen |
| El precio | si hay N copias idénticas, ninguna puede guardar estado adentro. **Tiene que vivir fuera**: eso es la clase 2 |
| Quién decide | el orquestador. Kubernetes es el nombre, y **queda como deuda que no se paga**, a propósito |
| Por qué se puede | veinte contenedores de **Podman** arrancan en 2.7 s; los mismos veinte en **Docker**, 5.5 s. Con VMs serían minutos |

Los `pods` no se mencionan aquí: llegan en 3/1. La cifra de arranque lleva su
línea de enlace a `[[lo-que-cuesta]]`, no el pie completo.

- Figura `cont-escalamiento`.
- `::: problem` — un servicio guarda las sesiones de sus usuarios en un archivo
  dentro del contenedor. Qué se rompe al correr tres copias, y dónde debería
  vivir ese archivo.

### 6 · VM contra contenedor — `vm-contra-contenedor` · 10 min · lectura

Meta: dónde ocurre el aislamiento, y cuándo el contenedor no es la respuesta.

Una sola tabla comparativa y tres casos de "no uses contenedor": hardware
directo, aislamiento máximo, kernel distinto. El segundo queda como deuda que
paga Kata. Aquí vive también la explicación de por qué **en macOS y en Windows
siempre hay una VM de por medio**, que es el hecho del que cuelgan tres páginas
de la sección 2.

- Figura `cont-vm-vs-contenedor`. `cont-espectro` aparece **como imagen suelta**
  sin directiva, y es donde se nombra **gVisor** por primera vez.
- `::: problem` — dado un `docker run` escrito, decir qué cambiaría si eso fuera
  una VM: arranque, tamaño, kernel, qué ve del host.

### 7 · Docker y Podman — `docker-y-podman` · 14 min · lectura

Meta: entender que la diferencia es arquitectónica, y **qué compra exactamente**.

Los cuatro problemas del daemon. El modelo fork-exec. Rootless y lo que sí
necesita: rango en `/etc/subuid` y `/etc/subgid` y los binarios
`newuidmap`/`newgidmap` del paquete `uidmap`, que en Debian y Ubuntu es
**Recommends** y falta en instalaciones mínimas. El **procedimiento** de eso vive
en 2/1; aquí vive el porqué, y 2/1 enlaza esta página. El alias.

Sólo tres filas de comparación; la tabla de diez se va a la chuleta.

**Y la corrección que la v2 tenía al revés:** el 2× de arranque **no lo compra la
ausencia de daemon**. Fijando todo menos el runtime, `podman --runtime crun` da
193 ms, `podman --runtime runc` 363 ms y `docker` 330 ms — con el runtime
igualado, Podman rootless es ~10 % **más lento**. Lo que la ausencia de daemon
compra es otra cosa, y hay que decirlo así: rootless, integración con systemd, y
ningún proceso privilegiado siempre encendido.

- Figuras `cont-docker-vs-podman` y `cont-bench-escala` (suelta).
- `::: problem` — **el ejercicio de benchmarking de la unidad, replanteado.** El
  script mide el RSS de `dockerd` pero **no el de los shims**, y **suma** el RSS
  de los `conmon` en vez de prorratear páginas compartidas. Corrige las dos cosas
  con los datos que se dan y vuelve a contestar quién usa menos memoria. El
  `answer`: el shim cuesta ~11 MB por contenedor y `conmon` ~2 MB, así que
  **Podman gana en todo N y el "cruce" no existe**; y sumar RSS infla a Podman
  unas seis veces, porque 12 `conmon` son 25 MB de RSS y 4 MB de PSS. Eso enseña
  benchmarking de verdad, y además cierra con la corrección #14 en vez de
  contradecirla.

### 8 · Capas y caché — `capas-y-cache` · 15 min · lectura

Meta: entender por qué un `build` a veces tarda tres segundos y a veces tres
minutos. Lectura, porque el capítulo 3 de DataCamp la drillea.

Cada instrucción es una capa con hash SHA-256 de su contenido. La tabla
git↔Docker, con la fila corregida: los dos guardan **snapshots direccionados por
contenido**, no diffs; enlace a `[[que-guarda-un-commit]]`. El caché es
secuencial y cae como dominó. `requirements.txt` primero, código después.

Node y Rust se cortan: no se han visto ni se van a ver en este curso.

- Figura `cont-capas-cache`.
- `::: problem` — Dockerfile mal ordenado: marcar qué capas se invalidan al tocar
  una línea de código y reescribirlo.

### 9 · Lo que cuesta — `lo-que-cuesta` · 15 min · lectura

Meta: tener números propios, **y saber leerlos**. Aquí vive el pie de versiones
completo de toda la unidad, y aquí se define `syscall`.

**LAUNCH** se paga una vez al crear el contenedor; **RUNNING**, mientras corre.
Confundirlos hace creer que "los contenedores son 20 % más lentos".

**Arranque** (exp 1): ~428 ms Docker, ~213 ms Podman, y el baseline de 1.8 ms con
lo que de verdad mide — el intervalo va de un `date` al siguiente, así que es el
**`fork`+`execve` de `/usr/bin/date`**: el costo de arrancar un programa, el
programa equivocado. Es mediana; la media es 3.1 ms por el ramp-up de frecuencia.
Alpine casi no cambia nada, y la explicación es buena: el arranque no descomprime
la imagen, ya está desplegada desde el `pull`.

**Ejecución** (exp 3). Los dos resultados se publican **diciendo qué miden**:

- El `hash` sale a favor del contenedor y **no por ser contenedor**: el host corre
  GNU coreutils 8.32 y la imagen `ubuntu:24.04` corre 9.4, y sobre los mismos
  100 MiB el `sha256sum` de 9.4 tarda 0.19 s contra 0.65 s. El experimento midió
  dos versiones de coreutils. No es SHA-NI —esta CPU no lo tiene— y no es
  `/dev/urandom`, que va igual de rápido en los dos lados.
- El `sort` sale +7.6 %, y **la mayor parte es el `docker exec`**: 71–82 ms sobre
  un workload de ~1.4 s. Restándolo quedan ~+4.7 %. La conclusión correcta es más
  fuerte que la publicada: **ejecutar dentro de un contenedor no cuesta**, que es
  exactamente la tesis de la unidad.

Tres conclusiones, no cinco. El VFS va en un recuadro `> [!NOTE]` breve, no en un
`::: note`, que está prohibido. Y la nota que justifica la clase 2, ahora
cualitativa: el overlay paga **copy-up** la primera vez que escribes sobre un
archivo de una capa inferior. El 20 % se cae porque su CSV reporta a Podman 3.7×
más rápido que bare metal: midió page cache.

Cierra invitando a repetirlo, que es el punto de publicar los scripts — con la
advertencia de que `bench_runtime.sh` **pinea `ubuntu:24.04`**, porque
`ubuntu:latest` hoy es 26.04 con coreutils en Rust y con eso el resultado del
hash **invierte el signo**.

- Figuras `cont-bench-arranque` (numerada) y `cont-bench-overhead` (suelta).
- `::: problem` — con esos números, cuánto cuesta un pipeline de 500 contenedores
  de 2 s contra uno de un contenedor de 1000 s.

### Deudas de la sección 1

| Deuda | Se abre en | Se paga en | Estado |
|---|---|---|---|
| Kata | 1/2 | 3/5 | paga |
| Orquestación | 1/1 | 1/5 | paga |
| gVisor | 1/6 (figura) | 3/5 | paga |
| Aislamiento máximo | 1/6 | 3/5 | paga |
| Estado persistente | 1/1 | 2/12 | paga |
| Bind mounts distintos en macOS/Windows | 1/6 | 2/8 y 2/9 | paga |
| `overlay` | 1/4, nombrado como deuda | 2/7 | paga |
| Escribir en el socket de Docker es mandar sobre un proceso root | 1/4 | 3/4 | paga |
| Que Docker no active user namespaces | 1/2 | 2/9 y 3/4 | paga |
| `CMD` contra `ENTRYPOINT` | 1/3, deuda explícita | 2/5 | paga |
| El arranque no descomprime la imagen | 1/4 | 1/9 | paga |
| `pods` | 1/7, deuda explícita | 3/1 | paga |
| **Kubernetes como herramienta** | 1/5 | — | **no se paga, a propósito** |

---

# Sección 2 — Manos a la obra · `session-11` · martes 2026-09-22 · 90 min

Todo ocurre en `~/fdd/docker-lab`, carpeta local y desechable, **no** un
repositorio — y el índice de la sección lo distingue explícitamente de
`estudiantes/<login>/08_contenedores/`, que sí es el repositorio.

**Cuatro páginas en clase y nueve de lectura.** Es la cadena mínima que sostiene
el modelo mental —el contenedor vive lo que su proceso → dónde vive cada byte →
el bind mount en las dos direcciones → las ocho predicciones— y es lo que cabe
en 90 minutos cuando se cuenta el tecleo. Las tres primeras son **lectura previa**
porque sus entregas vencen ese mismo día, y el índice las pone primero.

### 1 · Instalar Docker y Podman — `instalar-docker-y-podman` · 25 min · previa

Meta: dejar los dos runtimes corriendo sin `sudo`. Exenta a 260 líneas.

Docs oficiales por distribución. Post-install, `usermod -aG docker $USER`,
`newgrp docker`. Podman rootless con subuid y `uidmap`, enlazando
`[[docker-y-podman]]` para el porqué. En **macOS**, `podman machine init` y
`podman machine start` antes de cualquier `podman run`.

**Arquitectura de CPU**: `exec format error`, `the requested image's platform does
not match`, y `--platform linux/amd64` como parche. Es la pared del día de
instalación para quien trae Mac con Apple Silicon, y multi-platform está en un
capítulo de DataCamp que vence una semana después.

**La regla que decide dónde trabajar**: el laboratorio se hace en **Linux nativo
o en la ruta ext4 de WSL2** (`/home/<usuario>/fdd/docker-lab`), **nunca** en
`/mnt/c/...`. Ahí y sólo ahí los permisos se comportan como la unidad los
explica, y de paso es la razón concreta para preferir WSL2 nativo.

Y lo que se cobra en la clase 3: **estar en el grupo `docker` es ser root**,
porque puedes pedirle al daemon que monte el disco entero. Con su corolario:
**nunca** `chmod 666 /var/run/docker.sock`.

**Cierra con el prepull, y salva la clase del 22:** treinta alumnos detrás del
NAT del ITAM son **una sola IP**, y la sesión baja seis imágenes. El límite de
pulls anónimos muere en el minuto diez. Como ya hicieron `docker login` en 2/3,
los pulls autenticados cuentan contra la cuenta y no contra la IP — así que la
página pide, antes del martes: `docker login` y `docker pull` de `ubuntu:24.04`,
`alpine`, `hello-world`, `python:3.12-slim`, `postgres:16` y `postgres:17`, con
su `docker images` de comprobación. Y 2/3 termina recordando volver a
`docker login` después de su comprobación.

- Figura `cont-sin-sudo`.
- `::: problem` — el bloque de comprobación que sirve en las tres plataformas.

### 2 · Planes B — `planes-b-de-instalacion` · 12 min · previa

Meta: que nadie se quede sin poder hacer la tarea mientras resuelve la
instalación. Existe porque la unidad 4 tiene su página equivalente y porque
entre la clase 1 y la 2 hay cinco días sin ningún contacto humano.

Las trampas con su síntoma: `snap install docker` en Ubuntu, que está confinado y
rompe los bind mounts fuera de `$HOME` —o sea media clase—; WSL1 en vez de WSL2;
la integración por distro apagada en Docker Desktop; la virtualización
desactivada en el firmware; y **Secure Boot no tiene nada que ver con Docker**,
dicho explícitamente para que nadie pierda la tarde desactivándolo como le enseñó
la unidad 4. Más `df -h /`: las imágenes de la unidad pesan varios gigabytes y
quien instaló en dual boot puede tener una partición chica.

Y la fecha de reporte anticipada: **si el sábado 19 no te funciona, dilo el
sábado 19.**

- Figura `cont-planes-b`.
- `::: problem` — diagnosticar tres síntomas reales y decir cuál es la causa.

### 3 · A Docker Hub — `a-docker-hub` · 12 min · previa

Meta: publicar un artefacto propio y comprobar que existe para los demás.

`registro/usuario/nombre:tag`, y que `ubuntu` es `docker.io/library/ubuntu:latest`
— con la aclaración de que `library` **no es un usuario** sino el namespace
reservado de las imágenes oficiales, donde no puedes hacer push. **Los nombres van
en minúsculas siempre**, que es lo que tumba al alumno cuyo login de GitHub tiene
mayúsculas. `login`, `tag`, `push`. El digest y para qué sirve.

La comprobación que hace verificable la entrega: `docker logout`, `rmi -f`, `run`
— y que la salida traiga `Unable to find image locally` y el `Pulling from`.
Después, volver a `docker login` para el prepull de la página 1.

- Figura `cont-registro`.
- `::: problem` — qué se descarga exactamente con `docker run ubuntu` y de dónde;
  y por qué `hub.docker.com/repository/docker/…` da 404 a todo el mundo menos a ti.

### 4 · El ciclo de vida de un contenedor — `ciclo-de-vida-de-un-contenedor` · 12 min · clase

Meta, y **única idea de la página**: *un contenedor vive exactamente lo que vive
su proceso principal.* Es la pregunta número uno del principiante.

Sin esa regla, `docker run ubuntu` que termina de inmediato y `docker run -d
nginx` que se queda corriendo son dos magias distintas. Con ella el ciclo se
deduce: salir del `bash` mata el PID 1 y por eso el contenedor se detiene; `ps`
contra `ps -a`; `start`; **`exec -it` entra a uno vivo** y por eso no funciona con
uno detenido; `logs` es lo que escribió ese proceso; `rm` borra su capa de
escritura.

La tabla de los doce comandos se va a la chuleta. Un tramo `**Haz:**` provoca a
propósito un `exited (127)` y lo lee con `logs` y `ps -a`, que es la segunda
pregunta del principiante: *se murió con error, ¿cómo averiguo por qué?*

- Figura `cont-ciclo-de-vida`.
- `::: problem` — recorrer el ciclo **prediciendo qué muestra `ps -a`** en cada
  paso antes de correrlo, y explicar por qué `exec` falla en uno detenido.

### 5 · El Dockerfile por dentro — `el-dockerfile-por-dentro` · 15 min · lectura

Meta: construir una imagen y ver de qué está hecha. Lectura, porque los capítulos
2 y 3 de DataCamp la teclean.

`build -t`, el **contexto** y por qué el `.` importa, `.dockerignore`, `-f`,
`--no-cache`. Las capas reales con `docker history` y el peso con `docker images`:
ubuntu contra alpine. `CMD` contra `ENTRYPOINT` con `hola.sh` y sus tres
ejecuciones — aquí y sólo aquí.

- Figura `cont-build-contexto`.
- `::: problem` — **antes** de correr `hola.sh` de las tres formas, escribir qué
  imprime cada una; después verificar.

### 6 · Arreglar un Dockerfile — `arreglar-un-dockerfile` · 12 min · lectura

Meta: reconocer en un archivo real los tres defectos que DataCamp acaba de
enseñar. Es la entrega 2.

`roto/` lleva **tres archivos** —`Dockerfile`, `requirements.txt` y `app.py`—
porque sin el `requirements.txt` el defecto del orden no tiene nada que mover:

```dockerfile
FROM python:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Los tres arreglos son mecánicos y verificables: pinear a `python:3.12-slim`,
partir el `COPY`, y agregar `RUN useradd` + `USER`. Cada uno con su consecuencia
medible: el primero se ve en el tiempo del segundo build, el segundo en el dueño
de los archivos que escribe, el tercero en que la imagen de hoy no es la de
mañana.

Se arregla **tu copia**, en `estudiantes/$GHUSER/08_contenedores/roto/Dockerfile`.
El original se queda roto a propósito y tocarlo hace que la revisión rechace la
entrega.

- Figura `cont-dockerfile-roto`.
- `::: problem` — los tres defectos, su consecuencia y su arreglo. El `answer` es
  la rúbrica.

### 7 · Dónde vive cada byte — `donde-vive-cada-byte` · 10 min · clase

Meta: la tabla que ordena toda la clase. Paga la deuda de `overlay`.

| Capa | Quién la escribe | Cuándo muere |
|---|---|---|
| Capas de la imagen | `docker build` | `docker rmi` |
| Capa de escritura | el proceso de adentro | `docker rm` |
| Bind mount | los dos lados | nunca — es tu disco |
| Named volume | el contenedor | `docker volume rm` |

Con esas cuatro filas, el overlay y el volumen dejan de ser metáforas: predicen
el resultado de cualquier experimento de la sección.

- Figura `cont-overlay-volumen`.
- `::: problem` — **una sola** fila: dado un archivo concreto, decir en cuál cae y
  por qué. La predicción múltiple vive entera en 2/10.

### 8 · Rutas — `rutas-en-docker` · 10 min · lectura

Meta: que montar deje de fallar por la ruta.

Relativa contra absoluta. **Las relativas funcionan desde Docker CLI 23** y
también en Podman, así que se dice eso y no lo contrario; `"$(pwd)"` sigue siendo
lo portable. Pero **la trampa real no es la versión, es el `./`**: `-v dir:/app`
sin él **no es una ruta relativa, es un named volume** que Docker crea vacío en
silencio, sin error, y el alumno pierde media hora buscando su código.

Y aquí se paga la deuda de 1/6: **en macOS y en Windows el bind mount cruza la
frontera de una VM**, y por eso ahí es más lento y los permisos se comportan
distinto.

- Figura `cont-rutas`.
- `::: problem` — montar mal a propósito, cuatro casos, predecir y verificar. Uno
  de los cuatro es el `./` olvidado.

### 9 · El archivo compartido — `el-archivo-compartido` · 15 min · clase

Meta: ver el bind mount en las dos direcciones, **y que el resultado dependa de
tu plataforma sea parte de la lección**.

El laboratorio 1: sin volumen el contenedor no ve nada; con volumen ve todo; el
contenedor escribe y **el archivo aparece en tu host**; editas fuera y el
contenedor ve lo nuevo **sin rebuild**; borras desde dentro y desaparece afuera.
`:ro`.

Y de quién queda el archivo. Aquí la v2 prometía un resultado que **falla para la
mitad del grupo**, así que la página lleva la tabla:

| Plataforma | De quién queda el archivo |
|---|---|
| Linux nativo, Docker | **`root`** — porque Docker no activa user namespaces |
| Linux, Podman rootless | **tu usuario** — el UID 0 se mapea al tuyo |
| WSL2, ruta ext4 (`/home/...`) | **`root`**, igual que Linux |
| macOS con Docker Desktop, o Windows con ruta `C:\...` | **tu usuario**: el filesystem compartido inventa la propiedad |

Con la explicación que convierte el problema en contenido: *en macOS y en Windows
hay una VM y un sistema de archivos compartido de por medio, y ese sistema
inventa la propiedad para que nada falle. No es que ahí sí haya user namespaces —
es que ahí el bind mount no es tu disco, es un puente.*

Las salidas: `--user "$(id -u):$(id -g)"` en Docker, con su asterisco —rompe
imágenes que escriben en rutas del usuario de la imagen y deja al proceso sin
entrada en `/etc/passwd`—; y en Podman, **`--userns=keep-id`** o el sufijo `:U`
del volumen, que son la primera respuesta para montar tu propio árbol.
**`podman unshare` es la herramienta de diagnóstico, no la solución, y no existe
en macOS**, donde el cliente es remoto.

- Figura `cont-uid-plataformas`.
- `::: problem` — **predecir el dueño del archivo en tu plataforma** y después
  verificarlo. El `answer` trae las cuatro respuestas. Después, en Linux o WSL2
  ext4: intentar **modificarlo** como tu usuario y explicar por qué no puedes;
  borrarlo y explicar por qué **sí** puedes, que depende del permiso sobre el
  directorio.

### 10 · Los ocho casos — `los-ocho-casos` · 15 min · clase

Meta: cerrar el modelo con predicción antes de ejecución.

Código dentro de la imagen o montado por volumen × editas en el host o dentro ×
con rebuild o sin rebuild. Se llenan las ocho predicciones en `predicciones.md`
—que viaja en el espejo con la tabla ya armada y dos columnas vacías— y después
se verifican. Cierra con el bucle de trabajo diario en tres líneas de comandos:
editar → reconstruir → correr, y cuándo el volumen te lo ahorra.

- Figura `cont-matriz-volumen`.
- `::: problem` — la matriz. Si acertaste las ocho, entendiste volúmenes.

### 11 · Las cuatro trampas — `las-cuatro-trampas` · 15 min · lectura

Meta: los filos que cortan la primera vez. La trampa 1 lleva la redacción exacta,
porque es la corrección técnica más difícil de la unidad:

> Un **bind mount** siempre tapa: monta un directorio vacío sobre `/bin` y ya no
> existe `ls`. No copia nada, nunca, en ningún runtime.
>
> Un **named volume vacío hace lo contrario**: la primera vez que se monta,
> **copia** al volumen lo que la imagen tenía en ese path. Si ya tiene algo, tapa.
> La opción que lo apaga se escribe **`:nocopy`** con `-v` y `volume-nocopy` con
> `--mount`. **Podman hace exactamente lo mismo.**
>
> Esto es lo contrario de lo que dice medio internet, y explica por qué el
> laboratorio de Postgres funciona sin que lo pienses: el volumen vacío se lleva
> el `/var/lib/postgresql/data` que la imagen ya traía inicializado.

Las otras tres: permisos por UID numérico; es bidireccional y un `rm -rf` desde
dentro borra tu disco, para eso está `:ro` —que no es recursivo sobre
submontajes—; y volumen sobre volumen anidado, gana el más interno.

Cierra con que el bind mount de código es herramienta **de desarrollo**: en
producción el código va dentro de la imagen, porque el servidor no lo tiene en
disco. Deuda que recoge 3/2.

- Figura `cont-tapar`.
- `::: problem` — la diferencia bind mount contra named volume sobre un path con
  contenido, con los dos comandos y el `wc -l`.

### 12 · Named volumes y Postgres — `named-volumes-y-postgres` · 15 min · lectura

Meta: ver el estado sobrevivir a su contenedor. Lectura con guion paso a paso: es
el laboratorio más largo y el que más depende de que la instalación haya salido
bien, o sea el peor candidato para hacer en vivo.

Named volume contra bind mount y la regla: **bind mount para tu código, named
volume para datos de servicios**. `volume create`, `ls`, `inspect`, `rm`; el CLI
completo va a la chuleta. El laboratorio 2: Postgres con volumen, `CREATE TABLE`
e `INSERT` con `psql` —que se define, porque el curso nunca lo ha usado—,
destruir el contenedor, **resucitar los datos en uno nuevo**, y matar el volumen
para verlos morir. Por qué una base quiere named volume: permisos de uid 999 y
portabilidad.

Y una frase que evita una pared: **aquí no publicamos puerto**, entramos por
`exec`. Por qué eso es una decisión y no un atajo, en `[[la-red-y-el-nombre]]`.

- Figura `cont-estado-postgres`.
- `::: problem` — levantar `postgres:17` sobre el volumen de `postgres:16`:
  predecir si funciona y explicar por qué no. El `answer` trae el mensaje literal
  del fallo.

### 13 · Limpieza — `limpieza-de-docker` · 12 min · lectura

Meta: recuperar el disco y entender qué se borra.

Capas huérfanas, contenedores detenidos, volúmenes sin dueño. `container prune`,
`image prune`, `system prune`, `system df`, `volume ls` y `volume rm`, con la
advertencia de qué se lleva cada uno.

- Figura `cont-prune`.
- `::: problem` — crear cinco imágenes `lab-1`…`lab-5` y borrarlas con un solo
  pipeline: `docker images --format …` filtrado con `grep -E` y pasado a
  `xargs -r docker rmi`. Es la unidad 6 aplicada a algo que duele. Enlaza a
  `[[grep-awk-en-serio]]`.

### Deudas de la sección 2

| Deuda | Se abre en | Se paga en | Estado |
|---|---|---|---|
| Estar en el grupo `docker` es ser root | 2/1 | 3/4 | paga |
| Los UID altos de Podman rootless | 2/9 | 2/12 | paga |
| Por qué el Postgres "funciona sin pensarlo" | 2/11 | 2/12 | paga |
| El código va dentro de la imagen en producción | 2/11 | 3/2 | paga |
| No publicamos puerto todavía | 2/12 | 3/1 | paga |
| `docker cp` para sacar un archivo | 2/4, una fila de la chuleta | DataCamp *Intermediate* cap. 1 | **se delega, declarado** |

---

# Sección 3 — Diseño y seguridad · `session-12` · jueves 2026-09-24 · 90 min

Llegan con volúmenes y redes en los dedos por los capítulos 1 y 2 de
*Intermediate Docker*. La clase casi no gasta comandos: gasta decisiones. No se
usan APIs ni Python.

### 1 · La red y el nombre — `la-red-y-el-nombre` · 12 min

Meta: que dos contenedores se hablen, y entender quién los oye. Aquí se define
`puerto`.

Una red propia; se alcanzan **por nombre**, porque la IP cambia en cada arranque
—y en la red bridge por omisión **no hay resolución por nombre**, tiene que ser
una red definida por ti. `-p` contra red interna, y que publicar un puerto es una
decisión de diseño: todo lo que publicas es superficie expuesta. Los pods de
Podman como el caso extremo, comparten `localhost`.

- Figura `cont-red-y-pod`.
- `::: problem` — **predecir** si el `ping` al nombre funciona, si el `psql`
  funciona y si desde el host funciona; después correrlo. Crear la red, meter
  Postgres **sin `-p`**, y explicar el tercer resultado.

### 2 · El contrato de un servicio — `el-contrato-de-un-servicio` · 15 min

Meta: saber qué es un microservicio sin decirlo como si fuera magia.

Un contenedor, un proceso, una responsabilidad. **El contrato son tres cosas: qué
puerto escucha, qué variables de entorno espera, qué volumen necesita.** Si está
escrito, el servicio se reemplaza sin tocar a nadie; si no, tienes un monolito
repartido. Con estado y sin estado. Y **cuándo no partir**: partir cuesta red,
despliegue y depuración.

- Figura `cont-contrato`.
- `::: problem` — un contenedor que corre un cron, una API y una base a la vez.
  Qué se rompe al escalarlo y cómo se parte. El `answer` trae la partición
  canónica y las tres preguntas del contrato para cada pieza.

### 3 · Diseñar un sistema — `disenar-un-sistema` · 15 min

Meta: dibujar un sistema completo antes de escribirlo.

El pipeline de la unidad 2 como servicios: extracción, transformación, carga, la
base con su volumen, el tablero que lee. Enlace a `[[pipeline-de-datos]]`. Por
qué la base casi nunca se parte. Compose como el plano escrito — que es lo que
van a teclear **la semana que viene**, en el capítulo 4; aquí se lee para saber
qué estarán tecleando. Los doce factores se cortan: es doctrina sin falla
concreta que la motive, justo el registro que la unidad evita.

- Figura `cont-pipeline-servicios`.
- `::: problem` — diseñar un scraper diario que deja datos en Postgres más un
  tablero que los lee. El `answer` es un diseño de referencia con **cuatro
  comprobaciones cerradas**: ¿la base publica puerto al host? ¿el scraper tiene
  volumen? ¿la configuración va por variable de entorno? ¿qué sobrevive a un
  `docker rm` de cada servicio?

### 4 · Cuando se rompe el aislamiento — `cuando-se-rompe-el-aislamiento` · 15 min

Meta: entender que la mayoría de los escapes no son bugs, son decisiones. Exenta
a 260 líneas.

| Qué pasó | Por qué se pudo | Cómo se cierra |
|---|---|---|
| `runc` CVE-2019-5736 | el binario del runtime era alcanzable desde dentro vía `/proc/self/exe` | runc **sella** su propio binario — hoy con un overlayfs de sólo lectura, con `memfd` de respaldo |
| Leaky Vessels CVE-2024-21626 | `process.cwd` a `/proc/self/fd/N` vía `WORKDIR`; afecta runc **1.0.0-rc93 – 1.1.11**, en `build` y en `run` | **runc ≥ 1.1.12** y BuildKit ≥ 0.12.5. `USER` no lo mitiga, pero **estorba la sobrescritura**: defensa en profundidad |
| `--privileged` + cgroups v1 | mala configuración de siempre: `release_agent` escribible. Es de 2019 y es comportamiento **intencional** | nunca `--privileged`; y **sin jerarquías v1 montadas**, porque v2 no tiene `release_agent` |
| CVE-2022-0492 | el kernel omitió comprobar `CAP_SYS_ADMIN` **en el user namespace inicial**, así que bastaba un `unshare -UrC`. **Sin privilegios** | **ya estaba cerrado si no tocaste nada**: el seccomp por defecto bloquea `unshare` sin `CAP_SYS_ADMIN` y AppArmor bloquea montar cgroupfs. Se abre con `--privileged`, con `seccomp=unconfined`, o en Kubernetes, donde los pods vienen sin seccomp |
| Dirty Pipe CVE-2022-0847 | usa `splice()` y `write()`, que **todo** contenedor necesita: seccomp, AppArmor, capabilities y no-root **no lo paran**. Introducido en 5.8, corregido en 5.16.11 / 5.15.25 / 5.10.102 | kernel al día, y si no alcanza, **Kata**. La sobrescritura vive en el **page cache**: el binario en disco queda intacto, así que "se ve bien" no prueba nada — y por eso derrota el sellado del primer renglón |
| Socket de Docker montado | no es exploit: es entregar el host | no montarlo |
| Imagen envenenada | nombre parecido, minero adentro | pinear por digest, escanear, bases conocidas |

Más la tabla de defensas: rootless, `--cap-drop ALL`, seccomp y AppArmor,
`--read-only`, `USER` no-root, pineo por digest. Aquí se cobra la frase de la
instalación. Y se enlaza `[[contenedores-anidados]]`, encuadrado: esto es lo que
esta página te prohibió, y ahí está por qué en CI se hace igual y con qué precio.

La fila de CVE-2022-0492 es la que mejor sostiene la tesis de la página: **el bug
existía y la configuración por defecto lo tapaba.**

Sin exploits funcionales ni pasos reproducibles.

- Figura `cont-superficie-ataque`.
- `::: problem` — un `docker run` real con cuatro banderas peligrosas: señalar
  cada una, decir qué habilita, **correr** la versión reescrita con `--cap-drop
  ALL` y ver qué falla y por qué.

### 5 · Kata y los dos ejes — `kata-y-el-espectro` · 12 min

Meta: cerrar la pregunta de 1/2, y corregir el error de categoría que la v2 tenía.

**No es un espectro, son dos ejes**, y meter "Podman rootless" en una sola línea
enseña dos cosas falsas de un golpe:

> **Eje A — dónde aterriza la syscall que no controlas:** proceso → contenedor
> (**rootful y rootless caen en el mismo punto**) → gVisor, que reimplementa la
> interfaz de syscalls de Linux en espacio de usuario → Kata, que pone un segundo
> kernel real → VM completa.
>
> **Eje B — qué privilegio tiene quien se escapa:** root en el host → un usuario
> sin privilegios con su rango de subuid.
>
> **Rootless mueve sólo el eje B.** No añade ninguna frontera: mismo kernel, misma
> superficie de syscalls. Y no cuesta densidad, así que tampoco encaja en el eje
> que dice "de más a menos densidad". Por eso gVisor tiene *su propio* modo
> rootless: se componen, no se ordenan.

Y el matiz que evita enseñar que rootless sale gratis: habilitar user namespaces
no privilegiados **abre** interfaces de kernel que normalmente están restringidas.
Ubuntu 24.04 los restringe por defecto, y Red Hat advierte que esa restricción
rompe justamente los contenedores rootless de Podman.

**Kata**: un kernel propio **por sandbox** —un pod, o un contenedor suelto si lo
corres sin Kubernetes—, compatible con OCI, así que cambia el runtime y no el
Dockerfile. Necesita **virtualización por hardware, en la práctica `/dev/kvm`**.
**Es Linux**: no hay binarios para macOS. La virtualización anidada en Apple
Silicon existe desde M3 con macOS 15, pero Docker Desktop no expone `/dev/kvm` a
su VM. Por eso no es el runtime del curso.

De gVisor se dice lo que se puede sostener: no implementa todas las syscalls, y
sus autores advierten explícitamente que usar hardware de virtualización no hace
a un sistema más seguro por sí mismo.

La demostración, desde mi máquina: `uname -r` en un contenedor normal devuelve el
kernel del host; en uno de Kata devuelve otro.

- Figura `cont-espectro`, numerada aquí.
- `::: problem` — cuatro escenarios → runtime: tu laptop, el CI del curso, un
  SaaS que corre código de clientes, el clúster del ITAM. Cierra el escenario que
  1/6 dejó abierto, y el `answer` lo dice con esas palabras.

---

# Anexos

**`A_chuleta.md`** — `chuleta-contenedores`, 8 min, tope **320**. Los ~28 comandos
normalizados, Docker y Podman lado a lado, por tarea: correr, construir,
inspeccionar, volúmenes, red, registro, limpieza. Absorbe las tablas que las
páginas le mandan: los ocho comandos del Dockerfile (1/3), los doce del ciclo de
vida (2/4), la comparación de diez filas (1/7) y el CLI de volúmenes (2/12). Más
la tabla de errores frecuentes, que incluye los de instalación (`exec format
error`, `repository name must be lowercase`, `toomanyrequests`, `permission
denied`, `cannot find UID in /etc/subuid`) **y los de ejecución** (`exited (127)`,
el `no such file or directory` del script guardado con CRLF, `port is already
allocated`), más una fila de `docker cp`. Fuera de la forma de página.

**`B_prompts.md`** — los ocho prompts para LLM, más los enlaces oficiales de
Docker, Podman y Kata.

**`C_anidar.md`** — el capítulo 6 completo: DinD, el socket montado que no anida
sino que hace hermanos, Podman anidado, la tabla comparativa, el benchmark del
exp 4 con su figura `cont-bench-anidado`, y el ejercicio de cuatro partes. Abre
reconociendo la contradicción con 3/4. **Sus comandos entran a la chuleta.**

**`D_entregas.md`** — **el tablero de las cinco entregas**, y la pieza que hace la
unidad usable con la atención dispersa. Existe porque `content.instructions` se
escapa a texto plano en un solo párrafo: el objeto lleva el contrato, esta página
lleva la versión que se lee. Cinco bloques idénticos:

```markdown
## 1 · DataCamp: Introduction to Docker

| | |
|---|---|
| **Vence** | martes 22 de septiembre |
| **Vale** | 10 puntos |
| **Branch** | `tarea-08-datacamp-intro` |
| **Carpeta** | `estudiantes/<tu-login>/docker/` |

**Entregas dos archivos**

- `certificaciones.md` con la sección 1 llena y la URL del certificado
- `introduccion-a-docker.png`: el curso al 100 %, con tu nombre visible

**El ritual**

    git switch main && git fetch upstream && git merge upstream/main
    git switch -c tarea-08-datacamp-intro
    cp -r codigo/docker/. estudiantes/$GHUSER/docker/

**Acabaste cuando** el pull request está abierto y su revisión en verde.
```

La tabla de cuatro filas siempre primero —fecha, puntos, **branch**, carpeta—,
después qué archivos, después el ritual con la branch ya escrita para copiar, y
una línea de criterio de término. Arriba, una tabla resumen de las cinco para ver
el mes de un golpe. Abajo, qué **no** comprueba la revisión automática. Cada
objeto oficial la enlaza como su primer recurso.

---

# Objetos oficiales

`course/8_contenedores/_official/`, colocados junto a la unidad, así que omiten
`scope.quantum`.

| Archivo | id | Tipo | Branch | Abre | Vence | Pts |
|---|---|---|---|---|---|---:|
| `tasks/1_instalar_docker.yaml` | `setup-docker` | task | — | 09-17 | 09-22 | — |
| `assignments/1_datacamp_intro_docker.yaml` | `datacamp-introduccion-docker` | assignment | `tarea-08-datacamp-intro` | 09-17 | 09-22 | 10 |
| `assignments/2_imagen_en_docker_hub.yaml` | `imagen-en-docker-hub` | assignment | `tarea-08-imagen` | 09-17 | 09-22 | 10 |
| `assignments/3_datacamp_intermedio_1_2.yaml` | `datacamp-docker-intermedio-1` | assignment | `tarea-08-datacamp-inter-1` | 09-22 | 09-24 | 10 |
| `assignments/4_datacamp_intermedio_3_4.yaml` | `datacamp-docker-intermedio-2` | assignment | `tarea-08-datacamp-inter-2` | 09-24 | 09-29 | 10 |

**40 puntos.** Las fechas son las que fijó el profesor y no se mueven. Cada
entrega vence **justo antes de la clase que la usa**, y la última es el boleto de
entrada a la primera sesión de la unidad siguiente.

### Dos reglas nuevas en la revisión automática

Hoy `revisa_entrega.py` sólo compara la branch contra `main`: **el nombre
`tarea-08-imagen` no lo comprueba nadie**, y dos entregas en un mismo pull request
salen en verde.

**Regla 5 — el nombre de la branch.** Debe casar `^tarea-\d{2}-[a-z0-9-]+$`. El
mensaje nombra la branch exacta que esa entrega esperaba.

**Regla 6 — una entrega, una carpeta.** Todos los archivos tocados bajo
`estudiantes/<login>/` viven en **una sola subcarpeta**; lo suelto en la raíz
siempre pasa. Cierra tres agujeros: dos entregas en un pull request, el conflicto
`add/add` sobre `docker/certificaciones.md` entre las entregas 1, 3 y 4, y el
alumno que llena el `certificaciones.md` de `github/`.

| Branch | Única carpeta que puede tocar |
|---|---|
| `tarea-08-datacamp-intro` | `estudiantes/<login>/docker/` |
| `tarea-08-imagen` | `estudiantes/<login>/08_contenedores/` |
| `tarea-08-datacamp-inter-1` | `estudiantes/<login>/docker/` |
| `tarea-08-datacamp-inter-2` | `estudiantes/<login>/docker/` |

Tres condiciones: **el mapa vive en el `env` del workflow**, como `MANTENEDORES`,
para que el script siga sin leer nada del árbol de trabajo —ésa es la propiedad
que hace seguro `pull_request_target`, y su prueba la asserta—; **no rompe nada
hacia atrás**, porque las entregas de la unidad 7 ya cumplirían las dos; y
`CLAUDE.md` obliga a mover con el script la página
`4_el_flujo_del_curso.md`, que pasa de cuatro reglas a seis.

### Tres hechos del esquema que cambian cómo se escriben

1. **`content.instructions` no es Markdown.** El builder hace `html.escape()` y lo
   mete en un solo `<p>`. Por eso los objetos de la unidad 7 deletrean todo. Los
   de la unidad 8 describen comandos, URLs y nombres de branch: hay que seguir esa
   convención, y mandar la versión legible a `[[entregas-contenedores]]`.
2. **`branch` como llave de `content` sería invisible.** El nombre va dentro de
   `instructions`.
3. **`content.points` se omite en la task**, no se pone en `0`.

Cada objeto lleva `content.resources[]` —con `D_entregas` primero—,
`content.status: published`, `content.tags[]` y **`content.available`**, que
genera una segunda ocurrencia en el calendario y deja escrito cuándo abre cada
tarea. Con tres vencimientos el mismo 22, eso es lo que evita que parezca que todo
apareció de golpe.

### Qué se entrega

**0 · `setup-docker`** — nada que subir. La comprobación **no puede ser
`id -nG | grep docker`**: en macOS, en Windows y en rootless no existe grupo
`docker` ni debe existir. La que vale en las tres pega la salida completa de
`whoami`, `id -u`, `type -a docker`, `docker context ls`, `docker version` y
`docker run --rm hello-world`. Eso delata las **ocho** formas de creer que corres
sin `sudo` sin correr sin `sudo`: el alias, la función de shell, ser root en WSL2,
el `sudo -i` olvidado, el `newgrp` que sólo valía en esa ventana, el `chmod 666`
del socket, el `DOCKER_HOST` remoto, y usar Podman diciendo que es Docker. Son
ocho y no nueve: la v3 decía nueve y enumeraba ocho, porque el `chmod 666` del
socket y "el socket suelto" son la misma trampa.

**1 · DataCamp Introduction to Docker** — `certificaciones.md` sección 1, la
captura, y la **URL del Statement of Accomplishment**, que se verifica en un clic.

**2 · Imagen en Docker Hub** — `info.sh` modificado, `roto/Dockerfile` arreglado,
`bitacora.md` y `mi-imagen.md`. Para que sea verificable y no texto pegado:
`info.sh` lleva **tres líneas de código que hagan algo** —una imprime el login de
GitHub, otra la fecha de construcción, la tercera es suya—; `mi-imagen.md` lleva
la **URL pública** `hub.docker.com/r/<usuario>/<imagen>` —no la de
administración, que da 404 a los demás—, los dos nombres de usuario, el
**digest**, el comando exacto que el profesor debe correr, la salida esperada y la
salida real del `logout` + `rmi -f` + `run` con sus líneas `Unable to find image
locally` y `Pulling from`. **Menos de 300 MB.** Si la laptop es Apple Silicon,
`docker buildx build --platform linux/amd64`. No se pega la salida de `docker
login` —hay quien acaba subiendo su token— y no se sube la imagen como archivo.

**3 y 4 · Intermediate Docker** — secciones 2 y 3. Para medio curso **no hay
certificado ni pantalla de 100 %**, así que la evidencia válida se define: la
página del curso con sus cuatro capítulos, los entregados completos y el nombre
del alumno visible.

### Frases que los objetos tienen que decir

- **Las dos entregas del 22 son dos branches y dos pull requests**, y las dos
  nacen de `main`, no una de la otra.
- **Qué significa el check verde.** Corrige una afirmación falsa de la v1: la
  revisión no comprueba que existan los archivos pedidos, ni el contenido, ni la
  regla del mirror. El verde significa "no rompiste las reglas del repositorio".
- **La carpeta es `08_contenedores`, con el cero**, aunque la unidad se vea como
  "8" en el sitio. En la unidad 7 los nombres eran bastante distintos; aquí sólo
  cambia un cero.
- **La carpeta de certificaciones es `docker/`, no `github/`.**
- **Se copia con la barra y el punto**, desde la terminal, nunca arrastrando.
- **`__pycache__/` va a aparecer** al correr los `app.py` en local, y la revisión
  lo rechaza con razón.
- **La contraseña de Postgres va en la línea de comandos, no en un `.env`.**
- **Los cursos son premium**: quien perdió el acceso lo dice **antes del viernes
  18**, porque sin él se van 30 de los 40 puntos.
- **Son dos cursos de Docker, no tres**; el segundo se entrega en dos partes.

---

# El espejo

```
codigo/08_contenedores/
  README.md                        qué es cada carpeta y la regla del mirror
  bitacora.md                      plantilla: quién soy · qué corrí · qué se me rompió
  mi-imagen.md                     URL, digest, comandos y salida
  info/{info.sh, Dockerfile}       modificar y publicar
  roto/{Dockerfile, requirements.txt, app.py}   tres defectos a propósito
  volumenes/{app.py, predicciones.md}           la matriz de ocho filas, ya armada
  donde_vive/{app.py, Dockerfile}
  dev/{main.py, requirements.txt, Dockerfile}
codigo/docker/
  certificaciones.md               tres secciones, una por entrega
```

**`mi-imagen.md` vive en `08_contenedores/`, no en `docker/`**: las dos entregas
del 22 nacen del mismo `main`, así que si las dos copiaran `codigo/docker/.` las
dos **agregarían** `certificaciones.md` con contenido distinto y el merge daría un
conflicto add/add, treinta veces y con las dos revisiones en verde. Separando los
archivos, los conjuntos son disjuntos — y la regla 6 lo vuelve mecánico.

```
cp -r codigo/08_contenedores/. estudiantes/$GHUSER/08_contenedores/
cp -r codigo/docker/.          estudiantes/$GHUSER/docker/
```

`bitacora.md` pide la salida de `docker version`, `docker images` y el `docker
history` de su imagen, más qué se le rompió. `predicciones.md` viaja con la tabla
de ocho filas ya escrita y dos columnas vacías, `predicción` y `resultado`; **no
se entrega**, y el `README.md` del espejo lo dice, porque si no la mitad la sube y
la otra mitad no. `info.sh` se limpia del `echo` de depuración y `output.txt` no
viaja. Nada de `codigo/` lo valida raya ni ninguna prueba, y `revisa_entrega.py`
lo cubre por prefijo sin tocar nada.

# Código publicado y datos

`REFERENCE_EXTENSIONS` del esquema es exactamente `{".py": "code", ".ipynb":
"notebook"}`: **un enlace a un `.sh` o un `.csv` bajo `code/` hace fallar `raya
validate`** con `Local asset reference is outside supported asset roots`, y con
ella el build y el despliegue. Además `code/` sólo publica lo que alguna página
enlaza.

| Qué | Dónde | Enlazado desde |
|---|---|---|
| 5 scripts, `requirements.txt` y 13 CSV | `_assets/benchmarks/` | `lo-que-cuesta` |
| `analyze.py` | `code/analyze.py` | **`0_index.md` de la unidad**, mismo directorio, que es el precedente exacto de la unidad 3 |

`analyze.py` se ajusta para escribir junto al CSV (`Path(csv).parent`) en vez de
al `images/` que ya no existe, porque se publica justamente para que lo corran. Y
`bench_runtime.sh` **pinea `ubuntu:24.04`**: con `ubuntu:latest`, que hoy es 26.04
con coreutils en Rust, el resultado del hash se invierte y la lección de
reproducibilidad se vuelve su propio contraejemplo.

Los CSV alimentan las figuras según este mapa, que vive en el generador y que la
guarda lee de ahí:

| Figura | CSV | Columnas exigidas |
|---|---|---|
| `cont-bench-arranque` | `exp1_startup.csv` | `runtime,image,rep,startup_ms` |
| `cont-bench-escala` | `exp2_scale.csv` | `runtime,count,launch_time_s,per_container_kb,total_container_kb,daemon_rss_kb` |
| `cont-bench-overhead` | `exp3_runtime.csv` | `runtime,workload,rep,time_s` |
| `cont-bench-anidado` | `exp4_nested.csv` | `method,metric,rep,value` |

Los otros nueve viajan como datos crudos. **El estadístico es la mediana**,
declarado en una constante `ESTADISTICO = statistics.median` del generador y en el
pie de cada gráfica: los tres números que el spec cita son medianas, y quien use
`mean()` publicará 3.1 / 423 / 222 y contradirá la prosa sin que ninguna guarda lo
note.

# Figuras

Un solo catálogo, prefijo `cont-`, repartido en dos archivos porque son dos
estilos de código distintos: `tools/gen_contenedores.py` (las 25 conceptuales, el
catálogo y el `main`) y `tools/gen_contenedores_bench.py` (las cuatro gráficas y
la escala logarítmica). El primero importa el catálogo del segundo y los fusiona,
así que la guarda y el catálogo siguen siendo uno solo y ningún archivo pasa de
1,200 líneas.

**Antes de escribir una línea del generador se escriben las 31 filas de
`CREDITOS.md`**, una oración concreta por figura, al nivel de detalle de la unidad
7 ("Working directory, staging area y repositorio local, con `add` y `commit`
avanzando por arriba y `restore --staged` y `reset` regresando por abajo"). Ese es
el mínimo ejecutable: sin él, dos personas dibujan dos cosas distintas y cada
figura arrastra ~55 líneas de Python.

| Sección | Figuras |
|---|---|
| 1 | `cont-intermodal`, `cont-ns-cgroups`, `cont-tres-abstracciones`, `cont-anatomia-run`, `cont-escalamiento`, `cont-vm-vs-contenedor`, `cont-espectro`, `cont-docker-vs-podman`, `cont-capas-cache` |
| 2 | `cont-sin-sudo`, `cont-planes-b`, `cont-registro`, `cont-ciclo-de-vida`, `cont-build-contexto`, `cont-dockerfile-roto`, `cont-overlay-volumen`, `cont-rutas`, `cont-uid-plataformas`, `cont-matriz-volumen`, `cont-tapar`, `cont-estado-postgres`, `cont-prune` |
| 3 | `cont-red-y-pod`, `cont-contrato`, `cont-pipeline-servicios`, `cont-superficie-ataque` |
| Benchmarks | `cont-bench-arranque`, `cont-bench-escala`, `cont-bench-overhead`, `cont-bench-anidado` |

**Treinta SVG** más la portada, y el número sale de la tabla: la guarda
compara `len(DIAGRAMAS)` contra los archivos del disco. Cada página de lección
tiene la suya numerada; `cont-espectro` se numera en `kata-y-el-espectro` y
aparece suelta en `vm-contra-contenedor`, y `cont-bench-escala` y
`cont-bench-overhead` aparecen siempre sueltas, porque un id numerado es único en
todo el curso.

Tres restricciones duras del generador:

1. **Sólo biblioteca estándar.** CI instala `pytest pillow pyyaml` y la prueba
   **importa** el generador. Los CSV se leen con el módulo `csv`.
2. **`svg_base.py` no tiene ejes ni escalas, y no se toca** —modificarla regenera
   los 32 SVG de las unidades 6 y 7. De las cinco funciones de la unidad 3 que
   parecían reutilizables, **sólo `log_position()` se copia tal cual** (18 líneas,
   pura, sólo `math`); `_log_axis()` se reescribe, y `_plot_log_row()`,
   `_log_ticks()` y `_axes()` no sirven — además usan una paleta ajena al skin que
   la guarda de colores rechazaría. Hay que presupuestar ~150 líneas de
   infraestructura de gráfica nueva.
3. **Las cuatro gráficas también usan `svg_base.marco()`** y emiten strings, no
   `ElementTree`: `test_svg_tamano_intrinseco.py` exige `width`/`height` numéricos
   sin unidades, `viewBox` empezando en `0 0` y proporción con error < 0.01, y
   `marco()` lo cumple gratis. Mezclar los dos estilos es lo que produce el SVG
   deformado.

Los SVG **son de tema oscuro**, no "se leen igual en claro y oscuro": el skin es
sólo oscuro y las pruebas exigen fondo horneado y `fill` explícito en todo
`<text>`.

**La portada**, con `gen_ilustraciones.py` y una entrada en `ilustraciones.json`.
Cuatro trampas verificadas: `PROHIBIDOS_EN_PROMPT` compara **subcadenas** e
incluye `logotipo`, así que el prompt dice **"sin logos"**; el `CREDITOS.md` debe
contener literalmente `generada`, `ninguna` y `personas reales`; la cadena
`_assets/ilus-contenedores-portada.jpg` debe aparecer en alguna página; y
`PROHIBIDOS` se aplica al JSON entero. `CREDITOS.md` lleva **una sola tabla**:
`test_creditos.py` toma la última y compara el resto contra su encabezado.

# Guardas

**`tools/test_gen_contenedores.py`** — cada SVG del disco coincide con el
generador, **sin el fixture que regenera antes de comparar**: `test_gen_git.py` y
`test_gen_regex.py` lo tienen y por eso **no detectan una edición a mano**; sólo
`test_diagramas.py` la atrapa. Se replican las aserciones de los generadores
existentes: `aria-label` de 80 caracteres o más, `fill` explícito en todo
`<text>`, fondo horneado, colores contenidos en el skin, ningún texto fuera del
lienzo, cada SVG referenciado desde alguna página, y salida distinta de cero ante
un nombre desconocido. Más el mapa figura→CSV con sus columnas.

**`tools/test_contenedores_curriculum.py`** — molde de
`test_regex_curriculum.py`, pero **es reescritura, no adaptación**: la mitad
ejecutable del molde (correr los bloques bash exigiendo stderr vacío) no se puede
usar sin Docker, así que de las 421 líneas sólo se reaprovechan ~120 de forma de
página. Comprueba:

- Forma de página y marcador de posición, sobre las **26 páginas de lección**
  únicamente.
- Tope de líneas, con la lista de exentas y el 320 de la chuleta.
- **Ninguna línea de prosa con dos o más `$`**, quitando fences **y code spans**
  antes de contar — sin eso, `--user "$(id -u):$(id -g)"` dispara un falso
  positivo.
- **Ningún `@` suelto**, con el regex copiado literal de `numbered_objects.py`,
  no escrito a ojo.
- **Ningún HTML crudo**, permitiendo los placeholders `<tu-login>`, `<usuario>` y
  compañía sólo dentro de code span.
- Ningún `sudo docker` en prosa, con **lista blanca de páginas**, no de contextos.
- **Todo comando citado aparece en `A_chuleta.md`**, con esta normalización
  explícita, porque sin ella la guarda exigiría que la chuleta liste
  `docker stop mi-postgres-16`:

```python
GRUPOS = {"image","container","volume","network","system","context",
          "builder","buildx","compose","config","manifest","plugin","trust"}

def normaliza(linea):
    for m in re.finditer(r"\b(docker|podman)\s+(?!-)([a-z]+)(?:\s+(?!-)([a-z]+))?", linea):
        binario, a, b = m.groups()
        yield f"{binario} {a} {b}" if a in GRUPOS and b else f"{binario} {a}"
```

  El conjunto normalizado baja de ~60 instancias a ~28 entradas. El barrido ignora
  los fences que muestran **salida**, y `docker --version` se casa aparte de
  `docker version`.
- `bash -n` sobre todos los bloques ```bash: detecta el error de sintaxis sin
  necesitar Docker, y cada invocación se valida contra una lista blanca de
  subcomandos y banderas generada una vez de `docker --help`. Eso atrapa la
  bandera inventada y el subcomando que no existe, que son los dos fallos más
  frecuentes al escribir documentación de contenedores.
- Los archivos de `codigo/08_contenedores/` existen y sus Dockerfile empiezan con
  `FROM`.
- **`codigo/08_contenedores/roto/Dockerfile` sigue roto**, por **ruta exacta**:
  `"python:latest" in texto`, `"USER " not in texto`, y `texto.index("COPY . .") <
  texto.index("pip install")`. Si barriera por patrón o recorriera
  `estudiantes/`, el primer alumno que entregue su copia arreglada pondría el CI
  del curso en rojo.
- **Cobertura de la lista de verificación**: `tools/data/verificacion_contenedores.csv`,
  columnas `pagina,bloque,comando,runtime,version,fecha,resultado`, **una fila por
  fence bash** identificado por página e índice. La guarda comprueba que para cada
  página el número de filas iguale el número de bloques. Es lo único decidible sin
  parsear shell, y es lo que hace la disciplina real: alguien corrió ese bloque y
  anotó la fecha.
- Detalles del molde: **`rglob`, no `glob`** —con subsecciones, `glob` daría
  cero— y excluir `_assets/` completo del barrido de páginas.

`test_creditos.py`, `test_svg_tamano_intrinseco.py` y `test_wikilinks.py` son las
tres únicas guardas que barren todo `course/` y aplican solas. **Ninguna guarda
existente tiene lista de unidades que ampliar**; `test_vocabulario.py` no
interactúa. Nota local: `pytest tools/` corre un `raya build` completo por los
tests del dashboard de la unidad 3, así que un curso roto se ve como falla de
pytest.

# Orden de construcción

Seis fases, cada una validable, diseñadas para romper los tres ciclos del grafo
de dependencias.

**Fase 0 — lo que raya no mira.** `codigo/**` completo,
`_assets/benchmarks/` y `code/analyze.py` con su `images/` arreglado. Nada de eso
lo recorre raya mientras ninguna página lo enlace. Aquí se cierran el
`roto/Dockerfile`, la bitácora y las predicciones sin riesgo.

**Fase 1 — el esqueleto.** `0_index.md` de la unidad y los tres de sección, **sin
wikilinks salientes**: las tablas de contenido van en texto plano y se enlazan en
la fase 4. Primer `raya validate` con la unidad dentro.

**Fase 2 — generador + CREDITOS + portada, en un solo commit.** Van juntos: un SVG
sin su fila pone rojo `test_creditos.py`, y una fila sin su SVG también. La
portada no puede llegar antes que `0_index.md`, porque `test_ilustraciones.py`
exige que se use en alguna página.

**Fase 3 — las páginas, por rebanada vertical.** Cada una con su figura ya en
disco, y **cada comando nuevo entra a la chuleta en el mismo commit** —
reconstruirla al final desde 26 páginas son horas de trabajo mecánico. Un `[[id]]`
hacia una página que no existe tumba la validación entera, así que los enlaces
hacia adelante se agregan cuando el destino existe. **`test_contenedores_curriculum.py`
se escribe aquí**, con `LECCIONES` como lista que crece: escribirla al final
significa descubrir que 26 páginas la violan.

**Fase 4 — cerrar índices y medir la chuleta.**

**Fase 5 — objetos oficiales y después el calendario**, en ese orden: un `page:`
que no resuelve falla la validación, y en CI falla dentro del reusable workflow,
donde el mensaje es mucho menos obvio. Los `page:` son
`la-idea-del-contenedor`, `contenedores-con-las-manos` y
`disenar-con-contenedores`; los `title:`, "Contenedores: la idea", "Contenedores:
manos a la obra" y "Contenedores: diseño y seguridad".

**Fase 6 — `test_gen_contenedores.py` y lo de fuera.** La guarda del generador va
al final porque contiene "cada SVG referenciado desde alguna página", que sólo
pasa cuando las 35 páginas existen.

# Fuera de la unidad

| Archivo | Cambio |
|---|---|
| `course/_official/calendar/1_2026-o26.yaml` | `session-10` (09-17, **19:00–20:00**), `session-11` y `session-12` (19:00–20:30), con sus `page:` y sus `title:` |
| `CLAUDE.md` | Las sesiones existentes, la lista de `page` válidos, y la excepción al horario |
| `AGENTS.md` | El `CLAUDE.md` raíz obliga a mantenerlo consistente |
| `README.md` | La fila `Horario` |
| `course/0_index.md` | Sólo el horario: la sesión del 17 termina a las 20:00 |
| `course/1_introduccion/1_el_curso/0_index.md` | Combina "9 Docker I" y "10 Docker II" en una unidad de tres sesiones |
| `codigo/README.md` | Las dos carpetas nuevas |
| `codigo/08_contenedores/**` y `codigo/docker/**` | **Catorce** archivos nuevos |
| `tools/ilustraciones.json` | La portada |
| `tools/` | `gen_contenedores.py`, `gen_contenedores_bench.py` y las dos guardas |
| `tools/data/verificacion_contenedores.csv` | La lista de verificación de comandos |
| `.github/scripts/revisa_entrega.py` | Reglas 5 y 6 |
| `.github/workflows/entregas.yml` | El mapa branch→carpeta en su `env` |
| `tools/test_revisa_entrega.py` | Casos de las dos reglas nuevas |
| `course/7_git_y_github/2_github/4_el_flujo_del_curso.md` | De cuatro reglas a seis |

**No tocar** `tools/svg_base.py` ni `.github/workflows/pages.yml`: ninguna guarda
nueva debe necesitar una dependencia más allá de `pytest pillow pyyaml`.

# Trazabilidad

| Del material viejo | Dónde quedó |
|---|---|
| `00_index` — por qué contenedores, verificación, prompt de diagnóstico | `0_index` · `2/1` · `B_prompts` |
| `01` — McLean, definición, VM vs contenedor, namespaces, cgroups, cuándo no | `1/1` · `1/2` · `1/6` |
| `02` — cliente-servidor, tres abstracciones, capas, caché, orden, comandos, `CMD`/`ENTRYPOINT`, `info.sh`, `build`, `run`, limpieza | `1/3` · `1/4` · `1/8` · `2/4` · `2/5` · `2/13` · `A_chuleta` |
| `03` — daemon, rootless, comparación, alias, pods, cuándo elegir | `1/7` · `3/1` · `A_chuleta` |
| `04` — LAUNCH/RUNNING, exp 1-3, RSS, cgroup contra `free -m`, VFS, syscalls, nota de I/O | `1/9` · `1/7` · `_assets/benchmarks/` |
| `05` — overlay, bind contra named, lab 1, lab 2, los cuatro edge cases, dev workflow, lab 4 | `2/7` · `2/9` · `2/10` · `2/11` · `2/12` |
| `06` — DinD, socket, Podman anidado, exp 4 | `C_anidar.md` |
| Labs 1, 3 y 4 y `example/` | `codigo/08_contenedores/` |
| Cinco scripts y trece CSV | `_assets/benchmarks/` |
| `analyze.py` | `code/analyze.py`, arreglado |
| Las cuatro gráficas usadas | Cuatro SVG regenerados desde los CSV |
| Los nueve PNG huérfanos | No se publican; sus CSV sí viajan |
| Los ocho prompts para LLM | `B_prompts.md` |
| Tarea 7.0 de instalación | `_official/tasks/`, `2/1` y `2/2` |

# Lo que queda fuera a propósito

Kubernetes como herramienta —declarado como deuda que no se paga—. Compose
comando por comando. Multi-stage y multi-platform, salvo el `--platform` que hace
falta para sobrevivir la instalación. Los doce factores. APIs y Python. Y un
examen de la unidad.

# Decisiones tomadas

**Es una sola unidad, no dos.** Todo esto es contenedores: la idea, las manos y el
diseño son tres caras del mismo tema, y partirlas dejaría una unidad que enseña a
correr contenedores sin enseñar a diseñar con ellos. Lo que cambia respecto al
plan original es que ocupa **tres sesiones en vez de dos**, y por eso `el-curso`
combina sus dos filas de Docker en una. La consecuencia se asume: es la unidad más
grande del curso, del orden de 1.6× la unidad 7. El presupuesto se controla
**dentro** —cuatro páginas en clase por sesión, el resto lectura, las tablas
grandes a la chuleta— y no partiéndola.

**La primera sesión dura 60 minutos**; las otras dos, 90.

**Las fechas de entrega no se mueven.** Cada una vence justo antes de la clase que
la usa y la última es el boleto de entrada a la unidad siguiente. Los conflictos
que eso provocaba se resuelven por estructura: `mi-imagen.md` se muda de carpeta,
la regla 6 lo vuelve mecánico, y las páginas que la entrega del 22 necesita —la
instalación, los planes B, Docker Hub, el Dockerfile y el `roto/`— son todas
**lectura previa o posterior**, ninguna de las cuatro de clase.

**Los números de benchmark se republican como están**, con sus scripts para que
cualquiera los repita, y con la prosa diciendo qué mide cada experimento. Lo que
no se publica es una explicación inventada de un resultado que el experimento no
sostiene — ni la de la v1 (el VFS) ni la de la v2 (el "ruido" y el cruce en 146).

**El jueves 2026-09-10 se queda sin entrada** en el calendario: esa sesión es de la
unidad 7 y ya pasó. El calendario del curso es incremental por diseño.

# Riesgos y verificaciones pendientes

1. **El laboratorio de permisos en un Mac real.** Es lo único del informe técnico
   que no se pudo medir de primera mano y lo que más probabilidad tiene de
   arruinar una clase en vivo. Correrlo antes del 22 de septiembre.
2. **Kata.** Los comandos se prueban en `renna`, que tiene KVM. Si no corren, la
   página se queda con la explicación y sin demostración.
3. **Los temarios de DataCamp** se leyeron el 2026-09-15. Confirmar que
   *Intermediate Docker* sigue teniendo cuatro capítulos en ese orden, porque las
   tareas 3 y 4 los parten. Y **los límites de pull de Docker Hub**, que cambiaron
   en 2025.
4. **La salida de `ls /proc/1/ns/`** se captura en la versión exacta de Docker que
   se use en clase: el comportamiento de `time` cambia entre runtimes y versiones.
5. **La portada** necesita `OPENAI_API_KEY` y revisión a ojo.
6. **Versión del framework.** Todo se verificó contra el checkout local de
   `raya_lucaria`; el sitio se construye con el SHA pineado en `pages.yml`.
   Confirmar ahí `REFERENCE_EXTENSIONS` y `dollarmath` antes de publicar.
7. **Nada se puede probar con Docker en CI.** La corrección de los comandos
   depende de correrlos a mano y anotarlos en la lista de verificación.
