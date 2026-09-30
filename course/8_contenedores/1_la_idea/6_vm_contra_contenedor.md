---
id: vm-contra-contenedor
title: "VM contra contenedor"
nav_title: "VM contra contenedor"
summary: "Dónde ocurre el aislamiento en cada uno, tres casos en los que el contenedor no es la respuesta, y por qué en macOS y Windows siempre hay una VM de por medio."
status: ready
estimated_time: 10m
tags: [vm, hipervisor, kernel, aislamiento, gvisor, kata, macos, windows]
prerequisites: [escalamiento-y-orquestacion]
---

# VM contra contenedor

**Página 6 de 9 · sección 1 de 3**

Meta: entender dónde ocurre el aislamiento, y cuándo el contenedor no es la respuesta.

::: figure {#cont-vm-vs-contenedor title="Dónde está la frontera del aislamiento en cada pila"}
![Dos pilas lado a lado sobre el mismo hardware. A la izquierda, tres máquinas virtuales: cada una lleva su proceso, un sistema operativo completo con init, librerías y paquetes, y su propio kernel invitado; las tres se apoyan en un hipervisor —KVM, QEMU o Hyper-V— que está resaltado como la frontera del aislamiento. A la derecha, tres contenedores: cada uno lleva sólo su proceso y su rootfs con lo que se pidió, y los tres se apoyan directamente en un único kernel del host, también resaltado, porque ahí está la frontera de ese lado. Un recuadro enumera lo que el contenedor no lleva: ningún kernel invitado, ningún sistema operativo completo, ningún hipervisor. Al pie, una franja comparativa de tres filas: arranque, decenas de segundos contra cientos de milisegundos; tamaño en disco, gigabytes contra decenas o cientos de megabytes; y un bug del kernel, que en la VM tumba al invitado mientras el host sigue, y del lado del contenedor cae el kernel de todos porque no hay un segundo kernel](../_assets/cont-vm-vs-contenedor.svg)
:::

## En corto

- La diferencia no es de tamaño: es **dónde está la frontera**. En la VM la pone el hipervisor, debajo de un kernel invitado; en el contenedor la pone el kernel del host, que es uno solo para todos.
- Todo lo bueno del contenedor —arranca en milisegundos, pesa megabytes— sale de no llevar kernel propio, y todo lo malo también.
- Hay tres casos en los que la respuesta correcta sigue siendo una máquina virtual.

## La misma tabla, leída dos veces

::: table {#cont-tabla-vm title="Máquina virtual contra contenedor"}

| Criterio | Máquina virtual | Contenedor |
|---|---|---|
| Qué aísla | hardware virtual completo, con su hipervisor | vistas del kernel: namespaces y cgroups |
| Kernel | uno **propio** por cada VM | el del host, **compartido** por todos |
| Qué arranca | un sistema operativo entero, desde cero | un proceso |
| Arranque | decenas de segundos | cientos de milisegundos |
| Tamaño en disco | gigabytes | decenas o cientos de MB |
| Costo mientras corre | el del sistema operativo invitado, siempre encendido | el de tu proceso y nada más |
| Un bug del kernel | cae el invitado; el host sigue | cae el kernel de todos: **no hay un segundo kernel** |
| Kernel distinto del host | sí, cualquiera | no: es literalmente el mismo |

:::

**Las primeras seis filas** son el argumento a favor del contenedor, y son las que todo el mundo cita. **Las dos últimas** son la letra chica, y son las que deciden los tres casos de abajo.

> [!NOTE]
> **Las ocho filas salen de la misma causa: no hay un segundo kernel.** Por eso arranca rápido, por eso pesa poco, y por eso no te protege de un kernel roto.

## Tres veces que el contenedor no es la respuesta

Los tres son **«no puedes»**: hay algo que el contenedor no sabe hacer, y la alternativa tiene nombre.

::: table {#cont-tabla-no-puedes title="Tres cosas que un contenedor no sabe hacer"}

| # | Qué necesitas | Por qué el contenedor no puede | La alternativa |
|---:|---|---|---|
| **1** | **Hardware directo** — un dispositivo que hay que manejar de verdad, un módulo de kernel propio, un driver que no está en el host | un contenedor no tiene kernel, así que no tiene dónde cargar un módulo: quien los carga es el kernel del host, y hacerlo desde adentro requiere romper el aislamiento por completo | una máquina virtual |
| **2** | **Aislamiento máximo** — código que no escribiste tú y podría ser hostil: la entrega de un alumno, el trabajo de un cliente, un binario que te llegó por correo | comparte el kernel, así que **todo el kernel es superficie de ataque**: una vulnerabilidad ahí se salta el aislamiento | **Kata**, que pone un segundo kernel debajo del contenedor sin renunciar a trabajar con imágenes. **Ésta es una deuda que sí se paga**, en la sesión 3 |
| **3** | **Un kernel distinto** — correr Windows sobre Linux, probar contra un kernel viejo, usar una característica que tu host no tiene | no hay truco posible: el kernel del contenedor **es** el del host | una VM — y es justo lo que hacen Docker Desktop y `podman machine` |

:::

## Y dos veces en que puedes, pero no vale la pena

Los tres de arriba son «no puedes». Los dos que siguen son de otra clase, y son los que te vas a encontrar antes — **porque no fallan**. Funcionan perfecto, y aun así son la decisión equivocada.

**4. Es un script y ya.** Treinta líneas de `bash`, o un `.py` que sólo usa la biblioteca estándar. Meterlo en un contenedor te obliga a escribir un `Dockerfile`, construir una imagen, versionarla, publicarla y acordarte de montar la carpeta con los datos cada vez — todo para resolver un problema de dependencias que no tenías.

> [!TIP]
> El criterio no es el tamaño del programa: es **cuántas cosas tienen que estar instaladas para que corra**. Si la respuesta es «ninguna», el contenedor no está reproduciendo nada: está cobrando.

**5. Estado persistente complicado.** Una base de datos en un contenedor se puede, y de hecho vas a levantar una en [[named-volumes-y-postgres|la sesión 2]]. Pero mira lo que cuesta: el dato **no puede** quedarse en la capa de escritura, así que hay cuatro decisiones que tomar antes:

- en qué volumen vive,
- cómo se respalda,
- cómo se restaura,
- qué pasa cuando cambie la versión de la imagen.

**Una pregunta mal contestada ahí no da un error: da una pérdida silenciosa.** Para desarrollar en tu laptop sale barato. Para los datos de alguien más, la pregunta deja de ser «¿puedo?» y pasa a ser «¿quién administra este volumen a las tres de la mañana?».

## En macOS y en Windows siempre hay una VM de por medio

Este hecho sostiene tres páginas de la sesión 2, así que vale la pena decirlo despacio: **los contenedores son una función del kernel de Linux.** Namespaces y cgroups son código de Linux; no existen en el kernel de macOS ni en el de Windows.

Entonces, ¿cómo corre `docker run` en una MacBook? Porque hay **una máquina virtual con Linux adentro**, encendida todo el tiempo:

| Sistema | Quién pone el kernel de Linux | Qué tan visible es |
|---|---|---|
| **Linux** | el tuyo, directo | no hay VM |
| **macOS** | Docker Desktop la arranca por ti; con Podman la arrancas tú, con `podman machine init` y `podman machine start` | Docker la esconde bien; Podman no te deja ignorarla |
| **Windows** | WSL2, que también es una VM con un kernel de Linux real adentro | esconde la VM, no el hecho |

En macOS y en Windows el contenedor sigue siendo un proceso de Linux sobre un kernel de Linux — sólo que ese kernel **no es el de tu sistema operativo**.

> [!WARNING]
> **Si trabajas en Mac o en Windows, este renglón te va a tocar.** Montar una carpeta tuya dentro del contenedor **cruza la frontera de esa VM**: es más lento, y los permisos y el dueño de los archivos se comportan distinto que en Linux nativo. Se toca con la mano en la sesión 2.

## El aislamiento no es una línea

![Rejilla de dos ejes que ordena las opciones de aislamiento. El eje horizontal pregunta dónde aterriza la syscall que no controlas y va de izquierda a derecha: proceso suelto y contenedor, que la mandan directo al kernel del host; gVisor, que la manda a un núcleo en espacio de usuario que reimplementa la interfaz de syscalls de Linux; Kata, que la manda a un segundo kernel real dentro de una VM ligera; y la VM completa, que la manda a un kernel invitado detrás del hipervisor. El eje vertical pregunta qué privilegio tiene quien se escapa, y va de root en el host abajo a un usuario sin privilegios con su rango de subuid arriba. Contenedor rootful y contenedor rootless ocupan la misma columna y sólo se separan en el eje vertical, con una flecha corta que marca que rootless mueve un eje y no el otro; gVisor aparece dos veces, una a cada altura, porque tiene su propio modo rootless. Al pie, la conclusión: rootless no añade ninguna frontera, mismo kernel y misma superficie de syscalls, y los dos ejes se componen en vez de ordenarse](../_assets/cont-espectro.svg)

Entre «contenedor» y «máquina virtual» hay cosas en medio, y una de ellas aparece aquí por primera vez: **gVisor**, que no pone un kernel real ni renuncia a poner uno, sino que **reimplementa la interfaz de syscalls de Linux en espacio de usuario** y atiende ahí las llamadas de tu proceso.

Este mismo dibujo vuelve en la sesión 3 y ahí se desarma entero —es la @cont-s3p5-espectro, y por eso aquí va sin número—. Por ahora quédate con esto: **no es una recta de «poco» a «mucho» aislamiento, sino dos preguntas distintas que se responden por separado.**

::: problem {#cont-p6-si-fuera-vm title="Lo mismo, pero en una VM"}
Este comando arranca un contenedor que sirve una página web:

```bash
docker run -d -p 8080:80 --memory 512m nginx:1.27
```

Arranca en unos cientos de milisegundos y la imagen pesa unas decenas de MB. Ahora responde, para el caso en que exactamente lo mismo se hiciera levantando una máquina virtual con Ubuntu e instalando nginx adentro:

1. **Arranque** — ¿en qué cambia el tiempo, y por qué?
2. **Tamaño** — ¿qué hay que descargar y guardar en cada caso?
3. **Kernel** — ¿cuál kernel ejecuta a `nginx` en cada caso?
4. **Qué ve del host** — si alguien se escapa de `nginx`, ¿en qué máquina aparece?

Una frase por respuesta, y en la 4 di **qué tendría que romper** para llegar al host en cada caso.
:::

::: hint {of="cont-p6-si-fuera-vm"}
Las cuatro preguntas tienen la misma causa detrás, y está en la tabla de arriba: **la VM lleva un kernel propio y el contenedor no.** Contesta cada una empezando por ahí.
:::

::: answer {of="cont-p6-si-fuera-vm"}
| Pregunta | Máquina virtual | Contenedor |
|---|---|---|
| **1. Arranque** | decenas de segundos: firmware, kernel, init, servicios, y hasta entonces `nginx` | cientos de ms: sólo hace nacer un proceso — el rootfs ya estaba en disco desde el `pull` |
| **2. Tamaño** | una imagen de disco con Ubuntu entero: gigabytes, y no comparte nada con nadie | las capas de `nginx:1.27`, decenas de MB, y **comparte** las que ya tuvieras de otras imágenes |
| **3. Kernel** | **un kernel invitado propio**, que puede ser de otra versión o de otra distribución | **el de tu host**, el mismo que ejecuta tu navegador |
| **4. Qué ve del host** | empieza viendo poco, y para salir hay que romper el kernel invitado y **después** el hipervisor: una segunda frontera, y mucho más chica | empieza viendo poco, y para salir basta **una vulnerabilidad del kernel del host** — que es el tuyo, el que corre todo lo demás |

Las columnas van en el mismo orden que la tabla del principio de la página, para que puedas comprobarte sin voltear la cabeza.

**Y un detalle de la 3 que se pasa por alto:** el límite de `--memory 512m` también cambia de naturaleza. En el contenedor es una **cuota de cgroup** que el kernel del host contabiliza; en la VM es memoria que el hipervisor le entrega al invitado y que el invitado administra por su cuenta.

La diferencia no es qué ve cada uno, es **qué hay que romper para salir**. Por eso el caso 2 de arriba sigue siendo de VM, y por eso existe Kata.
:::

Esta página movió la frontera hacia abajo, hasta el kernel. La que sigue la mueve hacia arriba, hasta el otro extremo de la cadena de la página 4: **quitar el daemon**. Es el mismo tipo de pregunta —qué compras y qué no compras al sacar una pieza— y tiene la misma clase de respuesta incómoda, porque lo que casi todo el mundo cree que compra no es lo que compra. Y de paso, ahí la VM de macOS deja de ser invisible: es la que tienes que arrancar tú, a mano, con `podman machine`.

Sigue con [[docker-y-podman]].

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor no lleva kernel propio; de ahí sale que arranque en milisegundos y de ahí sale que un bug del kernel sea un bug de todos.
