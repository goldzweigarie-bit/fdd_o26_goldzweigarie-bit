---
id: chuleta-contenedores
title: "Chuleta"
nav_title: "Chuleta"
summary: "Todos los comandos de la unidad en una página, Docker y Podman lado a lado, agrupados por lo que quieres hacer y con el enlace a donde se explicó cada uno."
status: ready
estimated_time: 8m
tags: [docker, podman, referencia, comandos, chuleta, errores]
prerequisites: [contenedores]
---

# Chuleta

**Anexo A** · para consultar, no para memorizar

Aquí sólo están los comandos que esta unidad enseñó. Si uno no aparece, es a propósito: todavía no lo necesitas.

**Cómo leer la columna de Podman.** Los dos CLI son compatibles comando por comando, así que en casi todas las filas dice `igual`, y eso quiere decir literalmente igual: cambia `docker` por `podman` y el resto se copia tal cual. Las filas donde **no** dice `igual` son las que valen la pena, y casi todas salen de lo mismo: Podman corre rootless y sin daemon. En macOS y Windows, antes del primer `podman` de la sesión van `podman machine init` y `podman machine start`; la máquina no arranca sola.

En los ejemplos, `ubuntu:24.04`, `alpine:3.20` y `postgres:16` son las imágenes de la unidad, y las versiones van pineadas a propósito: `latest` no quiere decir «la más nueva», quiere decir «la que su autor haya dejado ahí».

## Correr un contenedor

::: table {#cont-chuleta-correr title="Lo que escribes cien veces"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Correrlo y que se borre al salir | `docker run --rm alpine:3.20 echo ok` | igual | [[anatomia-de-docker-run|1/4]] |
| Dejarlo corriendo, con nombre | `docker run -d --name lab ubuntu:24.04 sleep 300` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Entrar con terminal desde el arranque | `docker run -it ubuntu:24.04 bash` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Montar mi carpeta de trabajo | `docker run --rm -v "$(pwd)":/app ubuntu:24.04 ls /app` | igual | [[lab-con-volumen|2/6]] |
| Que el archivo que escriba quede **mío** | `docker run --rm --user "$(id -u):$(id -g)" …` | `podman run --rm --userns=keep-id …` | [[el-archivo-compartido|2/14]] |
| Pasarle configuración | `docker run -e POSTGRES_PASSWORD=fdd postgres:16` | igual | [[el-contrato-de-un-servicio|3/2]] |
| Correr una imagen de otra arquitectura | `docker run --rm --platform linux/amd64 ubuntu:24.04 uname -m` | igual | [[instalar-docker-y-podman|2/10]] |

:::

`--rm` borra el contenedor al terminar, no la imagen. Y `-d` no lo hace inmortal: un contenedor vive exactamente lo que vive su proceso principal, con `-d` o sin él.

## El ciclo de vida

Quince comandos que salen todos de la misma regla — el contenedor **es** su `PID` 1 — y se leen contra la figura de [[ciclo-de-vida-de-un-contenedor|la página 2 de la sección 2]].

::: table {#cont-chuleta-ciclo title="Los quince del ciclo de vida"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Ver los que están **vivos** | `docker ps` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Ver también los que ya terminaron | `docker ps -a` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Buscar uno por nombre | `docker ps -a --filter name=roto` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Leerlo en columnas que yo elijo | `docker ps -a --format '{{.Names}} {{.Status}}'` | igual | [[limpieza-de-docker|2/8]] |
| Ver lo que escribió | `docker logs lab` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Seguirlo en vivo, línea por línea | `docker logs -f lab` | `podman logs -f lab` | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Meterme a uno que **ya está corriendo** | `docker exec -it lab bash` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Correr un comando suelto adentro | `docker exec lab cat /datos.txt` | igual | [[lab-sin-volumen|2/5]] |
| Ver qué cambió en su capa de escritura | `docker diff lab` | `podman diff lab` | [[lab-sin-volumen|2/5]] |
| Detenerlo | `docker stop lab` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Revivirlo con su mismo comando | `docker start lab` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Pararlo y volverlo a arrancar de un golpe | `docker restart lab` | igual | [[el-contrato-de-un-servicio|3/2]] |
| Borrarlo de la lista | `docker rm lab` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Matarlo y borrarlo de un golpe | `docker rm -f lab` | igual | [[ciclo-de-vida-de-un-contenedor|2/2]] |
| Sacarle un archivo, **vivo o muerto** | `docker cp lab:/app/salida.csv .` | igual | esta página |

:::

`exec` no arranca nada: se mete en lo que ya existe. Sobre un contenedor terminado no hay adónde entrar, y los dos comandos que sí sirven son `docker ps -a` —para el código de salida— y `docker logs` —para lo que alcanzó a escribir—. `docker cp` es el tercero, y es el único que rescata un archivo de un contenedor que ya murió: funciona mientras no le hayas hecho `rm`.

Y dos que en Podman se escriben igual y conviene saber en qué se diferencian: `podman exec` entra exactamente como su gemelo, pero `podman ps` **no le pregunta a ningún daemon** — lee el estado del disco, en tu propio directorio, porque no hay un proceso central que sea dueño de la verdad. `docker restart`, en cambio, es literalmente un `stop` seguido de un `start`, con los mismos diez segundos de espera antes del `SIGKILL`.

::: table {#cont-chuleta-salidas title="Los códigos de salida que vas a ver"}

| Código | Qué suele querer decir |
|---|---|
| `0` | terminó bien: hizo su trabajo y se acabó |
| `1` | el programa falló por su cuenta — lee `logs` |
| `126` | el archivo existe pero no es ejecutable; casi siempre falta `chmod +x` |
| `127` | un shell (`sh -c …`) no encontró el comando: una errata, o no está instalado en esa imagen. Sin shell de por medio no hay `Exited (127)`: el contenedor queda `Created`, aunque el propio `docker run` sale con código 127 |
| `137` | lo mataron con `SIGKILL`: tu `stop` que se pasó del tiempo, o el límite de memoria |

:::

## Construir una imagen

::: table {#cont-chuleta-build title="Del Dockerfile a la imagen"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Construir con el contexto de aquí | `docker build -t mi-imagen .` | igual | [[el-dockerfile-por-dentro|2/3]] |
| Usar otro archivo, mismo contexto | `docker build -f docker/Dockerfile.prod -t app .` | igual | [[el-dockerfile-por-dentro|2/3]] |
| Ignorar el caché y rehacer todo | `docker build --no-cache -t mi-imagen .` | igual | [[capas-y-cache|1/8]] |
| Construir callado, y quedarme con el hash | `docker build -q -t mi-imagen .` | igual | [[el-dockerfile-por-dentro|2/3]] |
| Ver la imagen **por capas** | `docker history mi-imagen` | igual | [[el-dockerfile-por-dentro|2/3]] |
| Ver qué comando corre al arrancar | `docker inspect -f '{{.Config.Cmd}}' mi-imagen` | `podman inspect --format '{{.Config.Cmd}}' mi-imagen` | [[lab-sin-volumen|2/5]] |
| Volver imagen la capa de un contenedor — **existe, no se usa**: el Dockerfile no se entera | `docker commit lab mi-imagen:parche` | `podman commit lab mi-imagen:parche` | [[lab-sin-volumen|2/5]] |
| Ver qué imágenes tengo, y cuánto pesan | `docker images` | igual | [[instalar-docker-y-podman|2/10]] |
| Lo mismo, en las columnas que quiero | `docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'` | igual | [[el-dockerfile-por-dentro|2/3]] |
| Publicar para otra arquitectura | `docker buildx build --platform linux/amd64 -t app .` | `podman build --platform linux/amd64 -t app .` | [[instalar-docker-y-podman|2/10]] |

:::

El `.` final **no es «aquí»: es el contexto**. Con BuildKit no viaja entero: viaja lo que piden los `COPY`. Pero un `COPY . .` pide **todo**, y por eso existe `.dockerignore` —mismo formato que `.gitignore`—, que recorta **antes** de enviar:

```text
.git
__pycache__/
.venv/
*.csv
```

## Las ocho instrucciones del Dockerfile

::: table {#cont-chuleta-dockerfile title="Las que de verdad vas a escribir"}

| Instrucción | Qué hace | Cuándo ocurre |
|---|---|---|
| `FROM python:3.12-slim` | elige la imagen base; es la primera línea y la que decide el tamaño | build |
| `WORKDIR /app` | fija el directorio de trabajo — y **las dos**: vale para el resto del build y queda anotada para el contenedor | build **y** run |
| `COPY requirements.txt .` | copia del contexto a la imagen; el hash de lo copiado entra en la clave de caché | build |
| `RUN pip install -r requirements.txt` | ejecuta al construir y **congela el resultado** en una capa | build |
| `ENV PGHOST=base` | deja una variable por omisión en la imagen; lo que el `-e` de `run` sobreescribe | build (se lee en run) |
| `USER app` | el proceso deja de ser `root` incluso adentro; va **después** de los `RUN` que instalan | build (se aplica en run) |
| `ENTRYPOINT ["./hola.sh"]` | fija el programa; lo que escribas en `run` **se le pega detrás** como argumentos | run |
| `CMD ["mundo"]` | el comando por defecto; lo que escribas en `run` lo **reemplaza** | run |

:::

Con los dos juntos, `CMD` deja de ser «el comando» y pasa a ser los **argumentos por defecto** del `ENTRYPOINT`. La regla de decisión: `ENTRYPOINT` cuando la imagen *es* un programa, `CMD` solo cuando es un entorno. La corrida que lo enseña está en [[el-dockerfile-por-dentro|el Dockerfile por dentro]].

Y dos que aparecen mucho y aquí no hacen falta: **`ADD`**, que es `COPY` con magia de más —descomprime y baja URL—, y **`EXPOSE`**, que sólo documenta un puerto y **no publica nada**; publicar es `-p`, y se escribe en `docker run`.

## Volúmenes y rutas

::: table {#cont-chuleta-volumenes title="El CLI de volúmenes, completo"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Crear un named volume | `docker volume create pgdata` | igual | [[named-volumes-y-postgres|2/7]] |
| Listarlos | `docker volume ls` | igual | [[named-volumes-y-postgres|2/7]] |
| Ver dónde vive uno de verdad | `docker volume inspect pgdata` | igual | [[named-volumes-y-postgres|2/7]] |
| Borrarlo — **esto sí pierde el dato** | `docker volume rm pgdata` | igual | [[named-volumes-y-postgres|2/7]] |
| Borrar los volúmenes que ningún contenedor usa | `docker volume prune`: sólo los **anónimos** | `podman volume prune`: **todos**, también los que tienen nombre | [[limpieza-de-docker|2/8]] |
| …incluidos los **con nombre** | `docker volume prune -a` | no hay `-a`: el de arriba ya se los lleva | [[limpieza-de-docker|2/8]] |
| Montar **mi carpeta** (bind mount) | `-v "$(pwd)":/app` | igual | [[rutas-en-docker|2/13]] |
| Montar un **named volume** | `-v pgdata:/var/lib/postgresql/data` | igual | [[named-volumes-y-postgres|2/7]] |
| Montarlo de sólo lectura | `-v "$(pwd)":/app:ro` | igual | [[lab-con-volumen|2/6]] |
| Escribirlo sin ambigüedad | `--mount type=bind,src="$(pwd)/app",dst=/app` | igual | [[rutas-en-docker|2/13]] |
| Arreglar el dueño del origen (Podman) | — | `-v ./app:/app:U` | [[el-archivo-compartido|2/14]] |

:::

La regla que decide casi siempre: **bind mount para tu código mientras lo editas, named volume para los datos de un servicio.** Y la trampa que a todos nos cuesta una tarde: el primer argumento de `-v` **es un nombre de volumen si no empieza con `/` o con `./`**, así que `-v aap:/app` no monta tu carpeta `aap`, crea un volumen llamado `aap` y te lo monta vacío. El bind mount **tapa** lo que había en el destino; el named volume vacío **copia** lo que había, una sola vez.

## Red y puertos

::: table {#cont-chuleta-red title="Que dos contenedores se hablen, y quién más los oye"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Crear una red propia | `docker network create lab` | igual | [[la-red-y-el-nombre|3/1]] |
| Correr algo dentro de ella | `docker run -d --network lab --name pg postgres:16` | igual | [[la-red-y-el-nombre|3/1]] |
| Ver la IP de un contenedor | `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pg` | igual | [[la-red-y-el-nombre|3/1]] |
| Publicar un puerto al host | `docker run -d -p 15432:5432 --name pg2 postgres:16` | igual | [[la-red-y-el-nombre|3/1]] |
| Publicarlo **sólo para mí** | `-p 127.0.0.1:15432:5432` | igual | [[la-red-y-el-nombre|3/1]] |
| Ver qué publica un contenedor | `docker port pg` | igual | [[la-red-y-el-nombre|3/1]] |
| Meter varios en un `localhost` común | — | `podman pod create` | [[la-red-y-el-nombre|3/1]] |

:::

En la red por omisión **no hay resolución por nombres**: dos contenedores se alcanzan por IP, y la IP cambia en cada arranque. En una red que tú creas, el nombre del contenedor **es** su dirección. Y `-p` no sirve para que dos contenedores se hablen: sirve para que los oiga alguien más — `0.0.0.0` es *todas* las interfaces de tu máquina, incluida la del café.

## Registro

::: table {#cont-chuleta-registro title="Publicar y traer imágenes"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Entrar a Docker Hub | `docker login` | igual | [[a-docker-hub|2/12]] |
| Bajar una imagen | `docker pull postgres:16` | igual | [[instalar-docker-y-podman|2/10]] |
| Ponerle el nombre con el que se publica | `docker tag hola tuusuario/hola:v1` | igual | [[a-docker-hub|2/12]] |
| Subirla | `docker push tuusuario/hola:v1` | igual | [[a-docker-hub|2/12]] |
| Ver su digest, que es su nombre verdadero | `docker inspect --format '{{index .RepoDigests 0}}' tuusuario/hola:v1` | igual | [[a-docker-hub|2/12]] |
| Borrar una imagen local | `docker rmi -f tuusuario/hola:v1` | igual | [[a-docker-hub|2/12]] |
| Salir de la sesión | `docker logout` | igual | [[a-docker-hub|2/12]] |

:::

Un nombre de imagen son cuatro piezas: `docker.io/library/ubuntu:24.04`. Si no dices registro se asume `docker.io`, si no dices tag se asume `latest`, y `library` es el namespace de las imágenes oficiales, donde **no puedes hacer `push`**. En Podman el registro por omisión no es automático: se configura en `registries.conf`, y por eso ahí conviene escribir el nombre completo.

Y el que tumba a alguien cada semestre: **los nombres de imagen van en minúsculas, siempre**, aunque tu login lleve mayúsculas.

## Limpieza

::: table {#cont-chuleta-limpieza title="Qué se lleva cada prune"}

| Quiero | Docker | Podman | Dónde |
|---|---|---|---|
| Medir antes de borrar | `docker system df` | igual | [[limpieza-de-docker|2/8]] |
| Ver las capas huérfanas | `docker images -f dangling=true` | igual | [[limpieza-de-docker|2/8]] |
| Borrar los contenedores **detenidos** | `docker container prune` — sin `-f` la primera vez, para leer qué propone | igual | [[limpieza-de-docker|2/8]] |
| Borrar sólo las capas huérfanas | `docker image prune` | igual | [[limpieza-de-docker|2/8]] |
| …y además las imágenes que nadie usa | `docker image prune -a` | igual | [[limpieza-de-docker|2/8]] |
| Barrer contenedores, capas, redes y caché | `docker system prune -a` | igual | [[limpieza-de-docker|2/8]] |
| Incluir también los volúmenes | `docker system prune --volumes`: sólo los **anónimos** | `podman system prune --volumes`: **todos** los que nadie usa, también los que tienen nombre | [[limpieza-de-docker|2/8]] |
| Borrar por patrón | `docker images --format '{{.Repository}}:{{.Tag}}' \| grep -E '^lab-[1-5]:latest$' \| xargs -r docker rmi` | lo mismo con `podman`, pero Podman nombra `localhost/lab-1:latest`: el patrón es `^(localhost/)?lab-[1-5]:latest$` | [[limpieza-de-docker|2/8]] |

:::

Ningún `prune` toca lo que está **en uso**, y en Docker ninguno toca un volumen **con nombre** salvo `docker volume prune -a`: `system prune --volumes` y `volume prune` sin `-a` sólo se llevan los anónimos. **En Podman no hay esa red:** `podman volume prune` y `podman system prune --volumes` se llevan también los que tienen nombre. Esa excepción no es un descuido: es la única fila donde borrar es **perder un dato** y no rehacer un build.

## Mirar la instalación, y endurecer

::: table {#cont-chuleta-endurecer title="Diagnóstico y banderas"}

| Quiero | Comando | Dónde |
|---|---|---|
| Saber si el cliente habla con su daemon | `docker version` | [[instalar-docker-y-podman|2/10]] |
| Saber **cuál** `docker` estoy corriendo | `type -a docker` y `docker context ls` | [[instalar-docker-y-podman|2/10]] |
| Ver cómo está configurado el motor por dentro | `docker info` | [[contenedores-anidados|Anexo C]] |
| Comprobar mi rango rootless | `grep "^$USER:" /etc/subuid /etc/subgid` | [[instalar-docker-y-podman|2/10]] |
| Ver la máquina de Podman | `podman machine list` | [[instalar-docker-y-podman|2/10]] |
| Ver los uid como los ve Podman — diagnostica, no arregla | `podman unshare ls -ln` | [[el-archivo-compartido|2/14]] |
| Ver con qué capabilities arranca | `docker run --rm alpine:3.20 grep CapEff /proc/self/status` | [[cuando-se-rompe-el-aislamiento|3/4]] |
| Apagar todas las capabilities | `--cap-drop ALL` | [[cuando-se-rompe-el-aislamiento|3/4]] |
| Impedir que escale privilegios | `--security-opt no-new-privileges` | [[cuando-se-rompe-el-aislamiento|3/4]] |
| Que no pueda escribirse a sí mismo | `--read-only` | [[cuando-se-rompe-el-aislamiento|3/4]] |
| Fijar un contenido exacto | `imagen@sha256:…` en vez del tag | [[cuando-se-rompe-el-aislamiento|3/4]] |

:::

Las tres que **no** se escriben, y que la unidad desarma una por una: `--privileged`, `--security-opt seccomp=unconfined` y montar `/var/run/docker.sock` adentro. La tercera no es un exploit: es entregar el host. Y la prohibición sin matices: **nunca `chmod 666 /var/run/docker.sock`**.

## Docker y Podman, las diez diferencias

::: table {#cont-chuleta-podman title="La tabla larga que la página 7 mandó aquí"}

| | Docker | Podman |
|---|---|---|
| Quién arranca el contenedor | un daemon `root` siempre encendido, al otro lado de un socket | tu propio proceso, con `fork` y `exec` |
| Qué queda vivo mientras corre | `dockerd`, `containerd` y un shim por contenedor | un `conmon` por contenedor, y nada más |
| Quién eres adentro | `root` del host, salvo que lo configures | tú, mapeado a tu rango de `/etc/subuid` |
| Runtime por omisión | `runc` | `crun`, y ahí está la mitad del tiempo de arranque |
| Dónde guarda las imágenes | `/var/lib/docker/`, propiedad de `root` | `~/.local/share/containers/`, tuya |
| Registro por omisión | `docker.io`, implícito | se configura en `registries.conf`; conviene el nombre completo |
| Red | bridge por omisión sin DNS; redes propias con DNS | igual, pero en rootless la red corre **en espacio de usuario** |
| Volúmenes | idénticos comando por comando | idénticos, más el sufijo `:U` para arreglar el dueño |
| Varios contenedores juntos | Compose, integrado como `docker compose` | **pods**, de fábrica — la unidad de Kubernetes; para Compose, `podman-compose` |
| Arrancar con la máquina | `systemd` levanta el daemon | cada contenedor puede ser su propia unidad de `systemd` |

:::

El `docker compose` de DataCamp no se queda sin traducción: **`podman-compose`** es un paquete aparte —`pip install podman-compose`, o el de tu distribución— que lee el mismo `docker-compose.yml` y no necesita ningún socket. Desde **Podman 4.7** existe además **`podman compose`**, que no implementa nada: delega en el Compose que tengas instalado, y si el que encuentra es el de Docker, hace falta el socket de Podman encendido (`systemctl --user start podman.socket`). Comprueba cuál tienes con `podman --version` antes de teclear el que no es.

Lo que **no** compra la ausencia de daemon es velocidad: con el runtime igualado, Podman rootless sale ~3 % **detrás** de Docker. Los números y su pie están en [[docker-y-podman|la página 7 de la sección 1]].

## Mensajes que vas a ver, y qué significan

::: table {#cont-chuleta-errores title="Errores frecuentes, de instalación y de ejecución"}

| Mensaje | Qué pasó | Qué haces |
|---|---|---|
| `permission denied while trying to connect to the Docker daemon socket` | el socket es de `root` y del grupo `docker`, y tú no estás en el grupo | `sudo usermod -aG docker $USER`, y vuelve a entrar. **Nunca `chmod 666`** |
| `cannot find UID in /etc/subuid` | Podman rootless sin rango, o sin el paquete `uidmap` | `sudo apt-get install -y uidmap` y `sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 $USER` |
| `Cannot connect to Podman` | en macOS o Windows, la máquina de Podman está apagada | `podman machine start` |
| `exec format error` | el binario de adentro es de otra arquitectura | `--platform linux/amd64`, o busca una imagen que publique `arm64` |
| `The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8)` | lo mismo, dicho por el otro lado | igual; y si vas a **publicar**, `docker buildx build --platform linux/amd64` |
| `invalid reference format: repository name must be lowercase` | hay mayúsculas en el nombre de la imagen | todo en minúsculas, aunque tu login no lo esté |
| `toomanyrequests: You have reached your pull rate limit` | se agotó el límite de descargas anónimas de Docker Hub; treinta personas detrás de una sola IP lo agotan en minutos | `docker login`, y haz el prepull **antes** de la clase |
| `denied: requested access to the resource is denied` | el usuario del tag no es el de tu sesión — o le escribiste una mayúscula | `docker login`, revisa el `docker tag`, y vuelve a empujar |
| `no such file or directory` sobre una ruta que **sí** existe, al montarla | Docker instalado por `snap`, que está confinado y no ve fuera de tu carpeta personal | quítalo y reinstala desde el repositorio oficial — [[planes-b-de-instalacion|2/11]] |
| `failed to compute cache key: ... "/datos": not found` | un `COPY ../datos .`: BuildKit no sale del contexto, así que busca `datos` **dentro** de él. Si ahí existe un `datos/`, copia ése **sin error** | mueve el archivo dentro del contexto, o cambia qué directorio le pasas al `build`. `forbidden path outside the build context` es el mismo error en el builder viejo |
| `exec: "…": executable file not found in $PATH`, y el contenedor queda `Created` | `docker run img comando-que-no-existe`: el `run` falla en el acto, el proceso nunca arrancó y `docker logs` sale vacío | corrige el nombre, o instálalo en el `Dockerfile` |
| `Exited (127)`, y en `docker logs`: `sh: 1: …: not found` | el comando lo lanzó un shell —`sh -c comando-que-no-existe`— y el shell no lo encontró | igual: corrige el nombre, o instálalo en el `Dockerfile` |
| `Exited (126)` | el archivo existe y no es ejecutable | `chmod +x` al script, o un `RUN chmod +x` en el `Dockerfile` |
| `Exited (137)` | `SIGKILL`: tu `stop` se pasó de los diez segundos, o chocó con el límite de memoria | si fue memoria, sube `--memory`; si fue `stop`, atiende `SIGTERM` |
| `exec ./entrada.sh: no such file or directory`, **con el archivo ahí** | el script se guardó con saltos de línea de Windows: el `\r` quedó pegado al final del `#!` y ese intérprete no existe | guarda con saltos de línea de Unix, o `sed -i 's/\r$//' entrada.sh` y reconstruye |
| `Error response from daemon: container … is not running`, al hacer `exec` | el `PID` 1 terminó y no quedan namespaces en los que meterse | `docker ps -a` para el código de salida y `docker logs` para la última línea; **no insistas con `exec`** |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | ya hay algo publicado en ese puerto **del host** | cambia el lado izquierdo —`-p 18080:80`— o `docker rm -f` al que lo tiene |
| `ping: bad address 'dos'` | estás en la red por omisión, que no resuelve nombres | `docker network create lab` y corre los dos con `--network lab` |
| `FATAL: database files are incompatible with server` | el volumen lo inicializó otra versión mayor de Postgres | vuelve a la imagen que lo escribió, y migra con `pg_dump` o `pg_upgrade` |
| Se murió el contenedor y necesito un archivo de adentro | no es un error, es la pregunta que sigue a todos los anteriores | `docker cp <contenedor>:/ruta/archivo .` — funciona con el contenedor detenido, mientras no le hayas hecho `rm` |

:::

## Las reglas de la unidad

1. La imagen es **inmutable** y el contenedor es **efímero**: si quieres cambiar algo, cambias la receta y vuelves a construir.
2. El contenedor vive lo que vive su `PID` 1. «Se cerró solo» casi siempre significa «su proceso terminó».
3. Ante una falla, siempre los dos: `docker ps -a` para el código, `docker logs` para el mensaje.
4. Bind mount para tu código, named volume para los datos de un servicio.
5. Un servicio se publica con `-p` **sólo si alguien de fuera del sistema lo va a usar**.
6. El tamaño se elige en la primera línea del `Dockerfile`, no se recorta en la última.
7. Versiones pineadas, nunca `latest`, y para publicar, digest.
8. Si una respuesta de internet trae `--privileged` o `chmod 666` al socket, la respuesta está mal.

> [!NOTE]
> **Si sólo recuerdas una cosa:** casi todo lo de esta página es igual en Podman; lo que cambia de verdad es quién eres adentro, y eso decide qué pasa con los archivos que escribas.
