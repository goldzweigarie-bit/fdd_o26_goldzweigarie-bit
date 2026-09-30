---
id: el-contrato-de-un-servicio
title: "El contrato de un servicio"
nav_title: "El contrato de un servicio"
summary: "Qué es un microservicio sin decirlo como si fuera magia: el puerto que escucha, las variables que espera y el volumen que necesita."
status: ready
estimated_time: 15m
tags: [servicio, microservicio, contrato, estado, variables-de-entorno, volumen, diseno]
prerequisites: [la-red-y-el-nombre]
---

# El contrato de un servicio

**Página 2 de 5 · sección 3 de 3**

Meta: saber qué es un servicio, y qué tiene que estar escrito para poder cambiarlo sin romper a nadie.

::: figure {#cont-contrato title="Las tres cosas que un servicio promete, y lo que queda cuando no las promete"}
![Tres cajas colgando de un mismo contenedor, etiquetadas puerto que escucha, variables de entorno que espera y volumen que necesita, y a la derecha, por cada una, lo que le permite a quien lo consume: por dónde hablarle, cómo configurarlo sin reconstruir la imagen, y qué sobrevive a un docker rm. Debajo, el mismo servicio con las tres cajas en blanco y la etiqueta monolito repartido, que es lo que queda cuando el contrato no está escrito, y una línea que separa el servicio con estado del servicio sin estado, con el aviso de que partir cuesta red, despliegue y depuración](../_assets/cont-contrato.svg)
:::

## En corto

- **Un contenedor, un proceso, una responsabilidad.** No es purismo: es la consecuencia de que el contenedor viva exactamente lo que viva su proceso principal.
- El contrato de un servicio son **tres cosas**: qué puerto escucha, qué variables de entorno espera, qué volumen necesita.
- Si está escrito, la pieza se reemplaza sin tocar a nadie. Si no está escrito, no tienes servicios: tienes un **monolito repartido**, que es lo peor de los dos mundos.

## Un servicio es un programa al que se le habla por un puerto

No hace falta ninguna palabra nueva para esto. En [[la-red-y-el-nombre]] montaste una base de datos que no publicaba nada y otro contenedor le habló por su nombre. Eso ya era un servicio: **un programa que escucha en un puerto y contesta a quien le pregunta, sin que quien pregunta sepa nada de cómo está hecho por dentro.**

Quien usa Postgres no sabe en qué lenguaje está escrito, qué versión de `libc` tiene adentro ni dónde guarda sus archivos. Sabe tres cosas: le habla al nombre `pg` en el puerto 5432, le pasa un usuario y una contraseña, y lo que escriba va a seguir ahí mañana. Esas tres cosas son el contrato, y **todo lo demás es asunto privado del servicio**.

## Un contenedor, un proceso

La regla se oye dogmática hasta que se une con lo que ya sabes de [[ciclo-de-vida-de-un-contenedor|el ciclo de vida]]: el contenedor vive lo que vive su **proceso principal**, el `PID` 1 de adentro. Un contenedor con tres programas encima tiene tres formas de morir y una sola de decírtelo.

Peor aún, tiene un solo `docker logs` para las tres salidas revueltas, un solo estado en `docker ps` que no distingue cuál de los tres se cayó, y un solo `docker restart` que los reinicia a los tres para arreglar uno. La regla no es estética: **es que las herramientas que ya usas razonan por contenedor**, y si metes tres responsabilidades adentro, ninguna de ellas te sirve para ninguna.

## Las tres preguntas del contrato

::: table {#cont-s3p2-tabla-contrato title="Qué promete un servicio, y qué le permite a quien lo usa"}

| La pregunta | Qué fija | Qué te permite hacer |
|---|---|---|
| **¿Qué puerto escucha?** | por dónde se le habla, dentro de la red | cambiar el programa de adentro entero mientras siga contestando ahí |
| **¿Qué variables de entorno espera?** | cómo se configura, desde fuera | correr la **misma imagen** en tu laptop y en el servidor, apuntando a cosas distintas |
| **¿Qué volumen necesita?** | qué parte de lo que escribe tiene que sobrevivirle | borrar y recrear el contenedor sin perder nada |

:::

La segunda es la que más cuesta aceptar y es la que más paga. Configuración por variable de entorno significa que **la imagen no sabe en qué ambiente está**: no lleva adentro la contraseña de producción ni la ruta de tu laptop. Si la lleva, no la puedes publicar en [[a-docker-hub|un registro público]] y no la puedes reutilizar; cada ambiente se vuelve una imagen distinta, y volviste al problema de la página 1 de la unidad.

La tercera ya la contestaste con la mano en [[donde-vive-cada-byte]]: todo lo que el proceso escriba fuera de un volumen vive en la capa de escritura del contenedor y se va con él.

**Y ahí está la palabra que la unidad viene prometiendo.** Un **microservicio** no es «un servicio chico» y no se mide en líneas de código: es un servicio cuyo contrato cabe en esos tres renglones, de modo que quien lo usa no necesita leer su código para usarlo ni enterarse de que cambió por dentro. El «micro» no mide el programa, mide el contrato — y por eso un Postgres entero, que son cientos de miles de líneas, califica sin problema.

## Con estado y sin estado

Ésta es la línea que decide casi todo lo que viene en la página siguiente. Un servicio **sin estado** no guarda nada entre una petición y la siguiente: puedes correr cinco copias iguales y a nadie le importa en cuál cayó — son las [[escalamiento-y-orquestacion|réplicas]] de la sesión 1. Un servicio **con estado** guarda algo que espera volver a leer, y por eso no se multiplica alegremente: dos copias de una base de datos sobre el mismo volumen no son dos réplicas, son dos programas peleándose por los mismos archivos.

De ahí salen las dos reglas prácticas: **lo que no tiene estado se parte y se multiplica sin dolor; lo que tiene estado se parte una vez, con cuidado, y casi nunca se multiplica.**

## Cuándo **no** partir

Partir no es gratis, y presentar los microservicios como el final feliz de toda historia es venderle a un grupo de treinta personas una complejidad que ninguna de sus tareas necesita. Lo que cuesta partir, dicho sin adornos:

- **Cuesta red.** Lo que era una llamada a una función se vuelve una conexión que puede fallar, tardar o llegar a medias. Todas las fallas nuevas son fallas que antes no existían.
- **Cuesta despliegue.** Un programa se arranca; cinco servicios se arrancan **en orden**, con sus redes, sus volúmenes y sus variables. Esa es exactamente la razón por la que existe Compose.
- **Cuesta depuración.** El error ya no está en un archivo de bitácora, está repartido en cinco, y reconstruir qué pasó es un trabajo aparte.

La regla honesta: **parte cuando dos piezas tengan razones distintas para cambiar, para escalar o para caerse.** Un proceso que corre una vez al día y un programa que atiende peticiones todo el tiempo cumplen las tres. Dos funciones del mismo programa, ninguna.

::: problem {#cont-s3p2-tres-en-uno title="Un contenedor con tres cosas adentro"}
Te llega un contenedor que alguien ya tenía funcionando. Adentro corren, al mismo tiempo:

- un **cron** que a las 03:00 baja un archivo y lo procesa,
- un programa que **atiende peticiones** en el puerto 8000 y contesta con datos,
- y un **Postgres** que guarda todo, con sus archivos en `/var/lib/postgresql/data`, dentro del contenedor.

Funciona. Lo arrancas con un `docker run` y te da el puerto 8000.

1. Llega el triple de tráfico al 8000 y te piden correr **tres copias**. Escribe **qué se rompe**, y di si se rompe por el cron, por el que atiende o por la base.
2. **Pártelo.** Di cuántos contenedores son y qué corre en cada uno.
3. Para cada pieza, contesta **las tres preguntas del contrato**. Si una pieza no necesita algo, escribe «ninguno» — es una respuesta, no un hueco.
:::

::: hint {of="cont-s3p2-tres-en-uno"}
Para la 1, pregúntate qué pasa **tres veces** cuando corres tres copias, y cuál de las tres cosas de adentro no soporta pasar tres veces. Hay dos candidatas y fallan por razones distintas: una hace el trabajo repetido, la otra ni siquiera puede arrancar tres veces sobre los mismos archivos.
:::

::: answer {of="cont-s3p2-tres-en-uno"}
**1. Se rompen dos de las tres, y la que atiende peticiones no es ninguna.** El cron se dispara **tres veces a las 03:00**: baja el archivo tres veces y lo procesa tres veces, así que o duplica filas o pelea consigo mismo por el archivo a medio escribir. Y arrancan **tres Postgres**, cada uno con su propio directorio de datos adentro de su propio contenedor: son tres bases distintas, y la fila que escribiste en una no existe en las otras dos. El único que sí soporta tres copias es el que atiende el 8000, porque no guarda nada: es el que no tiene estado.

**2. Tres contenedores.** Uno para el que atiende peticiones, uno para el cron, uno para la base. La partición sale sola de la 1: **cada cosa que se rompió al multiplicarse es una pieza que tenía que estar aparte.**

**3. El contrato de cada uno:**

| Pieza | Puerto | Variables | Volumen |
|---|---|---|---|
| El que atiende | **8000**, y es el único que se publica al host | dónde está la base: nombre, usuario, contraseña | **ninguno** — no escribe nada que deba sobrevivirle |
| El cron | **ninguno**: nadie le habla, él habla | las mismas de la base, más de dónde baja el archivo | uno **sólo si** necesita guardar el archivo crudo; si no, ninguno |
| La base | **5432**, y **no** se publica: sólo la alcanzan los otros dos por su nombre en la red | usuario, contraseña, nombre de la base | **obligatorio**, en `/var/lib/postgresql/data` |

Léelo al revés y tienes el resumen de la página: la pieza sin estado se multiplica, la pieza con estado lleva volumen y no se multiplica, y el único puerto que cruza al host es el que alguien de fuera va a usar. Los tres «ninguno» son tan informativos como los datos: **un contrato escrito también dice lo que el servicio no necesita.**
:::

Sigue con [[disenar-un-sistema]], que toma estas tres preguntas y las aplica a un sistema completo —el pipeline de la unidad 2— antes de escribir una sola línea.

> [!NOTE]
> **Si sólo recuerdas una cosa:** un servicio es un programa con un contrato de tres renglones —puerto, variables, volumen— y lo que no está escrito en esos tres renglones no es un servicio, es un monolito repartido.
