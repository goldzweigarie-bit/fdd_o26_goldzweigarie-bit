---
id: lab-con-volumen
title: "Lab B: con volumen"
nav_title: "Lab B: con volumen"
summary: "Cinco experimentos, ocho casos: bind mount y named volume sobre /app, qué se ve adentro, qué cambia tu disco y cuándo cambia la imagen."
status: ready
estimated_time: 30m
tags: [bind-mount, named-volume, volumen, solo-lectura, rebuild, uid]
prerequisites: [lab-sin-volumen]
---

# Lab B: con volumen

**Página 6 de 16 · sección 2 de 3**

Meta: montar algo sobre `/app` y ver qué cambia qué: el contenedor, tu disco o la imagen.

::: figure {#cont-lab-con-volumen title="¿Qué cambia qué? Con volumen"}
![Matriz para predecir, sin respuestas: ocho filas y tres columnas de preguntas. Las filas son lo que haces: bind mount y editas en el host; bind mount y editas adentro; bind mount, editas adentro y haces build; bind mount y rebuild, corriendo con el montaje; bind mount de sólo lectura con dos puntos ro y escribes adentro; named volume sobre /app la primera vez; named volume sobre /app después de un rebuild con código nuevo; named volume de datos después de docker rm. Las columnas preguntan si se ve adentro, si cambia tu disco y si cambia la imagen. Cada celda lleva un signo de interrogación: predice cada una antes de correrla; las respuestas están en la tabla del final](../_assets/cont-lab-con-volumen.svg)
:::

## En corto

- Cinco experimentos, ocho casos. Un **bind mount** es tu carpeta: lo de afuera se ve adentro al instante, y lo de adentro cae en tu disco (y en el próximo build).
- Cualquier montaje sobre `/app` **tapa** lo que la imagen trae ahí: con montaje, el `build` deja de verse.
- Un **named volume** vacío copia la imagen **una sola vez**; después tapa. De ahí sale «hice build y sigo viendo el código viejo».


## El montaje
**Haz:** el de [[lab-sin-volumen]], en otra carpeta y con otra etiqueta.
```bash
mkdir -p ~/fdd/docker-lab/lab-b && cd ~/fdd/docker-lab/lab-b
cp ~/fdd/fdd_o26/codigo/08_contenedores/volumenes/app.py .
printf '%s\n' 'FROM python:3.12-slim' 'WORKDIR /app' 'COPY . .' \
  'CMD ["python", "app.py"]' > Dockerfile
docker build -t appv:1 .
docker run --rm appv:1 | head -3
```

**Qué hace cada pieza:**

- `mkdir -p ... && cd ...` — crea la carpeta (sin quejarse si ya existe) y, si salió bien, entra.
- `cp ... .` — copia `app.py` del repo a la carpeta actual (`.`).
- `printf '%s\n' ... > Dockerfile` — escribe cada texto en su propia línea, dentro de `Dockerfile`.
- `\` — el comando sigue en la línea de abajo.
- `docker build -t appv:1 .` — construye una imagen con nombre `appv:1`; `.` es tu carpeta, lo que lee `COPY`.
- `docker run --rm appv:1` — crea un contenedor de `appv:1`, corre su `CMD` y lo borra al salir.
- `| head -3` — pasa la salida a `head`, que muestra sólo las 3 primeras líneas.

**Deberías ver:** `Lab 1: Bind Mounts` entre dos filas de `=`. En macOS, el `sed -i` del host va como en [[lab-sin-volumen]].

### 1. Bind mount: editas en el host
**Predice:** ¿un contenedor que **ya corría** ve tu edición sin build ni reinicio?

**Haz:**
```bash
docker run -d --name vivo -v "$(pwd)":/app appv:1 sleep 600
sed -i 's/Bind Mounts/HOST/' app.py
docker exec vivo python app.py | head -3
docker run --rm appv:1 | head -3
```

**Qué hace cada pieza:**

- `-d` — el contenedor corre en segundo plano y te devuelve la terminal.
- `--name vivo` — le pone nombre, para usarlo abajo sin su ID.
- `-v "$(pwd)":/app` — bind mount, `origen:destino`: izquierda, tu carpeta en el host; derecha, dónde aparece adentro.
- `"$(pwd)"` — la ruta absoluta de tu carpeta actual; las comillas aguantan espacios.
- `sleep 600` — el comando de adentro, en vez del `CMD`: espera 10 minutos y lo mantiene vivo.
- `sed -i 's/A/B/' app.py` — cambia `A` por `B` en cada línea del archivo y lo guarda (`-i`).
- `docker exec vivo python app.py` — corre otro proceso dentro del contenedor que ya corría.

**Deberías ver:**
- `Lab 1: HOST` desde el `exec`, sin build ni reinicio.
- `Lab 1: Bind Mounts` sin montaje: la imagen no se enteró.

**Por qué:** `/app` adentro **es** tu carpeta. No hay copia que refrescar.

### 2. Bind mount: editas adentro
**Predice:** si el contenedor escribe en `/app`, ¿cambia tu disco? ¿Y la imagen?

**Haz:**
```bash
docker exec vivo sed -i 's/HOST/ADENTRO/' /app/app.py
grep -n 'Lab 1:' app.py
docker exec vivo sh -c 'echo hola > /app/nuevo.txt'
ls -l app.py nuevo.txt
docker run --rm appv:1 | head -3
```

**Qué hace cada pieza:**

- `grep -n 'Lab 1:' app.py` — muestra las líneas que contienen el texto, con su número.
- `sh -c '...'` — corre la línea completa en un shell de adentro, para que el `>` pase allá.
- `echo hola > /app/nuevo.txt` — crea el archivo con `hola` adentro (y en tu disco).
- `ls -l` — lista con detalle; la tercera y cuarta columnas son dueño y grupo.

**Deberías ver:**
- Dos líneas con `Lab 1: ADENTRO` en **tu** `app.py` (el docstring y el `print`).
- En Linux, `app.py` sigue siendo tuyo; `nuevo.txt` es de `root root`.
- `Lab 1: Bind Mounts`: la imagen, intacta.

**Por qué:** en Linux el uid 0 de adentro es el de afuera. `sed -i` conserva al dueño; lo **nuevo** queda de `root`.

| Plataforma | Archivo nuevo escrito desde adentro |
|---|---|
| Linux nativo o WSL2, con Docker | de `root` |
| macOS/Windows con Docker Desktop, o Podman rootless | tuyo |

Sólo en Linux con Docker (fila 1); en Podman rootless ya son tuyos: no lo corras.
```bash
docker run --rm -v "$(pwd)":/app alpine:3.20 \
  chown "$(id -u):$(id -g)" /app/nuevo.txt /app/output.txt
```

**Qué hace cada pieza:**

- `alpine:3.20` — una imagen mínima; aquí sólo presta un `root` que puede cambiar dueños.
- `chown dueño:grupo archivos` — cambia el dueño y el grupo de esos archivos.
- `"$(id -u):$(id -g)"` — tu uid y tu gid como números, p. ej. `1000:1000`.
- `--user "$(id -u):$(id -g)"` — (en la línea de abajo) corre el proceso con tu uid, no como `root`.

Para que nazcan tuyos desde el principio: `--user "$(id -u):$(id -g)"`. Detalle en [[el-archivo-compartido|2/14]].

### 3. Bind mount + build: ahora sí cambia la imagen
**Predice:** lo que el contenedor escribió en tu carpeta, ¿entra al próximo build? ¿Y si luego montas la carpeta?

**Haz:**
```bash
docker rm -f vivo
docker build -t appv:1 .
docker run --rm appv:1 | head -3
sed -i 's/ADENTRO/DISCO/' app.py
docker run --rm -v "$(pwd)":/app appv:1 | head -3
docker run --rm appv:1 | head -3
```

**Qué hace cada pieza:**

- `docker rm -f vivo` — detiene y borra el contenedor `vivo` en un solo paso (`-f`).
- Lo demás ya salió: `build` lee tu carpeta; el mismo `docker run` con y sin `-v`.

**Deberías ver:**
- `Lab 1: ADENTRO` en la imagen recién construida: la edición de adentro **sí** entró.
- Después, `Lab 1: DISCO` con montaje y `Lab 1: ADENTRO` sin él.

**Por qué:** el build lee tu carpeta, y el contenedor la escribió. Es el par del experimento 4 de [[lab-sin-volumen]]. Y la imagen nueva queda **tapada** por el montaje: su `/app` queda debajo.

> [!TIP]
> Monta la carpeta, no el archivo: con `-v "$(pwd)/app.py":/app/app.py`, un `sed -i` o un editor que reemplaza el archivo cambia el inode (el número con el que el disco identifica un archivo; `sed -i` y muchos editores crean uno nuevo), y el contenedor sigue viendo el viejo.

### 4. Bind mount `:ro`
**Predice:** la app escribe `output.txt` en `/app`. ¿Y si montas de sólo lectura?

**Haz:**
```bash
docker run --rm -v "$(pwd)":/app:ro appv:1 2>&1 | tail -1
```

**Qué hace cada pieza:**

- `:ro` — tercer campo del `-v`: monta de sólo lectura (*read-only*).
- `2>&1` — junta los errores con la salida normal, para que pasen por el `|`.
- `| tail -1` — muestra sólo la última línea: el error.

**Deberías ver:** `OSError: [Errno 30] Read-only file system: '/app/output.txt'`

**Por qué:** `:ro` deja entrar tu código y le prohíbe al contenedor tocarlo.

### 5. Named volume sobre `/app`: el código viejo que no se va
**Predice:** editas adentro del volumen, luego cambias `app.py` y haces build. ¿Qué ves con `-v codigo:/app`?

**Haz:**
```bash
docker run --rm -v codigo:/app appv:1 | head -3
docker run --rm -v codigo:/app appv:1 sed -i 's/ADENTRO/VOLUMEN/' /app/app.py
docker run --rm -v codigo:/app appv:1 | head -3
docker run --rm appv:1 | head -3
sed -i 's/DISCO/NUEVO/' app.py
docker build -t appv:1 .
docker run --rm -v codigo:/app appv:1 | head -3
```

**Qué hace cada pieza:**

- `-v codigo:/app` — **nombre** en vez de ruta a la izquierda: es un named volume, no tu carpeta.
- `codigo` — si no existe, Docker lo crea (como `docker volume create codigo`); lo ves con `docker volume ls`.
- `... appv:1 sed -i ... /app/app.py` — el comando final reemplaza al `CMD`: edita adentro del volumen.
- `docker volume rm codigo` — (en el Por qué) borra el volumen y lo que guarda.

**Deberías ver:**
- `ADENTRO`, no `DISCO`: el volumen no es tu carpeta, es copia de la imagen.
- `VOLUMEN` con el volumen; `ADENTRO` sin él: la imagen no cambió.
- Tras el build, **otra vez `VOLUMEN`**: el código nuevo no aparece.

**Por qué:** vacío, el volumen **copió** el `/app` de la imagen; ya no está vacío y tapa cada build ([[las-cuatro-trampas|2/16]]). Arreglo: `docker volume rm codigo`.

> [!WARNING]
> `-v codigo:/app` **sin `./`** es un named volume llamado `codigo`, no una carpeta tuya: [[rutas-en-docker|2/13]].

## La tabla del lab B
| Qué haces | ¿Se ve adentro? | ¿Cambia tu disco? | ¿Cambia la imagen? |
|---|---|---|---|
| Bind mount, editas en el host | **sí**, también en el que ya corría | **sí**: es tu disco | no |
| Bind mount, editas adentro | **sí** | **sí**, y en Linux lo nuevo queda de `root` | no |
| Bind mount, editas adentro + build | **sí**, en un contenedor nuevo sin montaje | **sí** | **sí**: el build lee tu carpeta |
| Bind mount + rebuild, corres con montaje | **no**: el montaje tapa el build | no | sí, pero tapada |
| Bind mount `:ro`, escribes adentro | no: `Read-only file system` | no | no |
| Named volume sobre `/app`, primera vez | lo que trae la imagen: lo **copia** | no | no |
| Named volume sobre `/app`, tras rebuild | **no**: sigue el código viejo | no | sí, pero tapada |
| Named volume de datos, tras `docker rm` | **sí**: sobreviven ([[named-volumes-y-postgres|2/7]]) | no | no |

**La regla:** bind mount para tu código mientras desarrollas; named volume para datos. La imagen que publicas lleva el código **adentro**, con `COPY` ([[los-ocho-casos|2/15]]).

::: problem {#cont-s2p6-cuatro-lineas title="Cuatro corridas: ¿qué código ve cada una?"}
Tras el experimento 5, la imagen y tu `app.py` dicen `NUEVO`. **Sin correr nada**, predice cada `docker run`:
```bash
docker volume rm codigo
docker run --rm -v codigo:/app appv:1 | head -3
sed -i 's/NUEVO/OTRO/' app.py
docker run --rm -v "$(pwd)":/app appv:1 | head -3
docker run --rm -v codigo:/app appv:1 | head -3
docker run --rm appv:1 | head -3
```
Nada nuevo en el bloque: todas sus piezas ya salieron arriba. Luego: ¿qué dos comandos hacen que los cuatro digan `OTRO`?
:::

::: hint {of="cont-s2p6-cuatro-lineas"}
Pregunta por cada línea qué lee el proceso: tu disco, la imagen o el volumen. Y cuándo copia un named volume.
:::

::: answer {of="cont-s2p6-cuatro-lineas"}
1. `NUEVO`: el volumen vacío copia la imagen.
2. `OTRO`: bind mount, tu disco.
3. `NUEVO`: el volumen ya no está vacío, tapa.
4. `NUEVO`: la imagen, sin build.

Los dos comandos: `docker build -t appv:1 .` y `docker volume rm codigo`; la siguiente corrida con `-v codigo:/app` copia otra vez y dice `OTRO`.
:::

Para limpiar: `docker volume rm codigo` (la imagen `appv:1` puede quedarse). Sigue con [[named-volumes-y-postgres]], donde el volumen de datos guarda una base de verdad.

> [!NOTE]
> **Si sólo recuerdas una cosa:** lo que montas sobre `/app` tapa a la imagen; un bind mount es tu carpeta, y un named volume es una copia que se quedó con lo de la primera vez.
