# Bitácora de la unidad 08

Llena este archivo en **tu copia**, dentro de
`estudiantes/<tu-login>/08_contenedores/`. No edites el original.

## Quién soy

- Nombre:Juan Pablo Medina Esquivel
- Usuario de GitHub:jpmedinae
- Usuario de Docker Hub:jpmedinae

## Qué corrí

Pega la salida de estos tres comandos, tal como te respondieron:

```text
docker version
Client: Docker Engine - Community
 Version:           29.8.1
 API version:       1.56
 Go version:        go1.26.8
 Git commit:        4a63305
 Built:             Tue Sep 15 16:25:42 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.8.1
  API version:      1.56 (minimum version 1.40)
  Go version:       go1.26.8
  Git commit:       464cd50
  Built:            Tue Sep 15 16:25:42 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.3.5
  GitCommit:        1294c24a7da8e5a793ed378161673abe94118892
 runc:
  Version:          1.5.1
  GitCommit:        v1.5.1-0-g8f2685a4
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

docker images
IMAGE                               ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest                  5e2309035332       25.9kB         9.49kB
jp-roto:1                           1d5ec10ebb3a       86.5MB           21MB
jpmedinae/info-fuentes-de-datos:1   9f73a8d546fe        117MB         29.8MB

docker history <tu-usuario>/<tu-imagen>
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
9f73a8d546fe   6 minutes ago   CMD ["./info.sh"]                               0B        buildkit.dockerfile.v0
<missing>      6 minutes ago   RUN /bin/sh -c chmod +x info.sh # buildkit      12.3kB    buildkit.dockerfile.v0
<missing>      6 minutes ago   COPY info.sh . # buildkit                       12.3kB    buildkit.dockerfile.v0
<missing>      6 minutes ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      10 days ago     /bin/sh -c #(nop)  CMD ["/bin/bash"]            0B
<missing>      10 days ago     /bin/sh -c #(nop) ADD file:43d479b270bbaf479…   87.6MB
<missing>      10 days ago     /bin/sh -c #(nop)  LABEL org.opencontainers.…   0B
<missing>      10 days ago     /bin/sh -c #(nop)  ARG LAUNCHPAD_BUILD_ARCH     0B
<missing>      10 days ago     /bin/sh -c #(nop)  ARG RELEASE                  0B

```

## Los tres defectos de `roto/Dockerfile`

Uno por línea: qué estaba mal, qué consecuencia tiene, y qué cambiaste.

1. La versión de python: en vez de la latest le puse 3.13.7-alpine3.22
2. COPY copia antes de instalar dependencias: separé COPY requirements.txt de COPY app.py
3. Se ejecutaba con root, le puse el usuario appuser.

## Una cosa que se me rompió

Tres o cuatro líneas sobre algo que te haya salido mal durante la unidad y cómo
lo resolviste. Si de verdad no se te rompió nada, dilo y explica qué parte te
costó más entender.
No se rompió nada, sólo me costó entender los problemas de roto.
