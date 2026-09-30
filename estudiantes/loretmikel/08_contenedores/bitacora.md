# Bitácora de la unidad 08

## Quién soy

- Nombre: Mikel Loret
- Usuario de GitHub: loretmikel
- Usuario de Docker Hub: mldmy27

## Qué corrí

```text
$ docker version
Client:
 Version:           29.7.2
 API version:       1.55
 Go version:        go1.26.5
 Git commit:        a7dcaa6
 Built:             Wed Aug  5 18:27:50 2026
 OS/Arch:           darwin/arm64
 Context:           desktop-linux

Server: Docker Desktop 4.86.0 (236216)
 Engine:
  Version:          29.7.2
  API version:      1.55 (minimum version 1.40)
  Go version:       go1.26.5
  Git commit:       6a43e3d
  Built:            Wed Aug  5 18:28:35 2026
  OS/Arch:          linux/arm64
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

$ docker images
IMAGE                             ID             DISK USAGE   CONTENT SIZE   EXTRA
alpine:3.20                       d9e853e87e55       13.7MB         4.17MB        
cassandra:5.0                     ee178b38a274        567MB          171MB   U    
docker/welcome-to-docker:latest   c4d56c24da4f       22.9MB         6.35MB        
hello-world:latest                5e2309035332       22.6kB         10.3kB        
info-test:latest                  34ede046a879        139MB         28.9MB        
mldmy27/fdd-roto:latest           a9d14ecff183        195MB         47.7MB        
postgres:16                       a3b7f434b2dc        663MB          165MB        
postgres:17                       f4c66b820c6f        667MB          166MB        
python:3.12-slim                  2f17fc044b57        382MB           89MB        
roto:antes                        4078eb49a132       1.64GB          410MB        
roto:despues                      c6bdfc489d48        221MB           48MB        
ubuntu:24.04                      008173c23f95        141MB         30.9MB        

$ docker history mldmy27/fdd-roto
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
a9d14ecff183   9 minutes ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      9 minutes ago   USER app                                        0B        buildkit.dockerfile.v0
<missing>      9 minutes ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      9 minutes ago   RUN /bin/sh -c pip install --no-cache-dir -r…   13.3MB    buildkit.dockerfile.v0
<missing>      9 minutes ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      9 minutes ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      9 minutes ago   RUN /bin/sh -c useradd --create-home app # b…   81.9kB    buildkit.dockerfile.v0
<missing>      3 days ago      CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;  for src in idle3 p…   16.4kB    buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.4MB    buildkit.dockerfile.v0
<missing>      3 days ago      ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      3 days ago      RUN /bin/sh -c set -eux;  apt-get update;  a…   4.95MB    buildkit.dockerfile.v0
<missing>      3 days ago      ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      3 days ago      ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      4 days ago      # debian.sh --arch 'amd64' out/ 'trixie' '@1…   87.6MB    debuerreotype 0.17
```

## Los tres defectos de `roto/Dockerfile`

1. `FROM python:latest`: la base es la imagen completa y no fija versión, así que la imagen pesaba 1.64 GB (el límite es 300 MB) y cada build podía traer otro Python; la cambié a `python:3.12-slim` y quedó en 195 MB.
2. `COPY . .` iba antes de `pip install`, así que cualquier cambio al código invalidaba la caché y reinstalaba las dependencias en cada build; ahora copio primero `requirements.txt`, instalo, y al final copio el código, y al cambiar `app.py` el `pip install` sale `CACHED`.
3. El contenedor corría como root (`Corriendo como: root`), y si algo escapa del contenedor lo hace con privilegios de más; creé un usuario con `useradd` y agregué `USER app`, y ahora imprime `Corriendo como: app`.

## Una cosa que se me rompió

Mi primer `docker run hello-world` falló con `failed to connect to the docker API ... no such file or directory`. No era la instalación: Docker Desktop estaba cerrado y el daemon no corría. Lo abrí con `open -a Docker` y funcionó. Después, en `codigo/` no aparecían ni `08_contenedores` ni `docker` porque mi `main` estaba atrasado respecto al repo del curso; lo arreglé con `git fetch upstream` y `git merge --ff-only upstream/main`.
