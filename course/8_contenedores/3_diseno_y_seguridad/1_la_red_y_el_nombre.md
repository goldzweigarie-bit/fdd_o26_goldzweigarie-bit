---
id: la-red-y-el-nombre
title: "La red y el nombre"
nav_title: "La red y el nombre"
summary: "Dos contenedores se alcanzan por nombre sólo si tú creaste la red, y publicar un puerto es una decisión de diseño, no un trámite."
status: ready
estimated_time: 12m
tags: [red, bridge, dns, puerto, publicar, pod, podman]
prerequisites: [limpieza-de-docker]
---

# La red y el nombre

**Página 1 de 5 · sección 3 de 3**

Meta: que dos contenedores se hablen, y entender quién más los oye.

::: figure {#cont-red-y-pod title="Tres formas de que dos contenedores se alcancen, y la única flecha que cruza al host"}
![Tres escenarios con la misma pareja de contenedores, un servicio web y una base. En la red bridge por omisión se alcanzan por IP pero no hay resolución por nombre, y el intento por nombre aparece tachado. En una red creada por ti se alcanzan por nombre, y la IP va tachada porque cambia en cada arranque. En un pod de Podman comparten localhost y se hablan por puerto, sin nombre de por medio. Alrededor de los tres, la línea del host, con la única flecha que la atraviesa rotulada -p 5432:5432 y etiquetada como lo que es: superficie expuesta y decisión de diseño](../_assets/cont-red-y-pod.svg)
:::

## En corto

- En la red bridge **por omisión no hay resolución por nombre**: dos contenedores sólo se alcanzan por IP, y la IP cambia en cada arranque.
- En una red **que tú creas**, el nombre del contenedor es su dirección. Eso es todo lo que hace falta para que dos servicios se hablen.
- `-p` no conecta contenedores entre sí: los **expone al host y a tu red local**. Todo lo que publicas es superficie.

::: definition {#cont-s3p1-def-puerto title="`puerto`"}
Un **`puerto`** es un número de 16 bits que acompaña a una dirección de red para decir *a cuál de los programas de esa máquina* va el paquete. La dirección elige la máquina; el puerto elige el proceso. Postgres escucha por costumbre en el 5432, un servidor web en el 80.

Como cada contenedor tiene su propio namespace `net` —el de [[que-es-un-contenedor|namespaces y cgroups]]—, tiene también **su propio juego completo de puertos**. Que el 5432 esté ocupado adentro no dice nada del 5432 de tu máquina, y al revés.
:::

## La red por omisión no sabe nombres

Es la que usas sin pedirla: todo `docker run` sin `--network` cae ahí.

**Haz:**

```bash
docker run -d --rm --name uno alpine:3.20 sleep 300
docker run -d --rm --name dos alpine:3.20 sleep 300
docker exec uno ping -c1 -W1 dos
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dos
```

**Deberías ver:** el `ping` falla con `bad address 'dos'` —no es que la base esté caída, es que **el nombre no existe**—, y sin embargo `docker inspect` sí te da una IP, algo como `172.17.0.3`. Los dos contenedores están en la misma red y se alcanzan; lo que falta es quién traduce el nombre.

Podrías copiar esa IP a mano y funcionaría. No lo hagas: **la IP se reparte en el orden en que arrancan los contenedores**, así que mañana, o después de un `docker rm` y un `docker run`, ese `172.17.0.3` es otro servicio. Escribir una IP en tu configuración es acordar una dirección que nadie prometió sostener.

## Una red tuya, y el nombre es la dirección

**Haz:**

```bash
docker network create lab
docker run -d --rm --network lab --name uno alpine:3.20 sleep 300
docker run -d --rm --network lab --name dos alpine:3.20 sleep 300
docker exec uno ping -c1 -W1 dos
```

**Deberías ver:** `1 packets transmitted, 1 packets received`, y arriba la IP a la que resolvió `dos`. La diferencia con el bloque anterior es una sola: la red. En toda red creada por ti —Docker las llama *user-defined*— el runtime levanta un resolvedor interno que traduce **el nombre del contenedor** a la IP que tenga en ese momento.

Eso convierte el nombre en la parte estable y a la IP en un detalle que no te importa. `--name pg` deja de ser una comodidad para leer `docker ps` y pasa a ser **la dirección publicada de ese servicio**: es lo que van a escribir los demás contenedores, y lo que no puedes cambiar sin avisar.

## `-p` es otra cosa, y es una decisión

Publicar no tiene nada que ver con que dos contenedores se hablen. `-p 5432:5432` le dice al host: *acepta conexiones en tu propio puerto 5432 y reenvíalas adentro*. El lado izquierdo es tu máquina; el derecho, el contenedor.

**Haz:**

```bash
docker run -d --rm --network lab --name pg -e POSTGRES_PASSWORD=fdd postgres:16
docker port pg
docker run -d --rm -p 15432:5432 --name pg2 -e POSTGRES_PASSWORD=fdd postgres:16
docker port pg2
```

**Deberías ver:** para `pg`, **nada** —ni una línea—, y para `pg2`, `5432/tcp -> 0.0.0.0:15432`. Los dos Postgres están corriendo y los dos aceptan conexiones; sólo uno de ellos es alcanzable desde fuera de la red de Docker.

Y ese `0.0.0.0` es el renglón que hay que leer despacio: no es «mi laptop», es **todas las interfaces de tu laptop**. En el café o en la red del ITAM, ese Postgres con contraseña `fdd` está ofrecido a quien comparta la red contigo. Si de verdad lo necesitas abierto sólo para ti, se escribe `-p 127.0.0.1:15432:5432`.

De ahí sale la regla de diseño que ocupa el resto de la sesión: **un servicio se publica sólo si alguien de fuera del sistema lo va a usar.** La base de datos de tu pipeline no es uno de ésos; el tablero que abres en el navegador, sí.

## El caso extremo: los pods de Podman

Podman puede meter varios contenedores en un **pod**, y ahí comparten el namespace `net`: no se alcanzan por nombre porque no hace falta, se alcanzan por `localhost` y puerto, como dos programas de la misma máquina. Es el aislamiento de red llevado a cero entre ellos, y a cambio los puertos se les vuelven comunes: dos contenedores del mismo pod no pueden escuchar los dos en el 5432. Es la unidad con la que trabaja Kubernetes, y por eso Podman la trae de fábrica.

::: problem {#cont-s3p1-predice-tres title="Tres conexiones, predichas antes de correrlas"}
Levanta una base en su propia red, **sin publicar nada**:

```bash
docker network create datos
docker run -d --name pg --network datos -e POSTGRES_PASSWORD=fdd postgres:16
until docker exec pg pg_isready -q; do sleep 1; done
```

**Escribe tus tres predicciones —sí o no, con una razón cada una— antes de teclear nada más:**

1. Un contenedor **en la red `datos`** hace `ping pg`.
2. Ese mismo contenedor corre `psql -h pg -U postgres -c 'SELECT 1;'`.
3. Desde **tu host**, ¿hay algo escuchando en el 5432?

Después córrelas:

```bash
docker run --rm --network datos alpine:3.20 ping -c1 -W1 pg
docker run --rm --network datos -e PGPASSWORD=fdd postgres:16 \
  psql -h pg -U postgres -c 'SELECT 1;'
docker port pg
```

La tercera es la que hay que explicar con palabras, no con un sí o un no.
:::

::: hint {of="cont-s3p1-predice-tres"}
Las tres preguntas son la misma pregunta hecha desde tres lugares distintos: **¿quién está adentro de la red `datos`?** Dibuja la línea de la red y pon a cada participante de un lado o del otro antes de contestar. Para la tercera, revisa qué bandera no escribiste en el `docker run`.
:::

::: answer {of="cont-s3p1-predice-tres"}
**1. Sí.** El contenedor está en `datos`, que es una red creada por ti, así que el resolvedor interno traduce `pg`.

**2. Sí, y sin haber publicado un solo puerto.** Postgres escucha en el 5432 de *su* namespace `net`, y cualquiera dentro de `datos` llega ahí. Publicar nunca fue requisito para que dos contenedores se hablen: es la confusión más común de la semana.

**3. No, y ésa es la respuesta correcta de diseño.** `docker port pg` no imprime nada porque no hay `-p`: el 5432 del contenedor no está mapeado a ningún puerto del host. En Linux puedes comprobarlo del otro lado con `ss -ltn 'sport = :5432'`, que devuelve sólo el encabezado; en macOS y Windows `ss` no existe, y ahí `docker port` es la comprobación que vale.

Esa base es alcanzable por exactamente quien tiene que alcanzarla y por nadie más. Es el mismo Postgres de [[named-volumes-y-postgres]], donde entraste por `docker exec` sin publicar nada: aquello no era un atajo del salón, era el diseño. **Publicar un puerto agranda el conjunto de quien puede tocar tu servicio, y ese conjunto es una decisión tuya cada vez.**
:::

Sigue con [[el-contrato-de-un-servicio]], que convierte estas dos cosas —el nombre por el que te llaman y el puerto en el que escuchas— en la primera mitad de lo que un servicio le promete a los demás.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el nombre sólo funciona en una red que tú creaste, y `-p` no sirve para que dos contenedores se hablen: sirve para que los oiga alguien más.
