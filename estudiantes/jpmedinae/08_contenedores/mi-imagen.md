# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub:jpmedinae
- Usuario de Docker Hub:jpmedinae

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL:https://hub.docker.com/r/jpmedinae/info-fuentes-de-datos

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>
jpmedinae/info-fuentes-de-datos@sha256:9f73a8d546fe97155dcf1dc4dc81b9d19d70f054df3372e5cada1b881249e242

```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm jpmedinae/info-fuentes-de-datos:1
```

Salida que debo esperar:

```text
=== Información del sistema ===
Hostname: [cambia en cada ejecución]
Usuario: root
Directorio: /app
Fecha: [cambia en cada ejecución]
Kernel: [kernel de la máquina]

=== Procesos ===
[lista de procesos]

=== Memoria ===
[datos de memoria]

=== Disco ===
[datos del disco]
GitHub: jpmedinae
Fecha de construcción: 2026-09-21
Curso: Fuentes de Datos, unidad 08
```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
docker rmi -f <tu-usuario>/<tu-imagen>
docker run --rm <tu-usuario>/<tu-imagen>
$ docker logout
Removing login credentials for https://index.docker.io/v1/

$ docker rmi -f jpmedinae/info-fuentes-de-datos:1
Untagged: jpmedinae/info-fuentes-de-datos:1
Deleted: sha256:9f73a8d546fe97155dcf1dc4dc81b9d19d70f054df3372e5cada1b881249e242

$ docker run --rm jpmedinae/info-fuentes-de-datos:1
Unable to find image 'jpmedinae/info-fuentes-de-datos:1' locally
1: Pulling from jpmedinae/info-fuentes-de-datos
52e8c5a7fd8d: Pull complete
35886062c342: Pull complete
079bcefe2428: Pull complete
44136fa355b3: Already exists
80d300b0c908: Download complete
Digest: sha256:9f73a8d546fe97155dcf1dc4dc81b9d19d70f054df3372e5cada1b881249e242
Status: Downloaded newer image for jpmedinae/info-fuentes-de-datos:1
=== Información del sistema ===
Hostname: 9ec3fc7728dc
Usuario: root
Directorio: /app
Fecha: Tue Sep 22 00:37:56 UTC 2026
Kernel: 7.0.0-31-generic

=== Procesos ===
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1 20.0  0.0   4336  3392 ?        Ss   00:37   0:00 /bin/bash ./info.sh
root          12  0.0  0.0   7904  4096 ?        R    00:37   0:00 ps aux

=== Memoria ===
               total        used        free      shared  buff/cache   available
Mem:            30Gi       4.8Gi        22Gi       1.0Gi       4.0Gi        25Gi
Swap:          8.0Gi          0B       8.0Gi

=== Disco ===
Filesystem      Size  Used Avail Use% Mounted on
overlay         177G   21G  147G  13% /
GitHub: jpmedinae
Fecha de construcción: 2026-09-21
Curso: Fuentes de Datos, unidad 08


```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>
docker images jpmedinae/info-fuentes-de-datos
IMAGE                               ID             DISK USAGE   CONTENT SIZE   EXTRA
jpmedinae/info-fuentes-de-datos:1   9f73a8d546fe        117MB         29.8MB

```
