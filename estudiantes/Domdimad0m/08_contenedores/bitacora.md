# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre: Dominique Ontiveros Arriaga
- Usuario de GitHub: Domdimad0m
- Usuario de Docker Hub: dominiqueont

## Qué corrí

```text
docker version

Client:
 Version:           29.6.2
 API version:       1.55
 Go version:        go1.26.5
 Git commit:        dfc4efb
 Built:             Thu Jul 16 16:11:35 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Desktop 4.85.0 (235549)
 Engine:
  Version:          29.6.2
  API version:      1.55 (minimum version 1.40)
  Go version:       go1.26.5
  Git commit:       3d80467
  Built:            Thu Jul 16 16:12:20 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.2.5
  GitCommit:        e53c7c1516c3b2bff98eb76f1f4117477e6f4e66
 runc:
  Version:          1.3.6
  GitCommit:        v1.3.6-0-g491b69ba
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0


docker images

IMAGE                              ID             DISK USAGE   CONTENT SIZE
dominiqueont/domdimad0m-info:v1    8ad06a32df0d        117MB         29.8MB
neo4j:latest                       dca31d0d938d       1.08GB          400MB
roto-arreglado:v1                  b0972bad920e        209MB         51.7MB


docker history dominiqueont/domdimad0m-info:v1

IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
8ad06a32df0d   6 hours ago   CMD ["./info.sh"]                               0B        buildkit.dockerfile.v0
<missing>      6 hours ago   RUN |1 BUILD_DATE=2026-09-17 /bin/sh -c chmo…   12.3kB    buildkit.dockerfile.v0
<missing>      6 hours ago   COPY info.sh . # buildkit                       12.3kB    buildkit.dockerfile.v0
<missing>      6 hours ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      6 hours ago   ENV BUILD_DATE=2026-09-17                       0B        buildkit.dockerfile.v0
<missing>      6 hours ago   ARG BUILD_DATE=2026-09-17                       0B        buildkit.dockerfile.v0
<missing>      6 days ago    /bin/sh -c #(nop) CMD ["/bin/bash"]              0B
<missing>      6 days ago    /bin/sh -c #(nop) ADD file:43d479b270bbaf479…   87.6MB
<missing>      6 days ago    /bin/sh -c #(nop) LABEL org.opencontainers.…    0B
<missing>      6 days ago    /bin/sh -c #(nop) ARG LAUNCHPAD_BUILD_ARCH      0B
<missing>      6 days ago    /bin/sh -c #(nop) ARG RELEASE                   0B
```

## Los tres defectos de `roto/Dockerfile`

1. La imagen base usaba `python:latest`. Esto hacía que la versión pudiera cambiar y además generaba una imagen más pesada. Lo cambié por `python:3.12-slim` para fijar la versión y reducir el tamaño.

2. Se hacía `COPY . .` antes de instalar las dependencias. Esto provoca que un cambio en el código pueda invalidar esa capa y obligar a instalar las dependencias otra vez. Separé primero `COPY requirements.txt .`, después `RUN pip install -r requirements.txt` y al final `COPY . .`.

3. No se especificaba un usuario, por lo que el programa se ejecutaba como `root`. Creé el usuario `app`, le di acceso a `/app` y agregué `USER app`. Lo comprobé con `docker run --rm roto-arreglado:v1 id`, que mostró `uid=1000(app)`.

## Una cosa que se me rompió

Al principio Docker estaba instalado en Windows, pero el comando no funcionaba desde mi terminal de WSL porque no estaba habilitada la integración. Después de activarla, Docker ya era reconocido, pero apareció un error de permisos al intentar conectarse a `/var/run/docker.sock`. Revisé mis grupos y vi que mi usuario no pertenecía al grupo `docker`. Lo agregué al grupo y después `docker version` ya pudo mostrar tanto Client como Server.
