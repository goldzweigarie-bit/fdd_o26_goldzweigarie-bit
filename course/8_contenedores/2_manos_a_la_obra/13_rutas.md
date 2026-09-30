---
id: rutas-en-docker
title: "Rutas"
nav_title: "Rutas"
summary: "Absoluta, relativa y portable — y la que no es una ruta: sin el punto barra, Docker crea un volumen vacío en silencio."
status: ready
estimated_time: 10m
tags: [bind-mount, rutas, volumen, pwd, mount, macos, windows]
prerequisites: [donde-vive-cada-byte]
---

# Rutas

**Página 13 de 16 · sección 2 de 3**

Meta: que montar deje de fallar por la ruta. La mitad de los «no me funciona el volumen» son un error de tecleo que Docker no reporta.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-rutas title="Cuatro maneras de escribir el origen de un `-v`, y una de las cuatro no es una ruta"}
![Cuatro tarjetas, una por cada forma de escribir el lado izquierdo de un guion v. La primera, la ruta absoluta, monta ese directorio y nada más: siempre funciona y nunca es portable, porque esa ruta no existe en la máquina de nadie más. La segunda, la ruta relativa que empieza con punto barra, funciona desde Docker CLI 23, de 2023, y también en Podman, y se resuelve contra tu directorio actual. La tercera, la forma portable, usa pwd entre comillas: el shell la vuelve absoluta antes de que Docker la vea, así que funciona con cualquier versión, y las comillas son por los espacios. La cuarta está marcada como la que no es una ruta: le falta el punto barra, y sin él Docker no ve una ruta sino un nombre, así que crea un named volume vacío con ese nombre y lo monta en silencio, sin error y sin aviso, de modo que el código no aparece por ningún lado dentro del contenedor y sólo docker volume ls lo delata. Abajo, un recuadro con tres cajas en fila —tu disco, la frontera de la máquina virtual y el contenedor— que muestra que en macOS y en Windows cada lectura y cada escritura del bind mount cruzan ese puente: por eso ahí es más lento y por eso los permisos los inventa el filesystem compartido, mientras que en Linux no hay puente y el bind mount es el mismo inodo del mismo kernel](../_assets/cont-rutas.svg)
:::

## En corto

- Las rutas relativas **sí funcionan**: desde Docker CLI 23 y también en Podman. `"$(pwd)"` sigue siendo lo portable, no lo único que sirve.
- La trampa real no es la versión, es el **`./`**: sin él, el lado izquierdo del `-v` no es una ruta, es el **nombre de un named volume** que Docker crea vacío y monta sin decir nada.
- En macOS y en Windows, ese bind mount **cruza la frontera de una máquina virtual**. Ahí es más lento y los permisos se comportan distinto.

## Las cuatro formas de escribir el origen

::: table {#cont-tabla-rutas title="El lado izquierdo del `-v`, y qué entiende Docker"}

| Lo que escribes | Qué entiende Docker | Cuándo usarla |
|---|---|---|
| `-v /home/tu/app:/app` | ruta **absoluta**: monta ese directorio | funciona siempre, y nunca es portable |
| `-v ./app:/app` | ruta **relativa** a tu directorio actual | cómoda; pide Docker CLI 23 o Podman |
| `-v "$(pwd)/app":/app` | el shell la vuelve absoluta **antes** de que Docker la vea | la portable: sirve con cualquier versión |
| `-v app:/app` | **no es una ruta**: es el nombre de un named volume | casi nunca lo que querías |

:::

Las tres primeras montan tu directorio. La cuarta no monta nada tuyo, y la diferencia entre la segunda y la cuarta son **dos caracteres**.

Fíjate en las comillas de la tercera: `"$(pwd)/app"` va entrecomillado porque tu ruta puede tener espacios, y sin comillas el shell parte el argumento en dos antes de que Docker lo vea. Es exactamente la regla de [[variables-comillas-y-salida|la unidad de Bash]], cobrada aquí.

## La que no es una ruta

**Haz:** monta bien, para tener con qué comparar.

```bash
cd ~/fdd/docker-lab
echo "print('hola')" > app.py
docker run --rm -v "$(pwd)":/app ubuntu:24.04 ls /app
```

**Deberías ver:** `app.py` listado. El contenedor está viendo tu carpeta.

**Haz:** ahora quítale el `./` y mira lo que no pasa.

```bash
docker run --rm -v trabajo:/app ubuntu:24.04 ls /app
docker volume ls
```

**Deberías ver:** `ls /app` **sin imprimir nada** —el directorio está vacío— y ningún error. Y en `docker volume ls`, un volumen nuevo llamado `trabajo` que tú no pediste: Docker leyó `trabajo` como un **nombre**, no como una ruta, creó el volumen vacío y lo montó encima de `/app`. Tu código no está ahí y nadie te lo dijo.

Ésa es media hora perdida buscando por qué «el volumen no funciona». La cura es mirar `docker volume ls` en cuanto una carpeta montada aparezca vacía: si ves un volumen con el nombre de tu carpeta, ya sabes qué pasó.

**Haz:** y ahora la variante con falta de ortografía, que es peor.

```bash
docker run --rm -v ./aap:/app ubuntu:24.04 ls /app
ls -ld aap
```

**Deberías ver:** otra vez nada adentro, y **un directorio `aap` recién creado en tu disco**, que tú no hiciste. Con `-v`, si la ruta de origen no existe, Docker **la inventa** —vacía, y en Linux nativo con dueño `root`—. No falla, no pregunta: obedece.

**Haz:** limpia lo que acabas de ensuciar, que no es poco.

```bash
docker volume rm trabajo
rmdir aap 2>/dev/null || sudo rmdir aap
```

## `--mount` no inventa nada

Hay una segunda sintaxis para lo mismo, más larga y explícita, que **falla en vez de adivinar**:

```bash
docker run --rm --mount type=bind,src="$(pwd)/aap",dst=/app ubuntu:24.04 ls /app
```

Con `--mount type=bind`, si el origen no existe, el comando **da error y no corre**. Es más que teclear: cuando un montaje te esté volviendo loco, cambiar el `-v` por un `--mount` convierte el silencio en un mensaje.

## En macOS y en Windows hay un puente

Aquí se paga la deuda que dejó [[vm-contra-contenedor]]. En esos dos sistemas el contenedor corre dentro de una máquina virtual con Linux, así que tu carpeta **no está en el mismo kernel** que el proceso que la lee: cada lectura y cada escritura del bind mount cruzan un sistema de archivos compartido que hace de puente entre los dos mundos.

Dos consecuencias, y las dos se tocan con la mano:

- **Es más lento.** Un proyecto con muchos archivos chicos —`node_modules`, un repositorio grande— lo nota de inmediato.
- **Los permisos los inventa el puente.** No salen de tu disco: los produce el filesystem compartido para que nada falle. Por eso el dueño del archivo que escribe el contenedor no es el mismo en las cuatro plataformas, y por eso la página que sigue lleva una tabla en vez de una respuesta.

En Linux nativo no hay puente: el bind mount es **el mismo inodo del mismo kernel**, y por eso ahí la pregunta del dueño sí tiene una respuesta limpia.

::: problem {#cont-s2p8-cuatro-montajes title="Cuatro montajes, cuatro predicciones"}
Estás en `~/fdd/docker-lab`, que contiene un solo archivo, `app.py`. Antes de correr nada, **escribe qué va a imprimir cada comando** y por qué:

```bash
docker run --rm -v "$(pwd)":/app ubuntu:24.04 ls /app
docker run --rm -v ./:/app       ubuntu:24.04 ls /app
docker run --rm -v datos:/app    ubuntu:24.04 ls /app
docker run --rm -v ./nada:/app   ubuntu:24.04 ls /app
```

Después córrelos, y contesta:

1. ¿Cuáles dos imprimieron `app.py`, y por qué las otras dos no?
2. Corre `docker volume ls` y `ls -ld nada`. ¿Qué apareció que tú no creaste, y quién es su dueño?
3. ¿Cuál de los cuatro es el que de verdad muerde en la vida real, y por qué es el peor de los cuatro?
4. Deja tu carpeta como estaba: dos comandos.
:::

::: hint {of="cont-s2p8-cuatro-montajes"}
Dos de los cuatro montan tu directorio y dos no montan nada tuyo — pero no fallan por la misma razón, y ahí está toda la página. Para la 3, piensa en cuál te da una pista y cuál no te da ninguna.
:::

::: answer {of="cont-s2p8-cuatro-montajes"}
**1.** Imprimen `app.py` el primero y el segundo. El primero porque el shell convirtió `"$(pwd)"` en una ruta absoluta antes de que Docker la viera; el segundo porque `./` la marca como ruta relativa, y eso **sí funciona** desde Docker CLI 23 y en Podman.

El tercero no imprime nada: `datos` no lleva `./`, así que Docker lo leyó como el **nombre de un named volume**, lo creó vacío y lo montó sobre `/app`. El cuarto tampoco: `./nada` sí es una ruta, pero no existía, y con `-v` Docker la crea vacía en tu disco.

**2.** `docker volume ls` lista un volumen `datos` que tú no pediste, y `ls -ld nada` muestra un directorio nuevo en tu carpeta — en Linux nativo con dueño `root`, porque quien lo creó fue el daemon, que corre como `root`.

**3. El tercero**, el del `./` olvidado, y por dos razones. Primero, porque es el más fácil de teclear por accidente: entre `-v app:/app` y `-v ./app:/app` hay dos caracteres. Segundo, y sobre todo, porque **no deja rastro donde lo estás buscando**: el cuarto al menos te deja un directorio visible en tu carpeta, mientras que el tercero esconde la evidencia en `docker volume ls`, que no es el primer lugar donde uno mira. Todo «monté el volumen y mi código no aparece» empieza aquí.

**4.** `docker volume rm datos` y `rmdir nada`. Si el segundo se queja de permisos, es porque el dueño es `root`: `sudo rmdir nada`.
:::

Sigue con [[el-archivo-compartido]], donde el bind mount ya montado bien se usa en las dos direcciones — y donde la pregunta del dueño por fin se contesta, con las cuatro respuestas que tiene.

> [!NOTE]
> **Si sólo recuerdas una cosa:** sin `./`, el lado izquierdo del `-v` no es una ruta sino el nombre de un volumen vacío que Docker crea en silencio — y `docker volume ls` es quien lo delata.
