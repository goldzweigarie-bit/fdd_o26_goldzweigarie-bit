# Mi imagen en Docker Hub

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`.

## Quién soy, en los dos lados

- Usuario de GitHub: RobertoUribeClemente
- Usuario de Docker Hub: bobuc05

No tienen por qué ser el mismo, y los nombres de imagen **van en minúsculas
siempre**.

## La URL pública

La que sirve es `https://hub.docker.com/r/<tu-usuario>/<tu-imagen>`. La que te
da el navegador cuando estás con tu sesión abierta empieza con
`hub.docker.com/repository/docker/` y **da 404 a todos los demás, incluido yo**.
Ábrela en una ventana privada antes de entregar.

URL: https://hub.docker.com/r/bobuc05/fdd-imagen

## El digest

```text
docker inspect --format '{{index .RepoDigests 0}}' <tu-usuario>/<tu-imagen>
sha256:e3b0ba9e152a71cde7f2714902e1d85f99b937e275d1f2175fd8e102c409ae08
```

## Cómo la corro yo

Comando exacto:

```text

docker run --rm bobuc05/fdd-imagen:latest

```




Salida que debo esperar:

```text
Corriendo como: app
requests 2.32.3



```

## La prueba de que se baja del registro

Pega la salida **completa**, con sus líneas `Unable to find image locally` y
`Pulling from`:

```text
docker logout
docker rmi -f <tu-usuario>/<tu-imagen>
docker run --rm <tu-usuario>/<tu-imagen>

bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/08_contenedores$ docker logout
Removing login credentials for https://index.docker.io/v1/
bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/08_contenedores$ docker rmi -f bobuc05/fdd-imagen:latest 
Untagged: bobuc05/fdd-imagen:latest
Deleted: sha256:e3b0ba9e152a71cde7f2714902e1d85f99b937e275d1f2175fd8e102c409ae08
bobuc05@bobuc05-MCLG-XX:~/fdd/fdd_o26_RobertoUribeClemente/estudiantes/RobertoUribeClemente/08_contenedores$ docker run --rm bobuc05/fdd-imagen:latest
Unable to find image 'bobuc05/fdd-imagen:latest' locally
latest: Pulling from bobuc05/fdd-imagen
58d4fc4405a1: Pull complete 
096595c37430: Pull complete 
0bcf80ba6424: Pull complete 
d4026ac44a72: Pull complete 
04469b766c05: Pull complete 
44136fa355b3: Download complete 
913b86817895: Download complete 
Digest: sha256:e3b0ba9e152a71cde7f2714902e1d85f99b937e275d1f2175fd8e102c409ae08
Status: Downloaded newer image for bobuc05/fdd-imagen:latest
Corriendo como: app
requests 2.32.3



```

## El tamaño

Menos de 300 MB. Pega la salida con el tamaño visible:

```text
docker images <tu-usuario>/<tu-imagen>
IMAGE                       ID             DISK USAGE   CONTENT SIZE   EXTRA
bobuc05/fdd-imagen:latest   e3b0ba9e152a        195MB         47.7MB        


```
