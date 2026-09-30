---
id: repaso-dockerfile-imagen-contenedor
title: "Repaso: Dockerfile, imagen, contenedor"
nav_title: "Repaso: las tres cosas"
summary: "Lo que ya viste en DataCamp, ordenado: tres cosas distintas, cada una cambia con su propia herramienta, y lo que el contenedor escribe en su capa no vuelve atrás."
status: ready
estimated_time: 8m
tags: [dockerfile, imagen, contenedor, build, run, repaso]
prerequisites: [contenedores-con-las-manos]
---

# Repaso: Dockerfile, imagen, contenedor

**Página 1 de 16 · sección 2 de 3**

Meta: ordenar lo que ya sabes en tres cajas, para que cada laboratorio de hoy tenga dónde caer.

::: figure {#cont-repaso-triada title="Tres cosas, tres comandos, una sola dirección"}
![Tres cajas en fila unidas por flechas. La primera, Dockerfile: la receta, texto en tu carpeta, la cambias con tu editor y la borras con rm. Una flecha rotulada docker build lleva a la segunda, Imagen: capas de sólo lectura, inmutable, no cambia: otro build hace otra; se ve con docker images y se borra con docker rmi. Una flecha rotulada docker run lleva a la tercera, Contenedor: un proceso más su capa de escritura, efímero, lo cambia el proceso o docker exec, se ve con docker ps -a y se borra con docker rm. Del contenedor sale una flecha punteada de regreso a la imagen, rotulada docker commit, existe pero no se usa, y una flecha tachada de regreso al Dockerfile, rotulada nunca desde su capa, con la nota de que sólo un bind mount escribe en tu carpeta. Colgando del contenedor hay dos cajas externas, bind mount, que es tu carpeta, y named volume, que es un área de Docker, ambas rotuladas no pasan por la imagen.](../_assets/cont-repaso-triada.svg)
:::

## En corto

- **Dockerfile, imagen y contenedor son tres cosas distintas**, y cada una vive en un lugar distinto.
- **Cada una cambia con una herramienta distinta:** tu editor, `docker build`, y el proceso (o `docker exec`) dentro del contenedor.
- **Lo que el contenedor escribe en su propia capa no vuelve** ni a la imagen ni al Dockerfile. Con tu carpeta montada, en cambio, sí cambia tu disco ([[lab-con-volumen|2/6]]).

Esto ya lo viste en DataCamp y en [[receta-imagen-contenedor|1/3]]. Aquí no se re-enseña: se ordena, porque toda la clase de hoy es una sola pregunta — **«cambié algo: ¿cuál de las tres cambió?»**

## Las tres cosas, con los nueve comandos de base

| | Dockerfile | Imagen | Contenedor |
|---|---|---|---|
| **Sale de** | tu editor | `docker build` | `docker run` |
| **La cambia** | tú, con tu editor | nada: otro `build` (o `docker commit`) hace **otra** | el proceso, o tú con `docker exec` |
| **La ves con** | `cat Dockerfile` | `docker images` | `docker ps -a` (vivos y detenidos) |
| **Le hablas con** | — | — | `docker exec` si corre; `docker logs` aunque ya haya terminado |
| **La borra** | `rm` | `docker rmi`: quita la etiqueta; si era la última, borra la imagen | `docker rm`, con su capa de escritura |

**La imagen no se edita; se reemplaza.** Las capas y la caché del rebuild están en [[capas-y-cache|1/8]]. Los demás comandos, en [[chuleta-contenedores|la chuleta]].

## Anatomía de un `docker run`

Un comando completo, desarmado. No lo corras: es para leerlo pieza por pieza.

`docker run -d --name web -v "$(pwd)":/app -e MODO=dev --rm app:1 python app.py`

| Pieza | Qué hace | Si la quitas… |
|---|---|---|
| `docker run` | crea un contenedor nuevo desde una imagen y lo arranca | — es el comando |
| `-d` | lo deja corriendo en segundo plano y te devuelve la terminal | se queda pegado a tu terminal hasta que el proceso termine |
| `--name web` | le pone nombre, para no usar su ID | Docker inventa uno al azar |
| `-v "$(pwd)":/app` | monta tu carpeta actual (`origen:destino`) en `/app` de adentro | ve sólo el `/app` que trae la imagen: la copia del build |
| `-e MODO=dev` | define la variable de entorno `MODO` adentro | la variable no existe, salvo que la imagen la traiga |
| `--rm` | borra el contenedor en cuanto su proceso termina | queda en `docker ps -a` como `Exited` hasta que lo borres |
| `app:1` | la imagen: nombre y etiqueta (versión) | error: Docker no sabe de qué imagen partir |
| `python app.py` | el comando que corre adentro; reemplaza al `CMD` de la imagen | corre el `CMD` que dejó el Dockerfile |

Las opciones van **antes** de la imagen; lo que va **después** de la imagen es el comando.

## Anatomía de un `docker build`

`docker build -t app:1 .`

| Pieza | Qué hace | Si la quitas… |
|---|---|---|
| `docker build` | lee el Dockerfile y arma una imagen nueva | — es el comando |
| `-t app:1` | le pone nombre y etiqueta a la imagen | la imagen sale sin nombre: sólo con su ID |
| `.` | el contexto: la carpeta que se manda al build; de ahí sale lo que copia `COPY` | error: `build` exige esa carpeta |

## Si cambias X, ¿qué tienes que hacer para verlo?

Hoy sólo mírala: cada fila se prueba en [[lab-sin-volumen|2/5]] y [[lab-con-volumen|2/6]]. El bind mount de la última se explica en [[donde-vive-cada-byte|2/4]].

| Cambias… | Para verlo | Por qué |
|---|---|---|
| tu código (`app.py`) en tu carpeta | `docker build` + un `docker run` nuevo | el contenedor tiene la copia que entró en el build |
| el Dockerfile | `docker build` + un `docker run` nuevo | la receta sólo actúa al construir |
| algo adentro del contenedor | nada: ya se ve, **sólo en ese contenedor** | vive en su capa de escritura y muere con `docker rm` |
| tu código, con tu carpeta montada (`-v "$PWD":/app`, un bind mount) | el archivo ya se ve; un proceso que ya lo había cargado, al volver a correrlo | el contenedor lee tu disco, no la imagen |

## Las tres, existiendo por separado

**Haz:** una receta de tres líneas, en su carpeta.

```bash
mkdir -p ~/fdd/docker-lab/repaso && cd ~/fdd/docker-lab/repaso
printf '%s\n' 'FROM alpine:3.20' \
  'RUN echo "horneado en el build" > /nota.txt' \
  'CMD ["cat", "/nota.txt"]' > Dockerfile
cat Dockerfile
```

**Qué hace cada pieza:**

- `mkdir -p ~/fdd/docker-lab/repaso` — crea la carpeta, y las de en medio si faltan.
- `&&` — corre lo de la derecha sólo si lo de la izquierda salió bien.
- `cd` — entra a esa carpeta.
- `printf '%s\n' 'a' 'b'` — escribe cada texto entre comillas en su propia línea.
- `\` al final de una línea — el comando sigue en la línea de abajo.
- `> Dockerfile` — manda esa salida al archivo `Dockerfile`, en vez de a la pantalla.
- `FROM alpine:3.20` — la receta parte de esa imagen base, una Linux mínima.
- `RUN echo ... > /nota.txt` — durante el build, escribe `/nota.txt` dentro de la imagen.
- `CMD ["cat", "/nota.txt"]` — el comando por defecto de cada contenedor: mostrar la nota.
- `cat Dockerfile` — muestra el archivo en pantalla.

**Deberías ver:** las tres líneas. Eso es **la primera cosa**: un archivo, nada más. Docker todavía no sabe que existe.

**Haz:** construye la imagen y búscala.

```bash
docker build -t repaso:1 .
docker images repaso
```

**Qué hace cada pieza:**

- `docker build -t repaso:1 .` — la anatomía de arriba, con nombre `repaso` y etiqueta `1`.
- `docker images repaso` — lista las imágenes locales llamadas `repaso`.

**Deberías ver:** al final del build, `naming to docker.io/library/repaso:1`, y luego una fila de `repaso` con la etiqueta `1`, su `ID` y su tamaño (unos 8 MB). Ésa es **la segunda cosa**, y ya no depende de tu archivo: bórralo y la imagen sigue ahí.

**Haz:** arranca tres contenedores de la misma imagen. El segundo escribe adentro; el tercero se borra solo al terminar (`--rm`).

```bash
docker run --name uno repaso:1
docker run --name dos repaso:1 sh -c 'echo "escrito adentro" > /nota.txt; cat /nota.txt'
docker run --rm repaso:1
docker ps -a
```

**Qué hace cada pieza:**

- `--name uno` / `--name dos` — nombres para encontrarlos después en la lista.
- `sh -c '...'` — reemplaza al `CMD`: corre ese texto como un comando del shell, adentro.
- `echo "escrito adentro" > /nota.txt` — sobrescribe la nota, en la capa de `dos`.
- `;` — separa dos comandos: corre uno y luego el otro, salga bien o mal.
- `--rm` — borra el tercer contenedor apenas termina.
- `docker ps -a` — lista todos los contenedores, vivos y detenidos.

**Deberías ver:**
- `horneado en el build`, luego `escrito adentro`, y otra vez `horneado en el build`;
- en `ps -a`, `uno` y `dos` con `Exited (0)`: **la tercera cosa**, dos veces. El de `--rm` ya no aparece.
- la escritura de `dos` se quedó en la capa de `dos`: el tercero leyó la imagen, que no se enteró, y el Dockerfile sigue igual.

**Haz:** limpia. **El primer `rmi` va a fallar a propósito.**

```bash
docker rmi repaso:1
docker rm uno dos
docker rmi repaso:1
```

**Qué hace cada pieza:**

- `docker rmi repaso:1` — quita esa etiqueta; si era la última, borra la imagen.
- `docker rm uno dos` — borra los dos contenedores, con su capa de escritura.

**Deberías ver:** el primer `rmi` falla con `conflict: unable to remove repository reference "repaso:1" (must force) - container ... is using its referenced image`. Un contenedor **detenido** también cuenta. Borrados los contenedores, sale `Untagged: repaso:1` y `Deleted: sha256:...`.

::: problem {#cont-repaso-cual-cambio title="¿Cuál de las tres cambió?"}
Tienes un proyecto con `Dockerfile` y `app.py`, una imagen `web:1` construida ayer y un contenedor `w` de esa imagen, corriendo, sin nada montado. Haces estas acciones **en este orden**; para cada una, di cuál de las tres cambió: **Dockerfile**, **imagen**, **contenedor**, o **ninguna**.

1. Editas `app.py` en tu editor y guardas.
2. Agregas `RUN pip install pandas` al Dockerfile y guardas.
3. Corres `docker exec w pip install requests`.
4. Corres `docker build -t web:1 .`
5. Corres `docker rm -f w`.
:::

::: hint {of="cont-repaso-cual-cambio"}
`app.py` no es ninguna de las tres: es material que el build **leerá** cuando lo corras. Y pregúntate en cada caso qué herramienta acabas de usar: editor, `build`, o algo que corre adentro.
:::

::: answer {of="cont-repaso-cual-cambio"}

| # | Cambió | Por qué |
|---|---|---|
| 1 | **ninguna** | tu disco cambió; la imagen y `w` tienen la copia vieja hasta el próximo build |
| 2 | **Dockerfile** | sólo la receta. `web:1` no tiene `pandas` hasta que construyas |
| 3 | **contenedor** | `requests` cae en la capa de escritura de `w`, y ni la imagen ni el Dockerfile se enteran |
| 4 | **imagen**, una nueva | la etiqueta `web:1` pasa a apuntar a ella, con `pandas` y tu `app.py` nuevo. `w` sigue sobre la vieja: **reconstruir no toca a `w`**, hace falta un `run` nuevo |
| 5 | **contenedor**, desaparece | se lleva el `requests` del paso 3. La imagen y el Dockerfile, intactos |
:::

Ya sabes cuáles son las tres cosas. Sigue con [[ciclo-de-vida-de-un-contenedor]]: cuánto vive la tercera, y por qué `uno` y `dos` terminaron solos.

> [!NOTE]
> **Si sólo recuerdas una cosa:** cada una de las tres cambia con su propia herramienta, y lo que el contenedor escribe en su propia capa nunca vuelve a la imagen ni al Dockerfile.
