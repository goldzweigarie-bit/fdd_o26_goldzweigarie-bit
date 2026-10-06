---
id: ejercicio-combinado
title: "Ejercicio combinado: Git, bash y Docker"
nav_title: "Combinado: Git, bash y Docker"
summary: "Un repo con un script de bash, un Dockerfile y datos; tres ramas que entran por fast-forward, por commit de merge y con conflicto; y builds cuyo resultado depende de qué se mezcló. Cada pregunta con su respuesta explicada debajo."
status: ready
estimated_time: 45m
tags: [ejercicios, git, merge, conflictos, bash, docker]
prerequisites: [ejercicios-github, ejercicios-docker]
---

# Ejercicio combinado: Git, bash y Docker

**[PDF sin respuestas, para imprimir](../_assets/practica-combinada.pdf)** · unos 45 minutos · sin apuntes

En los parciales cada herramienta se preguntó sola. Aquí van juntas: el script vive en Git, el Dockerfile lo copia, y lo que imprime el contenedor depende de qué ramas mezclaste y de qué había en tu disco al construir. Debajo de cada pregunta hay una **pista** y la **respuesta**, plegadas. Abre la pista sólo si llevas un rato atorado. Todo se comprobó corriendo el escenario completo con Git 2.34, bash 5.2 y Docker 29.6.

La idea que atraviesa el ejercicio: **Git, bash y Docker no se avisan entre sí**. Git guarda commits, `docker build` copia lo que hay en tu disco, y bash corre lo que le den.

## El repo

`reporte/` cuenta ventas. En `main` hay un solo commit, **B**, con esto:

```text
reporte/          ← estás aquí
├── Dockerfile
├── contar.sh
└── datos/
    └── ventas.csv
```

`contar.sh`, con sus números de línea:

```text
1  archivo="$1"
2  if [[ ! -f "$archivo" ]]; then
3      printf 'no existe: %s\n' "$archivo" >&2
4      exit 1
5  fi
6  printf 'filas: %s\n' "$(wc -l < "$archivo")"
```

`Dockerfile` (la imagen `bash:5.2` es Alpine con bash instalado):

```dockerfile
FROM bash:5.2
WORKDIR /r
COPY contar.sh .
CMD ["bash", "contar.sh", "datos/ventas.csv"]
```

`datos/ventas.csv`, cuatro renglones:

```text
MX,10
US,5
MX,7
CA,3
```

Tres personas crearon una rama cada una, todas desde B, con un commit cada una:

```text
   +---F      filtro
   |
   +---T      titulo
   |
   +---I      imagen
   |
   B          main
```

| Rama | Commit | Qué cambia |
|---|---|---|
| `filtro` | F | `contar.sh`, línea 6: `wc -l < "$archivo"` pasa a `grep -c MX "$archivo"` |
| `titulo` | T | `contar.sh`, línea 6: `'filas: %s\n'` pasa a `'total: %s\n'` |
| `imagen` | I | `Dockerfile`: agrega `COPY datos/ datos/` después de `COPY contar.sh .` |

`grep -c MX` cuenta los renglones que contienen `MX`; `wc -l` cuenta todos.

## Parte 1 · Antes de mezclar nada

Estás en `main`, con B tal cual.

::: problem {#xc-1a title="a · El script en tu máquina"}
¿Qué imprime `bash contar.sh datos/ventas.csv`?
:::

::: hint {of="xc-1a"}
¿Cuántos renglones tiene el archivo, y qué cuenta `wc -l`?
:::

::: answer {of="xc-1a"}
**`filas: 4`.** El archivo tiene cuatro renglones, y `wc -l` los cuenta.
:::

::: problem {#xc-1b title="b · Un archivo que no existe"}
¿Qué imprime `bash contar.sh datos/mayo.csv`, y qué imprime justo después `echo $?`? ¿Por qué ese número?
:::

::: hint {of="xc-1b"}
Sigue el `if` de la línea 2. ¿Qué número le deja `exit` a `$?`?
:::

::: answer {of="xc-1b"}
Imprime **`no existe: datos/mayo.csv`** y luego **`1`**. La prueba de la línea 2 es verdadera porque el archivo no existe. El mensaje va a stderr (`>&2`), y `exit 1` termina con código 1, que significa «algo falló». `echo $?` imprime el código del último comando.
:::

::: problem {#xc-1c title="c · La imagen sin datos"}
Corres `docker build -t rep:0 .` y luego `docker run --rm rep:0`. ¿Qué imprime, y por qué, si `datos/ventas.csv` sí existe en tu carpeta?
:::

::: hint {of="xc-1c"}
¿Qué copia el Dockerfile de B? ¿Ve un contenedor tu carpeta si nadie se la monta?
:::

::: answer {of="xc-1c"}
**`no existe: datos/ventas.csv`.** El archivo existe **en tu carpeta**, pero el Dockerfile de B sólo copia `contar.sh`. El contenedor sólo ve lo que trae la imagen o lo que le montes. El código de salida del contenedor también es 1: `docker run` lo devuelve tal cual.
:::

::: problem {#xc-1d title="d · Hazlo funcionar sin reconstruir"}
Escribe un `docker run` que haga funcionar `rep:0` sin reconstruir la imagen. ¿Qué imprime?
:::

::: hint {of="xc-1d"}
¿Dónde busca el `CMD` el archivo, si el `WORKDIR` es `/r`? Monta tu carpeta justo ahí.
:::

::: answer {of="xc-1d"}
```bash
docker run --rm -v "$(pwd)/datos":/r/datos rep:0
```

Imprime **`filas: 4`**. El montaje pone tu carpeta en `/r/datos`, justo donde la busca el `CMD`, porque el `WORKDIR` es `/r`.
:::

**Repasa:** [[variables-comillas-y-salida]] y [[lab-con-volumen]].

## Parte 2 · La secuencia

Los comandos se corren **en orden**, todos desde `reporte/` y empezando en `main`. Cada fila parte de lo que dejó la anterior.

::: problem {#xc-2-1 title="Fila 1 · ¿Fast-forward o commit de merge?"}
```bash
git merge filtro
```
:::

::: hint {of="xc-2-1"}
¿Dónde está `main` y de qué commit nació `filtro`? ¿Hay algo que juntar, o basta con mover la etiqueta?
:::

::: answer {of="xc-2-1"}
**Fast-forward.** `main` sigue en B, y `filtro` es B más un commit. No hay nada que juntar: Git sólo **adelanta** `main` hasta F, sin crear ningún commit.
:::

::: problem {#xc-2-2 title="Fila 2 · ¿Y ahora? ¿Por qué es distinto?"}
```bash
git merge imagen
```
:::

::: hint {of="xc-2-2"}
Después de la fila 1, ¿`imagen` sigue colgando de la punta de `main`?
:::

::: answer {of="xc-2-2"}
**Commit de merge.** Ahora `main` está en F, e `imagen` nació en B: las dos ramas ya se separaron, y cada una tiene un commit que la otra no. Git las **junta** con un commit nuevo de dos padres (`Merge made by the 'ort' strategy`). No hay conflicto, porque F tocó `contar.sh` e I tocó el `Dockerfile`.
:::

::: problem {#xc-2-3 title="Fila 3 · ¿Qué imprime el run?"}
```bash
docker build -t rep:1 .
docker run --rm rep:1
```
:::

::: hint {of="xc-2-3"}
¿Qué dos cambios tiene ya `main`? Cuenta los renglones con `MX`.
:::

::: answer {of="xc-2-3"}
**`filas: 2`.** `main` ya tiene el `grep -c MX` de F y el `COPY datos/` de I: la imagen trae los datos, y hay dos renglones con `MX`. Todavía dice `filas:`, porque `titulo` no se ha mezclado.
:::

::: problem {#xc-2-4 title="Fila 4 · ¿Qué imprime cada run? (dos casillas)"}
```bash
echo "MX,1" >> datos/ventas.csv
docker run --rm rep:1
docker run --rm -v "$(pwd)/datos":/r/datos rep:1
```
:::

::: hint {of="xc-2-4"}
¿Cuándo se copiaron los datos a la imagen? ¿Qué tapa un montaje?
:::

::: answer {of="xc-2-4"}
- **Primero: `filas: 2`.** La imagen guardó los datos del momento del build. Agregar un renglón a tu disco no la cambia.
- **Segundo: `filas: 3`.** El montaje tapa el `/r/datos` de la imagen con tu carpeta, que ya tiene el tercer `MX`.
:::

::: problem {#xc-2-5 title="Fila 5 · ¿Qué responde Git?"}
```bash
git merge titulo
```

¿Te deja intentarlo aunque `datos/ventas.csv` tiene un cambio sin commit?
:::

::: hint {of="xc-2-5"}
¿Qué línea cambió `filtro`, y cuál `titulo`? ¿Toca `titulo` el archivo de datos?
:::

::: answer {of="xc-2-5"}
**Conflicto:**

```text
Auto-merging contar.sh
CONFLICT (content): Merge conflict in contar.sh
Automatic merge failed; fix conflicts and then commit the result.
```

F y T cambiaron **la misma línea 6** de forma distinta, y Git no puede elegir por ti.

**Sí te deja intentarlo**, porque `titulo` no toca `datos/ventas.csv` y el merge no tiene que pisarlo. `git status --short` muestra `UU contar.sh` (en conflicto) y ` M datos/ventas.csv` (tu cambio, intacto).
:::

::: problem {#xc-2-6 title="Fila 6 · ¿Cómo se ve el archivo? ¿Cuál lado es HEAD?"}
```bash
cat contar.sh
```

Escribe cómo se ven ahora las últimas líneas.
:::

::: hint {of="xc-2-6"}
Los marcadores son `<<<<<<<`, `=======` y `>>>>>>>`. `HEAD` es la rama donde estás parado.
:::

::: answer {of="xc-2-6"}
```text
<<<<<<< HEAD
printf 'filas: %s\n' "$(grep -c MX "$archivo")"
=======
printf 'total: %s\n' "$(wc -l < "$archivo")"
>>>>>>> titulo
```

`HEAD` es **la rama donde estás parado**: `main`, que ya traía el `grep` de F. Debajo del `=======` está lo que viene de `titulo`. Las líneas 1 a 5 no aparecen en conflicto, porque nadie las cambió.
:::

::: problem {#xc-2-7 title="Fila 7 · ¿El build? ¿El run? ¿El código?"}
```bash
docker build -t rep:2 .
docker run --rm -v "$(pwd)/datos":/r/datos rep:2
echo $?
```
:::

::: hint {of="xc-2-7"}
¿Le importa a `COPY` lo que dice el archivo? ¿Cómo lee bash una línea que empieza con `<<<`?
:::

::: answer {of="xc-2-7"}
- **El build termina bien.** `COPY` copia bytes y no sabe que el archivo tiene marcadores.
- **El run** imprime:

  ```text
  contar.sh: line 6: syntax error near unexpected token `<<<'
  contar.sh: line 6: `<<<<<<< HEAD'
  ```

- **`echo $?` da `2`**, el código con que bash señala un error de sintaxis.

Ni Git ni Docker impiden empaquetar un archivo a medio resolver. El único que se queja es bash, y sólo cuando lo corre.
:::

::: problem {#xc-2-8 title="Fila 8 · Resuelve quedándote con los dos cambios"}
```bash
# editas contar.sh y resuelves el conflicto
git add contar.sh
git commit
```

Escribe la línea 6 resuelta. ¿Qué muestra después `git status --short`?
:::

::: hint {of="xc-2-8"}
«Los dos cambios» es el texto de uno y el conteo del otro, en una sola línea. ¿Commiteaste el renglón de la fila 4?
:::

::: answer {of="xc-2-8"}
```bash
printf 'total: %s\n' "$(grep -c MX "$archivo")"
```

El texto `total:` de T, con el conteo `grep -c MX` de F. Se borran las tres líneas de marcadores y queda una sola línea 6. `git add` le dice a Git «ya lo resolví», y `git commit` crea el commit de merge.

`git status --short` muestra sólo ` M datos/ventas.csv`: el conflicto quedó resuelto y guardado, y tu renglón extra sigue sin commit.
:::

::: problem {#xc-2-9 title="Fila 9 · ¿Qué sale de la caché?"}
```bash
docker build -t rep:3 .
```
:::

::: hint {of="xc-2-9"}
¿Qué archivo cambió desde el último build? Lo que viene después de una capa rehecha se rehace también.
:::

::: answer {of="xc-2-9"}
| Paso | Resultado | Por qué |
|---|---|---|
| `FROM`, `WORKDIR /r` | caché | No cambiaron |
| `COPY contar.sh .` | **se rehace** | `contar.sh` cambió |
| `COPY datos/ datos/` | **se rehace** | Va después de una capa que cambió, y además `datos/` cambió en la fila 4 |
:::

::: problem {#xc-2-10 title="Fila 10 · ¿total: 2 o total: 3?"}
```bash
docker run --rm rep:3
```

¿Por qué, si el cambio de la fila 4 nunca se commiteó?
:::

::: hint {of="xc-2-10"}
¿De dónde copia `docker build`: del último commit o de tu disco?
:::

::: answer {of="xc-2-10"}
**`total: 3`.** `docker build` copia **lo que hay en tu disco**, no lo que hay en el último commit. El renglón `MX,1` nunca se commiteó, pero estaba en `datos/ventas.csv` al construir.

Ésta es la trampa del ejercicio: una imagen puede contener cambios que nadie más tiene. Otra persona que clone el repo y construya obtiene `total: 2`.
:::

::: problem {#xc-2-11 title="Fila 11 · ¿Cuántos commits de merge?"}
```bash
git log --oneline --graph
```

¿Cuántos commits de merge tiene `main`? ¿Por qué no hay uno para `filtro`?
:::

::: hint {of="xc-2-11"}
¿Cuál de los tres merges fue fast-forward?
:::

::: answer {of="xc-2-11"}
```text
*   Merge branch 'titulo'
|\
| * titulo total
* |   Merge branch 'imagen'
|\ \
| * | datos en la imagen
| |/
* / solo MX
|/
* base
```

**Dos**: el de `imagen` y el de `titulo`. `filtro` entró por fast-forward: F quedó en la línea de `main` sin commit de merge, porque no había nada que juntar.
:::

**Repasa:** [[branches-y-merge]], [[capas-y-cache]] y [[rutas-en-docker]].

## Parte 3 · Las comillas

::: problem {#xc-3a title="a · Sin comillas dentro del script"}
Alguien le quita las comillas a la variable en la línea 6 del script ya resuelto: `grep -c MX $archivo`. Luego corre `bash contar.sh "datos/ventas mayo.csv"` sobre un archivo que sí existe con ese nombre. ¿Qué imprime? ¿Qué da `echo $?`? ¿Por qué ese número es peligroso?
:::

::: hint {of="xc-3a"}
Sin comillas, ¿qué hace bash con un espacio dentro del valor de una variable? ¿Cuál es el último comando que corre el script?
:::

::: answer {of="xc-3a"}
```text
grep: datos/ventas: No such file or directory
grep: mayo.csv: No such file or directory
total:
```

`echo $?` da **`0`**.

Sin comillas, bash parte el valor en el espacio, y `grep` recibe **dos** nombres que no existen. La prueba de la línea 2 sí tenía comillas y pasó. El `printf` funciona y es el último comando, así que el script termina con 0.

**Es peligroso** porque cualquier cosa que revise el código de salida, un `&&` o un pipeline de datos, cree que todo salió bien y sigue con un `total:` vacío.
:::

::: problem {#xc-3b title="b · Sin comillas al llamarlo"}
Con el script correcto, alguien corre `bash contar.sh datos/ventas mayo.csv`, sin comillas al llamarlo. ¿Qué imprime y por qué?
:::

::: hint {of="xc-3b"}
Sin comillas al llamarlo, ¿cuántos argumentos recibe el script? ¿Cuál mira?
:::

::: answer {of="xc-3b"}
**`no existe: datos/ventas`.** `$1` es `datos/ventas` y `$2` es `mayo.csv`, y el script sólo mira `$1`. Las comillas importan en los dos lados: al llamar y adentro del script.
:::

::: problem {#xc-3c title="c · ¿Quién te avisó del conflicto?"}
En la parte 2, ¿qué herramienta te habría avisado del conflicto antes de construir la imagen de la fila 7: Git, bash o Docker? ¿Con qué comando?
:::

::: hint {of="xc-3c"}
¿Cuál de los tres avisó algo en la fila 5?
:::

::: answer {of="xc-3c"}
**Git**, desde la fila 5: el mensaje `CONFLICT`, y después `git status`, que marca el archivo con `UU`. Docker no lo detecta, y bash sólo cuando ya es tarde.
:::

**Repasa:** [[variables-comillas-y-salida]] y [[como-lee-bash]].
