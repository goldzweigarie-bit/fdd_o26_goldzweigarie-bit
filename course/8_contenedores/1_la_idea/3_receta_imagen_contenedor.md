---
id: receta-imagen-contenedor
title: "Receta, congelado, servido"
nav_title: "Receta, imagen, contenedor"
summary: "Dockerfile, imagen y contenedor son tres cosas distintas, y confundirlas produce dos fallas que le pasan a todo el mundo."
status: ready
estimated_time: 10m
tags: [dockerfile, imagen, contenedor, build, run, capas]
prerequisites: [que-es-un-contenedor]
---

# Receta, congelado, servido

**Página 3 de 9 · sección 1 de 3**

Meta: separar las tres cosas que todo el mundo confunde.

::: figure {#cont-tres-abstracciones title="La receta, el platillo congelado y el platillo servido"}
![Tres paneles en fila, cada uno con su analogía arriba y su término técnico abajo: la receta escrita es el Dockerfile, el platillo congelado es la imagen y el platillo servido es el contenedor, unidos por las flechas docker build y docker run. Del platillo congelado salen tres platos servidos idénticos, para que se vea que de una sola imagen salen muchos contenedores; bajo la imagen va la etiqueta inmutable y bajo los contenedores, efímeros](../_assets/cont-tres-abstracciones.svg)
:::

## En corto

- **Dockerfile** es la receta que escribes, **imagen** es el platillo congelado que sale de `docker build`, **contenedor** es el platillo servido que sale de `docker run`.
- De **una** imagen salen **muchos** contenedores; la imagen es inmutable y cada contenedor es efímero.
- Las dos fallas más comunes del primer día son la misma confusión vista de los dos lados.

## Dos fallas que produce confundirlas

| Lo que dices | Lo que pasó |
|---|---|
| «**Cambié el Dockerfile y no cambió nada.**» | El contenedor **no lee tu Dockerfile**. Corre sobre una imagen que se construyó antes, y mientras no la vuelvas a construir sigue siendo la de antes. **Cambiar la receta no descongela el platillo** |
| «**Instalé una librería dentro del contenedor y al volver a arrancarlo ya no estaba.**» | Lo que instalaste se escribió en el **platillo servido**, y ese plato se tira. **La instalación tiene que entrar en la receta, no en el plato** |

Las dos se disuelven solas en cuanto las tres cosas dejan de ser una.

::: table {#cont-tabla-tres title="Las tres, una por columna"}

| Pieza | Qué es | De dónde sale | Cuántas hay |
|---|---|---|---|
| **Dockerfile** | texto plano que tú escribes y versionas en Git, como cualquier archivo del proyecto | lo escribes tú | una receta por proyecto |
| **Imagen** | un sistema de archivos ya armado, de sólo lectura, con todo lo que tu programa necesita | `docker build` | una por construcción, identificada por su hash |
| **Contenedor** | un proceso corriendo sobre su propia copia de escritura de esa imagen | `docker run` | los que quieras, todos de la misma imagen |

:::

![Cocina industrial vacía de madrugada vista a lo largo del pase, en azul hielo a la izquierda y ámbar cálido a la derecha: una ficha escrita a mano cuelga de un riel de acero, al centro un bloque sellado y opaco duerme cubierto de escarcha tras el cristal de un arcón, y bajo las lámparas cálidas tres platos servidos exactamente iguales humean alineados; una figura de espaldas, en silueta, mira los tres platos.](../_assets/ilus-contenedores-receta.jpg)

## Inmutable de un lado, efímero del otro

Esas dos palabras son el corazón de la página, y cada una explica una de las fallas de arriba.

**La imagen es inmutable. No existe «editar una imagen».** Cambias el Dockerfile, construyes otra vez y lo que obtienes es **otra** imagen, con otro hash, aunque le pongas la misma etiqueta.

Eso es lo que la vuelve un artefacto transportable: si dos máquinas corren la misma imagen, corren **exactamente los mismos bytes**, y no hay forma de que una se haya modificado a medio camino. Es el contenedor sellado de la página 1.

**El contenedor es efímero.** Cuando arranca, el runtime **no copia la imagen**: le pone encima una capa de escritura vacía, y todo lo que el proceso escriba cae ahí. Borras el contenedor y esa capa se va con él, mientras la imagen queda intacta debajo.

> [!TIP]
> Por eso puedes arrancar tres, diez o mil contenedores de la misma imagen **sin multiplicar nada**: comparten la parte de sólo lectura y cada uno pone su propia capa de encima.

Y por eso, también, la pregunta que deja abierta esta página es **dónde va lo que sí quieres conservar**. Si la despensa se tira con el plato, tus datos no pueden vivir en el plato. **Eso es la sesión 2 entera.**

## ¿Y qué corre cuando se sirve el plato?

Es la pregunta que sigue, y ya tienes media respuesta: **lo dice la receta.**

La otra mitad es que hay **dos** formas de escribirlo —`CMD` y `ENTRYPOINT`— y que la diferencia entre ellas sólo se asoma cuando le pasas argumentos a `docker run`: **una se deja reemplazar y la otra no.**

> [!NOTE]
> Esa frase, leída, no se queda; escrita de las dos formas, corrida y comparada, no se olvida. Por eso vive en la clase del martes, donde hay teclado, y no aquí.

Por la misma razón, las ocho instrucciones de Dockerfile que de verdad vas a usar viven en **la chuleta de la unidad**: eso es referencia, se consulta y no se memoriza.

**Lo que esta página quiere que cargues es la analogía.**

::: problem {#cont-p3-dos-columnas title="Parte el Dockerfile en dos columnas"}
Copia este Dockerfile donde te acomode —una hoja, tu editor, el margen de esta página—:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY app.py .
RUN pip install pandas
CMD ["python", "app.py"]
```

Ahora acomoda las cinco líneas en **dos columnas**:

- a la izquierda, las que ocurren cuando **se construye la imagen** (`docker build`);
- a la derecha, las que ocurren cuando **se arranca un contenedor** (`docker run`).

Una de las cinco **no cabe entera en una sola columna**. Escríbela en las dos y anota, en media línea, qué hace de cada lado.
:::

::: hint {of="cont-p3-dos-columnas"}
Pregúntate línea por línea: ¿esto **se ejecuta** mientras se cocina el platillo, o es una **nota escrita en la etiqueta** para quien lo va a servir? Y revisa si alguna de las cinco hace las dos cosas.
:::

::: answer {of="cont-p3-dos-columnas"}
Cuatro de las cinco caen limpias:

| Instrucción | Columna | Qué hace |
|---|---|---|
| `FROM`, `COPY`, `RUN pip install` | **build** | se ejecutan al construir y dejan su resultado congelado en la imagen: la base, tu archivo copiado y `pandas` ya instalado. Cuando alguien corra esa imagen, `pip` **no vuelve a correr** — ya corrió, hace rato, en otra máquina si hace falta |
| `CMD` | **run** | la única que **no ejecuta nada** durante el `build`: se apunta en la imagen como «el comando por defecto» y se dispara cuando nace un contenedor. Es, literalmente, la nota en la etiqueta del platillo congelado |

**Y `WORKDIR` va en las dos, que es el punto del ejercicio.** Actúa durante el `build` —el `COPY` y el `RUN` que siguen ocurren dentro de `/app`— y además queda anotada en la imagen como el directorio de trabajo con el que arranca el contenedor.

Si la escribiste de los dos lados, **no te equivocaste: ésa es la respuesta**.

Y es lo que hay que entender: **el Dockerfile no es un script que se ejecuta de arriba a abajo una vez.** Es una receta, y parte de la receta son instrucciones **para quien sirve el plato**, no para quien lo cocina.
:::

Ya sabes que un contenedor es una imagen puesta a correr. Sigue con [[anatomia-de-docker-run]], que abre esa frase por la mitad: quién hace qué, y en qué orden, entre que tecleas `docker run` y el proceso existe.

> [!NOTE]
> **Si sólo recuerdas una cosa:** la imagen es inmutable y el contenedor es efímero; si quieres cambiar algo, cambias la receta y vuelves a construir.
