---
id: named-volumes-y-postgres
title: "Named volumes y Postgres"
nav_title: "Named volumes y Postgres"
summary: "Bind mount para tu código, named volume para datos de servicios. Ver el estado sobrevivir a su contenedor, y después morir con su volumen."
status: ready
estimated_time: 15m
tags: [named-volume, postgres, psql, estado, persistencia, uid]
prerequisites: [lab-con-volumen]
---

# Named volumes y Postgres

**Página 7 de 16 · sección 2 de 3**

Meta: ver con los ojos que el estado no vive en el contenedor, sino al lado.

::: figure {#cont-estado-postgres title="El estado sobrevive a su contenedor"}
![Cuatro tiempos de la misma línea, de izquierda a derecha. Primero, un contenedor postgres:16 con un named volume llamado pgdata montado en /var/lib/postgresql/data y una tabla con su fila recién insertada. Segundo, el contenedor destruido con docker rm -f: se va su capa de escritura y su nombre, y el volumen queda solo en el dibujo con la fila adentro. Tercero, un contenedor nuevo que monta el mismo volumen y devuelve la misma fila, sin inicializar nada. Cuarto, docker volume rm, el único de los cuatro comandos que se lleva el dato, sin deshacer. Al pie, dos recuadros: uno explica que aquí no se publica ningún puerto y que se entra con docker exec, y el otro por qué el volumen es named y no bind mount, por el uid 999 de Postgres y por la portabilidad entre sistemas operativos](../_assets/cont-estado-postgres.svg)
:::

## En corto

- **Bind mount para tu código; named volume para datos de servicios.** Es la regla que decide casi siempre.
- El named volume lo administra el runtime: no eliges dónde vive, y por eso funciona igual en Linux, macOS y Windows.
- Borrar el contenedor es rehacer; borrar el volumen es **perder**.

## Los dos montajes, lado a lado

::: table {#cont-tabla-dos-montajes title="Bind mount y named volume, lado a lado"}

| | Bind mount | Named volume |
|---|---|---|
| Quién decide dónde vive | tú | el runtime |
| Portable entre sistemas operativos | no: la ruta cambia | sí: el comando es idéntico |
| Para qué | **tu código, mientras lo editas** | **los datos de un servicio** |

:::

- Lo demás —quién tapa, quién copia, qué sobrevive a qué— ya lo viste en [[lab-con-volumen|2/6]].
- El CLI es corto: `docker volume create`, `ls`, `inspect`, `rm`. Con su equivalente de Podman, en la chuleta.

## Por qué una base de datos quiere un named volume

- **El uid.** Postgres corre como el usuario `postgres`, **uid 999**.
  - En Linux un bind mount sí arranca: el arranque, como root, se apropia de tu carpeta (`drwx------ 999`).
  - Después tu `rm -rf` dice `Permission denied`: los permisos son números, [[las-cuatro-trampas|2/16]].
  - Borrarla pide root o un contenedor.
  - El named volume no te deja esa basura.
- **La portabilidad.** `-v pgdata:/var/lib/postgresql/data` es la misma línea en los tres sistemas. Un bind mount cambia de ruta y, en macOS y Windows, cruza la frontera de una VM.

::: definition {#cont-def-psql title="`psql`"}
**`psql`** es el cliente de línea de comandos de PostgreSQL: se conecta a una base y ejecuta SQL. Con `-c 'SELECT …'` corre una sola sentencia y sale; sin `-c` abre una sesión interactiva.
:::

## Tiempo 1: la base, con su volumen

**Haz:**

```bash
docker volume create pgdata
docker run -d --name pg -e POSTGRES_PASSWORD=fdd \
  -v pgdata:/var/lib/postgresql/data postgres:16
sleep 5; until docker exec pg pg_isready -q; do sleep 1; done
docker exec pg psql -U postgres -c 'CREATE TABLE notas (id serial PRIMARY KEY, nombre text);'
docker exec pg psql -U postgres -c "INSERT INTO notas (nombre) VALUES ('ada');"
docker exec pg psql -U postgres -c 'SELECT * FROM notas;'
```

**Qué hace cada pieza:**

- `docker volume create pgdata` — crea un named volume vacío llamado `pgdata`.
- `docker run` — crea un contenedor nuevo desde una imagen y lo arranca.
- `-d` — lo deja corriendo en segundo plano y te devuelve la terminal.
- `--name pg` — le pone nombre, para no usar su ID.
- `-e POSTGRES_PASSWORD=fdd` — pasa una variable de entorno: la contraseña del superusuario.
- `\` — el comando sigue en la línea de abajo.
- `-v pgdata:/var/lib/postgresql/data` — monta el volumen **por nombre** donde Postgres guarda sus datos.
- `postgres:16` — la imagen: Postgres, versión 16.
- `sleep 5;` — espera 5 segundos; el `;` separa dos comandos en una línea.
- `until …; do sleep 1; done` — repite `sleep 1` hasta que el comando de `until` salga bien.
- `docker exec pg` — corre un comando dentro del contenedor `pg`, que ya está encendido.
- `pg_isready -q` — pregunta si Postgres ya acepta conexiones; `-q` calla y sólo responde sí o no.
- `psql -U postgres` — el cliente de Postgres, entrando como el usuario `postgres`.
- `-c '…'` — corre esa sentencia SQL y sale.
- `"…('ada')"` — comillas dobles por fuera porque el SQL lleva comillas simples adentro.

**Deberías ver:**
- `CREATE TABLE`, luego `INSERT 0 1`;
- la tabla con su única fila: `1 | ada`, y `(1 row)`.

**Por qué el `sleep 5`:** `pg_isready` pregunta si Postgres ya acepta conexiones. La primera vez, un servidor temporal inicializa el directorio de datos, y `pg_isready` le contesta que sí a ése.

**Sin `-p`.** Entraste por `docker exec`, la puerta que ya existía. Publicar un puerto habría puesto la base en tu red sin que nadie lo pidiera: [[la-red-y-el-nombre]].

## Tiempo 2: destruir el contenedor, resucitar los datos

**Haz:**

```bash
docker rm -f pg
docker volume ls | grep pgdata
docker run -d --name pg2 -e POSTGRES_PASSWORD=fdd \
  -v pgdata:/var/lib/postgresql/data postgres:16
sleep 5; until docker exec pg2 pg_isready -q; do sleep 1; done
docker exec pg2 psql -U postgres -c 'SELECT * FROM notas;'
docker logs pg2 2>&1 | head -3
```

**Qué hace cada pieza:**

- `docker rm -f pg` — borra el contenedor; `-f` lo detiene antes si sigue corriendo.
- `docker volume ls` — lista los volúmenes que existen.
- `| grep pgdata` — pasa esa lista a `grep`, que deja sólo las líneas con `pgdata`.
- `pg2` — un contenedor **nuevo**, con otro nombre, sobre el mismo volumen.
- `docker logs pg2` — muestra lo que el contenedor ha escrito en su salida.
- `2>&1` — junta los errores con la salida normal, para que también pasen por el `|`.
- `| head -3` — deja sólo las 3 primeras líneas.

**Deberías ver:**
- `local     pgdata`: el volumen sigue ahí;
- **la misma fila**, `1 | ada`, desde un contenedor que nunca la insertó;
- en los logs: `PostgreSQL Database directory appears to contain a database; Skipping initialization`.

**Por qué:**
- `docker rm -f` se llevó la capa de escritura y el nombre; el estado estaba al lado ([[escalamiento-y-orquestacion]], puesta a prueba).
- La **inicialización** ocurrió una sola vez, en `pg`.
- La imagen trae `/var/lib/postgresql/data` vacío: la copia sólo aportó dueño y permisos.

## Tiempo 3: y ahora sí, matarlos

**Haz:**

```bash
docker rm -f pg2
docker volume rm pgdata
docker run -d --name pg3 -e POSTGRES_PASSWORD=fdd \
  -v pgdata:/var/lib/postgresql/data postgres:16
sleep 5; until docker exec pg3 pg_isready -q; do sleep 1; done
docker exec pg3 psql -U postgres -c 'SELECT * FROM notas;'
```

**Qué hace cada pieza:**

nada nuevo salvo `docker volume rm pgdata` — borra el volumen y lo que tenga adentro; no hay papelera.

**Deberías ver:**
- `ERROR:  relation "notas" does not exist`.

**Por qué:** `docker run` creó solo, sin avisar, un volumen `pgdata` **nuevo y vacío**. De todos los comandos de la página, `docker volume rm` es el único que borró un dato. Sin deshacer.

Limpia: `docker rm -f pg3 && docker volume rm pgdata` (`&&` corre lo segundo sólo si lo primero salió bien).

::: problem {#cont-p12-postgres-17 title="Un volumen de la 16, un servidor de la 17"}
Tienes un volumen inicializado por `postgres:16` y quieres actualizar: mismo volumen, imagen nueva.

```bash
docker volume create pg16data
docker run -d --name v16 -e POSTGRES_PASSWORD=fdd \
  -v pg16data:/var/lib/postgresql/data postgres:16
sleep 5; until docker exec v16 pg_isready -q; do sleep 1; done
docker rm -f v16
docker run -d --name v17 -e POSTGRES_PASSWORD=fdd \
  -v pg16data:/var/lib/postgresql/data postgres:17
sleep 3; docker logs v17
```

**Qué hace cada pieza:**

- `postgres:17` — otra imagen, Postgres 17, montando el volumen que escribió la 16.
- `sleep 3; docker logs v17` — le da 3 segundos para intentar arrancar y luego lees sus logs.

**Predice antes de correrlo:** ¿arranca `v17`? Si no, ¿qué lo impide, y por qué el volumen no lo resuelve?
:::

::: hint {of="cont-p12-postgres-17"}
El volumen no guarda «tus tablas»: guarda el **directorio de datos** de PostgreSQL, con su formato en disco. ¿Quién escribió ese formato?
:::

::: answer {of="cont-p12-postgres-17"}
**No arranca.** `docker ps -a` lo muestra `Exited (1)`, y `docker logs v17` trae, tras la marca de tiempo:

```text
FATAL:  database files are incompatible with server
DETAIL:  The data directory was initialized by PostgreSQL version 16,
         which is not compatible with this version 17.x.
```

(El parche, `17.x`, depende de la imagen del día.)

- El volumen hizo su trabajo **perfecto**: entregó intacto el directorio de datos.
- Ese directorio tiene un formato que cambia entre versiones mayores, y el 17 se niega a tocarlo antes que corromperlo. La negativa es la característica.
- **Un named volume preserva bytes, no compatibilidad.** Subir de mayor a mayor es una migración —`pg_upgrade`, o `pg_dump` de la 16 restaurado en la 17—, no una bandera.

Limpia: `docker rm -f v17 && docker volume rm pg16data`.
:::

Sigue con [[limpieza-de-docker]], porque todo esto dejó basura en tu disco.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor es desechable porque el dato no está adentro; borrar el contenedor es rehacer, borrar el volumen es perder.
