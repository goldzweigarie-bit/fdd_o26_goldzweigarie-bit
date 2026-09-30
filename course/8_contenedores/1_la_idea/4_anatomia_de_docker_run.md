---
id: anatomia-de-docker-run
title: "Qué pasa cuando escribes docker run"
nav_title: "La anatomía de docker run"
summary: "La cadena real —CLI, daemon, containerd, shim y runc—, quién hace cada cosa, y qué queda vivo cuando el contenedor ya corre."
status: ready
estimated_time: 12m
tags: [docker, dockerd, containerd, shim, runc, daemon, socket, systemd, cgroup]
prerequisites: [receta-imagen-contenedor]
---

# Qué pasa cuando escribes `docker run`

**Página 4 de 9 · sección 1 de 3**

Meta: que `docker run` deje de ser magia. Aquí se definen `daemon` y `socket`.

::: figure {#cont-anatomia-run title="La cadena real, y qué queda de ella cuando el contenedor ya corre"}
![Diagrama de la cadena completa de docker run. Arriba, cinco cajas en fila unidas por flechas: el CLI docker que tecleas, el daemon dockerd que corre como root, containerd que administra imágenes y tareas, containerd-shim-runc-v2 que es el supervisor del contenedor, y runc al final, dibujado en gris y con una marca de salida porque corre dos veces —en create y en start— y sale las dos. Sobre la primera flecha va rotulado el socket /var/run/docker.sock. El proceso del contenedor, un sleep 300 que es el PID 1 de adentro, cuelga del shim y no del daemon, y una flecha punteada sube del shim al PID 1 del host porque el shim se desacopla con un doble fork y queda reparentado a systemd. Al margen, dos correcciones: el rootfs ya está en disco desde el pull y lo monta dockerd con el graphdriver overlay2, y el cgroup lo crea systemd por D-Bus. Abajo, el árbol de procesos con el contenedor ya corriendo, donde ni dockerd ni containerd aparecen, y el orden real dentro de runc: primero el proceso, después el cgroup, al final los namespaces](../_assets/cont-anatomia-run.svg)
:::

## En corto

- `docker` no corre nada: le manda una petición por un socket a **`dockerd`**, que llama a **`containerd`**, que lanza **un shim por contenedor**, que llama a **`runc`**.
- **`runc` corre dos veces y sale las dos.** En estado estable no queda ningún `runc` en el árbol, y el proceso del contenedor cuelga **del shim**.
- Ni `runc` monta el rootfs ni `runc` crea el cgroup: lo primero es `dockerd` con `overlay2`, lo segundo es **systemd**.

::: definition {#cont-def-daemon title="`daemon` y `socket`"}
Un **`daemon`** es un programa que corre de fondo, sin terminal y sin nadie sentado enfrente, esperando a que alguien le pida trabajo. `dockerd` es uno: arranca con la máquina, corre como `root` y se queda encendido aunque tú no tengas ninguna terminal abierta.

Un **`socket`** es el buzón por el que dos procesos se hablan. El de Docker es un archivo en tu disco, `/var/run/docker.sock`: el CLI escribe ahí su petición y el daemon contesta por el mismo buzón. De ahí sale una consecuencia que se cobra en la sesión 3: **quien puede escribir en ese archivo manda sobre un proceso que es root**.
:::

## La cadena

```text
docker CLI  →  dockerd  →  containerd  →  containerd-shim-runc-v2  →  runc
```

::: table {#cont-tabla-cadena title="Quién hace qué en un `docker run`"}

| Pieza | Qué es | Qué hace |
|---|---|---|
| `docker` | el CLI que tecleas | traduce tu línea a una petición y la manda por `/var/run/docker.sock`. Después sólo espera |
| `dockerd` | el daemon, como `root` | resuelve la imagen, **monta el rootfs** con su graphdriver `overlay2`, arma la configuración y se la entrega a containerd |
| `containerd` | el gestor de imágenes y tareas | prepara el *bundle* y lanza **un shim por contenedor** |
| `containerd-shim-runc-v2` | el supervisor | llama a `runc` y **se queda**: sostiene la salida estándar y recoge el código de salida |
| `runc` | el runtime | crea el proceso, lo mete al cgroup, crea los namespaces — **y sale** |

:::

## Tres cosas que casi todo el material enseña mal

**1. El rootfs ya está en disco desde el `pull`.** Arrancar un contenedor **no descomprime la imagen**: cuando hiciste `docker pull` cada capa se desplegó en disco, y lo único que falta al arrancar es apilarlas.

Quien las apila —quien monta el `overlay`— es **`dockerd`** con su graphdriver `overlay2`, que es lo que vas a tener instalado, o el shim cuando se usa el *image store* de containerd. **Nunca `runc`**, que lo recibe ya montado. Qué es exactamente ese `overlay` es la sesión 2; aquí basta con saber quién lo monta y cuándo.

**2. El cgroup lo crea systemd, no `runc`.** Sobre cgroups v2 el *cgroup driver* por defecto es `systemd`, así que `runc` no escribe el árbol de cgroups a mano: le pide a systemd por D-Bus una **unidad `scope` transitoria**, y sólo después escribe los ajustes que systemd no expone.

> [!TIP]
> Se ve sin adivinar, con `systemctl list-units --type=scope`: la descripción de la unidad dice literalmente `libcontainer container <id>`.

**3. El orden es proceso → cgroup → namespaces.** Suena al revés y no lo es:

1. `runc` primero hace `fork` y `exec` de un `runc init`;
2. después **mete ese PID al cgroup** —el comentario del código dice que hay que hacerlo antes de sincronizar con el hijo, para que ningún hijo escape del cgroup—;
3. y **sólo entonces** se crean los namespaces.

**Si los namespaces fueran primero, un proceso podría nacer fuera de la cuota.**

## `runc` corre dos veces, y sale las dos

Una vez en `create` y otra en `start`. Las dos veces hace su trabajo y termina. Eso significa que **en un contenedor ya corriendo no hay ningún `runc` vivo**, y que el padre del proceso de adentro no es `runc` ni `dockerd`: es el shim, que a su vez se desacopló con un doble fork y quedó reparentado al `PID` 1 del host.

El árbol de procesos lo dice sin discusión:

```text
systemd
└─ containerd-shim-runc-v2
   └─ sleep 300
```

**Ni `dockerd` ni `containerd` aparecen ahí.** Y de eso salen dos cosas más:

- la cadena de Podman es `podman → conmon → crun/runc`, o sea que **se salta el daemon, no el runtime** — eso es la página 7;
- cuando quieras que el kernel tampoco sea compartido, la pieza que se sustituye es justamente la última, `runc`, por otra que arranca una VM ligera: **Kata**, en la sesión 3.

> [!WARNING]
> **Dos avisos para la demo en vivo.** `systemctl stop docker` **no apaga Docker**: `docker.socket` sigue escuchando y el siguiente `docker ps` reactiva el daemon — hay que parar los dos, `systemctl stop docker.socket docker.service`. Y parar `docker.service` **no para `containerd`**: la relación entre las dos unidades es `Wants=`, no una dependencia dura.

## Entonces, ¿queda algo de Docker en medio?

::: definition {#cont-def-syscall title="`syscall`"}
Una **`syscall`** (*system call*) es la única forma que tiene un programa de pedirle algo al kernel: abrir un archivo, reservar memoria, mandar un paquete por la red. Tu código no toca el disco ni la tarjeta de red — pide, y el kernel lo hace por él.
:::

**En el camino de ejecución, no.** Cuando tu programa pide memoria o abre un archivo, esa `syscall` va directo al kernel del host, sin pasar por `dockerd`, por `containerd` ni por `runc`. Ahí está la mitad de la tesis de la unidad — **ejecutar dentro de un contenedor no cuesta**.

**Pero decir «ya no hay nada de Docker en medio» a secas es falso: queda un supervisor.** El shim está ahí, sosteniendo la salida estándar de tu proceso para que `docker logs` tenga qué enseñarte y esperando su código de salida para que `docker ps -a` pueda decir `exited (0)`. **No está en el camino de los datos; está sosteniendo el contrato.**

::: problem {#cont-p4-la-cadena title="La cadena, de pie"}
**Caja de tiempo: 12 minutos.** Se hace de pie, y son seis voluntarios. Los cinco primeros reciben una hoja con su nombre y se forman en este orden, de izquierda a derecha:

```text
docker CLI    dockerd    containerd    shim    runc
```

El sexto recibe la hoja que dice `proceso del contenedor` y espera **sentado, detrás del shim**: todavía no existe.

Las dos reglas, antes de empezar:

1. **Sentarse es morirse.** Quien se sienta deja de existir, y ya no se vuelve a levantar.
2. **El proceso se sostiene de una sola mano.** Cuando el sexto voluntario se ponga de pie, apoya la mano en el hombro del shim — **sólo** en el del shim, de nadie más. Si el shim se sienta, la mano se queda sin hombro y el proceso se sienta con él. No hay que discutirlo: se ve.

**La predicción, también antes de empezar.** Apúntala ahora, antes de que nadie se mueva: de las cuatro sentadas que vienen —`runc`, `dockerd`, `containerd`, el shim—, ¿cuál crees que tira al proceso?

Entonces:

1. Se pasa un papelito que dice `corre ubuntu` por la cadena, de mano en mano, de izquierda a derecha.
2. Cuando le llega a `runc`, `runc` **se lo entrega al sexto voluntario**. Ésa es su señal de entrada: el proceso del contenedor se pone de pie y **apoya la mano en el hombro del shim**. Y entonces `runc` **se sienta**.
3. Ahora, uno por uno, se van sentando: primero `dockerd`, después `containerd`, y al final el shim.

Después de cada quien que se sienta, la pregunta para toda la sala es la misma: **¿el proceso sigue de pie?**
:::

::: hint {of="cont-p4-la-cadena"}
Mira otra vez el árbol de procesos de arriba y pregúntate de quién cuelga el proceso del contenedor. Lo que decide si el proceso cae no es quién arrancó la cadena, es **quién lo está sosteniendo ahora** — y la mano en el hombro ya te está señalando a quién.
:::

::: answer {of="cont-p4-la-cadena"}
| Se sienta | ¿El proceso sigue de pie? | Por qué |
|---|---|---|
| `runc` | **sí** | ya había salido: sentarse sólo hace visible lo que ya era cierto antes de empezar la ronda |
| `dockerd` | **sí** | un `kill -9` al daemon **no** mata a los contenedores: el daemon no los está sosteniendo |
| `containerd` | **sí** | por la misma razón |
| el shim | **NO** | es el único de los cuatro que lo sostiene |

**Sobre `runc`:** en la máquina real se ejecuta **dos veces** —una en `create` y otra en `start`— y termina las dos. La coreografía lo simplifica a una sola sentada porque lo que el ejercicio pregunta es qué queda vivo cuando el contenedor ya corre, y ahí la respuesta es la misma con una salida que con dos: **ningún `runc`**.

**Sobre el shim:** cuando cae, el proceso no se cae solo. containerd detecta que el shim murió y corre `cleanupAfterDeadShim`, que acaba en un `runc delete --force`.

**Y la cuarta pieza, la que el ejercicio no puede actuar: el daemon que vuelve.** Los contenedores sobrevivieron al `kill -9` de `dockerd`, pero **no sobreviven a que `dockerd` regrese**. Con el valor por defecto `live-restore: false`, al arrancar el daemon recorre lo que quedó vivo y lo **mata**:

| Qué haces | Con `live-restore: false` (el defecto) | Con `live-restore: true` |
|---|---|---|
| `systemctl stop docker.socket docker.service` | siguen corriendo | siguen corriendo |
| `systemctl restart docker` | **mueren** al volver el daemon | siguen corriendo, y el daemon los readopta |

«Matar el daemon mata los contenedores» es falso. «El daemon los readopta» también. Lo cierto es que **matar el daemon no los toca, y reiniciarlo sí los mata**.
:::

Sigue con [[escalamiento-y-orquestacion]], que dice por qué el mundo se movió a esto más allá de la reproducibilidad.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor no cuelga de Docker, cuelga de su shim; `runc` ya salió y cada `syscall` va directo al kernel.
