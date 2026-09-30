---
id: contenedores-anidados
title: "Contenedores anidados"
nav_title: "Anidar"
summary: "Docker dentro de Docker, el socket montado que no anida sino que hace hermanos, Podman anidado, y qué cuesta medido: poco en cómputo y bastante en arranque."
status: ready
estimated_time: 15m
tags: [dind, socket, privileged, ci, podman, benchmark, anidamiento]
prerequisites: [anatomia-de-docker-run]
---

# Contenedores anidados

**Anexo C** · para consultar, no para memorizar

## Esta página contradice a la anterior, y conviene decirlo primero

[[cuando-se-rompe-el-aislamiento]] termina con dos prohibiciones sin matices: **nunca `--privileged`** y **nunca montes `/var/run/docker.sock`**. Las dos son correctas, y este anexo describe cómo se hacen las dos a propósito, todos los días, en los servidores de integración continua de media industria — incluidos los de este repositorio.

No es que allá la regla no aplique. Es que allá se paga a conciencia, sobre una máquina **efímera y ajena**, que nace para ese trabajo y se destruye al terminarlo. La regla verdadera nunca fue «no lo hagas»: es **«no lo hagas sin saber qué estás entregando»**, y lo que se entrega es distinto en cada uno de los tres caminos de abajo. Esa diferencia es toda la página.

Léelo en ese orden, además, porque el anexo está escrito **después** de aquella página a propósito: primero qué abre cada bandera, después para qué se abre.

## Las tres maneras, y sólo dos anidan

### 1 · Docker dentro de Docker

Es lo que el nombre dice: un **segundo daemon completo**, corriendo dentro de un contenedor, con su propio `/var/lib/docker`. La imagen oficial es `docker:dind` y necesita `--privileged`, porque ese daemon de adentro tiene que hacer exactamente lo que hace el de afuera —montar `overlay`, crear cgroups y namespaces de red, hablarle a dispositivos—, y nada de eso está permitido dentro de un contenedor normal.

Lo que obtienes es un mundo aparte: sus imágenes no son tus imágenes, su caché de capas no es tu caché, y sus contenedores mueren cuando muere el de afuera. **Eso es anidar de verdad**, y es lo que hace que sirva para aislar un trabajo de construcción: nada de lo que el `build` ensucie sobrevive.

### 2 · El socket montado — que **no** anida

Es la receta más repetida de internet, y la que hay que entender con más cuidado, porque no hace lo que parece:

```bash
docker run -it -v /var/run/docker.sock:/var/run/docker.sock docker:cli sh
```

Adentro hay un CLI de Docker que funciona perfecto. Pero ya sabes de [[anatomia-de-docker-run|la anatomía de `docker run`]] que **el CLI no corre nada**: le manda una petición por ese socket a un daemon. Y el daemon que hay al otro lado de ese socket es **el del host**.

Así que los contenedores que crees desde adentro no nacen dentro de nada: nacen **al lado**, en el host, como hermanos del tuyo. No hay segundo nivel, no hay aislamiento nuevo, y no hace falta `--privileged` — lo cual lo vuelve más peligroso, no menos, porque parece barato. Quien escribe en ese socket le da órdenes a un proceso que es `root` en tu máquina.

### 3 · Podman anidado

Podman sí puede correr dentro de Podman, y es su argumento favorito: sin daemon, el problema deja de ser «cómo meto un servicio privilegiado adentro» y pasa a ser «cómo le doy almacenamiento a un proceso mío». La imagen es `quay.io/podman/stable`.

La versión limpia —rootless dentro de rootless— es posible y tiene requisitos propios: un volumen de verdad para el almacén de adentro, `--device /dev/fuse` para que `fuse-overlayfs` funcione, y el usuario `podman` de la imagen en vez de `root`. **Los números de abajo no midieron esa versión**: midieron la privilegiada, que es la que sale en un renglón y la que se teclea en «Con las manos». Dicho para que nadie cite la cifra como si fuera la del camino recomendado.

::: table {#cont-anexoc-tres-formas title="Las tres maneras, y qué entrega cada una"}

| | Docker dentro de Docker | El socket montado | Podman anidado |
|---|---|---|---|
| ¿Anida? | **sí**: hay un segundo daemon | **no**: son hermanos en el host | **sí**: hay un segundo almacén y un segundo supervisor |
| Quién ejecuta el contenedor nuevo | el daemon de adentro | el daemon **del host** | tu proceso `podman` de adentro |
| Qué hay que entregar | `--privileged` | el socket, que **es** `root` en el host | un volumen y `/dev/fuse`; `--privileged` sólo en el atajo |
| Qué lista un `ps` de adentro | sólo lo suyo | **los contenedores del host**, incluido el tuyo | sólo lo suyo |
| Contra qué disco resuelve un `-v` | el de adentro | **el del host** | el de adentro |
| Qué sobrevive al contenedor de afuera | nada | **todo**: los hermanos siguen corriendo | nada |
| Para qué sirve de verdad | aislar un `build` en una máquina desechable | reusar la caché de capas del host, a cambio del host | lo mismo que DinD, sin daemon privilegiado |

:::

La fila del `-v` es la que muerde en la vida real y casi nadie la predice. Cuando escribes `-v ./datos:/datos` **dentro** del contenedor con el socket montado, quien interpreta `./datos` es el daemon del host, que no tiene ni idea de qué hay dentro de tu contenedor: monta **la ruta del host**. Si no existe, la inventa vacía —exactamente lo de [[rutas-en-docker]]—, y tu trabajo corre sobre un directorio que no es el que creías.

## La cuarta manera: no anidar nada

Las tres de arriba contestan la misma pregunta —cómo meto un daemon, o un almacén, dentro de un contenedor—, y por eso las tres cobran algo. Pero antes de contestarla conviene comprobar que haga falta, porque el trabajo que de verdad manda a anidar en integración continua casi siempre es uno solo: **construir una imagen**. Y para construir no hace falta ningún daemon, ni el de adentro ni el de afuera. Un `Dockerfile` es una receta, y ejecutarla es desempacar capas, correr comandos y volver a empacar: eso lo hace un programa normal, sin `--privileged` y sin socket.

**Buildah** es el que está vivo, y además ya lo tienes instalado sin saberlo: **`podman build` *es* Buildah**, usado como librería. Construye imágenes OCI sin daemon y, con el rootless que montaste en la sesión 2, sin privilegios. **Kaniko** es el otro nombre que vas a encontrar, y hay que saber leerlo más que usarlo: fue durante años la forma estándar de construir dentro de un clúster de Kubernetes, así que aparece en miles de `.gitlab-ci.yml` heredados. **Google archivó el repositorio el 3 de junio de 2025**; lo que queda son forks de terceros. Si lo heredas, funciona; si lo eliges hoy, estás eligiendo un proyecto archivado.

Lo que esta familia compra es justo la columna que más duele de la tabla de arriba: **no entrega nada**. Lo que no compra es ejecutar — construir no es correr, y un pipeline que además tiene que levantar una base de datos de prueba vuelve a tener el problema de las tres maneras.

## Con las manos

**Haz:** monta el socket y pregúntale a ese CLI qué contenedores ve.

```bash
docker run -d --name testigo alpine:3.20 sleep 300
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  docker:cli docker ps --format '{{.Names}}'
```

**Deberías ver:** `testigo` en la lista, y con él todo lo que tengas corriendo en tu máquina. El contenedor de adentro está mirando **tu** daemon. Si hubieras corrido `docker rm -f testigo` desde ahí, se habría borrado de verdad.

**Haz:** ahora el mismo montaje, pero pidiéndole que monte una ruta.

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  docker:cli sh -c 'mkdir -p /solo-aqui && touch /solo-aqui/marca &&
    docker run --rm -v /solo-aqui:/x alpine:3.20 ls -A /x'
```

**Deberías ver:** `ls -A /x` **sin imprimir nada**, y un directorio `/solo-aqui` recién creado **en el disco de tu host**, que tú no hiciste. `marca` existe, pero existe dentro del contenedor intermedio, y el daemon del host nunca lo vio.

**Haz:** y ahora sí, un anidamiento de verdad. Este bloque tarda: el daemon de adentro necesita unos segundos para levantar.

```bash
docker run -d --privileged --name dind docker:dind
until docker exec dind docker info > /dev/null 2>&1; do sleep 1; done
docker exec dind docker ps -a
docker exec dind docker images
docker rm -f dind testigo
```

**Deberías ver:** las dos listas **vacías**. Ni tu `testigo` ni ninguna de las seis imágenes del prepull: ese daemon nació sin nada y su almacén no es el tuyo. Ésa es la diferencia entre anidar y tener hermanos, en dos comandos.

**Haz:** lo mismo con Podman, que es donde el anidamiento tiene su mejor argumento. Éste es el atajo privilegiado —el que midió la gráfica de abajo—, no el camino limpio de la sección 3.

```bash
podman run -d --privileged --name podman-nest quay.io/podman/stable sleep 600
podman exec podman-nest podman images
podman exec podman-nest podman run --rm alpine:3.20 echo "hola desde el nivel 2"
```

**Deberías ver:** la lista de imágenes **vacía** —sólo el encabezado—, aunque en tu host `alpine:3.20` esté bajada desde hace rato; y después el `podman run` **volviéndola a bajar**, con su `Trying to pull docker.io/library/alpine:3.20...`, antes de imprimir el saludo. Ahí está en dos renglones el «segundo almacén» de la tabla: sin daemon, el problema no es meter un servicio privilegiado adentro, es que hay un almacén nuevo y está vacío.

**Haz:** el tercer nivel. Un Podman, dentro de un Podman, dentro del tuyo.

```bash
podman exec podman-nest podman run --privileged --rm quay.io/podman/stable \
  podman run --rm alpine:3.20 echo "nivel 3"
podman rm -f podman-nest
```

**Deberías ver:** que **funciona** —imprime `nivel 3`—, y que antes de imprimirlo baja **dos** imágenes más: `quay.io/podman/stable` en el almacén del nivel 2 y `alpine:3.20` en el del nivel 3. No hay un tope arquitectónico: el anidamiento tiene fondo, y lo que se multiplica por nivel no es lo que mide la gráfica de abajo, es el almacén. Fíjate además en lo que le pasa al nivel 3, que corre con `--rm`: **su caché nunca se calienta**, porque muere con él. Cada corrida vuelve a bajarlo todo, y por eso el tercer nivel se siente lento aunque el arranque no lo explique.

![Un módulo de carga abierto de par en par en un muelle nocturno, en violeta eléctrico y ámbar de sodio: dentro no hay mercancía sino otro patio de maniobras completo, con su propia grúa y sus propios módulos más pequeños, y uno de ésos está abierto y contiene otro patio más, así hacia dentro hasta perderse en un túnel de repeticiones. Una figura de espaldas, en silueta contra la boca del módulo, alumbra con una linterna cuyo haz se apaga antes de llegar al fondo.](_assets/ilus-contenedores-anidados.jpg)

## Qué cuesta, medido

::: figure {#cont-anexoc-bench title="Anidar: qué cuesta un contenedor dentro de otro"}
![Dos paneles del experimento 4, con los mismos cinco métodos en el mismo orden: a pelo, docker, Docker dentro de Docker, podman y Podman anidado. Arriba, la mediana del arranque en milisegundos en escala logarítmica: 1.3, 315, 340, 166 y 241. Abajo, el tiempo de CPU del mismo trabajo en segundos: 0.47, 0.54, 0.58, 0.56 y 0.70. El par de paneles es el mensaje: anidar cuesta poco en cómputo y bastante en arranque. Dos anotaciones dan los incrementos: Docker dentro de Docker suma 25 milisegundos de arranque sobre docker, un 8 por ciento, y 0.045 segundos de CPU, otro 8 por ciento; Podman anidado suma 75 milisegundos sobre podman, un 45 por ciento, y 0.134 segundos de CPU, un 24 por ciento. Al pie, la máquina, el kernel y las versiones de los dos runtimes](_assets/cont-bench-anidado.svg)
:::

> Estos números son de la **tanda 1** de la unidad, cuyo pie completo —máquina, kernel y versiones— vive una sola vez, en [[lo-que-cuesta]]. Con una salvedad que aquel pie no cubre y que hay que decir aquí: **este experimento tiene cuatro repeticiones, no diez.** El CSV publicado, `_assets/benchmarks/results/exp4_nested.csv`, las trae contadas.

Los dos paneles miden cosas distintas a propósito, y por eso están juntos.

**El arranque sube, y bastante.** Docker dentro de Docker pasa de 315 ms a **340 ms**: veinticinco milisegundos, un 8 %. Podman anidado pasa de 166 ms a **241 ms**: setenta y cinco milisegundos, un **45 %**. Ese porcentaje grande es engañoso si se lee solo — es grande porque el número de partida es chico. En milisegundos absolutos, el contenedor anidado de Podman sigue arrancando **casi cien milisegundos antes** que un Docker no anidado.

**El cómputo casi no sube.** El mismo trabajo —generar 50 MiB y sacarles `sha256sum`— tarda 0.54 s en Docker y 0.58 s en DinD; 0.56 s en Podman y 0.70 s en Podman anidado. Y esto era predecible desde la sección 1: la `syscall` de tu proceso va **directo al kernel del host** aunque haya tres supervisores encima, porque ninguno de ellos está en el camino de los datos. Lo que se paga al anidar no es ejecutar: es **crear**.

Dos honestidades sobre la medición, porque esta unidad no publica un número sin ellas. La primera: el panel de CPU usa `exec` sobre contenedores **ya arrancados**, así que excluye el arranque a propósito — si no lo hiciera, estaría midiendo las dos cosas a la vez y atribuyéndoselas al cómputo. La segunda: el margen que queda en ese panel incluye el propio `docker exec` de cada nivel, que el experimento nunca aisló; con dos niveles son dos `exec`, y parte del 8 % es eso.

De ahí sale la única regla de diseño que estos números sostienen: **anidar no encarece el trabajo, encarece el número de arranques.** Es exactamente la conclusión de [[lo-que-cuesta]], cobrada un nivel más adentro.

## Entonces, ¿cuándo?

**Sí, en una máquina desechable que no es tuya.** Un servidor de integración continua levanta una máquina virtual limpia por trabajo, corre el `build` adentro y la destruye. Entregarle `--privileged` a esa máquina cuesta poco porque no hay nada ahí que perder: ni tus llaves, ni tu navegador, ni el resto del curso. Es la misma lógica de [[vm-contra-contenedor|el caso 2 de VM contra contenedor]] — el aislamiento fuerte lo pone la máquina, no el contenedor.

**No, en tu laptop.** Ahí sí hay algo que perder, y las dos banderas de esta página son la puerta grande. Si necesitas construir una imagen en tu máquina, constrúyela en tu máquina: no hay nada que anidar.

**Y el socket montado, casi nunca.** Se usa cuando lo que quieres es justamente **reusar la caché de capas del host** para no reconstruir todo desde cero, que es una ganancia real. El precio también es real y no se negocia: quien entre a ese contenedor tiene `root` en la máquina que lo corre. Si el contenedor ejecuta código que no escribiste tú, ya perdiste.

::: problem {#cont-anexoc-cuatro-partes title="Cuatro predicciones sobre anidar"}
Las cuatro se contestan con la tabla de arriba y con los números de la gráfica. **Escríbelas antes de correr nada.**

**1.** Tienes un contenedor corriendo llamado `testigo`. Arrancas otros dos: uno con el socket montado, otro con `docker:dind` y `--privileged`. Desde dentro de cada uno corres `docker ps`. ¿Qué imprime cada uno, y por qué son distintos?

**2.** Dentro del contenedor con el socket montado creas `/solo-aqui/marca` y después corres `docker run --rm -v /solo-aqui:/x alpine:3.20 ls -A /x`. ¿Qué imprime, y **dónde acabó de existir** el directorio `/solo-aqui`?

**3.** Un trabajo de integración continua arranca **40 contenedores cortos**. ¿Cuánto suma el arranque si corre sin anidar con Docker, y cuánto si corre anidado en DinD? Contesta también qué fracción del trabajo total representa esa diferencia si cada contenedor trabaja 3 segundos.

**4.** De las tres maneras, ¿cuál elegirías para el servidor que construye este curso, y qué le estás entregando exactamente al elegirla? Nombra lo que entregas, no lo que ganas.
:::

::: hint {of="cont-anexoc-cuatro-partes"}
Para la 1 y la 2, la pregunta es siempre la misma: **¿qué daemon recibe la petición?** Dibuja la flecha desde el CLI que teclea hasta el proceso que ejecuta, y las dos respuestas salen solas.

Para la 3, multiplica antes de opinar, y acuérdate de que el costo de anidar se paga **por arranque**, no por segundo de trabajo.
:::

::: answer {of="cont-anexoc-cuatro-partes"}
**1.** El del **socket montado** imprime `testigo`, y todo lo demás que tengas corriendo en el host — incluido él mismo. El de **DinD** imprime una lista **vacía**. La razón es una sola: el primero le manda su petición al daemon del host por el socket que tú le montaste, así que está mirando tu máquina; el segundo le habla a un daemon nuevo que nació dentro del contenedor, con su propio almacén y sin ningún contenedor que listar. **El primero no anidó nada.**

**2.** Imprime **nada**: `/x` está vacío. Y el directorio `/solo-aqui` acabó existiendo **en el disco del host**, creado vacío por el daemon, porque el `-v` lo resolvió el daemon del host y ahí esa ruta no existía. Tu `marca` sigue dentro del contenedor intermedio, invisible para todos. Es el mismo mecanismo de [[rutas-en-docker]] —con `-v`, si el origen no existe, Docker lo inventa— cobrado en el peor sitio posible: **el contenedor que pidió el montaje no es el que lo recibe**.

**3.** Sin anidar, `40 × 315 ms` = **12.6 s**. Anidado en DinD, `40 × 340 ms` = **13.6 s**. La diferencia es **un segundo** sobre 40 contenedores. Si cada uno trabaja 3 s, el trabajo útil son 120 s, así que ese segundo es **menos del 1 %** del total. Ése es el punto: en un pipeline de integración continua el sobrecosto de anidar es ruido, y por eso nadie lo discute — lo que se discute es la otra columna, la de qué hay que entregar.

**4.** **Docker dentro de Docker**, y lo que le entregas es `--privileged`: todas las capabilities, sin seccomp, sin AppArmor y con los dispositivos del host a la vista. Eso es aceptable **sólo** porque la máquina que corre el trabajo es efímera, ajena y desechable — nace para el `build` y se destruye después. Si esa misma decisión se toma sobre tu laptop, lo que entregaste es tu laptop.

Y la que **no** elegirías es el socket montado, aunque sea la más barata de escribir y la que reusa la caché: ahí no hay una máquina desechable en medio. Ahí lo que entregas es el host, directo, y sin que aparezca la palabra `--privileged` en ninguna parte.
:::

> [!NOTE]
> **Si sólo recuerdas una cosa:** montar el socket no anida nada — hace hermanos en el host; anidar de verdad cuesta poco en cómputo, algo en arranque, y `--privileged`.
