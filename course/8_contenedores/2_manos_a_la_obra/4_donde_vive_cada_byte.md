---
id: donde-vive-cada-byte
title: "Dónde vive cada byte"
nav_title: "Dónde vive cada byte"
summary: "Cuatro lugares posibles para lo que escribe un contenedor, y cada uno muere con un comando distinto. Es la tabla que ordena toda la clase."
status: ready
estimated_time: 10m
tags: [overlay, volumen, bind-mount, capa-de-escritura, copy-up, persistencia]
prerequisites: [el-dockerfile-por-dentro]
---

# Dónde vive cada byte

**Página 4 de 16 · sección 2 de 3**

Meta: dejar de preguntar «¿se guardó?» y preguntar «¿en cuál de los cuatro?». De ahí sale qué comando se lo lleva.

::: figure {#cont-overlay-volumen title="Los cuatro lugares donde puede caer un byte que escribe un contenedor"}
![Corte del sistema de archivos que ve un contenedor, colgando de la raíz. Abajo, apiladas y en sólo lectura, las capas de la imagen, rotuladas con las instrucciones que las produjeron: FROM python 3.12 slim, RUN pip install y COPY; las escribe docker build y mueren con docker rmi. Encima de ellas, dibujada por overlayfs, la capa de escritura del contenedor: la escribe el proceso de adentro y muere con docker rm, con una nota que explica el copy-up, es decir que la primera vez que el proceso escribe sobre un archivo que venía de una capa inferior, el archivo se copia entero hacia arriba. A un costado cuelgan dos rutas montadas aparte, que no pasan por el overlay: diagonal app, que sale de un bind mount apuntando a una carpeta del disco del host y que no muere nunca porque es tu disco, y diagonal var diagonal lib diagonal postgresql diagonal data, que sale de un named volume guardado en el área de Docker y que sobrevive a docker rm y muere con docker volume rm. Abajo, la tabla de cuatro filas con las mismas cuatro respuestas, una columna para quién escribe cada una, otra para qué comando la borra y otra que dice si sobrevive a docker rm: sí, NO, sí y sí](../_assets/cont-overlay-volumen.svg)
:::

## En corto

- Lo que un contenedor escribe cae en **uno de cuatro lugares**, y cada uno tiene un dueño distinto y un comando distinto que lo destruye.
- Sólo uno de los cuatro muere con `docker rm`: **la capa de escritura**. Los otros tres sobreviven, y por eso los datos van en uno de ellos, nunca en la capa de escritura.
- Esta tabla **predice** los dos laboratorios que siguen, [[lab-sin-volumen|2/5]] y [[lab-con-volumen|2/6]]. Sabiéndola, no memorizas ninguno.

## La tabla

::: table {#cont-tabla-bytes title="Las cuatro respuestas, con su dueño y su comando"}

| Dónde vive el byte | Quién lo escribe | Qué lo borra | ¿Sobrevive a `docker rm`? |
|---|---|---|---|
| Las capas de la imagen | `docker build` | `docker rmi` | sí |
| La capa de escritura | el proceso de adentro | `docker rm` | **no** |
| Bind mount | el host y el contenedor | tú, borrando el archivo | sí — **es tu disco** |
| Named volume | el contenedor | `docker volume rm` | sí |

:::

**Qué hace cada comando de la tabla:**

- `docker build` — lee tu Dockerfile y tu carpeta, y produce una imagen nueva.
- `docker rmi` — borra una imagen (sus capas, si nadie más las usa).
- `docker rm` — borra un contenedor detenido y, con él, su capa de escritura.
- `docker volume rm` — borra un named volume y todo lo que tenga adentro.

Lee despacio la segunda fila: es la única que dice «no», y ahí cae **todo** lo que escribes sin decir dónde.

La tercera y la cuarta existen justo para sacar los bytes de ahí.

## Filas 1 y 2: la pila del overlay

- La imagen es una pila de capas de **sólo lectura** ([[capas-y-cache]]).
- El driver `overlay2` le pone encima una **capa de escritura** vacía, propia de cada contenedor. Adentro ves la suma, aplanada.
- Todo lo que el proceso crea o modifica aterriza en esa capa de arriba, y sólo ahí.
- **Copy-up** (la deuda de [[lo-que-cuesta]]): la primera vez que escribes sobre un archivo de una capa inferior, el kernel lo **copia entero** hacia arriba. Cambiar un byte de un archivo de 2 GB copia 2 GB.

Escribir en la capa del contenedor se paga **y además se pierde**.

## Filas 3 y 4: los montajes se saltan el overlay

- **Bind mount:** un directorio de tu disco que aparece en una ruta de adentro. No es copia: es **el mismo directorio**, visto desde dos lados. `docker rm` no toca tu disco.
- **Named volume:** un directorio que administra Docker (por omisión en `/var/lib/docker/volumes/`; el tuyo te lo dice `docker volume inspect`), con nombre en vez de ruta. Sobrevive a `docker rm`; muere con `docker volume rm`.

Saltarse el overlay también es regla de diseño: si tu programa **escribe mucho** (una base de datos, un log que crece), monta un volumen, aunque no necesites persistencia.

- Medido en la misma máquina y el mismo disco: Docker escribió **510 MB/s** en un volumen (sin capas ni copy-up de por medio) contra **380 MB/s** en la capa overlay, mediana de **tres** repeticiones. Un **34 %** más rápido.
- El pie completo (máquina, kernel, versiones, y por qué se tiró otro brazo del CSV) está en [[lo-que-cuesta|1/9]]. El «~20 % más lento» que circula por internet no sale de ningún lado revisable.
- Lo que se transfiere es el signo y el mecanismo, no el 34 %: en tu disco saldrá otro número. Si lo necesitas exacto, **mídelo**.

Cada fila se prueba con las manos en los dos laboratorios: [[lab-sin-volumen|2/5]] y [[lab-con-volumen|2/6]].

::: problem {#cont-s2p7-una-fila title="Una fila, y todo lo que se deduce de ella"}
Corriste esto, y el programa escribió un archivo en `/app/salida.txt`:

```bash
cd ~/fdd/docker-lab
docker run --rm -v "$(pwd)":/app mi-imagen:v1
```

**Qué hace cada pieza:**

- `cd ~/fdd/docker-lab` — te mueve a tu carpeta de trabajo.
- `docker run` — crea un contenedor nuevo desde una imagen y lo arranca.
- `--rm` — borra el contenedor en cuanto su proceso termina.
- `-v origen:destino` — hace aparecer `origen` adentro, en la ruta `destino`.
- `"$(pwd)"` — la ruta de tu carpeta actual; las comillas aguantan espacios en la ruta.
- `:/app` — dónde aparece esa carpeta adentro del contenedor.
- `mi-imagen:v1` — la imagen: nombre y etiqueta (versión); corre su comando por omisión.

1. ¿En **cuál de las cuatro filas** cae `salida.txt`? Una frase con el porqué.
2. ¿Qué comando lo borra? ¿Y qué **no** lo borra?
3. El `--rm` destruyó el contenedor al terminar. ¿Cambia eso tu respuesta?
4. Si hubieras corrido lo mismo **sin** el `-v`, ¿en qué fila habría caído, y qué habría pasado con el archivo?
:::

::: hint {of="cont-s2p7-una-fila"}
Una sola pregunta decide las cuatro: **¿esa ruta de adentro está montada desde algún lado?** Si lo está, el byte nunca pasó por el overlay. Si no, cayó en la capa de escritura.
:::

::: answer {of="cont-s2p7-una-fila"}
**1. Bind mount**, tercera fila. `/app` está montado desde `~/fdd/docker-lab`: escribir ahí es escribir en **tu disco**, no en una copia.

**2.** Lo borra **`rm salida.txt`** en tu terminal. No lo borran `docker rm`, `docker rmi mi-imagen:v1` ni `docker volume prune` (que, sin `-a`, sólo borra los volúmenes anónimos sin uso): Docker no es dueño de ese directorio.

**3. No cambia nada, y ése es el punto.** El `--rm` se llevó la capa de escritura, y `salida.txt` no estaba ahí.

**4. Capa de escritura**, segunda fila: sin `-v`, `/app/salida.txt` es una ruta más del overlay. El programa corre igual, dice que escribió, y el `--rm` destruye el archivo. **Sin error, sin aviso y sin archivo.**
:::

Sigue con [[lab-sin-volumen]]: el laboratorio A pone a prueba las filas 1 y 2.

> [!NOTE]
> **Si sólo recuerdas una cosa:** de los cuatro lugares donde puede caer un byte, sólo la capa de escritura muere con `docker rm` — y es donde cae todo lo que escribes sin decir dónde.
