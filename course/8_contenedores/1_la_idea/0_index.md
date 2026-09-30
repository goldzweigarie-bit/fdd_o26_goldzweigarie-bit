---
id: la-idea-del-contenedor
title: "La idea"
nav_title: "1. La idea"
summary: "Qué es un contenedor, qué pasa cuando escribes docker run, y por qué el mundo se movió a esto."
status: ready
tags: [contenedor, namespace, cgroup, imagen, orquestacion]
---

# La idea

**Sección 1 de 3** · 9 páginas · unos 106 min · sesión del jueves 17 de septiembre, 19:00–20:00

Meta: que "proceso aislado" deje de ser una frase hecha, y que `docker run` deje de ser magia.

## En corto

- Sesión **sin computadora**: las páginas se proyectan y no se teclea nada.
- **Un contenedor es un proceso de Linux con la vista recortada y la despensa medida**: comparte el kernel del host y tiene su propia vista de archivos, procesos, red, usuarios y recursos.
- Tres páginas se ven en clase; las otras seis son lectura para completar antes de la sesión 2.

## Las nueve páginas

| # | Página | Qué agrega | Min | Dónde |
|---:|---|---|---:|---|
| 1 | [[en-mi-maquina-si-funciona]] | Qué problema resolvieron los contenedores, y la comparación con `venv`/conda | 8 | clase |
| 2 | [[que-es-un-contenedor]] | Namespaces y cgroups: qué ve un proceso contra cuánto puede usar | 12 | clase |
| 3 | [[receta-imagen-contenedor]] | Dockerfile, imagen y contenedor: las tres cosas que todo el mundo confunde | 10 | lectura |
| 4 | [[anatomia-de-docker-run]] | La cadena completa y medida: CLI, daemon, containerd, shim y runc | 12 | clase |
| 5 | [[escalamiento-y-orquestacion]] | Por qué el mundo se movió a esto, más allá de la reproducibilidad | 10 | lectura |
| 6 | [[vm-contra-contenedor]] | Dónde ocurre el aislamiento, y cuándo el contenedor no es la respuesta | 10 | lectura |
| 7 | [[docker-y-podman]] | La diferencia es arquitectónica, y qué compra exactamente correr sin daemon | 14 | lectura |
| 8 | [[capas-y-cache]] | Por qué un `build` a veces tarda tres segundos y a veces tres minutos | 15 | lectura |
| 9 | [[lo-que-cuesta]] | Números propios de arranque y ejecución, y cómo leerlos sin engañarte | 15 | lectura |

## Los 60 minutos de la sesión

| Cuánto | Qué | Con qué |
|---:|---|---|
| **3 min** | llegada y encuadre | |
| **8 min** | página 1, *En mi máquina sí funciona* | proyector |
| **18 min** | página 2, *Qué es un contenedor* | **papel**: el ejercicio de las hojas de `ls -la /proc/1/ns/` |
| **22 min** | página 4, *Qué pasa cuando escribes `docker run`* | **papel**: el ejercicio de la cadena de pie |
| **5 min** | cierre y qué queda de tarea | |

> [!NOTE]
> Suman **56**, no 60. Los cuatro minutos de diferencia son colchón **a propósito**: los dos ejercicios son de pie y con papel en las manos, y eso siempre se desborda.

## Antes de empezar

**Nada que instalar.** Esta sección corre entera sin terminal: instalar Docker y Podman vive en la sección siguiente, como página de referencia: [[instalar-docker-y-podman|2/10]].

## Lo que se reparte en clase

Nada que instalar no quiere decir nada que preparar: dos de los tres bloques de clase se hacen con papel en las manos, **y el papel hay que llevarlo impreso**. Esto es a la vez el aviso al grupo y la lista de quien imprime.

| Material | Cuánto | Para qué |
|---|---|---|
| La salida de `ls -la /proc/1/ns/` del host y la del contenedor, una junto a la otra | unas **15 hojas** | compararlas a mano — el ejercicio de la página 2 |
| Hojas rotuladas: `docker CLI`, `dockerd`, `containerd`, `shim`, `runc`, y una sexta que dice `proceso del contenedor` | **6 hojas** | la cadena de pie — el ejercicio de la página 4 |

La página 3 no pide nada impreso: se fue a lectura, y su ejercicio se hace a solas, con una hoja o con el editor abierto.

## Qué te llevas

- Un modelo mental de qué es un contenedor, **no una definición de memoria**.
- La cadena completa de lo que pasa al escribir `docker run`, y **qué queda vivo** cuando matas cada pieza.
- **Números propios** de cuánto cuesta arrancar y correr dentro de un contenedor.

## De dónde salen los números

Los números de esta sección vienen de **tres tandas de medición distintas**, y cada una lleva su propio pie con la máquina y las versiones con que se obtuvo:

| Tanda de medición | Qué contiene |
|---|---|
| Los benchmarks de arranque, escala, ejecución, anidamiento y escritura | del semestre pasado |
| La comparación de runtimes OCI de la página 7 | medida aparte, en otra máquina |
| Los inodos de namespaces de la página 2 | medidos ahora |

**No es un descuido: es la regla que la página 9 enseña con nombre y apellido.**

## Lo que esta sección te debe

Varias páginas abren una pregunta y **la dejan abierta a propósito**. No es descuido y no hace falta perseguirlas: cada una se paga en una página concreta, y aquí está dónde.

| Lo que queda abierto | Se abre en | Se paga en |
|---|---|---|
| Kata Containers | 1/2 | 3/5 |
| Orquestación | 1/1 | 1/5 |
| gVisor | 1/6 | 3/5 |
| Aislamiento máximo | 1/6 | 3/5 |
| Estado que sobrevive al contenedor | 1/1 | 2/7 |
| Bind mounts distintos en macOS y Windows | 1/6 | 2/6, y a fondo en 2/13 y 2/14 |
| `overlay` | 1/4 | 2/4 |
| El copy-up de la capa de escritura | 1/9 | 2/4 |
| Escribir en el socket de Docker es mandar sobre un proceso `root` | 1/4 | 3/4 |
| Que Docker no active user namespaces | 1/2 | 2/6, 2/14 y 3/4 |
| `CMD` contra `ENTRYPOINT` | 1/3 | 2/3 |
| El arranque no descomprime la imagen | 1/4 | 1/9 |
| `puerto`, con su definición completa | 1/2 | 3/1 |
| `pods` | 1/7 | 3/1 |
| **Kubernetes como herramienta** | 1/5 | **no se paga en este curso, a propósito** |
