---
id: arreglar-un-dockerfile
title: "Arreglar un Dockerfile"
nav_title: "Arreglar un Dockerfile"
summary: "Tres defectos puestos a propósito en un archivo real, cada uno con el comando que lo hace visible y el arreglo que lo cierra."
status: ready
estimated_time: 12m
tags: [dockerfile, build, cache, root, usuario, pin, entrega]
prerequisites: [el-dockerfile-por-dentro]
---

# Arreglar un Dockerfile

**Página 9 de 16 · sección 2 de 3**

Meta: encontrar en un archivo real los tres defectos que ya sabes nombrar, medir cada uno antes de arreglarlo, y entregar el resultado.

::: figure {#cont-dockerfile-roto title="Los tres defectos de `roto/Dockerfile`, cada uno con la medición que lo hace visible"}
![El Dockerfile de la carpeta roto, con sus cinco líneas a la izquierda y tres insignias numeradas señalando sus defectos: la línea FROM python:latest, sin pinear; el COPY punto punto puesto antes del RUN pip install; y un recuadro punteado donde no hay ninguna instrucción USER. A la derecha, una tarjeta por defecto, cada una con tres renglones: la consecuencia, cómo se mide y el arreglo. La primera dice que la imagen de hoy no es la de mañana porque la etiqueta latest se mueve, y que se mide construyendo hoy y dentro de un mes para obtener otro digest y otro Python. La segunda dice que cada cambio de una línea de código tira el caché de instalación, y que se mide en el segundo build tras tocar app.py, que baja de 6.53 a 0.41 segundos al reordenar, con la nota de que fue medido con una sola dependencia pequeña y de que la brecha crece con el número de paquetes. La tercera dice que el proceso corre como root y que lo que escribe en el bind mount queda de root, y que se mide con un ls guion l del archivo que escribió. Abajo a la izquierda, el mismo archivo ya arreglado y entero, con sus ocho instrucciones en el orden correcto. Al pie, la conclusión: ninguno de los tres es cuestión de gusto, porque los tres se comprueban con un comando](../_assets/cont-dockerfile-roto.svg)
:::

## En corto

- El `Dockerfile` de `roto/` trae **tres** defectos puestos a propósito: la base sin pinear, el `COPY . .` antes del `pip install`, y ninguna instrucción `USER`.
- Ninguno de los tres es cuestión de gusto: **los tres se comprueban con un comando**, así que se corrigen sin discutir.
- Arreglas **tu copia**. El original se queda roto a propósito, y tocarlo hace que la revisión rechace tu pull request.

## El archivo, y dónde se arregla

Está en `roto/`, dentro de la carpeta que copiaste con el ritual de [[el-flujo-del-curso|el mirror]]. Son **tres** archivos: el `Dockerfile`, un `requirements.txt` con una sola dependencia y un `app.py` de seis líneas. El `requirements.txt` no es relleno — sin algo que instalar, el defecto del orden no tendría nada que mover.

```dockerfile
FROM python:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Cinco líneas, y tres de ellas están mal. Se arregla en `estudiantes/<tu-login>/08_contenedores/roto/Dockerfile`, nunca en `codigo/`.

**Haz:** construye el archivo tal como viene, y después mira las dos bases.

```bash
cd ~/fdd/fdd_o26/estudiantes/$GHUSER/08_contenedores/roto
docker build -t roto:v1 .
docker images python
```

**Deberías ver:** el `build` bajando `python:latest`, que pesa cerca de un giga — hazlo con buena red y **antes** del martes. Y después dos renglones de `python` en `docker images`, con `3.12-slim` varias veces más chica. Ése es el renglón que decide si tu entrega cabe en los 300 MB.

## Defecto 1 — `FROM python:latest`

`latest` no es una versión: es **una etiqueta que se mueve**. Apunta hoy a una imagen y en un mes a otra, con otro Python y otro digest, sin que tú cambies una línea. Eso es exactamente lo que la unidad vino a resolver — una imagen que no es reproducible no es un contenedor, es una sorpresa diferida.

Se mide en el calendario: construye hoy y vuelve a construir dentro de un mes; el digest no es el mismo. **El arreglo es `FROM python:3.12-slim`**, que además resuelve el tamaño.

## Defecto 2 — el `COPY . .` antes del `pip install`

Éste ya lo conoces con nombre y apellido: es el dominó de [[capas-y-cache]]. El `COPY . .` copia también `app.py`, así que **tocar una línea de tu código invalida la capa del `COPY`**, y detrás cae el `RUN pip install`, que no tenía ninguna razón para volver a correr.

**Haz:** toca el código y reconstruye, con cronómetro.

```bash
echo "# una línea más" >> app.py
time docker build -t roto:v2 .
```

**Deberías ver:** el paso del `pip install` corriendo **entero** otra vez, sin `CACHED`, por un comentario. Medido con esta única dependencia pequeña, el segundo build tarda **6.53 s** mal ordenado contra **0.41 s** bien ordenado; con `pandas` y compañía son minutos contra segundos. *(Es una medición propia sobre `requests`, en la máquina de la tanda 2 de [[lo-que-cuesta]]: Docker 29.6.0 · Linux 6.17.9. El pie no es un adorno del número, es parte del número.)*

**El arreglo es partir el `COPY` en dos**: primero `requirements.txt`, luego el `RUN pip install`, y el código hasta abajo.

## Defecto 3 — no hay ningún `USER`

Sin una instrucción `USER`, el proceso de adentro corre como `root`. No es una advertencia abstracta: es el dueño de cada archivo que ese proceso escriba en un volumen montado.

**Haz:** pregúntale al propio contenedor quién es.

```bash
docker run --rm roto:v2
```

**Deberías ver:** `Corriendo como: root`. En Linux nativo, lo que ese proceso escriba en un bind mount queda de `root` y no lo borras sin `sudo`; en otras plataformas la respuesta cambia, y ése es el tema entero de [[el-archivo-compartido]].

**El arreglo son dos líneas**: crear un usuario y cambiarse a él antes del `CMD`, después de haber instalado lo que había que instalar como `root`.

## Los tres juntos

**Haz:** aplica los tres arreglos en tu copia y repite la medición del defecto 2.

```bash
docker build -t roto:v3 .
echo "# otra línea más" >> app.py
time docker build -t roto:v3 .
docker run --rm roto:v3
```

**Deberías ver:** el primer build pagando todo, como siempre; y el segundo con el `pip install` marcado `CACHED`, en menos de un segundo. Al final, `Corriendo como: app`. Tres defectos cerrados.

::: problem {#cont-s2p6-tres-defectos title="Arregla el archivo, y cóbrate la entrega"}
1. Para cada uno de los tres defectos, escribe **una línea** con tres partes: qué instrucción es, qué consecuencia tiene y con qué comando se comprueba. Son las tres líneas que va a llevar tu `bitacora.md`.
2. Escribe el archivo arreglado **completo**. ¿Cuántas instrucciones te quedaron?
3. El `RUN useradd`, ¿va antes o después del `COPY . .`? Justifica con lo que sabes del caché **y** con quién tiene que ser dueño de `/app`.
4. Antes de abrir el pull request, califícate tú con la rúbrica de abajo. Si no llegas a 10, todavía estás a tiempo.
:::

::: hint {of="cont-s2p6-tres-defectos"}
Para la 2, el archivo arreglado de la @cont-dockerfile-roto tiene **tres** instrucciones más que el roto, no una: el `COPY` se parte en dos y el usuario cuesta dos líneas. Para la 3, pregúntate qué pasa si `USER app` está arriba y luego `pip install` intenta escribir en un directorio del sistema — y qué pasa con el caché si el `RUN useradd` queda pegado al código que cambia todos los días.
:::

::: answer {of="cont-s2p6-tres-defectos"}
**1. Los tres defectos.**

| Defecto | Consecuencia | Cómo se comprueba |
|---|---|---|
| `FROM python:latest` | la etiqueta se mueve: la imagen de hoy no es la de mañana, y pesa cerca de un giga | construye hoy y en un mes: otro digest; `docker images python` para el tamaño |
| `COPY . .` antes del `RUN pip install` | cada cambio de una línea de código tira el caché de instalación | toca `app.py` y mide el segundo build: 6.53 s contra 0.41 s |
| no hay ninguna instrucción `USER` | el proceso corre como `root` y lo que escribe en un bind mount queda de `root` | `docker run --rm` y leer `Corriendo como:`; o `ls -l` del archivo escrito |

**2.** Ocho instrucciones en vez de cinco:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN useradd -m app && chown -R app /app
USER app
CMD ["python", "app.py"]
```

**3. Después del `COPY . .`, y `USER` hasta el final.** Por el caché, porque `useradd` no depende de tu código y sí de nada más: si cae detrás de una capa que cambia a diario, se rehace a diario para nada. Y por permisos en los dos sentidos: el `pip install` necesita ser `root` para instalar, y el `chown -R app /app` tiene que correr **cuando el código ya está copiado**, o le cambia el dueño a un directorio vacío.

**4. La rúbrica de la entrega, 10 puntos.** Se califica con este archivo en la mano:

| Qué se revisa | Puntos |
|---|---:|
| Los tres defectos arreglados en **tu** `roto/Dockerfile`: base pineada, `COPY` partido, `USER` no `root` | 3 |
| `info/info.sh` con tus tres líneas de **código** —no de comentario—, y sin el `echo` de depuración del original | 1 |
| La imagen existe y es pública: la URL `hub.docker.com/r/<usuario>/<imagen>` abre en ventana privada, y pesa menos de 300 MB | 2 |
| La prueba de que se baja del registro, pegada completa, con sus líneas `Unable to find image locally` y `Pulling from` | 2 |
| `mi-imagen.md` completo: los dos usuarios, el digest, el comando exacto que corro yo y la salida que debo esperar | 1 |
| `bitacora.md` completa: `docker version`, `docker images`, `docker history`, los tres defectos y la cosa que se te rompió | 1 |
| **Puerta, no puntos:** pull request en verde desde la branch `tarea-08-imagen` nacida de `main`, tocando **sólo** `estudiantes/<tu-login>/08_contenedores/`, sin `__pycache__` ni `output.txt` | 0 |

El último renglón no suma, pero sin él no hay nada que calificar: la revisión automática es la puerta, y lo que comprueba es el repositorio, no tu imagen. **Que tu imagen se baje de verdad lo corro yo, con el comando que tú me escribiste.**
:::

Aquí termina lo que pide la clase. Sigue con [[instalar-docker-y-podman]] sólo para consultar: de la página 10 a la 16 son referencia.

> [!NOTE]
> **Si sólo recuerdas una cosa:** pinear la base, partir el `COPY` y poner un `USER` no son estilo — cada uno se comprueba con un comando, y por eso los tres se califican.
