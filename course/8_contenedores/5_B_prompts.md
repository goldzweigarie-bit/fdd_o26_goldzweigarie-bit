---
id: prompts-contenedores
title: "Nueve prompts"
nav_title: "Prompts"
summary: "Nueve preguntas para hacerle a un modelo de lenguaje cuando esta unidad se acabe, seis cosas que te va a contestar mal, y dónde está la documentación que gana la discusión."
status: ready
estimated_time: 12m
tags: [prompts, llm, diagnostico, docker, podman, kata, referencia]
prerequisites: [contenedores]
---

# Nueve prompts

**Anexo B** · para consultar, no para memorizar

Un modelo de lenguaje es la herramienta correcta para la mitad de lo que te falta de esta unidad, y la equivocada para la otra mitad. Es buenísimo traduciendo un error a una causa, desarmando una línea de comando que no escribiste tú, y proponiendo tres opciones cuando no sabes ni cómo se llama lo que buscas. Es malísimo cuando la respuesta correcta es un número medido o una versión concreta, porque ahí contesta con la misma seguridad y sin haber medido nada.

De la unidad 4 te llevaste el movimiento general: **no preguntes el dato, pregunta cómo obtener el dato.** Aquí se le agrega uno propio de esta unidad, porque aquí sí tienes con qué: **pega la salida, no la describas.** «Me falla el volumen» no se puede contestar; `docker volume ls` junto con el `docker run` que corriste, sí.

## Seis cosas que te va a contestar mal

No son hipótesis: son las seis afirmaciones que esta unidad desarmó una por una, y las seis circulan lo suficiente como para que un modelo las repita sin dudar. Si te dice cualquiera de éstas, la página de la derecha es la que gana.

::: table {#cont-anexob-falsos title="Lo que circula, lo que se midió, y dónde"}

| Lo que te va a decir | Lo que de verdad pasa | Dónde se desarma |
|---|---|---|
| «Podman arranca al doble de velocidad porque no tiene daemon» | lo que compra la mitad del tiempo es `crun`; con el runtime igualado Podman sale **~3 % detrás** | [[docker-y-podman]] |
| «Usa `alpine` para que el contenedor arranque más rápido» | arrancar **no descomprime** la imagen: la diferencia es medio punto porcentual | [[lo-que-cuesta]] |
| «El named volume tapa y el bind mount copia» | exactamente al revés: el bind mount **nunca** copia, el named volume vacío copia **una** vez | [[las-cuatro-trampas]] |
| «Si te da `permission denied`, haz `chmod 666` al socket de Docker» | eso le abre `root` a cualquier proceso de tu máquina, incluido lo que ejecute el navegador | [[instalar-docker-y-podman]] |
| «`runc` monta el rootfs y crea el cgroup» | el rootfs lo monta `dockerd` con `overlay2`, y el cgroup lo crea **systemd** por D-Bus | [[anatomia-de-docker-run]] |
| «Matar el daemon mata los contenedores» | matarlo **no los toca**; reiniciarlo **sí los mata**, porque `live-restore` viene en `false` | [[anatomia-de-docker-run]] |

:::

Las seis tienen la misma forma, y por eso vale la pena verlas juntas: **son explicaciones plausibles de hechos reales**. El número de Podman existe, `alpine` sí es más chica, el socket sí se arregla con ese `chmod`. Lo que está mal es el mecanismo, y el mecanismo es justo lo que un modelo interpola cuando no lo tiene medido.

## Los nueve prompts

Están escritos para copiarse y rellenarse. Los corchetes son tuyos: si no los sustituyes, la respuesta va a ser genérica y no te va a servir.

### 1 · La instalación que no salió

Éste es el primero porque es el que más urge, y porque ya tienes exactamente lo que necesita: la salida de los seis comandos de la comprobación.

> **Prompt:** «Estoy instalando Docker y Podman para un curso. Mi sistema es `[distribución y versión, o macOS/Windows con WSL2]`. Corrí estos seis comandos y ésta es la salida completa, pegada tal cual: `[whoami, id -u, type -a docker, docker context ls, docker version, docker run --rm hello-world]`. Dime, leyendo **esa** salida y no lo que suele pasar: en qué punto exacto se rompe la cadena, cuál es la causa más probable y cuál la segunda más probable, y qué comando corro para distinguir entre las dos. No me des el arreglo todavía. Y dime qué parte de mi salida no puedes interpretar con certeza.»

La última frase es la que hace la diferencia. Un modelo te va a proponer un arreglo aunque no tenga cómo saber si aplica; pedirle que marque su incertidumbre te dice qué tienes que ir a comprobar tú.

### 2 · Desarmar una línea que no escribiste

Vas a encontrarte `docker run` de ocho banderas en un README, en un tutorial o en la respuesta anterior del propio modelo. Ninguna de las dos cosas que hay que saber de esa línea —qué hace y qué te está pidiendo que le entregues— se ve leyéndola rápido.

> **Prompt:** «Explícame esta línea bandera por bandera, antes de que la corra: `[pega el comando]`. Para cada bandera quiero tres cosas: qué hace, qué pasaría si la quito, y si amplía lo que ese contenedor puede ver o hacer sobre mi máquina. Al final, ordena las banderas de más a menos peligrosa y dime cuál de ellas no le hace falta para el objetivo que persigue el comando.»

### 3 · Auditar un Dockerfile ajeno

> **Prompt:** «Éste es un `Dockerfile` que voy a usar: `[pégalo completo]`. Revísalo en este orden y sin proponerme un reescrito todavía: 1) ¿la imagen base está fijada a una versión concreta o a una etiqueta que se mueve? 2) ¿el orden de las instrucciones tira el caché de instalación cada vez que cambio una línea de código, y en qué instrucción exacta empieza el dominó? 3) ¿el proceso acaba corriendo como `root`? 4) ¿hay algo que se borra en una capa posterior creyendo que adelgaza la imagen? Para cada punto dime **con qué comando lo compruebo yo**, no sólo si está bien o mal. Después, y sólo después, escríbeme la versión corregida.»

### 4 · Dónde va a vivir este byte

La pregunta que ordena toda la sección 2, hecha sobre un caso que el curso no te dio.

> **Prompt:** «Tengo `[describe el programa: qué escribe, dónde, cada cuánto y qué pasa si se pierde]`, que quiero correr en un contenedor. Para cada cosa que ese programa escribe, dime en cuál de los cuatro lugares debería vivir —capas de la imagen, capa de escritura del contenedor, bind mount o named volume—, qué comando lo borra, y si sobrevive a un `docker rm`. Justifica cada elección con **qué se pierde** si me equivoco, no con una buena práctica. Y dime cuál de las cuatro respuestas cambiaría si mañana corriera tres copias del mismo contenedor a la vez.»

### 5 · El contrato de tres renglones

> **Prompt:** «Quiero partir `[describe tu sistema en cinco líneas]` en contenedores. Antes de darme ningún `docker run`: propón la partición en servicios y, para **cada** servicio, escribe su contrato en tres renglones —qué puerto escucha, qué variables de entorno espera y qué volumen necesita—. Después dime cuáles de esos servicios **no** conviene separar y por qué, contando el costo en red, en despliegue y en depuración. Si crees que la respuesta correcta es no partir nada, dilo.»

### 6 · Leer un benchmark ajeno

> **Prompt:** «Encontré este benchmark que compara `[A]` contra `[B]`: `[pega la tabla, la gráfica descrita o el script]`. No me digas si el resultado es creíble. Dime primero, y por separado para cada lado: **qué se midió exactamente** —qué procesos entraron en la cuenta y cuáles no—, qué versiones de las herramientas medidas se declaran y cuáles faltan, y si la métrica que están sumando es aditiva. Después señala cualquier resultado que sea imposible aunque parezca menor, y explícame qué invalida: ese renglón o la tabla entera.»

La lista de preguntas de ese prompt no es genérica: es, una por una, la de los dos errores que [[lo-que-cuesta]] y [[docker-y-podman]] encontraron en sus propias mediciones.

### 7 · Traducir a Podman, incluido lo que no traduce

> **Prompt:** «Tengo esta secuencia de comandos de Docker: `[pégala]`. Tradúcela a Podman rootless en una tabla de dos columnas. En una tercera columna marca cada línea como *idéntica*, *cambia la sintaxis* o **no tiene equivalente directo**, y para las de la tercera categoría explícame qué diferencia arquitectónica lo causa —daemon, mapeo de usuarios, dónde vive el almacén de imágenes— y qué hago en su lugar. Incluye qué cambia en el dueño de los archivos que el contenedor escriba en una carpeta mía.»

### 8 · Lo que sigue cuando el kernel compartido no alcanza

> **Prompt:** «Tengo que correr `[describe el código y de quién viene]` y no confío en él. Compárame cuatro opciones —contenedor normal, contenedor rootless con `--cap-drop ALL`, gVisor y Kata Containers— contestando dos preguntas **por separado** para cada una: dónde aterriza una `syscall` que ese código haga, y con qué privilegio saldría quien se escape. No las ordenes de menos a más seguro, porque son dos preguntas distintas. Dime además qué necesita cada opción de mi máquina para siquiera arrancar, y cuáles no existen en mi sistema operativo, que es `[el tuyo]`.»

### 9 · El pipeline que construye imágenes dentro de un contenedor

El caso del [[contenedores-anidados|anexo C]], hecho sobre tu sistema y no sobre el ejemplo del curso.

> **Prompt:** «Tengo un trabajo de integración continua que corre **dentro** de un contenedor y que necesita dos cosas distintas: construir la imagen de mi aplicación y levantar contenedores de prueba `[los que sean: Postgres, Redis, …]`. Mi runtime es `[Docker / Podman]` y mi CI es `[GitHub Actions / GitLab CI / Jenkins / otro]`. Antes de escribirme ninguna configuración: compárame las cuatro opciones —Docker dentro de Docker, montar el socket del host, Podman anidado y construir sin daemon con Buildah— y para cada una dime **qué le estoy entregando exactamente a lo que corra ahí adentro**, no qué gano. Dime también cuál de mis dos necesidades cubre cada una, porque construir no es ejecutar. Sólo después escribe la configuración del runner para la que elijas, señala **qué línea concede el privilegio** y dime qué tendría que ser cierto de la máquina que corre el trabajo para que esa concesión sea aceptable. Si alguna de las cuatro no aplica a mi CI, dilo en vez de adaptarla.»

Fíjate en lo que este prompt **no** pide: una estimación del sobrecosto. Si se la pides, te la va a dar, y no tiene de dónde sacarla. Ese número se mide —el anexo C dice con qué y con cuántas repeticiones— o no se publica.

## La documentación que gana la discusión

Cuando el modelo y la documentación oficial no coinciden, no hay empate: gana la documentación. Éstos son los enlaces que conviene tener a mano, y que valen como fuente cuando algo de esta unidad se te quede corto.

::: table {#cont-anexob-oficiales title="Docker, Podman y Kata: la fuente de cada cosa"}

| Proyecto | Qué contesta | Enlace |
|---|---|---|
| Docker | referencia del CLI, comando por comando | [docs.docker.com/reference/cli/docker](https://docs.docker.com/reference/cli/docker/) |
| Docker | referencia del `Dockerfile`, instrucción por instrucción | [docs.docker.com/reference/dockerfile](https://docs.docker.com/reference/dockerfile/) |
| Docker | buenas prácticas de construcción, incluido el orden de las capas | [docs.docker.com/build/building/best-practices](https://docs.docker.com/build/building/best-practices/) |
| Docker | almacenamiento: capa de escritura, bind mounts y volúmenes | [docs.docker.com/engine/storage](https://docs.docker.com/engine/storage/) |
| Docker | redes: cómo se hablan dos contenedores y qué publica `-p` | [docs.docker.com/engine/network](https://docs.docker.com/engine/network/) |
| Docker | instalar Docker Engine, por distribución | [docs.docker.com/engine/install](https://docs.docker.com/engine/install/) |
| Podman | documentación completa y páginas de manual | [docs.podman.io/en/latest](https://docs.podman.io/en/latest/) |
| Podman | instalación en las tres plataformas | [podman.io/docs/installation](https://podman.io/docs/installation) |
| Podman | el tutorial de rootless, con `subuid`, `subgid` y `newuidmap` | [github.com/containers/podman/blob/main/docs/tutor…](https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md) |
| Podman | `podman machine`, que es lo que hace falta en macOS y Windows | [docs.podman.io/en/latest/markdown/podman-machine.…](https://docs.podman.io/en/latest/markdown/podman-machine.1.html) |
| Kata | qué es y para qué sirve un segundo kernel por sandbox | [katacontainers.io](https://katacontainers.io/) |
| Kata | documentación y requisitos de instalación, incluido `/dev/kvm` | [github.com/kata-containers/kata-containers/tree/m…](https://github.com/kata-containers/kata-containers/tree/main/docs) |

:::

Una advertencia sobre las dos últimas: **Kata es un runtime de Linux y no hay binarios para macOS.** Si un modelo te explica cómo instalarlo en tu MacBook, está inventando. Por qué no se puede, y qué sí hay en ese hueco, es [[kata-y-el-espectro|la última página de la unidad]].

> [!NOTE]
> **Si sólo recuerdas una cosa:** pega la salida en vez de describirla, y pídele siempre que marque lo que no puede saber — esa lista es tu tarea, no la suya.
