---
id: contenedores
title: "Contenedores"
nav_title: "Contenedores"
summary: "Tres clases. Qué es un contenedor, cómo se usa en tu máquina, y cómo se reparte un sistema en servicios."
status: ready
estimated_time: 462m
tags: [docker, podman, contenedor, imagen, volumen, namespace, cgroup, kata, seguridad, diseno]
prerequisites: [git-y-github]
---

# Contenedores

![Muelle de carga nocturno visto desde una pasarela elevada: una hilera de bloques sellados e idénticos entre sí desciende por un haz de luz vertical y se acomoda, sin abrirse, sobre un camión, un vagón de tren y la cubierta de un barco alineados abajo; al fondo se recorta la silueta de una grúa portuaria, y en primer plano una figura de espaldas observa el descenso a contraluz contra el resplandor del muelle.](_assets/ilus-contenedores-portada.jpg)

**Tres clases** · 38 páginas · unos 462 min

## En corto

- **Un contenedor no es una máquina pequeña: es un proceso de Linux con la vista recortada y la despensa medida.** Comparte el kernel del host; los namespaces deciden qué puede ver, los cgroups deciden cuánto puede usar.
- Con Docker y Podman ya instalados, vas a construir una imagen, montarle un volumen y averiguar, cambio por cambio, qué cambió: el Dockerfile, la imagen o el contenedor.
- La unidad termina en diseño: cómo se reparte una aplicación en varios contenedores, y por dónde se rompe el aislamiento cuando algo sale mal.

## Las tres secciones

| # | Sección | Qué contesta | Sesión | Páginas | Min |
|---:|---|---|---|---:|---:|
| 1 | [[la-idea-del-contenedor]] | Qué es un contenedor, y qué pasa exactamente cuando escribes `docker run` | jueves 17 de septiembre, 19:00–20:00 | 9 | 106 |
| 2 | [[contenedores-con-las-manos]] | Dockerfile, imagen y contenedor, y dos laboratorios de qué cambia qué. Dónde vive cada byte de tu contenedor | martes 22 de septiembre, 19:00–20:30 | 16 | 243 |
| 3 | [[disenar-con-contenedores]] | Cómo se reparte una aplicación en servicios, y por dónde se rompe el aislamiento | jueves 24 de septiembre, 19:00–20:30 | 5 | 69 |

## Los cuatro anexos

No son lectura de una sesión: son las páginas que se consultan. La chuleta y el tablero de entregas conviene tenerlos abiertos.

| Anexo | Qué es | Cuándo lo abres | Min |
|---|---|---|---:|
| [[chuleta-contenedores]] | Los comandos de Docker y Podman lado a lado, y 19 errores con su causa y su arreglo | En clase, y cada vez que algo truene | 8 |
| [[entregas-contenedores]] | Las cinco entregas: qué vence cuándo, con qué branch y en qué carpeta | Antes de cada entrega | 9 |
| [[prompts-contenedores]] | Nueve prompts para estudiar con un modelo, y las seis afirmaciones falsas que esta unidad desarma | Cuando estudies por tu cuenta | 12 |
| [[contenedores-anidados]] | Docker dentro de Docker: qué se entrega a cambio, medido | Después de la sesión 3 | 15 |

La primera sesión es **corta y sin computadora**: 60 minutos, no 90. Las páginas se proyectan y no se teclea nada; el teclado empieza en la sesión 2.

## Cuánto trabajo hay fuera de clase

Además de las tres clases, la unidad pide ≈ 167 minutos de lectura —las páginas marcadas «lectura» o «entrega» dentro de cada sección, los cuatro anexos de referencia, y las dos de referencia que sostienen las entregas del martes 22: [[instalar-docker-y-podman|2/10]] y [[a-docker-hub|2/12]]— más **8 h 27 de DataCamp**, repartidas entre *Introduction to Docker* e *Intermediate Docker*. En total son **unas 11 horas en doce días**. Las otras cinco páginas de «referencia» de la sección 2 (≈ 67 min) no cuentan: se consultan cuando hacen falta. Es el número con el que decides, desde el jueves 17, cómo repartes el resto de tu semana.

## Los benchmarks de la unidad

Los seis scripts que miden lo que de verdad cuesta un contenedor —arranque, escala, ejecución, anidamiento y la comparación de runtimes OCI, más el que los corre todos— viven en `_assets/benchmarks/`, junto con los CSV ya medidos. [`code/analyze.py`](code/analyze.py) los lee y genera las cuatro gráficas que usa la unidad; es opcional, no es una entrega, y sigue el mismo patrón que el notebook publicado en la unidad de arquitectura de computadoras.

## Antes de empezar

Necesitas Git y GitHub: la primera entrega de esta unidad ya se hace por pull request, igual que el resto del curso desde la unidad anterior. Nada más hace falta todavía. Instalar Docker y Podman se hace antes de la sesión 2, con [[instalar-docker-y-podman|2/10]]: en la sección 2 es una página de referencia, no de clase.
