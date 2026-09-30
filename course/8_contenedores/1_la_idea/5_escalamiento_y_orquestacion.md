---
id: escalamiento-y-orquestacion
title: "De uno a mil: escalamiento y orquestación"
nav_title: "Escalamiento y orquestación"
summary: "Por qué el mundo se movió a contenedores más allá de la reproducibilidad, y qué precio cobra correr N copias idénticas."
status: ready
estimated_time: 10m
tags: [escalamiento, replica, estado, orquestacion, kubernetes, desechable]
prerequisites: [anatomia-de-docker-run]
---

# De uno a mil: escalamiento y orquestación

**Página 5 de 9 · sección 1 de 3**

Meta: entender por qué el mundo se movió a esto, más allá de la reproducibilidad. Aquí se definen `estado` y `réplica`.

::: figure {#cont-escalamiento title="Lo que se rompe al pasar de una copia a cinco, y cómo se arregla"}
![Diagrama en tres bloques. Arriba, una sola copia del servicio con su archivo sesiones.db guardado adentro del contenedor: el usuario vuelve siempre al mismo proceso y al mismo archivo, y funciona. En medio, cinco réplicas idénticas de la misma imagen detrás de un repartidor de carga, cada una con su propio sesiones.db marcado en rojo; tres peticiones del mismo usuario caen en réplicas distintas y encuentran archivos distintos: unas no lo conocen porque su archivo está vacío y otras tienen otra cosa adentro, así que la sesión se pierde. Abajo, el mismo dibujo corregido: las cinco réplicas quedan sin estado y desechables, el estado sale a una caja compartida fuera de los contenedores, y el orquestador aparece rotulado como quien decide cuántas réplicas hay y repone la que muere](../_assets/cont-escalamiento.svg)
:::

## En corto

- La reproducibilidad es la mitad de la historia; la otra mitad es que un artefacto idéntico a sí mismo se puede correr **N veces a la vez**.
- Escalar con contenedores es **horizontal**: no se hace más grande una copia, se corren más copias iguales.
- El precio se paga de un solo golpe: si todas son intercambiables, **ninguna puede guardar estado adentro**.

## Dos palabras antes de empezar

::: definition {#cont-def-estado title="`estado` y `réplica`"}
El **`estado`** es lo que un proceso escribió y espera volver a leer después: una base de datos, un archivo que alguien subió, la sesión iniciada de un usuario. Todo lo demás —el código, la configuración, las librerías— es lo que el proceso *lee* pero nunca cambia, y por eso viaja bien dentro de una imagen.

Una **`réplica`** es una de las N copias idénticas de la misma imagen que corren a la vez. Idénticas de verdad: no hay una principal y unas secundarias, y para quien las usa da igual en cuál cayó.
:::

## Por qué el mundo se movió

En la página 1 el contenedor resolvía «en mi máquina sí funciona». **Eso solo no explica por qué se movió la industria entera**: el problema de la reproducibilidad ya tenía respuestas parciales, y ninguna arrastró a tanta gente.

Lo que sí lo explica es lo que viene **después** de sellar el artefacto.

::: table {#cont-tabla-escalar title="Las cinco ideas que hacen escalable a un contenedor"}

| Idea | Qué quiere decir |
|---|---|
| **La unidad es desechable** | un contenedor es idéntico a sus hermanos, así que se puede matar sin pensarlo y volver a levantar sin ceremonia |
| **Escalar es horizontal** | no se agranda una copia: se corren N réplicas de la misma imagen, y si sobra tráfico se corren más |
| **El precio** | con N copias idénticas, ninguna puede guardar estado adentro. **Tiene que vivir afuera** — y dónde exactamente es la sesión 2 entera |
| **Quién decide** | alguien tiene que decidir cuántas réplicas hay, repartirles el tráfico y reponer la que muere. Ese alguien es el **orquestador** |
| **Por qué se puede** | porque arrancar una réplica cuesta milisegundos. Veinte contenedores de **Podman** arrancan en 2.7 s; los mismos veinte en **Docker**, 5.5 s. Con máquinas virtuales serían minutos |

:::

> [!WARNING]
> Esas dos cifras salen de una medición propia, con su máquina, su kernel y sus versiones anotadas; el pie completo vive una sola vez en la unidad, en [[lo-que-cuesta|«Lo que cuesta»]], que es la página 9 de esta sección. Y una salvedad que aquella página exige decir cada vez: ese experimento es **una sola corrida por tamaño**, así que esos 2.7 y 5.5 s no son medianas y no sostienen un tiempo fino — sostienen el orden de magnitud. **Un número de benchmark sin su pie no vale nada**, y ése es medio contenido de aquella página.

## El precio, dicho en concreto

Imagina un servicio que guarda las sesiones de sus usuarios en un archivo, `sesiones.db`, **dentro** del contenedor. Con una sola copia funciona perfecto: cada petición cae en el mismo proceso y encuentra el archivo donde lo dejó.

**Arranca cuatro copias más y el servicio se rompe sin que ninguna falle.** Cada réplica tiene **su propia** capa de escritura, así que cada una tiene su propio `sesiones.db`, vacío al nacer:

- la primera petición del usuario cae en la réplica 2 y ahí queda su sesión;
- la segunda cae en la réplica 4, que no lo conoce, y lo manda a iniciar sesión otra vez.

**No hay error en los logs. Nada crashea.** Simplemente el sistema se comporta al azar, y qué tan mal se comporta depende de la suerte con la que se repartió el tráfico.

> [!NOTE]
> **Es la mitad de esta unidad: si el estado vive adentro del contenedor, las réplicas dejan de ser intercambiables, y si dejan de ser intercambiables no puedes escalar.** Sacarlo afuera —a una base de datos, a un caché compartido, a un volumen— es lo que las vuelve desechables de verdad.

![Vista aérea nocturna de un patio de maniobras en teal frío y blanco de reflector: cientos de módulos idénticos, todos del mismo molde, dispuestos en rejilla perfecta hasta donde alcanza la vista, con grúas pórtico moviéndose entre las filas. Al borde se alza una torre de control estrecha con una sola ventana encendida, y de ella sale un haz que barre filas enteras de golpe; la torre es diminuta frente al patio que gobierna.](../_assets/ilus-contenedores-escala.jpg)

## Quién decide: el orquestador

Con cinco réplicas puedes arrancarlas a mano. Con quinientas, repartidas en cuarenta máquinas, no. Alguien tiene que decidir:

- cuántas hay y en qué máquina cabe cada una,
- a cuál mandarle cada petición,
- qué hacer cuando una muere,
- y cómo subir de la versión vieja a la nueva sin apagar el servicio.

Ese trabajo tiene nombre —**orquestación**— y era la deuda que dejó abierta la página 1.

La herramienta que ganó se llama **Kubernetes**, y aquí termina lo que este curso va a decir de ella. **Es una deuda que no se paga, a propósito.** Kubernetes es un curso entero, y aprenderlo sin entender antes qué es un contenedor produce gente que copia manifiestos de internet sin saber qué está pegando.

Lo que sí te llevas es lo que hace falta para entrar por la puerta correcta el día que la necesites: **qué problema resuelve un orquestador, y por qué ese problema sólo existe cuando las unidades son desechables e idénticas.**

::: problem {#cont-p5-sesiones title="Tres copias y un archivo"}
Un servicio web guarda la sesión de cada usuario en `/app/sesiones.db`, un archivo dentro del contenedor. Hoy corre una sola copia y funciona bien. Mañana el tráfico crece y arrancas **tres** copias de la misma imagen detrás de un repartidor de carga.

1. ¿Qué se rompe, exactamente? Descríbelo desde el punto de vista de un **usuario**, no del servidor.
2. ¿Cuántos archivos `sesiones.db` hay ahora, y qué tienen adentro?
3. ¿Dónde debería vivir ese archivo para que las tres copias sirvan igual?
4. Y la pregunta que no es obvia: si mañana matas una de las tres, ¿se pierde algo?
:::

::: hint {of="cont-p5-sesiones"}
Vuelve a la página 3: cada contenedor arranca con **su propia** capa de escritura vacía encima de la misma imagen. Nadie comparte nada de lo que escribe. Ahora cuenta cuántas capas de escritura hay.
:::

::: answer {of="cont-p5-sesiones"}
**1.** El usuario inicia sesión, navega dos páginas y de pronto el servicio le pide iniciar sesión otra vez. Recarga y vuelve a estar dentro. No hay error, no hay caída: el comportamiento depende de en qué réplica cayó cada petición. **Eso es lo peor del bug — se ve como intermitencia, y se diagnostica tarde.**

**2.** Hay **tres** archivos, uno por capa de escritura, y los tres tienen cosas distintas: cada uno sólo conoce las sesiones de las peticiones que cayeron en su réplica.

**3.** Afuera de los tres contenedores, en un lugar que las tres réplicas vean igual: una base de datos, un caché de sesiones compartido, o —para el caso de un archivo— un volumen. Cuál de los tres y por qué es la decisión de la sesión 2.

**4.** Depende de dónde esté el estado:

| Dónde vive el estado | ¿Se pierde algo? |
|---|---|
| Con el archivo **adentro** | **sí**: se pierden las sesiones que esa réplica guardaba, y no hay forma de recuperarlas |
| Con el estado **afuera** | **no se pierde nada** — y ésa es exactamente la propiedad que buscas |

**Un contenedor es desechable sólo si tirarlo no tira información**; mientras guarde estado adentro no es desechable, es frágil disfrazado de moderno.
:::

Sigue con [[vm-contra-contenedor]], que dice dónde ocurre el aislamiento y cuándo el contenedor no es la respuesta.

> [!NOTE]
> **Si sólo recuerdas una cosa:** escalar es correr N copias idénticas, y eso sólo funciona si el estado vive afuera de todas ellas.
