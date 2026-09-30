---
id: las-cuatro-trampas
title: "Las cuatro trampas"
nav_title: "Las cuatro trampas"
summary: "Tapar contra copiar, UID numéricos, el borrado que cruza al host y el montaje anidado: los filos que cortan la primera vez."
status: ready
estimated_time: 15m
tags: [volumen, bind-mount, named-volume, nocopy, permisos, uid, readonly]
prerequisites: [los-ocho-casos]
---

# Las cuatro trampas

**Página 16 de 16 · sección 2 de 3**

Meta: los cuatro filos del montaje que cortan la primera vez, y cómo se ve cada uno.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-tapar title="Tapar y copiar no son lo mismo"}
![Dos montajes sobre el mismo path de la misma imagen, con resultados opuestos. Arriba, un bind mount de un directorio vacío sobre /bin: lo que la imagen traía —ls, cat, sh, bash— queda debajo del montaje, intacto e inalcanzable, y adentro no se ve nada; el intento de correr ls devuelve command not found. Abajo, un named volume vacío sobre ese mismo /bin: una flecha rotulada COPIA lleva los cuatro binarios de la imagen al volumen, y adentro sí se ven; el volumen los conserva después del docker rm. Al margen, la opción que apaga la copia escrita en sus dos sintaxis, dos puntos nocopy con la corta y volume-nocopy con la larga, y un recuadro que explica que por eso el laboratorio de Postgres funciona sin pensarlo](../_assets/cont-tapar.svg)
:::

## En corto

- Un **bind mount** siempre tapa; un **named volume vacío** copia la primera vez lo que la imagen tenía en ese path. Medio internet lo cuenta al revés.
- El montaje es **bidireccional**: un `rm -rf` desde dentro borra tu disco de verdad. `:ro` lo evita, pero **no es recursivo** sobre los submontajes.
- Los permisos se comparan por **número**, no por nombre: el contenedor no sabe cómo te llamas.

## Trampa 1: tapar no es copiar

Un **bind mount** siempre tapa: monta un directorio vacío sobre `/bin` y ya no existe `ls`. No copia nada, nunca, en ningún runtime.

Un **named volume vacío hace lo contrario**: la primera vez que se monta, **copia** al volumen lo que la imagen tenía en ese path. Si ya tiene algo, tapa. La opción que lo apaga se escribe **`:nocopy`** con `-v` y `volume-nocopy` con `--mount`. **Podman hace exactamente lo mismo.**

Esto es lo contrario de lo que dice medio internet, y explica por qué el laboratorio de Postgres funciona sin que lo pienses: el `/var/lib/postgresql/data` de la imagen viene vacío, pero con el dueño y los permisos de Postgres, y el volumen vacío se lleva eso; la base se inicializa después, al primer arranque ([[named-volumes-y-postgres|2/7]]).

La regla no es «el volumen copia y el bind mount no». Es que el bind mount **nunca** copia, y el named volume copia **una** vez, y sólo si está vacío. El ejercicio del final lo mide con `wc -l`; hazlo antes de creerle a esta página.

## Trampa 2: los permisos son números

El kernel no compara usuarios, compara **UID**. `/etc/passwd` sólo traduce número a nombre para que tú lo leas, y adentro del contenedor ese archivo es el de la imagen, no el tuyo.

**Haz:**

```bash
docker run --rm alpine:3.20 id
docker run --rm -u "$(id -u):$(id -g)" alpine:3.20 id
docker run --rm -u estudiante alpine:3.20 id
```

**Deberías ver:** primero `uid=0(root)`; después **tu número, sin nombre entre paréntesis**, porque adentro nadie se llama así; y el tercero ni siquiera arranca: `unable to find user estudiante`. El nombre no viaja. El número sí, y es lo único que el kernel mira cuando decides si puedes escribir en una carpeta montada.

## Trampa 3: es bidireccional, y borra de verdad

El bind mount no es una copia ni una sincronización: es **tu directorio**, visto desde otro namespace de montaje. Lo que el contenedor borre ahí, se borra en tu disco.

**Haz:**

```bash
mkdir -p ~/fdd/docker-lab/ro && cd ~/fdd/docker-lab/ro
printf 'no me borres\n' > importante.txt
docker run --rm -v "$(pwd)":/data alpine:3.20 rm -f /data/importante.txt
ls
docker run --rm -v "$(pwd)":/data:ro alpine:3.20 touch /data/x
```

**Deberías ver:** `ls` sin salida —el archivo se fue, y no hay papelera que lo tenga—, y el último comando fallando con `Read-only file system`. Un `rm -rf /data/*` con tu carpeta de proyecto montada hace exactamente lo que dice.

`:ro` es la respuesta, y tiene letra chica: **no es recursivo**. Si dentro del path montado en sólo lectura hay otro montaje, ese otro conserva sus propios permisos y sigue siendo escribible.

## Trampa 4: montaje sobre montaje, gana el más interno

Puedes montar dos cosas donde una queda dentro de la otra. El resultado no se mezcla: el montaje **más interno** cubre a su padre en ese subárbol.

**Haz:**

```bash
mkdir -p ~/fdd/docker-lab/anidado/sub /tmp/vacio && cd ~/fdd/docker-lab/anidado
printf 'del host\n' > sub/marca.txt
docker run --rm -v "$(pwd)":/app alpine:3.20 cat /app/sub/marca.txt
docker run --rm -v "$(pwd)":/app -v /tmp/vacio:/app/sub alpine:3.20 ls -A /app/sub
```

**Deberías ver:** primero `del host`; después, **nada**. Tu `sub/` sigue en el disco con su archivo adentro; lo que pasa es que el segundo montaje lo cubre. Es el mismo mecanismo de la trampa 1, aplicado a un path que tú mismo montaste.

## Esto es una herramienta de desarrollo

Montar el código es lo que hace que el ciclo de [[los-ocho-casos]] cueste dos pasos y no tres. Pero fíjate en lo que implica: **el código tiene que existir en el disco de la máquina que corre el contenedor.**

En tu laptop existe. En el servidor no. Nadie va a clonar tu repositorio al lado del contenedor para después montárselo: ahí el código viaja **dentro de la imagen**, que es justo el caso 2 de la página anterior. El bind mount de código es una comodidad del desarrollo, no un modo de desplegar, y confundir las dos cosas es el error de diseño que abre [[el-contrato-de-un-servicio]].

Para **datos** la historia es la contraria, y ésa es [[named-volumes-y-postgres|la página 7]].

::: problem {#cont-p11-tapar-o-copiar title="Tres montajes sobre `/etc`, tres números"}
`alpine:3.20` trae archivos en `/etc`. Vas a montar tres cosas distintas sobre ese path y contar lo que queda visible. **Escribe los tres números antes de correr nada** — el primero como *N*, y los otros dos en función de *N*.

```bash
mkdir -p /tmp/vacio
docker run --rm alpine:3.20 sh -c 'ls /etc | wc -l'
docker run --rm -v /tmp/vacio:/etc alpine:3.20 sh -c 'ls /etc | wc -l'
docker run --rm -v etcvol:/etc alpine:3.20 sh -c 'ls /etc | wc -l'
```

Y una cuarta, para cerrar: ¿qué imprime si al tercero le agregas `:nocopy`?
:::

::: hint {of="cont-p11-tapar-o-copiar"}
Los tres corren la misma imagen y cuentan el mismo directorio. Lo único que cambia es qué hay encima de `/etc`: nada, un directorio vacío de tu disco, o un volumen recién creado. Sólo uno de los tres tiene permitido copiar.
:::

::: answer {of="cont-p11-tapar-o-copiar"}
**Referencia: *N*. Bind mount vacío: `0`. Named volume vacío: *N*. Con `:nocopy`: `0`.**

El bind mount tapó `/etc` con un directorio vacío de tu disco: los archivos de la imagen siguen ahí abajo, intactos y fuera de alcance, y no hay manera de verlos mientras dure el montaje.

El named volume dio el mismo número que la imagen porque **Docker copió**: `etcvol` estaba vacío, y al montarse por primera vez se llevó adentro los *N* archivos. Compruébalo con `docker volume ls` — el volumen sigue ahí, y ahora pesa.

Vuelve a correr el tercero. Sigue dando *N*, pero ya no por la misma razón: ahora el volumen **no** está vacío, así que tapa, exactamente como el bind mount. La copia ocurre una sola vez en la vida del volumen.

Y `:nocopy` da `0` porque es la opción que apaga ese comportamiento por omisión. Que haya que apagarlo es la prueba de cuál de los dos es el comportamiento por omisión.

Limpia cuando termines: `docker volume rm etcvol`.
:::

Con esto cierra la sección. Sigue con [[disenar-con-contenedores]], donde el volumen deja de ser una trampa y pasa a ser una de las tres preguntas del contrato de un servicio.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el bind mount nunca copia y el named volume copia una sola vez, y las dos veces que te sorprenda va a ser porque creíste lo contrario.
