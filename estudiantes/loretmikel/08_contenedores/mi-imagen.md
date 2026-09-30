# Mi imagen en Docker Hub

## Quién soy, en los dos lados

- Usuario de GitHub: loretmikel
- Usuario de Docker Hub: mldmy27

## La URL pública

URL: https://hub.docker.com/r/mldmy27/fdd-roto

## El digest

```text
$ docker inspect --format '{{index .RepoDigests 0}}' mldmy27/fdd-roto
mldmy27/fdd-roto@sha256:a9d14ecff183ecdf52c6cea13f8afd1952fd5d7c816e3b7738d843c15b778780
```

## Cómo la corro yo

Comando exacto:

```text
docker run --rm mldmy27/fdd-roto
```

La imagen está construida para `linux/amd64`. En una Mac con Apple Silicon se corre con `docker run --rm --platform linux/amd64 mldmy27/fdd-roto`.

Salida que debo esperar:

```text
Corriendo como: app
requests 2.32.3
```

## La prueba de que se baja del registro

```text
$ docker logout
$ docker rmi -f mldmy27/fdd-roto
$ docker run --rm --platform linux/amd64 mldmy27/fdd-roto
Removing login credentials for https://index.docker.io/v1/
Untagged: mldmy27/fdd-roto:latest
Deleted: sha256:a9d14ecff183ecdf52c6cea13f8afd1952fd5d7c816e3b7738d843c15b778780
Unable to find image 'mldmy27/fdd-roto:latest' locally
latest: Pulling from mldmy27/fdd-roto
628ba040a5e8: Pulling fs layer
cfa9d829b318: Pulling fs layer
4bb649492fcf: Pulling fs layer
98f8930df68b: Pulling fs layer
d6f4fc7281a3: Pulling fs layer
628ba040a5e8: Already exists
cfa9d829b318: Already exists
4bb649492fcf: Already exists
98f8930df68b: Already exists
d6f4fc7281a3: Already exists
44136fa355b3: Already exists
cfa9d829b318: Pull complete
4bb649492fcf: Pull complete
98f8930df68b: Pull complete
628ba040a5e8: Pull complete
d6f4fc7281a3: Pull complete
590b81d1bfea: Download complete
Digest: sha256:a9d14ecff183ecdf52c6cea13f8afd1952fd5d7c816e3b7738d843c15b778780
Status: Downloaded newer image for mldmy27/fdd-roto:latest
Corriendo como: app
requests 2.32.3
```

## El tamaño

```text
$ docker images mldmy27/fdd-roto
IMAGE                     ID             DISK USAGE   CONTENT SIZE   EXTRA
mldmy27/fdd-roto:latest   a9d14ecff183        195MB         47.7MB
```
