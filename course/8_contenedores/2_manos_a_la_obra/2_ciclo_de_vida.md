---
id: ciclo-de-vida-de-un-contenedor
title: "El ciclo de vida de un contenedor"
nav_title: "El ciclo de vida"
summary: "Una sola idea explica todo el ciclo: un contenedor vive exactamente lo que vive su proceso principal."
status: ready
estimated_time: 12m
tags: [ciclo-de-vida, run, start, stop, exec, logs, rm, pid, exited]
prerequisites: [repaso-dockerfile-imagen-contenedor]
---

# El ciclo de vida de un contenedor

**Página 2 de 16 · sección 2 de 3**

Meta: que todo el ciclo se deduzca de una sola regla, en vez de memorizarse como doce comandos sueltos.

::: figure {#cont-ciclo-de-vida title="Tres estados, y qué comando alcanza a cuál"}
![Máquina de estados de tres casillas rotuladas created, running y exited, con cada transición etiquetada por lo que la provoca: docker run, que es create más start; docker start; la salida del proceso PID 1 —la única razón por la que un contenedor se detiene: docker stop y docker kill sólo se la piden—; y docker rm, que saca la casilla del dibujo junto con su capa de escritura. A la derecha, qué alcanza cada comando: docker ps sólo ve running, docker ps -a ve las tres, docker logs muestra lo que escribió ese proceso, y la flecha de docker exec -it entra a running y aparece tachada contra exited. Un caso al pie, el exited con código 127 de docker run --name roto ubuntu:24.04 sh -c comando-que-no-existe, cuya shell no encuentra el comando: docker logs roto trae sh: 1: comando-que-no-existe: not found](../_assets/cont-ciclo-de-vida.svg)
:::

## En corto

- **Un contenedor vive exactamente lo que vive su proceso principal.** Todo lo demás sale de ahí.
- Detenido no es borrado: `stop` conserva la capa de escritura; sólo `rm` se la lleva.
- `ps` ve a los vivos; `ps -a` y `logs` explican a los muertos. Los quince comandos, en [[chuleta-contenedores|la chuleta]].

## La pregunta número uno del principiante

**Haz:** dos arranques, dos comportamientos.

```bash
docker run --rm ubuntu:24.04
docker run --rm -d --name corto ubuntu:24.04 sleep 300
docker ps --filter name=corto
```

**Qué hace cada pieza:**

- `docker run` — crea un contenedor nuevo desde una imagen y lo arranca.
- `--rm` — borra el contenedor en cuanto termina su proceso.
- `ubuntu:24.04` — la imagen: nombre y etiqueta (versión).
- `-d` — lo deja corriendo en segundo plano y te devuelve la terminal.
- `--name corto` — le pone nombre, para no usar su ID.
- `sleep 300` — el comando que corre adentro: espera 300 segundos y termina.
- `docker ps` — lista los contenedores que están corriendo.
- `--filter name=corto` — muestra sólo los que tengan `corto` en el nombre.

**Deberías ver:** el primero te devuelve el prompt sin imprimir nada; el segundo, un ID largo, y `corto` en `Up Less than a second`.

- El comando por defecto de `ubuntu` es `bash`. Sin terminal no tiene de dónde leer: **termina en el acto**.
- El segundo corre `sleep 300`: dura cinco minutos, y el contenedor también. `--rm` los borra al terminar.
- Por eso `uno` y `dos` de [[repaso-dockerfile-imagen-contenedor|2/1]] terminaron solos: su `CMD` era `cat`, que acaba en el acto.

## Los tres estados

**Haz:** arranca uno y míralo desde las dos listas.

```bash
docker run -d --name lab ubuntu:24.04 sleep 3600
docker ps
docker ps -a
```

**Qué hace cada pieza:**

- `sleep 3600` — espera una hora: el contenedor vive esa hora.
- `-a` — *all*: suma a la lista los contenedores que ya terminaron.

**Deberías ver:** `lab` en las dos listas, `Up` (`Less than a second` o `N seconds`). `ps` ve sólo vivos; `ps -a`, también terminados.

**Haz:** entra, mira los procesos, sal.

- `ps aux` y `exit` los tecleas ya adentro, en la shell del contenedor.

```bash
docker exec -it lab bash
ps aux
exit
docker ps -a
```

**Qué hace cada pieza:**

- `docker exec` — corre un comando más dentro de un contenedor que ya está vivo.
- `-it` — te conecta el teclado (`-i`) y una terminal (`-t`): una shell interactiva.
- `lab` — en qué contenedor entrar.
- `bash` — el comando que corre adentro: una shell nueva, al lado del `sleep`.
- `ps aux` — ya adentro: lista todos los procesos del contenedor, con su `PID`.
- `exit` — cierra esa shell y te regresa a tu terminal.

**Deberías ver:** en `ps aux`, tu `bash` y el `sleep` (el `PID` 1); tras `exit`, `lab` **aún** `Up`.

- Tu `bash` era un invitado de `exec`: saliste tú, no él. Con `docker run -it ubuntu:24.04 bash` sí sería el `PID` 1, y `exit` lo apagaría.

## Seguir en vivo lo que escribe

**Haz:** un contenedor que imprime la hora cada segundo, y síguelo con `-f` (*follow*, como `tail -f`).

```bash
docker run -d --name reloj alpine:3.20 sh -c 'while true; do date; sleep 1; done'
docker logs -f reloj
```

**Qué hace cada pieza:**

- `alpine:3.20` — una imagen mínima (unos MB), con `sh` en vez de `bash`.
- `sh -c '...'` — le pasa a la shell un programa completo, escrito entre comillas.
- `while true; do ...; done` — repite para siempre lo de en medio.
- `date` — imprime la fecha y hora.
- `sleep 1` — espera un segundo antes de la siguiente vuelta.
- `docker logs` — muestra lo que el proceso ha escrito en su salida.
- `-f` — *follow*: se queda esperando y enseña cada línea nueva al llegar.

**Deberías ver:** una línea por segundo (`Tue Sep 22 22:01:15 UTC 2026`, `...16`, `...17`). Ctrl-C corta **`logs`**, no el contenedor.

Tras Ctrl-C, compruébalo y limpia:

```bash
docker ps --filter name=reloj
docker rm -f reloj
```

**Qué hace cada pieza:**

- `docker rm` — borra un contenedor terminado y su capa de escritura.
- `-f` — *force*: si sigue vivo, primero lo mata. Aquí `-f` no es *follow*.

## Detener no es borrar

**Haz:** detén `lab`, mira la lista, revívelo.

```bash
docker stop lab
docker ps -a --filter name=lab
docker start lab
```

**Qué hace cada pieza:**

- `docker stop` — pide al proceso que termine (`SIGTERM`); a los 10 s lo mata (`SIGKILL`).
- `docker start` — vuelve a arrancar un contenedor detenido, con su mismo comando.

**Deberías ver:** `Exited (137) Less than a second ago`, y tras `start`, otra vez `Up`.
- `stop` tarda ~10 s: `sleep` ignora `SIGTERM`; el 137 es el `SIGKILL`.
- Lo que el proceso escribió adentro **sigue ahí** tras `stop`/`start`; sólo `rm` se lo lleva. Lo pruebas en [[lab-sin-volumen|2/5]].

## Se murió con error: ¿por qué?

**Haz:** provoca la falla a propósito.

```bash
docker run --name roto ubuntu:24.04 sh -c comando-que-no-existe
docker ps -a --filter name=roto
docker logs roto
```

**Qué hace cada pieza:**

- `sh -c comando-que-no-existe` — la shell intenta correrlo, no lo encuentra y sale con 127.
- `docker run` sin `-d` — se queda pegado a tu terminal hasta que el proceso termina.

**Deberías ver:** `sh: 1: comando-que-no-existe: not found` dos veces (en el `run` y en `logs`), y `Exited (127) Less than a second ago` en `ps -a`.

- `ps -a` da el **código de salida** del `PID` 1; `logs`, **lo que escribió** por salida estándar y de error. Corre los dos.
- El `sh -c` importa: sin él, Docker no encuentra el ejecutable, el `run` falla en el acto y `roto` queda `Created` con `logs` vacío. Limpia con `docker rm -f roto lab`.

| Código | Qué suele querer decir |
|---|---|
| `0` | terminó bien; el contenedor hizo su trabajo y se acabó |
| `1` | el programa falló por su cuenta: lee `logs` |
| `126` | el archivo existe pero no es ejecutable — casi siempre falta `chmod +x` |
| `127` | la shell no encontró el comando; una errata, o no está instalado en esa imagen |
| `137` | lo mataron con `SIGKILL`: tu `docker stop` que se pasó del tiempo, o el límite de memoria |

::: problem {#cont-s2p4-predice-ps title="Predice `ps -a` en cada paso"}
**Escribe tus cinco predicciones antes de teclear nada.** Para cada paso, di qué imprime `docker ps -a` justo después: ¿aparece `demo`?, y si aparece, ¿con qué `STATUS`?

1. `docker run -d --name demo ubuntu:24.04 sleep 20`
2. espera 25 segundos
3. `docker start demo`
4. `docker stop demo`
5. `docker rm demo`

Y la que cierra: tras el paso 2, `docker exec -it demo bash` **falla**. ¿Con qué mensaje, y qué necesita `exec` que no encuentra? («Porque está detenido» no cuenta.)
:::

::: hint {of="cont-s2p4-predice-ps"}
Una sola pregunta por paso: **¿está vivo el proceso principal?** Nada más decide el `STATUS`.

Para la última: la flecha tachada de la figura, y que el `bash` de un `exec` llega **al lado** de otro.
:::

::: answer {of="cont-s2p4-predice-ps"}
**1.** Aparece, `Up X seconds`. El `sleep` está vivo.
**2.** Aparece, `Exited (0) X seconds ago`. El `sleep` terminó **bien**, así que el contenedor terminó bien. Sigue en la lista: terminar no es desaparecer.
**3.** Aparece, `Up X seconds`. `docker start` vuelve a lanzar el **mismo** comando de siempre, así que arranca otro `sleep 20` — y en veinte segundos va a volver a salir solo.
**4.** Aparece, `Exited (137)`. `stop` manda `SIGTERM` y espera diez segundos; `sleep` no lo atiende, así que le cae el `SIGKILL`, y eso es el 137. Compáralo con el `Exited (0)` del paso 2: **mismo estado final, causa distinta, y el código lo dice**.
**5.** **No aparece.** `rm` lo saca de la lista y borra su capa de escritura. Si querías algo de adentro, ya se fue.

**El `exec` que falla.** Mensaje: `Error response from daemon: container ... is not running`.

- `exec` **no arranca nada: se mete en lo que ya existe** — los namespaces y el cgroup del contenedor.
- Existen sólo mientras hay un proceso vivo; al terminar el `PID` 1 se fueron con él. Reflejo: si `exec` dice `is not running`, no insistas. Corre `docker ps -a` (código) y `docker logs` (qué escribió).
:::

Sigue con [[el-dockerfile-por-dentro]], que construye la imagen sobre la que corre todo esto.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor vive lo que vive su `PID` 1; si terminó, `exec` no tiene dónde entrar y lo que queda son `ps -a` y `logs`.
