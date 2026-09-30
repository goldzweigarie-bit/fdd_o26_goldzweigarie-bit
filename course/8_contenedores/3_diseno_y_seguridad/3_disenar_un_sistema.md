---
id: disenar-un-sistema
title: "Diseñar un sistema"
nav_title: "Diseñar un sistema"
summary: "El pipeline de la unidad 2 repartido en servicios, por qué la base casi nunca se parte, y Compose como el plano escrito."
status: ready
estimated_time: 15m
tags: [diseno, compose, pipeline, servicios, volumen, red, estado]
prerequisites: [el-contrato-de-un-servicio]
---

# Diseñar un sistema

**Página 3 de 5 · sección 3 de 3**

Meta: dibujar un sistema completo antes de escribirlo.

::: figure {#cont-pipeline-servicios title="El pipeline de la unidad 2, repartido en servicios"}
![El pipeline de la unidad 2 repartido en servicios dentro de una red propia: extracción, transformación y carga como tres contenedores sin estado, la base de datos con su named volume como el único que guarda algo, y el tablero que la lee. Cada flecha lleva rotulado el contrato por el que pasa —nombre y puerto, o variable de entorno— y sólo una cruza la línea del host, la del tablero, porque la base no publica puerto. Al margen, por qué la base casi nunca se parte, y qué sobrevive a un docker rm de cada pieza](../_assets/cont-pipeline-servicios.svg)
:::

## En corto

- Diseñar es decidir **cuántas cajas hay y qué promete cada una**, y eso se hace en papel antes de teclear nada.
- Casi todas las piezas de un pipeline **no tienen estado**: el estado se concentra a propósito en una sola, la base, y ahí se queda.
- **Compose es ese dibujo, escrito.** Sus tres secciones son las tres preguntas del contrato, una por una.

## El mismo pipeline, ahora con cajas

En [[pipeline-de-datos|la unidad 2]] el pipeline era una secuencia de etapas: se extraen los datos de algún lado, se transforman, se cargan a donde alguien los va a consultar. Era una idea, y corría como un programa en tu laptop. Ahora es un sistema, y lo primero que hay que decidir es **dónde caen los cortes**.

Las etapas de [[etl-y-elt]] ya venían cortadas: extraer, transformar y cargar tienen razones distintas para cambiar —la fuente cambia sin avisar, la regla de negocio cambia cuando alguien la discute, el destino casi nunca cambia— y ésa es exactamente la prueba de la página anterior. Faltan las dos piezas que no son etapas: **dónde quedan los datos** y **quién los mira**.

::: table {#cont-s3p3-tabla-sistema title="Cinco servicios, con su contrato y lo que sobrevive a un `docker rm`"}

| Servicio | Puerto | Variables | Volumen | Qué sobrevive a un `docker rm` |
|---|---|---|---|---|
| **extracción** | ninguno | de dónde baja, cada cuándo | ninguno | nada, y está bien |
| **transformación** | ninguno | ninguna, o la regla del día | ninguno | nada |
| **carga** | ninguno | nombre, usuario y contraseña de la base | ninguno | nada |
| **base de datos** | 5432, **sin publicar** | usuario, contraseña, nombre de la base | **sí**, un named volume | **todo**: los datos siguen ahí |
| **tablero** | 8501, **publicado al host** | nombre, usuario y contraseña de la base | ninguno | nada |

:::

Cuatro de las cinco filas dicen «nada» en la última columna, y eso es el diseño, no un descuido. Un servicio del que no sobrevive nada es un servicio que puedes **borrar y volver a crear a media noche sin pensarlo**: si se cuelga, lo matas; si cambia el código, lo reconstruyes; si el servidor se reinicia, arranca solo. Todo el cuidado se concentra en la única fila que dice «todo».

Y fíjate en la columna del puerto: de los cinco, **uno solo cruza la línea del host**, el tablero, porque es el único que una persona abre en su navegador. La base no la abre nadie de fuera; el tablero le habla por su nombre dentro de la red, como en [[la-red-y-el-nombre]].

## Por qué la base casi nunca se parte

Es la pregunta que siempre sale: si partir es bueno, ¿por qué no dos bases?

Porque **partir es barato exactamente donde no hay estado, y carísimo donde sí lo hay**. Dos contenedores de transformación son dos copias del mismo programa haciendo trabajo distinto; no se estorban porque no comparten nada. Dos contenedores de base de datos sobre el mismo volumen son dos programas escribiendo los mismos archivos, y eso no es escalar: es corromper. Postgres no está escrito para que dos servidores compartan un directorio de datos, y cuando de verdad hace falta más de una copia, la respuesta tiene nombre propio —replicación— y es un tema completo, con su propio protocolo, no una bandera de `docker run`.

La consecuencia de diseño: **si vas a partir mal una vez, que no sea la base.** Y por eso se le da el trato distinto: el volumen con nombre de [[named-volumes-y-postgres]], ningún puerto publicado, y el respaldo como una decisión aparte.

## El plano, escrito

Un sistema de cinco contenedores se puede levantar con cinco `docker run` largos, una red creada a mano y un volumen creado a mano. Funciona una vez, en tu máquina, si te acuerdas del orden. Lo que no hace es **existir en el repositorio**: si mañana alguien más lo tiene que levantar, lo que le entregas es un mensaje de chat con cinco comandos.

Compose es ese mismo dibujo, en un archivo que se versiona con Git:

```yaml
services:
  base:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: fdd
    volumes:
      - pgdata:/var/lib/postgresql/data
  tablero:
    image: tablero:1
    ports:
      - "8501:8501"
    environment:
      PGHOST: base
    depends_on:
      - base
volumes:
  pgdata:
```

Léelo contra la tabla de arriba y vas a reconocer todo: `ports` es la primera pregunta del contrato, `environment` es la segunda, `volumes` es la tercera. `PGHOST: base` es el nombre del servicio usado como dirección — Compose crea una red propia para el proyecto, así que el nombre resuelve por lo mismo que en la página 1.

**Esto no se teclea hoy.** Es el capítulo 4 de *Intermediate Docker*, y es la tarea de la semana que viene; aquí se lee para que, cuando lo escribas, ya sepas qué estás escribiendo. Un aviso para entonces, que sale de lo que ya te pasó en [[named-volumes-y-postgres]]: `depends_on` espera a que el contenedor **arranque**, no a que Postgres esté listo para aceptar conexiones. Es la misma espera que resolviste con `pg_isready`, y Compose no te la regala.

::: problem {#cont-s3p3-scraper-y-tablero title="Un scraper diario y un tablero, en papel"}
**En parejas, siete minutos, sin teclado.** Te piden un sistema que baje una vez al día los precios de una página pública, los guarde, y los enseñe en un tablero que se abre en el navegador.

Dibuja el diseño y entrega tres cosas:

1. **Cuántos contenedores son** y qué corre en cada uno.
2. **Qué red** hay y quién está en ella.
3. **El contrato de cada pieza**: puerto, variables, volumen.

Cuando lo tengas, pasa las **cuatro comprobaciones** del `answer` — una por una, con un sí o un no.
:::

::: hint {of="cont-s3p3-scraper-y-tablero"}
Empieza por la pregunta del estado: de todo lo que va a pasar en ese sistema, **¿qué tiene que seguir existiendo mañana?** Esa respuesta te da la única pieza que lleva volumen. Después pregúntate quién abre algo en un navegador: ésa es la única que publica puerto.
:::

::: answer {of="cont-s3p3-scraper-y-tablero"}
**El diseño de referencia: tres contenedores en una red propia.**

- **`scraper`** — corre, baja los precios, los escribe en la base y **termina**. No escucha en ningún puerto, no lleva volumen, y no está prendido las otras veintitrés horas del día. Que se dispare a diario lo decide algo de fuera: un `cron` en el host, o el programador del servidor.
- **`base`** — `postgres:16`, con su named volume y **sin `-p`**.
- **`tablero`** — lee la base y la sirve en el 8501, que es el único puerto publicado.

**Las cuatro comprobaciones:**

1. **¿La base publica puerto al host?** **No.** Sólo la alcanzan `scraper` y `tablero`, por su nombre dentro de la red. Si contestaste que sí, acabas de ofrecerle tu base de datos a toda la red del café.
2. **¿El scraper tiene volumen?** **No.** Lo que baja no se queda en su disco: lo escribe en la base, que es donde vive el estado. Si le pusiste volumen, tienes el estado en dos lugares y ninguno es la verdad.
3. **¿La configuración va por variable de entorno?** **Sí**, toda: el nombre de la base, el usuario, la contraseña y la URL que se raspa. Nada de eso va escrito dentro de la imagen, porque si va adentro no puedes correr la misma imagen contra la base de prueba y contra la de verdad.
4. **¿Qué sobrevive a un `docker rm` de cada servicio?** De `scraper`, nada. De `tablero`, nada. De `base`, **todo**, porque el volumen no es del contenedor. Ésa es la prueba de que el diseño está bien repartido: **puedes borrar dos de los tres contenedores sin perder un solo dato.**

Si tu diseño falla alguna de las cuatro, no está mal escrito: está mal repartido, y se arregla moviendo una caja, no cambiando código.
:::

Sigue con [[cuando-se-rompe-el-aislamiento]], que le da la vuelta al tablero: hasta aquí decidiste qué expones a propósito, y ahí se ve qué expones sin querer.

> [!NOTE]
> **Si sólo recuerdas una cosa:** concentra el estado en una sola pieza, publica un solo puerto, y escribe el dibujo en un archivo que se versione — todo lo demás del diseño sale de esas tres decisiones.
