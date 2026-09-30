---
id: instalar-docker-y-podman
title: "Instalar Docker y Podman"
nav_title: "Instalar Docker y Podman"
summary: "Los dos runtimes corriendo sin sudo en Linux, macOS y Windows, la comprobación que de verdad lo prueba, y el prepull que salva la clase del martes."
status: ready
estimated_time: 25m
tags: [docker, podman, instalacion, rootless, wsl2, macos, uidmap, prepull]
prerequisites: [contenedores-con-las-manos]
---

# Instalar Docker y Podman

**Página 10 de 16 · sección 2 de 3**

Meta: dejar los dos runtimes corriendo sin `sudo` antes del martes, y bajar de antemano las imágenes de la clase.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-sin-sudo title="La comprobación que vale en las tres plataformas, y las ocho formas de creer que corres sin `sudo`"}
![Árbol de comprobación de que de verdad corres sin sudo. Arriba, la cadena de comandos whoami, id -u, type -a docker, docker context ls, docker version y docker run con la bandera rm sobre hello-world. Abajo, las ocho formas de creer que corres sin sudo sin correr sin sudo, cada una colgada del comando que la delata: el alias con sudo adentro, la función de shell, ser root en WSL2, el sudo -i olvidado, el newgrp que sólo valía en esa ventana, el chmod 666 del socket tachado en rojo, un DOCKER_HOST apuntando a otra máquina, y usar Podman diciendo que es Docker. Al margen, la advertencia que se cobra en la sección 3: estar en el grupo docker es ser root](../_assets/cont-sin-sudo.svg)
:::

## En corto

- Son **dos** programas y se instalan los dos: Docker porque es lo que da por hecho DataCamp, Podman porque es el que corre sin un proceso privilegiado encendido.
- **Listar tus grupos no prueba nada.** La comprobación que sirve en las tres plataformas es correr seis comandos y leer la salida completa.
- **Dónde trabajas importa**: Linux nativo o la ruta ext4 de WSL2, nunca `/mnt/c/`.

## Antes de teclear: dónde vas a trabajar

Todo el laboratorio de esta sección vive en `~/fdd/docker-lab`, una carpeta local y desechable. En Linux eso es literal. En **WSL2 hay que decirlo con cuidado**, porque hay dos discos a la vista y sólo uno sirve:

| Ruta | Qué es | ¿Sirve? |
|---|---|---|
| `/home/<tu-usuario>/fdd/docker-lab` | el disco ext4 de tu distribución | **sí** |
| `/mnt/c/Users/<tu-usuario>/...` | tu disco de Windows, visto por un puente | **no** |

En `/mnt/c/` los permisos no son los de Linux: son una traducción de NTFS, y un archivo escrito por un contenedor sale con el dueño y los modos que el puente decida, no los que esta unidad explica. Además el puente es lentísimo — [[planes-b|ya lo viste en la unidad 4]]. Ésa es, de paso, la razón concreta para preferir WSL2 nativo sobre cualquier arreglo con carpetas de Windows.

**Haz:** deja creada la carpeta ahora, en el disco correcto.

```bash
mkdir -p ~/fdd/docker-lab && cd ~/fdd/docker-lab && pwd
```

**Deberías ver:** una ruta que empieza con `/home/`. Si empieza con `/mnt/`, estás en el disco equivocado y el resto de la sección te va a dar resultados que ninguna página explica.

## Linux — el camino largo, que es el bueno

Docker se instala **desde su repositorio oficial**, no desde el paquete de tu distribución y mucho menos desde `snap`. Los comandos exactos, por distribución, están en [la guía oficial](https://docs.docker.com/engine/install/); en Ubuntu y Debian son éstos.

**Haz:** agrega el repositorio y su llave.

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**Deberías ver:** `apt` instalando siete paquetes sin quejarse. En Debian, cambia las dos veces que dice `ubuntu` en las URL por `debian`.

### El paso que quita el `sudo`

Recién instalado, `docker ps` te va a responder `permission denied while trying to connect to the Docker daemon socket`. Es correcto: el socket es de `root` y del grupo `docker`, y tú todavía no estás en ese grupo.

**Haz:** métete al grupo y abre una sesión que ya lo tenga.

```bash
sudo usermod -aG docker $USER
newgrp docker
id -nG | tr ' ' '\n' | grep -x docker
```

**Deberías ver:** la palabra `docker` sola en una línea. `usermod` cambia el archivo de grupos, pero **tu sesión ya abierta no se entera**: `newgrp docker` te abre una shell que sí lo tiene. Eso vale para **esa ventana**. Para que valga siempre, cierra sesión y vuelve a entrar — y ésa es una de las ocho trampas de la figura.

### Podman, rootless, con lo que de verdad necesita

En [[docker-y-podman|la página 7 de la sección anterior]] quedó el porqué: rootless necesita un rango en `/etc/subuid` y `/etc/subgid`, y los binarios `newuidmap` y `newgidmap`, que en Debian y Ubuntu vienen en el paquete **`uidmap`**, que es `Recommends` y falta en instalaciones mínimas.

**Haz:** instala los dos paquetes y comprueba tu rango.

```bash
sudo apt-get install -y podman uidmap
grep "^$USER:" /etc/subuid /etc/subgid
podman run --rm hello-world
```

**Deberías ver:** dos líneas del tipo `alumna:100000:65536`, y después el saludo de `hello-world`. Si el `grep` no imprime nada, el error que sigue es literal —`cannot find UID in /etc/subuid`— y se arregla con `sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER`.

## macOS

Docker Desktop, [de su página oficial](https://docs.docker.com/desktop/), con el instalador de tu arquitectura: **Apple silicon** o **Intel chip**. Bajar el equivocado produce un `.dmg` que ni siquiera abre.

Podman en macOS es distinto y aquí es donde se atora medio mundo: **Podman es un runtime de Linux**. En tu Mac no hay Linux, así que `podman` arranca una máquina virtual ligera y le habla a ella. Esa máquina no existe hasta que la creas.

**Haz:** crea la máquina y enciéndela, **antes** de cualquier `podman run`.

```bash
brew install podman
podman machine init
podman machine start
podman machine list
```

**Deberías ver:** una fila con `podman-machine-default` y el estado `Currently running`. Si te saltas estos dos comandos, el primer `podman run` contesta `Cannot connect to Podman` y parece una instalación rota cuando sólo está apagada. La máquina **no** arranca sola al reiniciar tu Mac: `podman machine start` es parte del ritual.

En macOS **no existe el grupo `docker`** y no debe existir: Docker Desktop habla con su propia VM. Si alguien te manda a hacer `usermod` aquí, te está mandando a otro sistema operativo.

## Windows

Windows corre Docker **a través de WSL2**, no al lado. Si todavía no lo tienes, [[planes-b|la página de la unidad 4]] trae `wsl --install` con sus tropiezos. Después:

1. Instala **Docker Desktop** y déjalo en el backend de WSL2 (es el predeterminado).
2. Abre **Settings → Resources → WSL integration** y **enciende el interruptor de tu distribución**. Apagado, `docker` no existe dentro de tu Ubuntu aunque Docker Desktop esté corriendo.
3. Trabaja **dentro de la distribución** —`wsl` desde PowerShell, o la terminal de Ubuntu—, no desde PowerShell.

Podman en Windows también necesita `podman machine init` y `podman machine start`, por la misma razón que en macOS.

## La pared del día de instalación: la arquitectura del CPU

Si tu Mac es Apple Silicon —M1 a M4— tu CPU es `arm64`, y **la mayoría de las imágenes publicadas son `amd64`**. Cuando no coinciden, el error tiene dos caras y las dos significan lo mismo:

| Lo que sale | Qué pasó |
|---|---|
| `exec format error` | el binario de adentro está compilado para otra arquitectura y el kernel no sabe ejecutarlo |
| `The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)` | la imagen sólo publica `amd64`, y tu máquina es `arm64` |

El parche para **correr** es `--platform linux/amd64`: Docker Desktop emula, funciona, y va más lento.

```bash
docker run --rm --platform linux/amd64 ubuntu:24.04 uname -m
```

Ojo con el corolario, porque se cobra en la entrega: **si construyes tu imagen en una Mac con Apple Silicon sin decir nada, publicas una imagen que sólo corre en máquinas como la tuya**. Para publicarla se construye con `docker buildx build --platform linux/amd64`. Construir para varias plataformas a la vez es un capítulo de DataCamp que vence una semana después; por ahora basta con la bandera.

## Estar en el grupo `docker` es ser `root`

Esto no es una advertencia de trámite, es la consecuencia directa de lo que ya sabes. En [[anatomia-de-docker-run|la anatomía de `docker run`]] quedó que el CLI no corre nada: le manda una petición por `/var/run/docker.sock` a un daemon que **es `root`**. Quien puede escribir en ese archivo le puede pedir a ese daemon lo que quiera — por ejemplo, que monte el disco entero dentro de un contenedor y te siente adentro como `root`.

Meter tu usuario al grupo `docker` es, literalmente, darle privilegios de `root` sin que aparezca la palabra. En tu laptop es el precio razonable de trabajar; en un servidor compartido es una decisión que se toma a conciencia. Con las manos se desarma en la sesión 3.

De ahí sale la prohibición que no tiene matices: **nunca `chmod 666 /var/run/docker.sock`.** Es el consejo más repetido de internet para «arreglar el permiso denegado», y lo que hace es abrirle `root` a cualquier proceso de la máquina, incluido cualquier cosa que ejecute tu navegador. Si el grupo no te funcionó, cierra sesión y vuelve a entrar.

## El prepull, y por qué salva la clase del martes

La sesión del 22 baja seis imágenes. Somos treinta personas detrás del NAT del ITAM, o sea **una sola dirección IP para todos**: el límite de descargas anónimas de Docker Hub se agota alrededor del minuto diez y la clase se detiene para todo el grupo. El mensaje, cuando pasa, es `toomanyrequests: You have reached your pull rate limit`, y no se arregla reintentando: se arregla habiendo bajado las imágenes antes.

Hay dos salidas y conviene usar las dos. La primera: los **pulls autenticados cuentan contra tu cuenta, no contra la IP** — y si ya hiciste [[a-docker-hub|la página 12]], ya tienes cuenta. La segunda: bajarlas desde tu casa, antes.

**Haz:** esto, en tu red, antes del martes.

```bash
docker login
docker pull ubuntu:24.04
docker pull alpine:3.20
docker pull hello-world
docker pull python:3.12-slim
docker pull postgres:16
docker pull postgres:17
docker images
```

**Deberías ver:** seis renglones en `docker images`, uno por imagen, con su tamaño. Son unos cuantos cientos de megabytes y se bajan **una sola vez**. Si `docker login` te pide usuario y contraseña y no tienes cuenta todavía, esa cuenta se hace en la página 12 — y conviene hacer esa página antes que este bloque.

::: problem {#cont-s2p1-comprobacion title="¿De verdad corres sin `sudo`?"}
Circula una comprobación que aquí **no sirve**: listar tus grupos y buscar `docker` entre ellos. Sólo dice algo en Linux con el daemon del sistema; en macOS, en Windows y en cualquier instalación rootless ese grupo no existe ni debe existir, así que su ausencia no prueba nada.

La que sí vale en las tres plataformas es ésta. Córrela **en ese orden**, sin `sudo` en ninguno, y guarda la salida completa en un archivo de texto:

```bash
whoami
id -u
type -a docker
docker context ls
docker version
docker run --rm hello-world
```

Contesta, mirando tu propia salida:

1. ¿Qué imprimieron `whoami` e `id -u`, y qué pasaría si dijeran `root` y `0`?
2. `type -a docker` — ¿qué tendría que salir para que el comando **no** fuera el binario de Docker?
3. ¿Qué te dice `docker context ls` que ninguno de los otros te dice?
4. `docker version` imprime dos bloques, `Client` y `Server`. ¿Qué significa que el segundo falte?
:::

::: hint {of="cont-s2p1-comprobacion"}
La figura de arriba tiene ocho trampas y cada una cuelga del comando que la delata. Cuatro de ellas se resumen en una sola pregunta: **¿estoy corriendo lo que creo que corro, con el usuario que creo que soy, contra la máquina que creo?** Cada uno de los seis comandos contesta un pedazo de esa pregunta.

Y `docker version` tiene una peculiaridad: para imprimir el bloque `Server` **tiene que hablar con el daemon**.
:::

::: answer {of="cont-s2p1-comprobacion"}
**1.** Deben imprimir **tu** nombre de usuario y un número distinto de `0`. Si dicen `root` y `0`, no estás corriendo sin `sudo`: estás corriendo **como `root`**, y no lo notaste. Pasa con un `sudo -i` de hace media hora que se quedó abierto, y pasa por omisión en muchas instalaciones de WSL2, donde el usuario por defecto **es** `root`. Todo lo que hagas así va a funcionar, y nada de lo que aprendas será cierto para tu compañero.

**2.** Debe salir una ruta, `/usr/bin/docker` o parecida. Si sale `docker is an alias for sudo docker` o `docker is a shell function`, el comando que corres no es el binario: alguien le encajó un `sudo` adentro. Y si sale la ruta de `podman` —o si `type -a` lista `podman` además—, estás usando Podman convencido de que es Docker. Los dos casos dan salidas perfectamente plausibles, y por eso hay que mirar.

**3.** Te dice **con qué daemon estás hablando**, y es lo único que delata un `DOCKER_HOST` apuntando a otra máquina. Si la fila activa —la que trae el asterisco— no es `default` o `desktop-linux`, tus contenedores están naciendo en otra computadora, y todo lo que hagas el martes va a existir en un lugar al que no le vas a poder pedir nada.

**4.** Que el cliente está instalado y **el daemon no te contesta**. Ahí caen a la vez el `permission denied` del socket, el daemon apagado y, en macOS y Windows, el `podman machine` que nunca arrancó. Es la diferencia entre «no tengo Docker» y «tengo Docker y no me está hablando», que son dos problemas con arreglos distintos.

**Y la trampa que ninguno de los seis comandos delata, porque es tuya**: el `newgrp docker` que corriste hace rato sólo valía en esa ventana. Cierra la terminal, abre una nueva, y vuelve a correr los seis. Si ahí siguen saliendo bien, terminaste.
:::

Sigue con [[planes-b-de-instalacion]], que es adonde vas si algo de esta página no salió.

> [!NOTE]
> **Si sólo recuerdas una cosa:** listar tus grupos no prueba nada; corre los seis comandos en una terminal recién abierta y lee la salida completa.
