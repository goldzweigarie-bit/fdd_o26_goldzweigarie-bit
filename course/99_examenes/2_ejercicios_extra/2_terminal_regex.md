---
id: ejercicios-terminal
title: "Ejercicios extra de terminal y regex"
nav_title: "Terminal y regex"
summary: "Ejercicios con la forma del parcial 2, cada uno con una pista y su respuesta plegadas: leer y escribir regex, nombrar comandos, y moverse y mover archivos con rutas absolutas y relativas."
status: ready
estimated_time: 40m
tags: [ejercicios, terminal, bash, regex, rutas]
---

# Ejercicios extra de terminal y regex

Miden lo mismo que el [[parcial-terminal|parcial 2]] con casos nuevos. Debajo de cada pregunta hay dos cosas plegadas:

- **la pista**: ábrela sólo si llevas un rato atorado; si la abres de inmediato, el ejercicio pierde su chiste;
- **la respuesta**, con su explicación.

Las regex se probaron con `grep -E` y las rutas en un árbol de carpetas real. Si tienes una terminal a la mano, compruébalo tú también.

## Parte 1 · Leer y escribir regex

Todas las regex van para `grep -E`. Ahí `\d` **no** funciona (busca una `d` literal), así que los dígitos se escriben `[0-9]`.

::: problem {#xt-r1 title="R1 · Lee el patrón"}
¿Cuáles de estas líneas acepta `^[A-Z]{3}-[0-9]{4}$`?

`ABC-1234` · `AB-1234` · `ABC-12345` · `abc-1234` · `ABCD-1234`
:::

::: hint {of="xt-r1"}
Lee de izquierda a derecha y cuenta: ¿cuántas letras exige antes del guion, de qué tipo, y cuántos dígitos después? ¿Qué hacen `^` y `$`?
:::

::: answer {of="xt-r1"}
**Sólo `ABC-1234`.**

- `AB-1234` tiene dos letras, y se piden exactamente tres (`{3}`).
- `ABC-12345` tiene cinco dígitos: el `$` exige que la línea termine después del cuarto.
- `abc-1234` usa minúsculas, y `[A-Z]` sólo acepta mayúsculas.
- `ABCD-1234` tiene cuatro letras: el `^` exige que la línea empiece justo en la primera de las tres.

Sin `^` y `$`, `ABCD-1234` y `ABC-12345` **sí** pasarían, porque contienen un pedazo que cumple. Por eso los anclajes importan cuando quieres validar la línea completa.
:::

::: problem {#xt-r2 title="R2 · Código postal"}
Escribe una regex que acepte un código postal mexicano: exactamente **cinco dígitos**, nada más. Acepta `01000`; rechaza `1000`, `123456` y `0100A`.
:::

::: hint {of="xt-r2"}
Necesitas una clase para «un dígito», un cuantificador para «exactamente cinco», y anclas para que no sobre nada.
:::

::: answer {of="xt-r2"}
```text
^[0-9]{5}$
```

`[0-9]` es un dígito, `{5}` exactamente cinco veces, y `^`…`$` impiden que haya algo antes o después. También vale `^[[:digit:]]{5}$`. `[0-9]+` estaría mal, porque acepta cualquier cantidad de dígitos.
:::

::: problem {#xt-r3 title="R3 · Hora de 24 horas"}
Escribe una regex para una hora `HH:MM` de 24 horas: de `00:00` a `23:59`, siempre con dos dígitos. Acepta `07:30` y `23:59`; rechaza `24:00`, `7:30` y `12:60`.
:::

::: hint {of="xt-r3"}
Las horas no se pueden describir con una sola clase por dígito: de `00` a `19` el segundo dígito es libre, pero con `2` adelante sólo llega a `3`. Parte las horas en dos casos con `|`. Con los minutos basta mirar el primer dígito.
:::

::: answer {of="xt-r3"}
```text
^([01][0-9]|2[0-3]):[0-5][0-9]$
```

- `[01][0-9]` cubre de `00` a `19`.
- `2[0-3]` cubre de `20` a `23`.
- Los paréntesis agrupan las dos opciones para que el `|` no se lleve el resto del patrón.
- `[0-5][0-9]` cubre los minutos de `00` a `59`.

**Error típico:** `[0-2][0-9]`. Acepta `29:00`.
:::

::: problem {#xt-r4 title="R4 · Fecha AAAA-MM-DD"}
Escribe una regex para fechas `AAAA-MM-DD`, con mes de `01` a `12` y día de `01` a `31`. Luego contesta: ¿tu regex acepta `2026-02-30`? ¿Está mal por eso?
:::

::: hint {of="xt-r4"}
Es la misma idea de R3, aplicada dos veces: el mes y el día tienen casos distintos según su primer dígito.
:::

::: answer {of="xt-r4"}
```text
^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$
```

- Mes: `0[1-9]` (de `01` a `09`) o `1[0-2]` (de `10` a `12`).
- Día: `0[1-9]`, `[12][0-9]` (de `10` a `29`) o `3[01]` (`30` y `31`).

**Sí acepta `2026-02-30`, y no está mal.** Una regex valida **la forma**, no el calendario. No sabe que febrero tiene 28 días, ni cuáles años son bisiestos. Esa comprobación le toca al programa, por ejemplo convirtiendo el texto a fecha con Python. Usar la regex como primer filtro y el programa para lo demás es lo normal.
:::

::: problem {#xt-r5 title="R5 · Correo institucional"}
Escribe una regex que acepte correos que terminan exactamente en `@itam.mx`, con un usuario de minúsculas, dígitos, punto o guion bajo. Acepta `ana.perez@itam.mx`; rechaza `ana@itamxmx` y `ana@itam.mx.com`.
:::

::: hint {of="xt-r5"}
Hay un carácter en `itam.mx` que en una regex no significa lo que parece. ¿Qué acepta `.` sin escapar?
:::

::: answer {of="xt-r5"}
```text
^[a-z0-9._]+@itam\.mx$
```

- `[a-z0-9._]+` es el usuario: uno o más de esos caracteres. **Dentro** de los corchetes el punto es literal.
- `\.` es un punto literal. Sin la barra, `itam.mx` también aceptaría `itamxmx`, porque `.` es «cualquier carácter».
- El `$` rechaza `ana@itam.mx.com`.

Si tu terminal está en español y quieres aceptar mayúsculas, `[[:alnum:]._]` es más seguro que `[a-zA-Z]`.
:::

::: problem {#xt-r6 title="R6 · La palabra repetida"}
En un texto hay errores de dedo como «el el gato». ¿Qué imprime `grep -Eo '\b(\w+) \1\b'` con estas líneas?

```text
el el gato
la casa
esto es es raro
los losas
```
:::

::: hint {of="xt-r6"}
`(\w+)` captura una palabra, y `\1` exige **la misma** otra vez. `\b` marca dónde empieza o termina una palabra. ¿Termina una palabra justo después de `los` en «losas»?
:::

::: answer {of="xt-r6"}
```text
el el
es es
```

- `(\w+)` captura una palabra, y `\1` (la **retro-referencia**) exige repetir exactamente lo capturado.
- `-o` imprime sólo el pedazo que coincidió, no la línea completa.
- `los losas` no coincide: después del segundo `los` viene una `a`, no un fin de palabra, y el `\b` final lo exige.

La retro-referencia en `grep -E` es una extensión de GNU: funciona en Linux, y puede no funcionar en el `grep` de macOS.
:::

::: problem {#xt-r7 title="R7 · Enteros sin ceros a la izquierda"}
¿Qué líneas acepta `^(0|[1-9][0-9]*)$`? `0` · `7` · `10` · `007` · `00` · `120` · `-3`. Explica con una frase qué describe.
:::

::: hint {of="xt-r7"}
Hay dos caminos separados por `|`. ¿Con qué puede empezar el segundo? ¿Qué permite `*`?
:::

::: answer {of="xt-r7"}
**`0`, `7`, `10` y `120`.**

Describe **enteros no negativos sin ceros a la izquierda**: o el `0` solo, o un dígito de 1 a 9 seguido de cualquier cantidad de dígitos (`*` también acepta cero repeticiones, por eso pasa el `7`). Rechaza `007` y `00` por el cero inicial, y `-3` porque nadie permite el signo.

Es la misma idea que el importe del examen B del parcial: separar el caso del cero.
:::

**Repasa:** [[piezas-de-un-patron|Las piezas de un patrón]], [[cuantas-veces|Cuántas veces]], [[taquigrafia-perl|La taquigrafía de Perl]] y [[grupos-y-captura|Grupos y captura]].

## Parte 2 · El comando de cada acción

::: problem {#xt-c1 title="C · Diez acciones, diez comandos"}
Escribe el comando para cada acción:

1. Listar los archivos de la carpeta, **incluidos los ocultos**.
2. Ver el contenido completo de un archivo.
3. Ver sólo las primeras líneas de un archivo grande.
4. Contar cuántas líneas tiene un archivo.
5. Buscar las líneas que contienen una palabra.
6. Crear `a/b/c` de una vez, aunque `a` no exista.
7. Renombrar `viejo.txt` a `nuevo.txt`.
8. Subir a la carpeta madre.
9. Mandar la salida de un comando como entrada de otro.
10. Borrar una carpeta **vacía**.
:::

::: hint {of="xt-c1"}
Casi todos son abreviaturas en inglés: *list*, *concatenate*, *word count*, *make directory*, *move*, *change directory*, *remove directory*. El 9 no es un comando, es un símbolo.
:::

::: answer {of="xt-c1"}
| # | Respuesta | Nota |
|---|---|---|
| 1 | `ls -a` | Los ocultos empiezan con punto. `ls -la` también vale y muestra detalles |
| 2 | `cat archivo` | Para archivos largos, `less archivo` deja moverse |
| 3 | `head archivo` | Las 10 primeras; `head -n 3` las 3 primeras. `tail` muestra las últimas |
| 4 | `wc -l archivo` | `wc` sin `-l` cuenta también palabras y bytes |
| 5 | `grep palabra archivo` | `grep -c` cuenta las líneas en vez de mostrarlas |
| 6 | `mkdir -p a/b/c` | Sin `-p` falla si `a` no existe |
| 7 | `mv viejo.txt nuevo.txt` | En la terminal, renombrar es mover a otro nombre |
| 8 | `cd ..` | `..` es la carpeta madre; `cd` a secas va a tu home |
| 9 | `\|` (tubería) | `history \| grep cd` busca en el historial |
| 10 | `rmdir carpeta` | Se niega si no está vacía (comprobado). Es la versión segura |
:::

**Repasa:** [[archivos-y-comandos|Archivos y comandos]] y [[flujos-procesos-y-herramientas|Historial, tuberías y herramientas]].

## Parte 3 · Rutas

Todas las preguntas usan este árbol:

```text
/home/ana/
├── proyecto/
│   ├── datos/
│   │   └── crudo.csv
│   └── scripts/
└── descargas/
    └── nuevo.csv
```

::: problem {#xt-p1 title="P1 · Las dos relativas"}
Estás en `/home/ana/proyecto/scripts/`. Mueve `nuevo.csv` a la carpeta `datos/` usando **rutas relativas** en origen y destino.
:::

::: hint {of="xt-p1"}
Desde `scripts/`, ¿cuántos niveles subes para llegar a `ana/`? ¿Y para llegar a `proyecto/`?
:::

::: answer {of="xt-p1"}
```bash
mv ../../descargas/nuevo.csv ../datos/
```

- **Origen:** subes dos niveles (`scripts` → `proyecto` → `ana`) y bajas a `descargas/`.
- **Destino:** subes uno (a `proyecto`) y bajas a `datos/`.
:::

::: problem {#xt-p2 title="P2 · Las dos absolutas"}
Mismo lugar, misma acción, ahora con **rutas absolutas**.
:::

::: hint {of="xt-p2"}
Una ruta absoluta no depende de dónde estés: empieza en `/` y baja nombre por nombre.
:::

::: answer {of="xt-p2"}
```bash
mv /home/ana/descargas/nuevo.csv /home/ana/proyecto/datos/
```

Funciona igual desde cualquier carpeta. `~/descargas/nuevo.csv` también vale: la shell lo convierte en `/home/ana/descargas/nuevo.csv` antes de correr el comando.
:::

::: problem {#xt-p3 title="P3 · Renombrar sin mover"}
Estás en `/home/ana/`. Cambia el nombre de `crudo.csv` a `ventas.csv` sin sacarlo de `datos/`.
:::

::: hint {of="xt-p3"}
`mv` no distingue entre mover y renombrar: sólo cambia la ruta de un archivo. ¿Qué ruta debe tener al final?
:::

::: answer {of="xt-p3"}
```bash
mv proyecto/datos/crudo.csv proyecto/datos/ventas.csv
```

El archivo se queda en la misma carpeta con otro nombre. Si escribes sólo `ventas.csv` como destino, lo mueves a `/home/ana/` **y** lo renombras.
:::

::: problem {#xt-p4 title="P4 · ¿Dónde quedaste?"}
Estás en `/home/ana/proyecto/datos/` y corres `cd ../scripts/../../descargas`. ¿Qué imprime `pwd`?
:::

::: hint {of="xt-p4"}
Avanza pedazo por pedazo, separando en cada `/`. Cada `..` deshace un paso.
:::

::: answer {of="xt-p4"}
**`/home/ana/descargas`.**

| Pedazo | Quedas en |
|---|---|
| `..` | `/home/ana/proyecto` |
| `scripts` | `/home/ana/proyecto/scripts` |
| `..` | `/home/ana/proyecto` |
| `..` | `/home/ana` |
| `descargas` | `/home/ana/descargas` |

Entrar a `scripts` para salir enseguida no sirve de nada, pero es válido.
:::

::: problem {#xt-p5 title="P5 · El error de la diagonal"}
Estás en `/home/ana/proyecto/` y corres:

```text
$ mv /datos/crudo.csv scripts/
mv: cannot stat '/datos/crudo.csv': No such file or directory
```

El archivo sí existe. ¿Qué pasó, y cuál es el comando correcto?
:::

::: hint {of="xt-p5"}
¿Qué significa una `/` al **principio** de una ruta?
:::

::: answer {of="xt-p5"}
La `/` inicial vuelve la ruta **absoluta**: busca una carpeta `datos` colgando de la raíz, y `/datos` no existe. «cannot stat» significa que no encontró ese archivo.

```bash
mv datos/crudo.csv scripts/
```

Sin la diagonal, la ruta es relativa a donde estás. En una terminal en español, el mismo error dice «No existe el archivo o el directorio».
:::

::: problem {#xt-p6 title="P6 · mv con destino que existe o no existe"}
Estás en `datos/`, que contiene `crudo.csv`. ¿Qué hace `mv crudo.csv respaldo` en cada caso?

a) No existe nada llamado `respaldo`.

b) `respaldo/` ya existe y es una carpeta.
:::

::: hint {of="xt-p6"}
`mv` mira el destino antes de decidir: si es una carpeta, mete el archivo adentro.
:::

::: answer {of="xt-p6"}
- **a)** Lo **renombra**: ahora hay un archivo llamado `respaldo`, sin extensión.
- **b)** Lo **mete en la carpeta**: queda `respaldo/crudo.csv`.

Las dos cosas se comprobaron. Para dejar claro que esperas una carpeta, escribe el destino con diagonal final: `mv crudo.csv respaldo/`. Si la carpeta no existe, eso falla en lugar de renombrar a escondidas.
:::

**Repasa:** [[entrar-y-orientarte|Entrar y orientarte]] y [[archivos-y-comandos|Archivos y comandos]].
