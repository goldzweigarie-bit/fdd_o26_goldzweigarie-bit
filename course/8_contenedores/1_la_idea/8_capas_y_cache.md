---
id: capas-y-cache
title: "Capas y caché"
nav_title: "Capas y caché"
summary: "Por qué un build a veces tarda tres segundos y a veces tres minutos, y la única regla de orden que hay que recordar."
status: ready
estimated_time: 15m
tags: [imagen, capas, cache, build, dockerfile, hash, sha256, git]
prerequisites: [docker-y-podman]
---

# Capas y caché

**Página 8 de 9 · sección 1 de 3**

Meta: entender por qué el mismo `docker build` tarda tres segundos o tres minutos, y qué lo decide.

::: figure {#cont-capas-cache title="El mismo cambio, con dos Dockerfiles: el caché cae en dominó"}
![Dos versiones del mismo build comparadas de arriba abajo, cada instrucción del Dockerfile con su capa y su hash SHA-256 truncado al lado. Arriba, la versión mal ordenada, con COPY punto punto antes del RUN pip install: FROM y WORKDIR salen marcadas CACHED, pero al tocar una línea de código la tercera capa, la del COPY, queda INVALIDADA, y detrás de ella caen la del pip install y la del CMD; una anotación dice que caen en dominó y que pip vuelve a correr entero sin que nada suyo haya cambiado. Abajo, la versión bien ordenada, que copia primero requirements.txt y el código después, lo que parte el COPY en dos y deja seis instrucciones en vez de cinco: FROM, WORKDIR, el COPY de requirements.txt y el RUN pip install salen las cuatro CACHED, y sólo se invalidan las dos últimas, el COPY del código y el CMD. La nota final explica que el caché es secuencial, que una capa sólo se reusa si todas las de arriba se reusaron, y deja la regla práctica: lo que cambia poco, arriba; lo que cambia en cada commit, hasta abajo](../_assets/cont-capas-cache.svg)
:::

## En corto

- Cada instrucción del Dockerfile produce **una capa**, identificada por el hash SHA-256 de su contenido; la imagen es esa pila.
- El caché es **secuencial**: una capa sólo se reusa si **todas** las de arriba se reusaron, así que una invalidada tumba todo lo que sigue.
- De ahí sale una sola regla de orden: **lo que cambia poco, arriba; lo que cambia en cada commit, hasta abajo.**

## Cada instrucción es una capa

En la página 3 quedó que la imagen es un sistema de archivos ya armado y de sólo lectura. Ahora la letra chica: **no es un bloque.** Es una pila de capas, y cada instrucción del Dockerfile que toca el sistema de archivos agrega una.

Una capa no guarda «lo que cambió» como una lista de instrucciones: guarda el **estado del sistema de archivos después de esa instrucción**, y de ese contenido sale su hash SHA-256.

> [!NOTE]
> **El hash no es un número de serie que alguien asignó: es el contenido resumido.** Dos capas con exactamente los mismos bytes tienen el mismo hash, siempre, en cualquier máquina del mundo.

Eso es lo que hace que bajar una imagen sea barato. Si ya tienes en disco la capa `sha256:6a2f…` de `python:3.12-slim`, **no se vuelve a descargar**, aunque venga dentro de otra imagen de otro proyecto: el registro te manda la lista de hashes, tú comparas con lo que tienes y pides sólo lo que falta.

## Esto ya lo viste, y se llamaba Git

Si la frase «el hash sale del contenido» te suena, es porque es exactamente la de [[que-guarda-un-commit|la unidad 7]], y conviene ponerlas lado a lado porque **el modelo mental se transfiere entero**.

::: table {#cont-tabla-git-docker title="La misma idea, dos herramientas"}

| Criterio | Git | Docker |
|---|---|---|
| La unidad | el **commit** | la **capa** |
| Qué guarda | un **snapshot** completo del árbol, direccionado por contenido | un **snapshot** del sistema de archivos, direccionado por contenido |
| De dónde sale su nombre | del hash del contenido, no de un contador | del hash SHA-256 del contenido, no de un contador |
| Cómo se encadenan | cada commit apunta a su padre | cada capa se apila sobre la de abajo |
| El nombre legible | la rama, que se mueve | la etiqueta de la imagen, que se mueve |
| Duplicados | dos commits con el mismo árbol lo guardan una vez | dos imágenes con la misma capa la guardan una vez |

:::

> [!WARNING]
> **La segunda fila hay que leerla despacio, porque la versión que circula dice lo contrario: ninguno de los dos guarda diffs.** Git no guarda parches y Docker no guarda listas de cambios; los dos guardan **estados completos**, direccionados por su contenido. El «diff» es algo que se **calcula** después, al comparar dos de ellos. Que casi nunca se dupliquen bytes no viene de guardar diferencias: viene de que dos contenidos idénticos producen el mismo hash y por lo tanto **son el mismo objeto**.

Donde se separan es en una sola cosa, y es la que importa para el resto de la página: **en Git tú decides cuándo hacer un commit. En Docker no decides nada** — cada instrucción hace una capa, te guste o no, y por eso el orden en que escribes el Dockerfile tiene consecuencias de minutos.

## Qué decide si una capa se reusa

Al construir, el `build` recorre las instrucciones de arriba abajo y, para cada una, arma una **clave de caché** con tres cosas:

1. **la capa de la que parte**,
2. **la instrucción escrita tal cual**,
3. y —sólo para `COPY` y `ADD`— **el hash del contenido de los archivos que se copian**.

Las consecuencias salen solas:

| Lo que pasa | Por qué |
|---|---|
| Cambiar **un espacio** en una línea del Dockerfile **es** un cambio | la instrucción se compara como texto |
| Un `COPY` se invalida **aunque no toques la línea** | se invalida cuando cambia **lo que copia** |
| **Y la que duele:** una instrucción idéntica se invalida igual | si **la capa de la que parte** cambió, la clave cambió |

**Esa tercera es todo el dominó.**

## El dominó

Mira la parte de arriba de la figura. El Dockerfile copia el código y después instala las dependencias:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Tocas una línea de `app.py` —una sola, un `print`— y reconstruyes:

- `FROM` y `WORKDIR` salen del caché.
- El `COPY` **no**, porque lo que copia cambió.
- Y a partir de ahí **ya no hay caché para nadie**: el `RUN pip install` parte de una capa distinta a la de la vez pasada, así que su clave es distinta, así que se ejecuta.

`pip` vuelve a resolver, a bajar y a instalar todo, **sin que `requirements.txt` haya cambiado una coma**. Tres minutos, por un `print`.

## La regla, y por qué es una instrucción más

La versión de abajo de la figura hace una cosa y sólo una: **parte el `COPY` en dos.**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Ahora el `pip install` parte de una capa que sólo depende de `requirements.txt`. Mientras no toques ese archivo, esa capa se reusa y **`pip` no corre**: cambias `app.py` y sólo se rehacen las dos últimas. **Tres segundos.**

El Dockerfile tiene seis instrucciones en vez de cinco, y esa instrucción de más es el precio entero de la mejora.

> [!TIP]
> **El orden no es estético: ordena el archivo por frecuencia de cambio.** Las dependencias cambian una vez al mes; tu código, quince veces al día. Lo que cambia poco va arriba.

Y el corolario que tranquiliza: cuando **sí** cambias `requirements.txt`, `pip` vuelve a correr entero. Eso no es un fallo del orden, es lo correcto — cambió lo que instala.

::: problem {#cont-p8-capas-que-caen title="Marca las capas que caen"}
Este Dockerfile construye un servicio de Python que lee un CSV y expone un reporte:

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY . .
RUN pip install -r requirements.txt
RUN python precalcula.py
CMD ["python", "servidor.py"]
```

El `RUN pip install` tarda 95 segundos y el `RUN python precalcula.py` tarda 40. Hoy corregiste una falta de ortografía en un mensaje de `servidor.py`.

1. Escribe las seis instrucciones en una columna y marca cada una con **CACHED** o **INVALIDADA**. Di en una línea por qué cae cada invalidada.
2. ¿Cuánto tarda la reconstrucción, contando sólo esos dos `RUN`?
3. Reescríbelo para que ese mismo cambio sea barato. ¿Cuántas instrucciones te quedaron?
4. Con tu versión, ¿qué pasa si mañana agregas una línea a `requirements.txt`? ¿Y si cambias `precalcula.py`?
:::

::: hint {of="cont-p8-capas-que-caen"}
Para la 1, recuerda que la clave de caché de una instrucción incluye **la capa de la que parte**: no busques qué instrucciones cambiaron, busca **la primera que cae** y lee hacia abajo. Para la 3, la pregunta que ordena el archivo es «¿cada cuánto cambia esto?», y aquí hay **tres** frecuencias distintas, no dos.
:::

::: answer {of="cont-p8-capas-que-caen"}
**1.**

| Instrucción | | Por qué |
|---|---|---|
| `FROM python:3.12-slim` | **CACHED** | no depende de nada tuyo |
| `WORKDIR /srv` | **CACHED** | tampoco |
| `COPY . .` | **INVALIDADA** | `servidor.py` está entre lo que copia y su contenido cambió |
| `RUN pip install` | **INVALIDADA** | su instrucción es idéntica, pero **parte de una capa nueva**: su clave es otra |
| `RUN python precalcula.py` | **INVALIDADA** | por lo mismo |
| `CMD [...]` | **INVALIDADA** | y es la única que no cuesta nada |

**2. 135 segundos** —los 95 de `pip` más los 40 de `precalcula.py`— por arreglar una falta de ortografía. Ninguno de los dos trabajos tenía razón para volver a correr.

**3.** Quedan **ocho** instrucciones en vez de seis, porque el `COPY` se parte en tres — una por cada frecuencia de cambio:

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY precalcula.py datos.csv ./
RUN python precalcula.py
COPY . .
CMD ["python", "servidor.py"]
```

Lo que importa no es el número: es que **cada `RUN` caro va inmediatamente después del `COPY` mínimo que lo alimenta**, y nada más. Cambiar `servidor.py` ahora sólo invalida el último `COPY` y el `CMD`: **cero segundos** de los dos `RUN`.

**4.** Dos casos distintos, y los dos son correctos:

- Tocas **`requirements.txt`** → cae todo desde ahí: vuelven los 95 s **y** los 40 s, porque `precalcula.py` corre sobre las librerías recién instaladas y ésas cambiaron.
- Tocas **`precalcula.py`** → `pip` se reusa y sólo pagas los 40 s.

Eso es exactamente lo que se quería: **el orden no evita el trabajo, evita el trabajo que no hacía falta.**
:::

Sigue con [[lo-que-cuesta]], que cierra la sección con números medidos y con cómo leerlos sin engañarte.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el caché cae en dominó hacia abajo, así que ordena el Dockerfile por frecuencia de cambio: dependencias arriba, código hasta abajo.
