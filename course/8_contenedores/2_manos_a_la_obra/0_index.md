---
id: contenedores-con-las-manos
title: "Manos a la obra"
nav_title: "2. Manos a la obra"
summary: "Dockerfile, imagen y contenedor, y dos laboratorios de qué cambia qué. Dónde vive cada byte de tu contenedor."
status: ready
tags: [docker, podman, volumen, bind-mount, dockerfile, registro]
---

# Manos a la obra

**Sección 2 de 3** · 16 páginas · 90 min de clase · unos 243 min si lees también las de referencia · sesión del martes 22 de septiembre, 19:00–20:30

Meta: saber, ante cualquier cambio, cuál de las tres cambió —Dockerfile, imagen o contenedor— y dónde vive cada byte que escribe un contenedor.

## Cómo se lee esta sección

- **Páginas 1 a 8: la clase.** En orden, con teclado. Es lo único que se recorre el martes.
- **Página 9 (con la 2/12): la entrega `tarea-08-imagen`.** Vencía hoy, antes de clase.
- **Páginas 10 a 16: referencia.** Instalar, planes B, Docker Hub, rutas y los casos raros del montaje. La clase no las recorre. Dos son base de lo que vence hoy: [[instalar-docker-y-podman|2/10]] (la tarea de instalar) y [[a-docker-hub|2/12]] (publicar la imagen de la entrega).

La instalación **ya no se ve en clase**: se da por hecha, igual que lo que trae DataCamp. Si algo de tu instalación sigue fallando, [[instalar-docker-y-podman|2/10]] y [[planes-b-de-instalacion|2/11]] siguen ahí.

## Las dieciséis páginas

| # | Página | Qué agrega | En clase | Min | Dónde |
|---:|---|---|---:|---:|---|
| 1 | [[repaso-dockerfile-imagen-contenedor]] | Tres cosas distintas, cada una cambia con su propio comando, y lo que escribe el contenedor en su capa no vuelve a la imagen | 8 | 8 | clase |
| 2 | [[ciclo-de-vida-de-un-contenedor]] | La única idea que explica todo el ciclo: un contenedor vive lo que vive su proceso | 12 | 12 | clase |
| 3 | [[el-dockerfile-por-dentro]] | Qué se lleva el `build`, de qué capas está hecha la imagen, `CMD` contra `ENTRYPOINT` | 10 | 15 | clase |
| 4 | [[donde-vive-cada-byte]] | La tabla que ordena toda la clase: capas de imagen, capa de escritura, bind mount, named volume | 6 | 10 | clase |
| 5 | [[lab-sin-volumen]] | Lab A: cambios sin montaje —en tu carpeta, en el Dockerfile, adentro, con `commit`— y qué ve cada quien | 20 | 25 | clase |
| 6 | [[lab-con-volumen]] | Lab B: bind mount y named volume sobre `/app`, y por qué un build puede no servir de nada | 18 | 30 | clase |
| 7 | [[named-volumes-y-postgres]] | Ver el estado sobrevivir a su contenedor, y morir con su volumen | 6 | 15 | clase |
| 8 | [[limpieza-de-docker]] | Recuperar el disco y saber qué se lleva cada `prune` | 5 | 12 | clase |
| 9 | [[arreglar-un-dockerfile]] | Reconocer y corregir los tres defectos de un Dockerfile real | — | 12 | entrega |
| 10 | [[instalar-docker-y-podman]] | Los dos runtimes corriendo sin `sudo`, en las tres plataformas | — | 25 | referencia · base de la tarea de instalar |
| 11 | [[planes-b-de-instalacion]] | Qué hacer si la instalación no salió: las trampas comunes y su síntoma | — | 12 | referencia |
| 12 | [[a-docker-hub]] | Publicar una imagen propia y comprobar que existe para los demás | — | 12 | referencia · base de la entrega |
| 13 | [[rutas-en-docker]] | Relativa contra absoluta, y por qué un `./` olvidado crea un volumen vacío en silencio | — | 10 | referencia |
| 14 | [[el-archivo-compartido]] | El bind mount en las dos direcciones, y de quién queda el archivo según tu plataforma | — | 15 | referencia |
| 15 | [[los-ocho-casos]] | Código en la imagen o en volumen, editado dentro o fuera, con o sin rebuild | — | 15 | referencia |
| 16 | [[las-cuatro-trampas]] | Los filos que cortan la primera vez, incluida la del volumen que copia en vez de tapar | — | 15 | referencia |

- **En clase** son los minutos de la sesión. Suman **85**: los otros 5 son llegada y cierre.
- Es un plan apretado. Si el tiempo no alcanza, los ejercicios de 2/2, 2/7 y 2/8 se quedan de tarea: los dos laboratorios no se recortan.
- **Min** es lo que tarda leerla sola, con calma.

## Antes de empezar

- Docker o Podman corriendo **sin `sudo`**. Si no, [[instalar-docker-y-podman|2/10]] antes que nada.
- Las imágenes de la clase ya descargadas: el prepull está en la misma página.
- DataCamp *Introduction to Docker* hecho: la clase arranca repasándolo, no enseñándolo.

## Qué te llevas

- Una respuesta para cada cambio: **¿cambió el Dockerfile, la imagen o el contenedor?**
- Qué hace un bind mount y qué hace un named volume sobre la misma carpeta, probado con tus manos.
- Un modelo de dónde vive cada byte, y por qué eso decide si sobrevive a un `docker rm`.

## Dónde vive cada cosa

Todo el trabajo de práctica —construir, romper, montar volúmenes— ocurre en `~/fdd/docker-lab`: una carpeta **local y desechable**, que **no es un repositorio** de Git. Se puede borrar y rehacer sin ninguna consecuencia. Nada de lo que hagas ahí se sube a ningún lado por sí solo.

Lo que sí se entrega llega a tu fork por pull request, igual que todo desde la unidad de Git y GitHub, y cae en **dos** carpetas distintas. Son dos porque las entregas del martes 22 nacen las dos de `main`: si escribieran en la misma carpeta, cada pull request agregaría su propia versión de los mismos archivos y el merge acabaría en conflicto. Separadas, los conjuntos no se tocan.

- `estudiantes/<tu-login>/docker/` **acumula tus certificaciones de DataCamp** a lo largo del mes: un solo `certificaciones.md`, que llenas una sección por entrega, más las capturas. Es espejo de `codigo/docker/`, exactamente como la unidad 7 hizo con `github/certificaciones.md`. Ahí van las tres entregas de DataCamp de esta unidad.
- `estudiantes/<tu-login>/08_contenedores/` **guarda el trabajo de la unidad**: tu imagen publicada, el `Dockerfile` arreglado y la bitácora. Es la carpeta de una sola entrega, la del `tarea-08-imagen`.

De ahí sale una regla que la revisión automática comprueba y que no tiene periodo de gracia: **cada pull request toca una sola de las dos**, nunca las dos a la vez.

## Lo que esta sección te debe

Igual que la anterior: lo que queda abierto, queda abierto a propósito, y cada cosa tiene su página.

| Lo que queda abierto | Se abre en | Se paga en |
|---|---|---|
| Estar en el grupo `docker` es ser `root` | 2/10 | 3/4 |
| De quién queda lo que escribe el contenedor, y los UID de Podman rootless | 2/6 | 2/7 y 2/14 |
| El código va dentro de la imagen en producción | 2/6 | 2/15, 2/16 y 3/2 |
| Todavía no publicamos ningún puerto | 2/7 | 3/1 |
| `docker cp` para sacar un archivo | 2/5, en la respuesta del problema, y una fila de la chuleta | **se delega a DataCamp**, *Intermediate Docker* cap. 1 |
