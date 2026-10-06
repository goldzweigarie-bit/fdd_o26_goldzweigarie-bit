---
id: ejercicios-github
title: "Ejercicios extra de GitHub"
nav_title: "GitHub"
summary: "Ejercicios nuevos con la forma del parcial de GitHub, cada uno con su respuesta explicada debajo: tres árboles de commits, siete errores reales de Git y un ritual con errores."
status: ready
estimated_time: 40m
tags: [ejercicios, git, github, ritual, branches, errores]
---

# Ejercicios extra de GitHub

**[PDF sin respuestas, para imprimir](../_assets/practica-github.pdf)** · unos 40 minutos · sin apuntes

Miden lo mismo que el parcial, con escenarios nuevos. Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado. Donde dice «con tus palabras», no escribas comandos. En `<login>` imagina el tuyo.

Casi todo sale de una idea: **un pull request muestra la diferencia entre tu rama y el punto donde se separó del `main` del curso**.

## Parte 1 · Lee el árbol

Los árboles se leen de izquierda a derecha: los commits viejos a la izquierda. Las letras son commits y los nombres de la derecha son ramas.

### Árbol 1 · Trabajó en main

Ana no creó rama: hizo sus commits M1 y M2 directamente en `main`, los subió a su fork y abrió el pull request desde `main`.

```text
o-o-o              upstream/main
     \
      M1---M2      main, origin/main
                   (pull request abierto desde main)
```

::: problem {#xg-1a title="Árbol 1a · ¿Qué muestra, y por qué sale en rojo?"}
¿Qué archivos muestra su pull request? Si todos están dentro de `estudiantes/ana/`, ¿por qué la revisión automática lo marca en rojo?
:::

::: hint {of="xg-1a"}
Además de los archivos, la revisión mira de qué rama sale el pull request.
:::

::: answer {of="xg-1a"}
Muestra M1 y M2: sólo su carpeta. Sale en rojo porque el pull request sale **desde `main`**, y la rama es parte de la entrega. Tu `main` tiene que ser una copia limpia del curso: es el punto de partida de todas tus tareas.
:::

::: problem {#xg-1b title="Árbol 1b · ¿Cómo queda su main después de actualizar?"}
La semana siguiente el curso publica un commit P, y Ana hace el bloque A completo del ritual. ¿Cómo queda su `main`? ¿Sigue siendo una copia del curso?
:::

::: hint {of="xg-1b"}
Después de que el curso publica P, ¿están `main` y `upstream/main` en la misma línea, o ya se separaron?
:::

::: answer {of="xg-1b"}
Su `main` y `upstream/main` ya se separaron, así que el merge no puede avanzar en línea recta y crea un **commit de merge**. Queda con todo lo del curso **más** M1 y M2. Ya no es una copia del curso, y no lo será mientras M1 y M2 no lleguen al curso.
:::

::: problem {#xg-1c title="Árbol 1c · ¿Qué arrastra la tarea siguiente?"}
Desde ese `main` crea la rama de la tarea siguiente. Si el primer pull request todavía no se ha mergeado, ¿qué arrastra el nuevo?
:::

::: hint {of="xg-1c"}
Una rama hereda todo lo del commit donde nace. ¿Qué tiene ese `main`?
:::

::: answer {of="xg-1c"}
Arrastra M1 y M2. La rama nace de un `main` que los contiene, y el curso no los tiene. Es el mismo problema del examen A del parcial, sólo que aquí la herencia viene de `main`.
:::

::: problem {#xg-1d title="Árbol 1d · ¿Cómo lo arreglas sin perder M1 y M2?"}
Con tus palabras.
:::

::: hint {of="xg-1d"}
Primero pon el trabajo a salvo en un lugar que no sea `main`, y después limpia `main`.
:::

::: answer {of="xg-1d"}
Primero se pone a salvo el trabajo, y después se limpia `main`:

1. Parada en `main`, que apunta a M2, crea la rama de la tarea. Esa rama se lleva M1 y M2.
2. Sube esa rama y abre el pull request **desde ella**. Cierra el que salía de `main`.
3. Regresa `main` a donde está `upstream/main`.

**También vale:** para el paso 3, `git reset --hard upstream/main` parada en `main`. Ojo: sólo es seguro **después** de que el trabajo ya vive en la otra rama, porque `--hard` pisa los archivos de tu disco.
:::

### Árbol 2 · Dos ramas hermanas

Beto actualizó `main` y desde ahí creó las dos ramas, una para cada tarea. El pull request de la 07 sigue abierto.

```text
       A---B       tarea-07-git (PR abierto)
      /
o-o-o              main = upstream/main
      \
       D---E       tarea-08-datacamp-intro
```

::: problem {#xg-2a title="Árbol 2a · ¿Qué muestra el pull request de la 08?"}
¿Qué archivos muestra el pull request de `tarea-08-datacamp-intro`?
:::

::: hint {of="xg-2a"}
¿Dónde se separó la 08 de `main`? Cuenta lo que hay entre ese punto y E.
:::

::: answer {of="xg-2a"}
Sólo D y E: la carpeta `docker/`. La 08 se separó de `main` en el último `o`, y entre ese punto y E sólo está lo suyo.
:::

::: problem {#xg-2b title="Árbol 2b · ¿Perdió la tarea 07?"}
Parado en `tarea-08-datacamp-intro`, Beto lista `estudiantes/beto/` y **no ve** `07_git/`. ¿Perdió su tarea 07? ¿Qué hizo `git switch` con esos archivos?
:::

::: hint {of="xg-2b"}
`git switch` cambia los archivos de tu disco por los de la rama a la que llegas.
:::

::: answer {of="xg-2b"}
No perdió nada. `git switch` pone en tu disco los archivos **de la rama a la que llegas**. La 08 nunca tuvo `07_git/`, así que esa carpeta desaparece al entrar y reaparece al volver a `tarea-07-git`. La tarea vive en su rama, en su fork y en su pull request.
:::

::: problem {#xg-2c title="Árbol 2c · Si se mergea la 07, ¿cambia la 08?"}
Se mergea la tarea 07. ¿Cambia lo que muestra el pull request de la 08?
:::

::: hint {of="xg-2c"}
¿Cargaba la 08 algún commit de la 07?
:::

::: answer {of="xg-2c"}
No. La base de la 08 sigue siendo el último `o`, y entre ese punto y E siguen estando sólo D y E.
:::

::: problem {#xg-2d title="Árbol 2d · ¿Por qué en el examen A sí cambiaba?"}
En el examen A del parcial, la 08 nació de la 07. ¿Por qué allá mergear la 07 sí cambiaba el pull request y aquí no?
:::

::: hint {of="xg-2d"}
Compara dónde nació la 08 en cada caso.
:::

::: answer {of="xg-2d"}
Allá la rama de la 08 **cargaba** A, B y C. Al mergear la 07, esos commits pasaban a la base y dejaban de aparecer. Aquí la 08 nunca cargó A y B, así que no hay nada que deje de aparecer.
:::

### Árbol 3 · Editó el archivo del curso

Carla no copió la plantilla a su carpeta: editó directo `codigo/docker/certificaciones.md` en su commit X. Mientras tanto el profesor cambió **esa misma línea** en el commit R.

```text
o---o---R          upstream/main
     \             (R cambia la línea 3)
      X            tarea-08-datacamp-intro
                   (X cambia la misma línea 3)
```

::: problem {#xg-3a title="Árbol 3a · ¿Qué dice la revisión automática?"}
¿Qué dice la revisión automática de su pull request, y por qué?
:::

::: hint {of="xg-3a"}
¿Qué regla de la revisión automática habla de la carpeta donde están los archivos?
:::

::: answer {of="xg-3a"}
**Rojo.** El pull request toca un archivo fuera de `estudiantes/carla/`. Si se mergeara, su cambio quedaría en la plantilla de todo el grupo.
:::

::: problem {#xg-3b title="Árbol 3b · ¿Merge limpio o conflicto?"}
Si alguien intentara mergearlo, ¿Git lo mezcla solo o hay conflicto? ¿Por qué?
:::

::: hint {of="xg-3b"}
¿Cuántos lados cambiaron la misma línea desde el ancestro común?
:::

::: answer {of="xg-3b"}
**Conflicto.** Git compara las dos versiones contra el ancestro común. Si sólo una cambió una línea, se queda con esa sola. Aquí **las dos** cambiaron la línea 3, y Git no puede saber cuál es la buena.
:::

::: problem {#xg-3c title="Árbol 3c · ¿Y si hubiera escrito en su copia?"}
Si hubiera escrito en `estudiantes/carla/docker/certificaciones.md`, ¿habría conflicto con R?
:::

::: hint {of="xg-3c"}
¿Es el mismo archivo, o son dos rutas distintas?
:::

::: answer {of="xg-3c"}
No. Son dos archivos en dos rutas distintas: R toca uno y X el otro. Git los mezcla solo.
:::

::: problem {#xg-3d title="Árbol 3d · ¿Qué regla lo evita?"}
¿Qué regla del curso evita esto, y por qué funciona aunque treinta personas entreguen la misma tarea?
:::

::: hint {of="xg-3d"}
Es la regla que dice dónde copias la plantilla y dónde trabajas.
:::

::: answer {of="xg-3d"}
**La regla del espejo**: copiar la plantilla a `estudiantes/<login>/` con la misma ruta, y trabajar sólo ahí. Cada quien escribe en una carpeta que nadie más toca, y nadie edita `codigo/`. Treinta pull requests no comparten ni una línea: ninguno choca con otro ni con las correcciones del curso.
:::

**Repasa:** [[branches-y-merge]], [[branches-en-serio]], [[el-flujo-del-curso]] y [[deshacer-en-git]].

## Parte 2 · Lee el error

Cada caso trae lo que la persona corrió y lo que Git contestó, tal cual. Escribe **qué pasó** y **cuál es el siguiente paso**.

::: problem {#xg-e1 title="Error 1 · Primer push de una rama nueva"}
```text
$ git push
fatal: The current branch tarea-09-uv-docker has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin tarea-09-uv-docker
```
:::

::: hint {of="xg-e1"}
«no upstream branch»: la rama nunca se ha subido. Git te sugiere el comando en el mismo mensaje.
:::

::: answer {of="xg-e1"}
**Qué pasó.** La rama existe en su máquina pero nunca se ha subido, y un `git push` a secas no sabe a dónde mandarla.

**Siguiente paso.** `git push -u origin tarea-09-uv-docker`. Con el `-u`, de ahí en adelante basta `git push`.
:::

::: problem {#xg-e2 title="Error 2 · Editó el README desde la página de GitHub"}
El día anterior editó el README de su fork **desde la página de GitHub**. Hoy, en su máquina:

```text
$ git push origin main
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'github.com:ana/fdd_o26_ana.git'
hint: Updates were rejected because the remote contains work that you do
hint: not have locally.
```
:::

::: hint {of="xg-e2"}
«the remote contains work that you do not have locally»: ¿qué commit tiene el fork que tu máquina no?
:::

::: answer {of="xg-e2"}
**Qué pasó.** Su fork tiene un commit, la edición en la web, que su máquina no tiene. Git no sube para no borrarlo.

**Siguiente paso.** Traerlo y mezclarlo: `git pull origin main`. Luego `git push origin main`. **Nunca** `--force`, porque borraría el commit de la web.
:::

::: problem {#xg-e3 title="Error 3 · Permiso denegado"}
Clonó el repositorio del curso y dejó para después la conexión con su fork.

```text
$ git push -u origin tarea-08-imagen
ERROR: Permission to raya-lucaria/fdd_o26.git denied to ana.
fatal: Could not read from remote repository.
```
:::

::: hint {of="xg-e3"}
¿A quién le intentaste subir? Lee el nombre del repositorio en el error.
:::

::: answer {of="xg-e3"}
**Qué pasó.** `origin` apunta al repositorio del curso, donde nadie del grupo puede escribir.

**Siguiente paso.** `git remote -v` para confirmarlo, y terminar de conectar: `git remote rename origin upstream` y `git remote add origin` con la URL de su fork.
:::

::: problem {#xg-e4 title="Error 4 · Cambiar de rama con trabajo sin guardar"}
Editó `notas.md` en la rama de la tarea, no hizo commit, y quiere volver a `main`.

```text
$ git switch main
error: Your local changes to the following files would be overwritten by checkout:
	estudiantes/ana/09_python/notas.md
Please commit your changes or stash them before you switch branches.
Aborting
```
:::

::: hint {of="xg-e4"}
Git se niega para no perder tu trabajo. ¿Cuáles son las dos formas de guardarlo antes de cambiar de rama?
:::

::: answer {of="xg-e4"}
**Qué pasó.** Tiene un cambio sin guardar en un archivo que es distinto en `main`. Cambiar de rama lo pisaría, y Git se niega a perderlo.

**Siguiente paso.** `git commit` si el cambio ya está listo. Si no, `git stash` y, de regreso en la rama, `git stash pop`.
:::

::: problem {#xg-e5 title="Error 5 · El .venv no aparece"}
Corrió `uv sync`, que creó `estudiantes/ana/09_python/uv_docker/.venv/` con cientos de archivos. Luego `git status --short` no muestra nada. ¿Se perdió el ambiente? ¿Es un problema?
:::

::: hint {of="xg-e5"}
¿Qué archivo del curso le dice a Git qué rutas no mirar?
:::

::: answer {of="xg-e5"}
**No es un problema: así debe ser.** El `.gitignore` del curso excluye `.venv/`, así que Git ni lo mira. El ambiente sigue en el disco. `.venv/` no se sube, porque se recrea con `uv sync`.
:::

::: problem {#xg-e6 title="Error 6 · Un .DS_Store apartado"}
Quiere sacar `.DS_Store` de lo que va a guardar **sin borrarlo** de su disco.

```text
$ git status
On branch tarea-09-uv-docker
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   estudiantes/ana/09_python/.DS_Store
	new file:   estudiantes/ana/09_python/uv_docker/pyproject.toml
```
:::

::: hint {of="xg-e6"}
El propio `git status` dice el comando entre paréntesis.
:::

::: answer {of="xg-e6"}
**Qué pasó.** `.DS_Store` es basura de macOS y quedó apartada para el commit.

**Siguiente paso.** `git restore --staged estudiantes/ana/09_python/.DS_Store`. Sólo la saca del staging area; el archivo sigue en el disco. `git rm --cached` hace lo mismo. Para que no vuelva a pasar, la ruta va al `.gitignore`.
:::

::: problem {#xg-e7 title="Error 7 · Un commit que salió mal, sin push"}
Hizo commit y se dio cuenta de que le faltó un archivo y de que el mensaje está mal. **Todavía no hace push.** Quiere deshacer el commit pero conservar los cambios.
:::

::: hint {of="xg-e7"}
Necesitas deshacer el commit pero conservar los cambios apartados. En [[deshacer-en-git|Deshacer]] hay un `reset` que hace justo eso.
:::

::: answer {of="xg-e7"}
**Siguiente paso.** `git reset --soft HEAD~1`. Deshace el commit y deja los cambios apartados, listos para agregar lo que faltaba y repetir el commit con el mensaje correcto.

**Por qué sólo antes del push.** Reescribir un commit que ya subiste obliga a forzar el push, y eso borra historia en tu fork. Después del push, lo correcto es un commit nuevo que corrija.
:::

**Repasa:** [[deshacer-en-git]], [[lo-que-no-se-sube]] y la tabla de errores de [[cheatsheet-git]].

## Parte 3 · Encuentra los errores

Dani escribió este ritual para entregar `tarea-09-uv-docker`, cuya carpeta es `09_python/`. Lo corrió completo y **ningún comando falló**, pero la entrega salió mal. Ya tenía conectado su fork.

```text
 1   git switch -c tarea-09-uv-docker
 2   git switch main
 3   git fetch upstream
 4   git merge upstream/main
 5   git push origin main
 6   mkdir -p estudiantes/$GHUSER/09_python
 7   cp -r codigo/09_python estudiantes/$GHUSER/09_python/
 8   git status
 9   git add .
10   git commit -m "tarea 9"
11   git push -u origin main
```

::: problem {#xg-r1 title="a · Los cinco problemas"}
Hay **cinco** problemas: cuatro líneas mal y una que falta. Para cada uno, di la línea, qué se rompe y por qué.
:::

::: hint {of="xg-r1"}
Revisa cada línea contra el ritual del curso: el orden, el `/.`, el `add` y el `push`. Uno de los cinco es una línea que falta.
:::

::: answer {of="xg-r1"}
- **Línea 1.** La rama nace de un `main` sin actualizar, y además la línea 2 la saca de ella: todo lo que sigue pasa en `main`. Crear la rama va **después** de las líneas 2 a 5.
- **Línea 7.** Sin el `/.` final, `cp -r` copia **la carpeta**, y como el destino ya existe (lo creó la línea 6) la mete adentro: `09_python/09_python/`.
- **Línea 9.** `git add .` aparta todo lo que cambió en el repo, incluida la basura. El curso aparta por ruta: `git add estudiantes/$GHUSER/09_python`.
- **Falta un `git status` después de la 9.** Es la última oportunidad de ver qué se va a guardar antes de guardarlo.
- **Línea 11.** Sube `main` y no la rama de la tarea. Desde `main` la revisión rechaza el pull request.
:::

::: problem {#xg-r2 title="b · ¿En qué rama quedaron los commits?"}
Después de correr todo, ¿en qué rama quedaron sus commits? ¿Qué rama subió a su fork?
:::

::: hint {of="xg-r2"}
Sigue con el dedo en qué rama estás después de cada `git switch`.
:::

::: answer {of="xg-r2"}
En `main`. La línea 2 la cambió a `main` y nunca volvió: `tarea-09-uv-docker` existe, pero vacía y sin subir. A su fork subió `main`, con su trabajo adentro: es el árbol 1 de esta misma página.
:::

::: problem {#xg-r3 title="c · ¿Dónde quedó hola.py?"}
Escribe la ruta donde quedó `hola.py`, que en el curso está en `codigo/09_python/ambientes/hola.py`.
:::

::: hint {of="xg-r3"}
¿Qué hace `cp -r` sin `/.` cuando la carpeta destino ya existe?
:::

::: answer {of="xg-r3"}
`estudiantes/<login>/09_python/09_python/ambientes/hola.py`, con un `09_python` de más (comprobado). Así no es espejo del curso, y la revisión no encuentra los archivos donde los busca.
:::

::: problem {#xg-r4 title="d · El ritual corregido"}
Escribe el ritual corregido, completo y en orden.
:::

::: hint {of="xg-r4"}
Es el ritual del curso con `tarea-09-uv-docker` y `09_python`. Empieza por `main`.
:::

::: answer {of="xg-r4"}
```bash
git switch main
git fetch upstream
git merge upstream/main
git push origin main
git switch -c tarea-09-uv-docker
mkdir -p estudiantes/$GHUSER/09_python
cp -r codigo/09_python/. estudiantes/$GHUSER/09_python/
git status
git add estudiantes/$GHUSER/09_python
git status
git commit -m "unidad 09: labs y mi ambiente uv en Docker"
git push -u origin tarea-09-uv-docker
```

Y al final el pull request en el navegador: base `raya-lucaria/fdd_o26` · `main`, compare `tarea-09-uv-docker`.
:::

**Repasa:** [[el-ritual-del-curso]].
