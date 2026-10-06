---
id: ejercicios-colaborativos
title: "Ejercicios colaborativos: GitHub y Docker en equipo"
nav_title: "Colaborativos: GitHub y Docker"
summary: "Dos ejercicios largos donde tres personas trabajan el mismo repositorio a la vez: pushes rechazados, conflictos, merges limpios que rompen, y lo que eso le hace a cada imagen, contenedor y volumen. Con pista y respuesta plegadas."
status: ready
estimated_time: 90m
tags: [ejercicios, git, github, merge, conflictos, docker, volumenes, postgres, equipo]
prerequisites: [ejercicios-github, ejercicios-docker]
---

# Ejercicios colaborativos: GitHub y Docker en equipo

En los parciales, una sola persona cambiaba un archivo y seguías qué pasaba. Aquí trabajan **tres a la vez**: Ana, Beto y Caro. Cada quien tiene su clon, su máquina, sus imágenes, sus contenedores y sus volúmenes. Los cambios llegan de una máquina a otra **sólo** a través de GitHub, con `push` y `pull`.

Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado.

Los dos escenarios se reprodujeron completos: un repositorio local hizo de GitHub, hubo tres clones, y cada comando corrió con Git 2.34 y Docker 29.6. Las salidas que ves son las reales.

**Cómo leerlos.** Cada fila dice quién actúa y en qué orden; cada fila parte de lo que dejaron las anteriores. Las preguntas usan sólo comandos que ya viste en los parciales. Al final de cada ejercicio no se piden comandos: se pregunta **qué práctica** lo habría evitado.

**Una diferencia con el curso.** Aquí el equipo comparte **un solo repositorio** donde los tres pueden escribir, como en un proyecto de trabajo. En el curso cada quien tiene su fork y propone por pull request. Con un repositorio compartido aparece algo que con forks casi no pasa: dos personas empujando a la misma rama.

## Ejercicio 1 · El umbral

### El punto de partida

El equipo mantiene `alertas/`, un servicio que imprime el umbral con el que filtra. En GitHub, `main` tiene un solo commit, **B**:

```text
alertas/
├── Dockerfile
├── alerta.sh
└── config.env
```

`config.env`:

```text
UMBRAL=5
```

`alerta.sh` carga ese archivo e imprime el valor:

```bash
. ./config.env
echo "umbral: $UMBRAL"
```

`Dockerfile`: la configuración se **copia dentro de la imagen**.

```dockerfile
FROM alpine:3.20
WORKDIR /app
COPY config.env alerta.sh ./
CMD ["sh", "alerta.sh"]
```

Los tres ya clonaron el repositorio y, cada uno en su máquina, corrieron:

```bash
docker build -t alertas:1 .
docker run -d --name alerta alertas:1 sleep 600
```

Así que cada quien tiene una imagen `alertas:1` y un contenedor `alerta` encendido, los dos con `UMBRAL=5`. Ningún `sleep 600` termina durante el ejercicio.

### La secuencia

::: problem {#xco1-1 title="Fila 1 · Ana cambia y sube"}
```bash
# Ana
echo "UMBRAL=10" > config.env
git commit -am "umbral 10"
git push origin main
docker run --rm alertas:1
```

¿Qué `UMBRAL` hay ahora en GitHub, en el clon de Beto y en la imagen de Ana? ¿Qué imprime el `docker run` de Ana?
:::

::: hint {of="xco1-1"}
Un `push` actualiza GitHub, y nada más. ¿Hizo Beto algo para recibirlo? ¿Reconstruyó Ana su imagen?
:::

::: answer {of="xco1-1"}
| GitHub | Clon de Ana | Clon de Beto | Imagen de Ana |
|---|---|---|---|
| **10** | 10 | **5** | **5** |

El run de Ana imprime **`umbral: 5`**.

- El push sube el commit a GitHub. **No llega** a nadie más: Beto y Caro lo reciben sólo cuando hagan `pull`.
- La imagen de Ana se construyó con el 5. Commitear y subir no reconstruye nada: la imagen sólo cambia con un `docker build`.
:::

::: problem {#xco1-2 title="Fila 2 · Ana reconstruye"}
```bash
# Ana
docker build -t alertas:1 .
docker run --rm alertas:1
docker exec alerta sh alerta.sh
```

¿Qué imprime el run? ¿Y el exec?
:::

::: hint {of="xco1-2"}
El run crea un contenedor nuevo de la imagen recién construida. ¿Y el contenedor `alerta`, cuándo nació?
:::

::: answer {of="xco1-2"}
- **run: `umbral: 10`.** La imagen nueva copió el `config.env` de su disco.
- **exec: `umbral: 5`.** El contenedor `alerta` nació de la imagen **vieja**, y reconstruir una imagen no cambia los contenedores que ya existen. Ana tiene ahora dos versiones corriendo en su propia máquina.
:::

::: problem {#xco1-3 title="Fila 3 · Beto, sin haber hecho pull"}
```bash
# Beto
echo "UMBRAL=20" > config.env
git commit -am "umbral 20"
git push origin main
```

Git le contesta:

```text
 ! [rejected]        main -> main (fetch first)
hint: Updates were rejected because the remote contains work that you do
```

¿Por qué lo rechaza? ¿Qué `UMBRAL` hay en GitHub? Si ahora Beto corre `docker build -t alertas:1 .` y `docker run --rm alertas:1`, ¿qué imprime?
:::

::: hint {of="xco1-3"}
GitHub tiene un commit (el de Ana) que la máquina de Beto no tiene. ¿Y de dónde copia el build: de GitHub o del disco de Beto?
:::

::: answer {of="xco1-3"}
- **Rechazado** porque GitHub tiene el commit de Ana y Beto no. Si Git aceptara, el commit de Ana desaparecería de `main`. Git obliga a **integrar primero**.
- En GitHub sigue **`UMBRAL=10`**: el push no entró.
- El run imprime **`umbral: 20`**. El build copia **el disco de Beto**, no GitHub. Beto tiene una imagen con un valor que no existe en ningún otro lado.
:::

::: problem {#xco1-4 title="Fila 4 · Caro se pone al día"}
```bash
# Caro
git pull origin main
docker run --rm alertas:1
docker run --rm -v "$(pwd)/config.env":/app/config.env alertas:1
```

¿Qué hace el pull? ¿Qué imprime cada run?
:::

::: hint {of="xco1-4"}
¿Tenía Caro commits propios? ¿Reconstruyó su imagen? ¿Qué tapa un montaje?
:::

::: answer {of="xco1-4"}
- **El pull es un fast-forward.** Caro no tenía commits propios, así que su `main` sólo avanza hasta el commit de Ana. Su disco dice ahora `UMBRAL=10`.
- **Primer run: `umbral: 5`.** Su imagen sigue siendo la del principio: un pull no reconstruye.
- **Segundo run: `umbral: 10`.** El montaje tapa el `config.env` de la imagen con el de su disco.

Mismo commit en el disco, dos resultados distintos según **cómo** corra el contenedor.
:::

::: problem {#xco1-5 title="Fila 5 · Beto integra"}
```bash
# Beto
git pull origin main
```

Git contesta:

```text
CONFLICT (content): Merge conflict in config.env
Automatic merge failed; fix conflicts and then commit the result.
```

¿Cómo se ve ahora `config.env` en el disco de Beto? ¿Qué imprime `docker exec alerta sh alerta.sh`? ¿Y `docker run --rm alertas:1`?
:::

::: hint {of="xco1-5"}
Los dos cambiaron la misma línea desde B. `HEAD` es el lado de Beto. El contenedor `alerta` y la imagen se construyeron antes de este pull.
:::

::: answer {of="xco1-5"}
```text
<<<<<<< HEAD
UMBRAL=20
=======
UMBRAL=10
>>>>>>> 635d1a8
```

`HEAD` es lo de Beto (el 20), y abajo lo que llegó de GitHub (el 10 de Ana). En lugar de un nombre de rama, Git pone el hash del commit que trajo. `git status --short` lo marca `UU config.env`.

- **exec: `umbral: 5`.** El contenedor `alerta` nació al principio.
- **run: `umbral: 20`.** La imagen es la que Beto construyó en la fila 3.

Ninguno de los dos ve el conflicto: está **sólo en el disco**.
:::

::: problem {#xco1-6 title="Fila 6 · Beto «termina»"}
```bash
# Beto
git add config.env
git commit -m "listo"
docker build -t alertas:1 .
docker run --rm alertas:1
echo $?
git push origin main
```

Beto no editó el archivo. ¿Git acepta el commit? ¿El build termina bien? ¿Qué imprime el run y qué da `echo $?`? ¿GitHub acepta el push?
:::

::: hint {of="xco1-6"}
Para Git, `git add` significa «ya lo resolví», sin revisar el contenido. ¿Le importa a `COPY` lo que dice el archivo? ¿Qué hace `sh` al cargar una línea que empieza con `<<<`?
:::

::: answer {of="xco1-6"}
- **El commit se acepta.** `git add` le dice a Git que el conflicto está resuelto, y Git le cree: no revisa si quedaron marcadores.
- **El build termina bien.** `COPY` copia bytes.
- **El run truena:**

  ```text
  alerta.sh: ./config.env: line 1: syntax error: unexpected redirection
  ```

  `echo $?` da **2**: `sh` intentó leer `<<<<<<<` como una redirección.
- **El push se acepta.** Ahora el `main` de Beto contiene el commit de Ana, así que subir ya no borra nada. GitHub no revisa contenido: **el archivo roto ya está en `main`**.

Beto tuvo tres avisos y no miró ninguno: el `CONFLICT`, el `UU` y su propio contenedor tronando.
:::

::: problem {#xco1-7 title="Fila 7 · Caro vuelve a ponerse al día"}
```bash
# Caro
git pull origin main
docker run --rm alertas:1
docker run --rm -v "$(pwd)/config.env":/app/config.env alertas:1
```

¿Qué hace el pull? ¿Qué imprime cada run?
:::

::: hint {of="xco1-7"}
Caro sigue sin commits propios. ¿Qué trae ahora `main` en su `config.env`?
:::

::: answer {of="xco1-7"}
- **El pull es otro fast-forward**: le trae el commit «listo» con los marcadores. Caro no hizo nada mal, y aun así su disco tiene el archivo roto.
- **Primer run: `umbral: 5`.** Su imagen sigue siendo la del principio, y por eso **parece que todo funciona**.
- **Segundo run: truena**, con el mismo `syntax error` y código 2, porque ahora monta el archivo con marcadores.

Si Caro sólo probara sin montaje, tardaría en descubrirlo. Si reconstruye, su imagen también queda rota.
:::

::: problem {#xco1-8 title="Fila 8 · Ana lo arregla"}
El equipo acuerda un umbral de 15.

```bash
# Ana
git pull origin main
echo "UMBRAL=15" > config.env
git commit -am "umbral acordado 15"
git push origin main
docker build -t alertas:1 .
docker run --rm alertas:1
```

¿Cómo sale el pull? ¿Qué imprime el run?
:::

::: hint {of="xco1-8"}
¿Tenía Ana commits que GitHub no tuviera?
:::

::: answer {of="xco1-8"}
- **El pull es un fast-forward**: Ana no tenía commits nuevos. Le trae el archivo con marcadores, y ella lo reemplaza completo.
- **El run imprime `umbral: 15`.** `main` en GitHub vuelve a estar sano.
:::

::: problem {#xco1-9 title="Fila 9 · La foto final"}
Nadie más hace nada. Llena la tabla con lo que dice cada lugar: un número, «marcadores» o «truena».

| Lugar | ¿Qué dice? |
|---|---|
| `main` en GitHub | |
| Disco de Ana | |
| Disco de Beto | |
| Disco de Caro | |
| Imagen de Ana | |
| Imagen de Beto | |
| Imagen de Caro | |
| Contenedor `alerta` de Ana | |
| Contenedor `alerta` de Beto | |
| Contenedor `alerta` de Caro | |
:::

::: hint {of="xco1-9"}
Recorre fila por fila quién hizo `pull` después de la fila 8, quién reconstruyó y quién recreó su contenedor. Los contenedores `alerta` nacieron al principio y nadie los tocó.
:::

::: answer {of="xco1-9"}
| Lugar | ¿Qué dice? | Por qué |
|---|---|---|
| `main` en GitHub | **15** | El arreglo de Ana |
| Disco de Ana | **15** | Lo escribió ella |
| Disco de Beto | **marcadores** | No ha hecho pull desde su commit roto |
| Disco de Caro | **marcadores** | Su último pull fue el de la fila 7 |
| Imagen de Ana | **15** | Reconstruyó en la fila 8 |
| Imagen de Beto | **truena** | La construyó con marcadores en la fila 6 |
| Imagen de Caro | **5** | Nunca reconstruyó |
| Contenedor `alerta` de Ana | **5** | Nació al principio |
| Contenedor `alerta` de Beto | **5** | Nació al principio |
| Contenedor `alerta` de Caro | **5** | Nació al principio |

**Cuatro valores distintos para la misma variable**, y el único que GitHub considera correcto (15) sólo vive en la máquina de Ana. Comprobado: cuando Beto por fin hace pull y reconstruye, su imagen da 15, pero su contenedor `alerta` sigue en 5 hasta que lo borre y lo cree otra vez.
:::

### Diagnóstico y prácticas

Aquí no se piden comandos: se pide entender qué falló y qué costumbre del equipo lo habría evitado.

::: problem {#xco1-d1 title="D1 · ¿Dónde entró el error?"}
¿En qué fila entró el archivo roto a `main`? ¿Quién pudo detenerlo antes, y con qué señal?
:::

::: hint {of="xco1-d1"}
Busca la fila donde GitHub aceptó un commit con marcadores. Luego cuenta los avisos que Beto vio y no atendió.
:::

::: answer {of="xco1-d1"}
**En la fila 6**, con el push de Beto. Beto tuvo tres señales:

1. el mensaje `CONFLICT` de la fila 5;
2. el `UU` de `git status`;
3. su propio contenedor tronando con código 2, **antes** de hacer push.

Cualquiera de las tres bastaba para no subir. Nadie más pudo detenerlo: el equipo subía directo a `main`, sin una revisión en medio.
:::

::: problem {#xco1-d2 title="D2 · ¿Por qué cada quien ve otra cosa?"}
Al final hay cuatro valores distintos de `UMBRAL` en el equipo. Explica las **tres** razones por las que una persona puede estar corriendo una versión distinta de la que hay en GitHub.
:::

::: hint {of="xco1-d2"}
Piensa en las tres copias que separan a GitHub de lo que imprime un contenedor: el disco, la imagen y el contenedor.
:::

::: answer {of="xco1-d2"}
Entre GitHub y lo que imprime un contenedor hay **tres copias**, y cada una se actualiza por separado:

1. **El disco** sólo cambia con `pull`. Si no lo haces, trabajas sobre lo viejo, como Beto en la fila 3.
2. **La imagen** sólo cambia con `build`, y copia **el disco**, no GitHub. Con cambios sin subir, o con un archivo roto en el disco, tu imagen no es igual a la de nadie.
3. **El contenedor** se queda con la imagen con la que nació. Reconstruir no lo actualiza: hay que borrarlo y crear otro.

«En mi máquina funciona» suele significar que una de esas tres copias está vieja.
:::

::: problem {#xco1-d3 title="D3 · Las prácticas que faltaron"}
Sin escribir comandos: ¿qué cuatro o cinco costumbres de equipo habrían evitado este ejercicio completo? Para cada una, di qué fila habría cambiado.
:::

::: hint {of="xco1-d3"}
Repasa las filas 3, 5, 6, 7 y 9, y pregúntate en cada una qué debió pasar antes.
:::

::: answer {of="xco1-d3"}
Cualquiera de éstas, bien ligada a una fila, vale:

| Práctica | Qué habría cambiado |
|---|---|
| **Ponerse al día antes de empezar a trabajar** | Beto habría partido del 10 de Ana: no habría habido rechazo ni conflicto (filas 3 y 5) |
| **Ramas y pull requests en vez de subir directo a `main`** | El commit roto se habría quedado en una rama, y otra persona lo habría visto antes de que llegara a Caro (filas 6 y 7) |
| **Revisar un conflicto antes de declararlo resuelto**: abrir el archivo, buscar marcadores, preguntar al autor del otro cambio cuál valor gana | Beto no habría commiteado marcadores (fila 6) |
| **Probar antes de subir**, y mejor aún, una revisión automática que construya la imagen y la **arranque** en cada pull request | El código 2 habría bloqueado el merge (fila 6) |
| **La configuración afuera de la imagen**: montada o por variable de entorno | Cambiar un número no exigiría reconstruir ni dejaría imágenes con valores distintos (filas 2, 4 y 9) |
| **Nombrar la imagen con el commit del que salió**, en lugar de `alertas:1` siempre, **y recrear los contenedores** al actualizar | Cualquiera sabría qué versión corre cada contenedor (fila 9) |
| **Acordar quién decide un valor compartido** antes de que dos personas lo cambien | El 10 contra el 20 era un desacuerdo de personas, no de Git |
:::

## Ejercicio 2 · La base de datos

### El punto de partida

El equipo mantiene `tienda/`, con una base Postgres. Los cambios a la base son archivos SQL versionados en Git:

```text
tienda/
└── sql/
    └── 001_clientes.sql
```

`001_clientes.sql`:

```sql
CREATE TABLE clientes (id serial PRIMARY KEY, nombre text);
```

Cada quien levanta la base en su máquina, desde la carpeta del repo, siempre con el mismo comando:

```bash
docker run -d --name db -e POSTGRES_PASSWORD=fdd \
  -v datos:/var/lib/postgresql/data \
  -v "$(pwd)/sql":/docker-entrypoint-initdb.d \
  postgres:16
```

- `datos` es un **named volume**: ahí vive la base, y sobrevive a `docker rm`.
- El segundo `-v` monta la carpeta `sql/` del repo donde la imagen busca scripts de arranque.

**Un dato que necesitas.** Al arrancar, la imagen de Postgres:

- corre los `.sql` de `/docker-entrypoint-initdb.d`, en orden alfabético, **sólo si el volumen de datos está vacío**;
- si el volumen ya tiene una base, se salta todos los scripts y arranca;
- si un script falla, se detiene, y el contenedor se apaga.

Para ver las tablas: `docker exec db psql -U postgres -c '\dt'`.

Los tres clonaron el repo y levantaron su base. Cada quien tiene un volumen `datos` con la tabla `clientes`.

### La secuencia

::: problem {#xco2-1 title="Fila 1 · Ana agrega la tabla ventas, en una rama"}
```bash
# Ana
git switch -c ventas
# crea sql/002_ventas.sql:
#   CREATE TABLE ventas (id serial PRIMARY KEY,
#                        cliente int REFERENCES clientes(id), total numeric);
git add sql
git commit -m "tabla ventas"
git push -u origin ventas
docker rm -f db
docker run -d --name db ... postgres:16      # el mismo comando de arriba
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve Ana?
:::

::: hint {of="xco2-1"}
¿Está vacío el volumen `datos` de Ana? `docker rm` borra el contenedor; ¿borra el volumen?
:::

::: answer {of="xco2-1"}
**Sólo `clientes`.** El volumen `datos` ya tenía una base, porque `docker rm` no borra volúmenes. Postgres se salta **todos** los scripts, incluido el nuevo `002_ventas.sql`, aunque esté montado ahí mismo.

Comprobado: en los registros del contenedor (`docker logs db`) aparece *Skipping initialization*.
:::

::: problem {#xco2-2 title="Fila 2 · Ana prueba con un volumen nuevo"}
```bash
# Ana
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve ahora? ¿Qué perdió?
:::

::: hint {of="xco2-2"}
Con el volumen borrado, el siguiente `run` crea uno nuevo y vacío.
:::

::: answer {of="xco2-2"}
**`clientes` y `ventas`.** El volumen es nuevo, así que corren `001` y `002`, en ese orden.

**Perdió** todos los datos que tuviera en su base anterior: `docker volume rm` no tiene papelera. Satisfecha, Ana abre su pull request **#1** desde `ventas`.
:::

::: problem {#xco2-3 title="Fila 3 · Beto agrega reportes, en su rama"}
Al mismo tiempo, Beto necesita una tabla con ventas por mes:

```bash
# Beto
git switch -c reportes
# crea sql/003_ventas_mensuales.sql:
#   CREATE TABLE ventas (mes text PRIMARY KEY, total numeric);
git add sql
git commit -m "ventas mensuales"
git push -u origin reportes
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve Beto?
:::

::: hint {of="xco2-3"}
¿Existe el `002_ventas.sql` de Ana en la rama de Beto?
:::

::: answer {of="xco2-3"}
**`clientes` y `ventas`.** Pero **su** `ventas` tiene las columnas `mes` y `total`. Su rama nació antes del trabajo de Ana, así que en su disco no existe `002_ventas.sql`. En su máquina todo funciona, y abre su pull request **#2** desde `reportes`.
:::

::: problem {#xco2-4 title="Fila 4 · Se mergean los dos pull requests"}
En GitHub alguien mergea el #1 y luego el #2. ¿Hay conflicto? ¿Por qué? ¿Qué archivos hay ahora en `sql/` en `main`?
:::

::: hint {of="xco2-4"}
Git compara líneas de archivos. ¿Tocaron Ana y Beto algún archivo en común?
:::

::: answer {of="xco2-4"}
**Sin conflicto.** Ana creó `002_ventas.sql` y Beto creó `003_ventas_mensuales.sql`: **archivos distintos**, así que no hay ninguna línea que Git tenga que elegir. Comprobado: el segundo merge sale con un commit de merge normal.

En `main` quedan `001_clientes.sql`, `002_ventas.sql` y `003_ventas_mensuales.sql`.

Git no sabe SQL. No puede ver que **los dos archivos crean una tabla con el mismo nombre**.
:::

::: problem {#xco2-5 title="Fila 5 · Ana y Beto se ponen al día"}
Cada uno, en su máquina, con su volumen de la fila 2 y de la fila 3:

```bash
# Ana, y luego Beto
git switch main
git pull origin main
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\d ventas'
```

`\d ventas` muestra las columnas de la tabla. ¿Qué columnas ve cada uno? ¿Corrió algún script?
:::

::: hint {of="xco2-5"}
Los dos volúmenes ya tienen una base. ¿Qué hace Postgres con los scripts en ese caso?
:::

::: answer {of="xco2-5"}
| | Columnas de `ventas` |
|---|---|
| Ana | `id`, `cliente`, `total` |
| Beto | `mes`, `total` |

**No corrió ningún script**: los dos volúmenes ya tenían base. Los dos tienen el **mismo commit** en el disco y una tabla `ventas` **distinta** en la base. Y los dos dirían «en mi máquina funciona».
:::

::: problem {#xco2-6 title="Fila 6 · Caro se pone al día"}
Caro todavía tiene su volumen del principio.

```bash
# Caro
git pull origin main
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

¿Qué tablas ve?
:::

::: hint {of="xco2-6"}
Mismo razonamiento que la fila 5, pero ¿qué tenía el volumen de Caro?
:::

::: answer {of="xco2-6"}
**Sólo `clientes`.** Su volumen ya tenía base, así que no corre nada nuevo. Caro tiene el código más reciente y la base más vieja del equipo.
:::

::: problem {#xco2-7 title="Fila 7 · Caro empieza desde cero"}
```bash
# Caro
docker rm -f db
docker volume rm datos
docker run -d --name db ... postgres:16
docker ps
docker logs db
```

¿Aparece `db` en `docker ps`? ¿Qué dice el log?
:::

::: hint {of="xco2-7"}
Con el volumen vacío, corren los tres scripts en orden. Cuando llega al `003`, ¿qué tabla ya existe?
:::

::: answer {of="xco2-7"}
**`db` no aparece en `docker ps`**: el contenedor se apagó. El log dice:

```text
running /docker-entrypoint-initdb.d/001_clientes.sql
running /docker-entrypoint-initdb.d/002_ventas.sql
running /docker-entrypoint-initdb.d/003_ventas_mensuales.sql
ERROR:  relation "ventas" already exists
```

El `002` creó `ventas`, y el `003` intentó crearla otra vez. Postgres detuvo la inicialización y el contenedor terminó con error. Es la primera vez que alguien prueba **el resultado del merge** sobre una base nueva, y truena. Cada rama por separado funcionaba.
:::

::: problem {#xco2-8 title="Fila 8 · Caro lo intenta otra vez"}
```bash
# Caro
docker rm -f db
docker run -d --name db ... postgres:16
docker exec db psql -U postgres -c '\dt'
```

No borró el volumen. ¿Arranca? ¿Qué tablas ve? ¿Por qué esto es **peor** que el error de la fila 7?
:::

::: hint {of="xco2-8"}
Después del intento fallido, ¿quedó vacío el volumen?
:::

::: answer {of="xco2-8"}
**Sí arranca**, y ve **`clientes` y `ventas`**, la de Ana. El intento de la fila 7 dejó la base a medias dentro del volumen, así que esta vez Postgres ve una base, se salta los scripts y arranca sin avisar. En el log sólo dice *Skipping initialization*.

**Es peor** porque ya no hay error que ver. Caro tiene una base sin la tabla de Beto, y nada se lo dice. Un error que se apaga solo es más caro que uno que se queda a la vista.
:::

::: problem {#xco2-9 title="Fila 9 · La contraseña"}
Beto sube por error un archivo con la contraseña real de producción, y en el siguiente commit lo borra:

```bash
# Beto
echo "POSTGRES_PASSWORD=Tienda2026!" > .env
git add .env
git commit -m "config local"
git push origin main
rm .env
git commit -am "quita .env"
git push origin main
```

Alguien clona el repo después. ¿Ve `.env` en su disco? ¿La contraseña sigue en GitHub?
:::

::: hint {of="xco2-9"}
Un commit nuevo no borra los anteriores. ¿Qué guarda Git de cada commit?
:::

::: answer {of="xco2-9"}
- **En el disco no**: el último commit ya no tiene `.env`.
- **Pero la contraseña sigue en GitHub**, en el historial: el commit «config local» guarda el archivo completo. Comprobado: desde un clon nuevo se puede leer con `git show` sobre ese commit.

Borrar el archivo **no** borra el secreto. Lo único seguro es dar la contraseña por filtrada y **cambiarla**.
:::

### Diagnóstico y prácticas

::: problem {#xco2-d1 title="D1 · ¿Qué tiene cada base?"}
Después de la fila 8, ¿qué tablas y qué columnas de `ventas` tiene la base de Ana, la de Beto y la de Caro? ¿Cuál de las tres es «la correcta»?
:::

::: hint {of="xco2-d1"}
Junta las respuestas de las filas 5 y 8.
:::

::: answer {of="xco2-d1"}
| | Tablas | `ventas` |
|---|---|---|
| Ana | `clientes`, `ventas` | `id`, `cliente`, `total` |
| Beto | `clientes`, `ventas` | `mes`, `total` |
| Caro | `clientes`, `ventas` | `id`, `cliente`, `total`, a medias: nunca corrió el `003` |

**Ninguna es la correcta**, porque `main` no describe una base posible: sus scripts no pueden correr completos. Tres bases distintas salieron del mismo commit, porque cada volumen guarda **la historia de cuándo se creó**, no el código actual.
:::

::: problem {#xco2-d2 title="D2 · Sin conflicto, pero roto"}
Git dijo «sin conflicto» en la fila 4. Explica por qué eso no garantizaba nada.
:::

::: hint {of="xco2-d2"}
¿Qué compara Git cuando mezcla? ¿Qué tendría que entender para ver este problema?
:::

::: answer {of="xco2-d2"}
Git compara **líneas de archivos**, no lo que significan. Un conflicto de Git aparece cuando dos personas cambian **las mismas líneas**. Aquí cambiaron archivos distintos, así que para Git no había nada que decidir.

El choque era de **significado**: dos archivos distintos crean la misma tabla. Es un conflicto que sólo aparece al **ejecutar** el resultado. «Se mezcla limpio» no es lo mismo que «funciona junto».
:::

::: problem {#xco2-d3 title="D3 · Las prácticas que faltaron"}
Sin escribir comandos: ¿qué costumbres habrían evitado los problemas de las filas 1, 5, 7, 8 y 9?
:::

::: hint {of="xco2-d3"}
Piensa en tres frentes: cómo se cambia la estructura de una base que ya existe, qué se prueba antes de mergear, y qué nunca entra a Git.
:::

::: answer {of="xco2-d3"}
| Práctica | Qué habría cambiado |
|---|---|
| **Migraciones, no scripts de arranque.** Cada cambio a la base es un paso numerado que se aplica **una sola vez y en orden**. Una herramienta lleva la cuenta, dentro de la propia base, de cuáles ya se aplicaron | Ana, Beto y Caro recibirían los cambios nuevos sin borrar su volumen (filas 1, 5 y 6) |
| **Probar el resultado del merge, no cada rama sola**: una revisión automática que levante la base **desde un volumen vacío** con el `main` que resultaría del merge | El choque de la fila 7 habría aparecido en el pull request #2, antes de llegar a `main` |
| **Revisar los pull requests por lo que hacen**, no sólo porque mezclan limpio. Quien revisa el #2 debe preguntarse si `ventas` ya existe | Beto habría llamado distinto a su tabla, o se habrían puesto de acuerdo |
| **Coordinar la numeración y los nombres**: un solo lugar donde se ve qué cambios a la base están en curso | Dos personas no inventan la misma tabla al mismo tiempo |
| **Leer el error antes de reintentar**, y no reintentar sobre un volumen que quedó a medias | Caro no habría tapado el error con un arranque silencioso (fila 8) |
| **Los secretos nunca entran a Git**: `.env` va en el `.gitignore`, y al repo sube un ejemplo sin valores reales. Si uno se filtra, se cambia | La contraseña no estaría en el historial (fila 9) |
| **Tratar el volumen como estado, no como algo desechable**: decidir en equipo cuándo se borra, y respaldar antes | Ana no habría perdido sus datos de prueba (fila 2) |
:::

**Repasa:** [[branches-y-merge]], [[el-flujo-del-curso]], [[named-volumes-y-postgres]], [[donde-vive-cada-byte]] y [[lo-que-no-se-sube]].
