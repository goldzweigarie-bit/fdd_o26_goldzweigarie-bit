---
id: cuando-se-rompe-el-aislamiento
title: "Cuando se rompe el aislamiento"
nav_title: "Cuando se rompe el aislamiento"
summary: "Las fugas reales de contenedor, con su año y su cierre, y por qué casi todas fueron una decisión de configuración y no un bug."
status: ready
estimated_time: 15m
tags: [seguridad, aislamiento, seccomp, apparmor, capabilities, privileged, cve, rootless]
prerequisites: [disenar-un-sistema]
---

# Cuando se rompe el aislamiento

**Página 4 de 5 · sección 3 de 3**

Meta: entender que la mayoría de los escapes no son bugs, son decisiones.

::: figure {#cont-superficie-ataque title="Las capas que ya traes puestas, y las banderas que abren un boquete en cada una"}
![El contenedor rodeado de sus capas de defensa por omisión —seccomp, AppArmor, capabilities recortadas y usuario no root— y, atravesándolas, las decisiones que abren un agujero en cada una, dibujadas como brechas rotuladas: --privileged, --security-opt seccomp=unconfined, --cap-add SYS_ADMIN y el socket de Docker montado, que no es un exploit sino entregar el host. Dos casos marcados sostienen la tesis: CVE-2022-0492 funcionaba sin privilegios y aun así la configuración por defecto lo tapaba, y Dirty Pipe atraviesa todas las capas porque usa splice y write, que todo contenedor necesita](../_assets/cont-superficie-ataque.svg)
:::

## En corto

- Un contenedor **por omisión** ya trae tres capas puestas —capabilities recortadas, seccomp y AppArmor— y una cuarta que depende de la imagen: correr como un usuario que no sea `root`. Casi todos los escapes famosos empiezan por quitar una.
- **La mayoría no son bugs, son decisiones**: `--privileged`, el socket de Docker montado, una imagen que nadie miró.
- Y hay una excepción que conviene saber: cuando el agujero está en el **kernel**, ninguna de las cuatro capas te salva, porque el kernel es de todos.

## Lo que ya traes puesto

Antes de hablar de cómo se rompe, mira qué hay que romper. Nada de esto se pide: viene por omisión.

**Haz:**

```bash
docker run --rm alpine:3.20 grep -E 'CapEff|CapBnd' /proc/self/status
docker run --rm --cap-drop ALL alpine:3.20 grep CapEff /proc/self/status
```

**Deberías ver:** primero `00000000a80425fb`, y después `0000000000000000`. Ese número es una **máscara de bits**: cada bit encendido es un permiso de superusuario que el proceso conserva. El `root` de adentro no es el `root` completo del host — arranca ya con la mayoría de los bits apagados, y `--cap-drop ALL` apaga los que quedaban.

Las otras dos capas no se ven en un número, pero están: un perfil de **seccomp** que filtra qué `syscall` puede pedirle el proceso al kernel —de las [[anatomia-de-docker-run|syscalls]] de la sesión 1— y un perfil de **AppArmor** (o SELinux, según tu distribución) que restringe qué archivos y qué operaciones toca.

Ésas son tres. **La cuarta no es gratis y por eso va aparte: quién eres adentro.** El `root` recortado de arriba sigue siendo `root`, y la imagen puede pedir otra cosa con un `USER` en su `Dockerfile` —el mismo de [[el-dockerfile-por-dentro|la página 3 de la sección 2]]—. Es la única de las cuatro que depende de quien construyó la imagen y no de tu `docker run`, y la que decide **con qué privilegio sale quien se escape**, que es el segundo eje de [[kata-y-el-espectro|la página que sigue]].

Y una que **no** es una capa aunque se le parezca: el **cgroup**. Un cgroup mide cuánto puede usar el proceso, no qué puede alcanzar; contra un escape no defiende nada. En esta página aparece del otro lado, como **vector**: el `release_agent` de las dos filas de cgroups v1 de la tabla de abajo es exactamente un cgroup usado para ejecutar algo en el host.

## Quitar una capa se ve así

`--privileged` es la bandera que más aparece en las respuestas de internet, y lo que hace se puede mirar sin romper nada.

**Haz:**

```bash
docker run --rm alpine:3.20 sh -c 'ls /dev | wc -l'
docker run --rm --privileged alpine:3.20 sh -c 'ls /dev | wc -l'
```

**Deberías ver:** **15** en el primero y unos **231** en el segundo — el número exacto depende de tu máquina, porque el segundo es la lista de dispositivos de tu hardware. Medido en **Docker 29.6.0 sobre Linux 6.17**.

Esos quince son un juego mínimo e inofensivo: `null`, `zero`, `random`, las tres salidas estándar. Los doscientos y pico incluyen **tus discos**. `--privileged` no es «un poco más de permisos»: devuelve todas las capabilities, apaga los perfiles de seccomp y AppArmor, y expone los dispositivos del host. Es, casi literalmente, un proceso normal de tu máquina con el nombre puesto de contenedor.

## La prueba de que la configuración por omisión sí trabaja

**Haz:**

```bash
docker run --rm alpine:3.20 unshare -Ur id
docker run --rm --security-opt seccomp=unconfined alpine:3.20 unshare -Ur id
```

**Deberías ver:** el primero falla con `unshare: unshare(0x10000000): Operation not permitted`; el segundo imprime `uid=0(root) gid=0(root)`. El programa es el mismo y la imagen es la misma. Lo único que cambió fue el filtro de seccomp.

Guarda ese contraste, porque es la fila más importante de la tabla que sigue: **hubo un bug del kernel al que se llegaba con exactamente ese `unshare`, y la configuración por omisión de Docker lo tapaba sin que nadie hiciera nada.**

## Siete formas de que se rompa, con su año

::: table {#cont-s3p4-tabla-fugas title="Qué pasó, por qué se pudo, y cómo se cierra"}

| Qué pasó | Por qué se pudo | Cómo se cierra |
|---|---|---|
| **`runc`, CVE-2019-5736** (2019) | el binario del runtime era alcanzable desde dentro del contenedor, vía `/proc/self/exe`, y se podía sobrescribir | `runc` **sella** su propio binario antes de entrar: hoy con un overlay de sólo lectura, y con una copia en `memfd` como respaldo |
| **Leaky Vessels, CVE-2024-21626** (2024) | el directorio de trabajo del proceso podía quedar apuntando a `/proc/self/fd/N`, usando `WORKDIR`; afectaba a `runc` **1.0.0-rc93 – 1.1.11**, tanto en `build` como en `run` | **`runc` ≥ 1.1.12** y BuildKit ≥ 0.12.5. `USER` no lo mitiga, pero **estorba la sobrescritura**: es defensa en profundidad, no cierre |
| **`--privileged` con cgroups v1** (2019) | mala configuración de siempre: con las jerarquías v1 montadas, el archivo `release_agent` era escribible y el kernel ejecuta lo que ahí diga, **en el host** | nunca `--privileged`; y **sin jerarquías v1 montadas**, porque cgroups v2 no tiene `release_agent`. Nunca fue un bug: es comportamiento **intencional** |
| **CVE-2022-0492** (2022) | el kernel omitió comprobar `CAP_SYS_ADMIN` **en el user namespace inicial**, así que bastaba un `unshare -UrC` para llegar al mismo `release_agent`. **Sin privilegios de partida** | **ya estaba cerrado si no tocaste nada**: el seccomp por omisión bloquea `unshare` sin `CAP_SYS_ADMIN`, y AppArmor bloquea montar `cgroupfs`. Se abre con `--privileged`, con `seccomp=unconfined`, o en Kubernetes, donde los pods vienen sin seccomp |
| **Dirty Pipe, CVE-2022-0847** (2022) | usa `splice()` y `write()`, dos llamadas que **todo** contenedor necesita. Seccomp, AppArmor, capabilities y correr como no-root **no lo paran**. Introducido en Linux 5.8, corregido en 5.16.11, 5.15.25 y 5.10.102 | kernel al día, y si eso no alcanza, un segundo kernel: **Kata**. La sobrescritura vive en el **page cache**, así que el archivo en disco queda intacto y «se ve bien» no prueba nada — por eso derrota el sellado del primer renglón |
| **El socket de Docker montado** | no es un exploit: es entregar el host. Quien escribe en `/var/run/docker.sock` le pide al daemon —que es `root`— que monte el disco entero en un contenedor nuevo | no montarlo |
| **Imagen envenenada** | un nombre parecido al que buscabas, con un minero adentro. Nadie tuvo que romper nada | pinear por digest, escanear, y partir siempre de bases conocidas |

:::

Lee la columna del medio de corrido. **Cinco de las siete no son fallas del aislamiento: son configuraciones.** Las dos que sí son bugs se distinguen de todas las demás en una cosa: no había bandera que quitar, porque el agujero estaba en el runtime o en el kernel.

Y la fila de **CVE-2022-0492** es la que mejor sostiene la tesis de la página, por eso el `unshare` de arriba: el bug del kernel existía, era explotable sin privilegios, y **la configuración por omisión lo tapaba de todos modos**. Quien había copiado un `--privileged` de una respuesta de internet no estaba tapado.

![Un mamparo de acero remachado visto de frente y muy de cerca, en gris hierro y ceniza, ocupando casi todo el cuadro: una grieta finísima lo recorre de arriba abajo y por ella escapa una línea de luz roja incandescente que ilumina el vapor del aire. Todo lo demás está intacto y en orden; el fallo es del grosor de un cabello. Abajo a la izquierda, pequeña y de espaldas, una figura en silueta acaba de notarlo y ha detenido el paso.](../_assets/ilus-contenedores-fuga.jpg)

## Las seis defensas, en orden de cuánto pagas por ellas

::: table {#cont-s3p4-tabla-defensas title="Qué poner, qué compra, qué cuesta"}

| Defensa | Qué compra | Qué cuesta |
|---|---|---|
| **Correr rootless** (Podman) | que quien se escape sea un usuario sin privilegios, no `root` del host | algunas cosas no se pueden hacer; **no** añade ninguna frontera nueva — la página 5 explica por qué |
| **`--cap-drop ALL`** | apaga los bits que quedaban encendidos | si tu programa de verdad necesitaba uno, hay que devolverlo con `--cap-add` y decir cuál |
| **seccomp y AppArmor por omisión** | filtran syscalls y accesos; ya los traes | nada, **mientras no escribas `unconfined`** |
| **`--read-only`** | el sistema de archivos del contenedor no se puede modificar | hay que montar explícitamente lo que sí se escribe |
| **`USER` no-root en el Dockerfile** | el proceso no arranca como `root` ni siquiera adentro | los permisos de tus volúmenes tienen que cuadrar con ese uid, como el 999 de [[named-volumes-y-postgres|Postgres]] |
| **Pinear por digest** | `imagen@sha256:…` es un contenido exacto, no una etiqueta que alguien puede mover | hay que actualizarlo a mano cuando quieras la versión nueva |

:::

Fíjate en el tercer renglón: es la única defensa de la lista que **no cuesta nada, porque ya está puesta**. Lo único que hay que hacer es no quitarla.

## La frase de la instalación, cobrada

En [[instalar-docker-y-podman]] quedó dicho que meter tu usuario al grupo `docker` es darle privilegios de `root` sin que aparezca la palabra, y que nunca se hace `chmod 666 /var/run/docker.sock`. Ahora tienes el mecanismo completo: el CLI no corre nada, le manda una petición por ese socket a un daemon que es `root`, y **el daemon no pregunta quién eres**, sólo si pudiste escribir en el archivo.

Por eso el renglón del socket montado en la tabla no es una fuga de aislamiento: es el sistema funcionando como fue diseñado, usado por alguien que no lo necesitaba. Y por eso la contraparte de esa misma frase es el argumento de fondo de Podman *rootless*: si no hay un proceso privilegiado encendido, no hay a quién pedirle nada.

## Y sin embargo, en CI se hace justo lo que esta página prohíbe

Hay una contradicción honesta que vale la pena nombrar antes de que la encuentres tú: correr Docker **dentro** de Docker —que es lo que hace media industria en sus servidores de integración continua— suele exigir exactamente las banderas que acabas de aprender a no escribir. No es que ahí la regla no aplique; es que ahí se paga a conciencia, con la máquina aislada y desechable, y sabiendo qué se entregó. El anexo C de esta unidad, [[contenedores-anidados|*Contenedores anidados*]], lo desarma con sus números y con su precio; está escrito **después** de esta página a propósito, para que lo leas sabiendo qué se está entregando y no al revés.

Esta página no lleva ningún exploit funcional ni pasos para reproducir uno, y no es por timidez: los siete renglones de arriba se entienden por su mecanismo, y el mecanismo es lo que te deja **decidir**. Reproducirlos no agrega nada que sirva para diseñar.

::: problem {#cont-s3p4-cuatro-banderas title="Cuatro banderas peligrosas en una sola línea"}
Éste es un `docker run` real, de los que aparecen en respuestas de internet con muchos votos. **No lo corras**: léelo.

```bash
docker run -it --privileged \
  --security-opt seccomp=unconfined \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /:/host \
  alpine:3.20 sh
```

1. Señala **las cuatro** decisiones peligrosas y di, en una línea cada una, **qué habilita**. Dos de ellas se solapan: di cuál sobra si la otra está.
2. Ahora **corre** la versión reescrita. Crea antes la carpeta de datos:

```bash
mkdir -p ~/fdd/seguro && echo dato > ~/fdd/seguro/archivo.txt
docker run --rm --cap-drop ALL --security-opt no-new-privileges \
  -v ~/fdd/seguro:/datos:ro alpine:3.20 sh -c '
cat /datos/archivo.txt
ls /dev | wc -l
grep CapEff /proc/self/status
chown nobody /tmp || echo "chown: falló"
'
```

3. **Una cosa falla.** Di cuál, con qué error, y —la pregunta de verdad— **si eso rompe el trabajo que el contenedor tenía que hacer**.
:::

::: hint {of="cont-s3p4-cuatro-banderas"}
Para la 1, pregúntate por cada bandera: *¿qué capa de las cuatro por omisión está apagando, o qué cosa del host está metiendo adentro?* Dos apagan capas y dos meten cosas. Para la 3, compara lo que falló contra la primera línea de la salida: el contenedor tenía **un** trabajo.
:::

::: answer {of="cont-s3p4-cuatro-banderas"}
**1. Las cuatro:**

- **`--privileged`** — devuelve todas las capabilities, apaga seccomp y AppArmor, y expone los dispositivos del host. Es el renglón que abre, él solo, tres de las siete filas de la tabla.
- **`--security-opt seccomp=unconfined`** — quita el filtro de syscalls. **Ésta es la que sobra**: `--privileged` ya la desactiva. Que alguien escriba las dos es la señal de que copió sin leer.
- **`-v /var/run/docker.sock:/var/run/docker.sock`** — le entrega al contenedor el buzón de un daemon que corre como `root`. Desde adentro se puede pedir otro contenedor con el disco montado. No hay que romper nada.
- **`-v /:/host`** — monta **el sistema de archivos entero del host**, de escritura. Ni siquiera hace falta el socket: ahí están `/etc/shadow` y el directorio de todos los usuarios.

**2 y 3. Falla el `chown`**, con `chown: /tmp: Operation not permitted`, porque cambiar el dueño de un archivo requiere `CAP_CHOWN` y `--cap-drop ALL` lo apagó junto con todo lo demás. `CapEff` sale en `0000000000000000`, y `/dev` tiene quince entradas, las mínimas.

Y la respuesta que importa: **no, no rompe nada.** La primera línea de la salida imprime `dato`. El contenedor tenía que leer un archivo, y leerlo no necesita ninguna capability. El `chown` estaba ahí como sonda, no como trabajo.

Ése es el hábito que se lleva de esta página: **quita todo, corre, y devuelve con `--cap-add` sólo lo que el programa demuestre que necesita.** Casi siempre la respuesta es «nada», y cuando no lo es, por lo menos ya sabes qué le diste y por qué.

Dos avisos de honestidad sobre la misma corrida. Uno: `ping` **sí funciona** con `--cap-drop ALL`, aunque muchas guías digan que no — Docker configura el rango de grupos que pueden abrir sockets ICMP de datagrama, así que `ping` no necesita `CAP_NET_RAW`. Dos: nada de lo que hiciste aquí te protege de Dirty Pipe, porque ese agujero estaba en el kernel que compartes. Ésa es la puerta que abre la página siguiente.
:::

Sigue con [[kata-y-el-espectro]], que contesta la pregunta que quedó abierta desde [[vm-contra-contenedor|la sesión 1]]: qué haces cuando compartir el kernel no es aceptable.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor ya venía con cuatro capas puestas, y casi todos los escapes famosos empiezan con alguien quitando una a propósito.
