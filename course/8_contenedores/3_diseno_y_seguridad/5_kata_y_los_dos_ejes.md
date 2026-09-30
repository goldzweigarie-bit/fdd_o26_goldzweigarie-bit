---
id: kata-y-el-espectro
title: "Kata y los dos ejes"
nav_title: "Kata y los dos ejes"
summary: "No es un espectro de aislamiento: son dos ejes que se componen, y rootless sólo mueve uno de ellos."
status: ready
estimated_time: 12m
tags: [kata, gvisor, rootless, aislamiento, kernel, kvm, user-namespace]
prerequisites: [cuando-se-rompe-el-aislamiento]
---

# Kata y los dos ejes

**Página 5 de 5 · sección 3 de 3**

Meta: cerrar la pregunta que abrió la sesión 1 —qué haces cuando compartir el kernel no es aceptable— sin enseñar un orden falso.

::: figure {#cont-s3p5-espectro title="Los dos ejes, desarmados: dónde aterriza la syscall, y con qué privilegio sales"}
![Rejilla de dos ejes que ordena las opciones de aislamiento. El eje horizontal pregunta dónde aterriza la syscall que no controlas y va de izquierda a derecha: proceso suelto y contenedor, que la mandan directo al kernel del host; gVisor, que la manda a un núcleo en espacio de usuario que reimplementa la interfaz de syscalls de Linux; Kata, que la manda a un segundo kernel real dentro de una VM ligera; y la VM completa, que la manda a un kernel invitado detrás del hipervisor. El eje vertical pregunta qué privilegio tiene quien se escapa, y va de root en el host abajo a un usuario sin privilegios con su rango de subuid arriba. Contenedor rootful y contenedor rootless ocupan la misma columna y sólo se separan en el eje vertical, con una flecha corta que marca que rootless mueve un eje y no el otro; gVisor aparece dos veces, una a cada altura, porque tiene su propio modo rootless. Al pie, la conclusión: rootless no añade ninguna frontera, mismo kernel y misma superficie de syscalls, y los dos ejes se componen en vez de ordenarse](../_assets/cont-espectro.svg)
:::

## En corto

- **No es un espectro, son dos ejes**: *dónde aterriza la syscall que no controlas* y *qué privilegio tiene quien se escapa*. Ponerlos en una sola recta enseña dos cosas falsas de un golpe.
- **Rootless mueve sólo el segundo.** Mismo kernel, misma superficie de syscalls, ninguna frontera nueva.
- **Kata** pone un segundo kernel real debajo del contenedor, sin cambiar tu Dockerfile — y por eso necesita virtualización por hardware.

## Los dos ejes

Es la misma rejilla que [[vm-contra-contenedor|la sesión 1]] te enseñó de lejos; aquí se desarma.

**Eje A — ¿dónde aterriza la syscall que no controlas?** Si el código que corres resulta hostil, va a pedirle algo al kernel. La pregunta es a **cuál** kernel:

```text
proceso suelto  ·  contenedor  →  gVisor  →  Kata  →  VM completa
     ↑                ↑             ↑          ↑          ↑
 kernel del      kernel del     un núcleo   un segundo  un kernel
 host, directo   host, filtrado en espacio  kernel real invitado tras
                 por seccomp    de usuario  en una VM   el hipervisor
```

**Eje B — ¿qué privilegio tiene quien se escapa?** Va de `root` en el host, abajo, a un usuario sin privilegios con su rango de *subuid*, arriba. No dice nada de qué tan difícil es escaparse: dice **dónde caes** si lo logras.

Y ahora la parte que casi todas las explicaciones arruinan: **el contenedor *rootful* y el contenedor *rootless* caen en el mismo punto del eje A.** Los dos hablan con el kernel del host, con la misma lista de syscalls y el mismo filtro. Rootless mueve sólo el eje B. No añade ninguna frontera; cambia con qué identidad sales si atraviesas la que ya había.

De ahí salen las dos cosas falsas que enseña la recta única. Una: que rootless «aísla más», cuando no aísla distinto, sino que abarata la consecuencia. Dos: que la recta va de más a menos densidad —cada paso cuesta memoria y arranque—, y rootless **no cuesta densidad**, así que no cabe en esa recta ni siquiera como paso barato. La prueba de que son ejes y no una línea es que **gVisor tiene su propio modo rootless**: si fueran puntos de la misma recta, esa combinación no existiría. Se componen; no se ordenan.

## Y rootless tampoco sale gratis

El matiz que conviene decir en voz alta, porque el resto de esta página se lee como un elogio a rootless: para que un usuario sin privilegios pueda crear sus propios namespaces, el kernel tiene que permitir **user namespaces no privilegiados**, y eso **abre** interfaces del kernel que normalmente están restringidas a `root`. Es superficie que antes no estaba disponible para un usuario común.

No es un argumento teórico: **Ubuntu 24.04 restringe esos user namespaces por omisión**, y Red Hat advierte en su documentación que aplicar esa misma restricción **rompe justamente los contenedores rootless de Podman**. Las dos posturas son defendibles y las dos están en distribuciones que vas a usar. La lectura correcta no es «rootless es seguro» ni «rootless es inseguro», es la de siempre: **cada capa que pones cambia la forma de la superficie, no sólo su tamaño.**

## Kata: un kernel propio por sandbox

Kata Containers es la respuesta al caso que la sesión 1 dejó pendiente. Arranca una **máquina virtual ligera por sandbox** —un pod, o un contenedor suelto si lo corres sin Kubernetes— con su propio kernel adentro, y corre tu contenedor ahí.

Lo importante para ti es lo que **no** cambia: Kata es compatible con OCI, así que es un runtime que se elige al correr. La imagen es la misma, el Dockerfile es el mismo, el `docker run` es casi el mismo. **Cambias el runtime, no tu trabajo.**

Lo que sí exige es **virtualización por hardware**, que en la práctica quiere decir `/dev/kvm`. Y de ahí sale por qué no es el runtime de este curso:

- **Kata es Linux.** No hay binarios para macOS, y no es un descuido que alguien vaya a corregir: es un runtime que habla con el kernel de Linux y con KVM.
- El argumento que siempre aparece —«es por Apple Silicon»— **es falso desde hace tiempo**: la virtualización anidada en Apple Silicon existe **desde el M3, con macOS 15**. Lo que falta no es el hardware, es que Docker Desktop le exponga `/dev/kvm` a su propia VM.

Así que en el salón, con treinta laptops de tres sistemas operativos distintos, Kata se explica y no se instala. Lo que sí se puede mirar es en qué se nota.

## Cómo se ve la diferencia, en una línea

Ésta es la demostración, proyectada. En un contenedor normal:

```text
$ uname -r
6.17.9-76061709-generic
$ docker run --rm alpine:3.20 uname -r
6.17.9-76061709-generic
```

**El mismo número, exactamente.** No es que se parezcan: es el mismo kernel, como lleva diciendo la unidad desde la primera sesión. Un contenedor bajo Kata contesta **otra cosa** en esa segunda línea —la versión del kernel que Kata arranca dentro de su VM, que no tiene por qué parecerse a la tuya—, y ése es el punto entero: si `uname -r` cambia, hay un segundo kernel de por medio, y una syscall hostil aterriza ahí y no en el tuyo.

## De gVisor, sólo lo que se sostiene

gVisor ocupa la casilla intermedia del eje A porque no pone un kernel real: **reimplementa la interfaz de syscalls de Linux en espacio de usuario** y atiende ahí las llamadas. Dos cosas que hay que decir con él, y ninguna es un eslogan:

- **No implementa todas las syscalls.** Hay programas que simplemente no corren, y eso se descubre probando, no leyendo.
- Sus propios autores advierten explícitamente que **usar hardware de virtualización no hace a un sistema más seguro por sí mismo**. Es la advertencia que mejor resume esta página: la frontera no vale por la tecnología que la implementa, vale por lo que deja pasar.

::: problem {#cont-s3p5-cuatro-escenarios title="Cuatro escenarios, un runtime cada uno"}
Para cada escenario elige **qué corres**: contenedor normal, contenedor rootless, gVisor, Kata o máquina virtual completa. Una línea de razón, y la razón tiene que nombrar **cuál de los dos ejes** te movió.

1. **Tu laptop**, haciendo la tarea de esta unidad.
2. **El servidor de integración continua del curso**, que construye el sitio en cada pull request.
3. **Un servicio que vendes**, donde tus clientes suben código suyo y tú lo corres.
4. **El clúster del ITAM**, compartido por varias materias y varios equipos.
:::

::: hint {of="cont-s3p5-cuatro-escenarios"}
Antes de elegir, contesta para cada uno: **¿quién escribió el código que voy a correr?** Si lo escribiste tú o alguien de tu equipo, el eje A casi nunca se mueve. Si lo escribió un desconocido, el eje A es toda la pregunta.
:::

::: answer {of="cont-s3p5-cuatro-escenarios"}
**1. Tu laptop: contenedor normal, y rootless cuando puedas.** El código es tuyo. No hay nada que aislar de ti mismo, así que el eje A no se mueve. Rootless mueve el eje B y es gratis en densidad: es la mejor compra de la lista, no porque te proteja de tu propio código, sino porque el día que corras algo ajeno sin pensarlo, ya estabas un escalón arriba.

**2. El CI del curso: contenedor normal, en una máquina desechable.** Corre código de pull requests, o sea código que no controlas — pero el eje A se paga distinto aquí: lo que protege no es un segundo kernel, es que **la máquina entera se tira** al terminar. Es también el único lugar donde la unidad admite banderas que la página anterior te prohibió, y eso se cobra en el anexo de contenedores anidados.

**3. El servicio que vendes: Kata, o gVisor.** Aquí sí se mueve el eje A, y es el único de los cuatro donde se mueve de verdad. Estás corriendo código de clientes que no conoces, junto al de otros clientes, en la misma máquina; el kernel compartido es tu superficie de ataque y Dirty Pipe es el ejemplo de por qué. **Éste es el escenario que la sesión 1 dejó abierto** cuando dijo que hay una deuda que sí se paga: correr código que no escribiste tú y que podría ser hostil. Se paga aquí, y se paga con un segundo kernel.

**4. El clúster del ITAM: contenedor normal con todo lo de la página anterior puesto, y rootless donde se pueda.** Compartido no es hostil: los equipos son identificables y responden por lo que suben. Lo que hay que resolver son cuotas, permisos y aislamiento entre proyectos —eje B— y no un kernel por equipo. Poner Kata aquí es pagar densidad y complejidad por una amenaza que no es la tuya, y eso también es un error de diseño.

Lee las cuatro respuestas juntas: **en tres de los cuatro escenarios el eje A no se movió.** El segundo kernel no es el final de un camino que todos deban recorrer; es la respuesta a una pregunta concreta —*¿de quién es el código?*— y cuando ésa no es tu pregunta, es puro costo.
:::

Con esto cierra la unidad: un contenedor es un proceso con la vista recortada, lo sabes construir y montar, sabes repartir un sistema en servicios con su contrato, y sabes por dónde se rompe el aislamiento y qué hay del otro lado. Sigue con [[chuleta-contenedores|la chuleta de comandos]], [[prompts-contenedores|los prompts para seguir preguntando]], [[contenedores-anidados|los contenedores anidados]] y [[entregas-contenedores|el tablero de entregas]]: son referencia, no lectura corrida, y están para volver a ellos.

> [!NOTE]
> **Si sólo recuerdas una cosa:** rootless cambia con qué privilegio sales, Kata cambia a qué kernel le hablas, y son preguntas distintas — sólo la segunda se resuelve con un segundo kernel.
