---
id: a-docker-hub
title: "A Docker Hub"
nav_title: "A Docker Hub"
summary: "El nombre completo de una imagen, qué es library, y la comprobación que prueba que tu imagen existe para alguien más."
status: ready
estimated_time: 12m
tags: [registro, docker-hub, tag, push, digest, login, entrega]
prerequisites: [planes-b-de-instalacion]
---

# A Docker Hub

**Página 12 de 16 · sección 2 de 3**

Meta: publicar un artefacto propio y comprobar que existe para los demás, no sólo para ti.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-registro title="El nombre de una imagen, desarmado, y el viaje de ida y vuelta al registro"}
![Un nombre de imagen desarmado en sus cuatro piezas rotuladas registro, usuario, nombre y tag, con ubuntu expandido abajo a docker.io diagonal library diagonal ubuntu con el tag latest, y la aclaración de que library no es un usuario sino el namespace reservado de las imágenes oficiales, donde no puedes hacer push. A la derecha, el viaje del artefacto propio: docker login, docker tag, docker push hacia el registro, y docker pull de vuelta desde otra máquina, con el digest sha256 colgando de la imagen como su nombre verdadero e inmutable. Dos avisos marcados: los nombres van en minúsculas siempre, y la URL pública de la imagen no es la de administración](../_assets/cont-registro.svg)
:::

## En corto

- Toda imagen tiene un nombre completo de cuatro piezas —`registro/usuario/nombre:tag`— y casi siempre ves sólo la tercera.
- El tag se mueve; el **digest** no. Ése es el nombre verdadero de una imagen.
- Que la imagen exista en tu máquina no prueba nada: la prueba es **bajarla desde afuera**.

## El nombre completo

`ubuntu` no se llama `ubuntu`. Es una abreviatura que el CLI expande por ti:

```text
docker.io  /  library  /  ubuntu  :  24.04
   ▲             ▲          ▲         ▲
registro      usuario     nombre     tag
```

Sin registro, se asume `docker.io`. Sin tag, se asume `latest` — y `latest` **no quiere decir «la más nueva»**: es sólo el tag que se usa cuando no dices ninguno, y apunta a lo que su autor haya decidido. Por eso las páginas de esta unidad pinean versiones.

**`library` no es un usuario.** Es el namespace reservado de las imágenes oficiales, curadas por Docker, y **ahí no puedes hacer `push`** por más que lo intentes. Tus imágenes van a `docker.io/<tu-usuario>/<nombre>`, y ese `<tu-usuario>` es tu cuenta de Docker Hub, que no tiene por qué llamarse igual que tu cuenta de GitHub.

Y el aviso que tumba a alguien cada semestre: **los nombres van en minúsculas, siempre**. Si tu login de GitHub lleva mayúsculas y lo copias tal cual, `docker tag` responde `invalid reference format: repository name must be lowercase` y el error no dice qué parte del nombre le molestó.

## Publicar: login, tag, push

**Haz:** una imagen mínima y propia, en el laboratorio.

```bash
mkdir -p ~/fdd/docker-lab/hola && cd ~/fdd/docker-lab/hola
printf 'FROM alpine:3.20\nCMD ["echo", "hola desde mi imagen"]\n' > Dockerfile
docker build -t hola .
docker run --rm hola
```

**Deberías ver:** el `build` recorriendo sus dos instrucciones y después la línea `hola desde mi imagen`. Esa imagen existe **sólo en tu disco**: nadie más puede pedirla.

**Haz:** ponle su nombre completo y súbela. Sustituye `TUUSUARIO` por tu usuario de Docker Hub, en minúsculas.

```bash
docker login
docker tag hola TUUSUARIO/hola:v1
docker push TUUSUARIO/hola:v1
```

**Deberías ver:** `Login Succeeded`, y después el `push` empujando capa por capa hasta una última línea con el tag y un `digest: sha256:…`. Si dice `denied: requested access to the resource is denied`, casi siempre es que el usuario del tag no es el de tu sesión — o que le escribiste una mayúscula.

`docker tag` no copia ni construye nada: le pone **otro nombre a la misma imagen**. Las dos etiquetas apuntan al mismo montón de bytes, y eso se ve porque `docker images` las lista con el mismo `IMAGE ID`.

## El digest, que es el nombre verdadero

El tag es una etiqueta movible, como una rama de Git: `TUUSUARIO/hola:v1` puede apuntar hoy a una imagen y mañana a otra, si vuelves a hacer `push` con el mismo tag. El **digest** es el hash SHA-256 del contenido, y por lo tanto no se puede mover: nombra exactamente esos bytes y ningún otro. Es la misma idea que ya viste en [[capas-y-cache|capas y caché]], aplicada a la imagen entera.

**Haz:** léelo, que es lo que va en tu entrega.

```bash
docker inspect --format '{{index .RepoDigests 0}}' TUUSUARIO/hola:v1
```

**Deberías ver:** algo como `TUUSUARIO/hola@sha256:9f6c…`. Sirve para dos cosas: pedirle a alguien exactamente la imagen que tú probaste —`docker run TUUSUARIO/hola@sha256:9f6c…`— y demostrar que la que corre en el servidor es la que revisaste, byte por byte.

## La comprobación que hace verificable la entrega

Todo lo anterior funciona igual de bien si el `push` falló a medias: la imagen sigue en tu disco y `docker run` la encuentra ahí. Así que la única prueba real es **quitarla de tu máquina y ver si el registro te la devuelve**.

**Haz:** en este orden, sin saltarte el `logout`.

```bash
docker logout
docker rmi -f TUUSUARIO/hola:v1
docker run --rm TUUSUARIO/hola:v1
```

**Deberías ver**, y esto es lo que se pega en la entrega:

```text
Unable to find image 'TUUSUARIO/hola:v1' locally
v1: Pulling from TUUSUARIO/hola
...
hola desde mi imagen
```

Esas dos líneas —`Unable to find image ... locally` y `Pulling from`— son la prueba de que la imagen está publicada y es pública: se bajó **sin sesión iniciada**, que es exactamente la situación de quien la va a revisar. Si en vez de eso sale un `pull access denied`, el repositorio quedó privado y se cambia a público desde la configuración del repositorio en Docker Hub.

Y el paso que se olvida siempre: **este ejercicio te dejó deslogueado.** Vuelve a `docker login` antes del prepull de [[instalar-docker-y-podman|la página 10]], porque el prepull sólo cuenta contra tu cuenta si tienes sesión.

::: problem {#cont-s2p3-que-se-baja title="¿Qué se baja, de dónde, y por qué esa URL da 404?"}
Dos preguntas, y las dos se contestan con la figura de arriba.

1. Escribes `docker run ubuntu` en una máquina recién instalada. **¿Qué nombre completo resuelve el CLI, qué se descarga exactamente y de dónde?** Y la de propina: ¿por qué el mismo comando, mañana, podría bajar otros bytes sin que tú cambiaras nada?

2. Publicas tu imagen, abres su página en el navegador y copias la URL de la barra de direcciones. Te queda algo que empieza con `hub.docker.com/repository/docker/…`. La pegas en la entrega y **a todo el mundo le da 404, menos a ti**. ¿Por qué, y cuál es la URL que sí sirve?
:::

::: hint {of="cont-s2p3-que-se-baja"}
Para la 1, cuenta las cuatro piezas del nombre y pregúntate cuántas escribiste tú. Para la de propina, vuelve a leer qué es un tag y qué es un digest.

Para la 2, la pista está en la palabra `repository` y en el hecho de que a ti sí te funciona. Pruébala en una ventana privada antes de contestar.
:::

::: answer {of="cont-s2p3-que-se-baja"}
**1.** El CLI expande a **`docker.io/library/ubuntu:latest`**: le pone el registro por omisión, el namespace `library` de las imágenes oficiales y el tag `latest`. De las cuatro piezas tú escribiste una. Lo que se descarga **no es un archivo**: el registro manda un *manifest* con la lista de capas y sus digests, tu máquina compara contra lo que ya tiene en disco y pide **sólo las que faltan** — que es lo mismo que hace un `git fetch`.

La propina: porque `latest` es un tag, y los tags se mueven. Canonical publica una versión nueva, mueve `latest`, y el mismo comando te trae otros bytes. Por eso lo que se fija en producción es el **digest**, no el tag, y por eso esta unidad escribe `ubuntu:24.04` en vez de `ubuntu`.

**2.** Porque `hub.docker.com/repository/docker/…` es la URL de **administración**: la vista con la que tú editas tu repositorio. Existe sólo para su dueño, y a cualquier otra persona le devuelve 404 aunque la imagen sea pública. Que te funcione a ti no prueba nada — te funciona porque estás dentro de tu sesión.

La pública es **`hub.docker.com/r/<tu-usuario>/<tu-imagen>`**. Ábrela en una ventana privada antes de entregar: si ahí se ve, se ve para todos.

Las dos preguntas son la misma, y es la de toda la página: **lo que existe para ti no es lo que existe para los demás**, y la única forma de saberlo es quitarte tus privilegios y volver a mirar.
:::

Sigue con [[rutas-en-docker]], la siguiente de consulta: cómo escribir el origen de un `-v` sin que Docker invente un volumen.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el tag se mueve y el digest no; y una imagen no está publicada hasta que te la bajas sin sesión iniciada.
