---
id: en-mi-maquina-si-funciona
title: "En mi máquina sí funciona"
nav_title: "En mi máquina sí funciona"
summary: "Tres fallas del propio curso, el contenedor intermodal de 1956, y en qué se diferencia esto de un venv."
status: ready
estimated_time: 8m
tags: [contenedor, reproducibilidad, imagen, venv, conda, intermodal]
prerequisites: [la-idea-del-contenedor]
---

# En mi máquina sí funciona

**Página 1 de 9 · sección 1 de 3**

Meta: entender qué problema resolvieron los contenedores y por qué el mundo se movió a ellos.

::: figure {#cont-intermodal title="El mismo truco, dos veces: sellar la carga y estandarizar el agarre"}
![Dos recorridos paralelos del mismo puerto al mismo almacén. Arriba, la carga suelta de antes de 1956 —sacos, barriles y cajas— que se descarga y se vuelve a cargar a mano en cada trasbordo, con su costo marcado en cada uno. Abajo, el contenedor intermodal sellado que pasa de camión a grúa a barco sin abrirse una sola vez. A la derecha, la columna de equivalencias con el software: la carga suelta es tu programa con sus dependencias, el contenedor sellado es la imagen, y los tres vehículos van etiquetados como tu laptop, la máquina del compañero y el servidor](../_assets/cont-intermodal.svg)
:::

## En corto

- «En mi máquina sí funciona» no es una excusa: es el síntoma de que tu programa depende de cosas que tú nunca escribiste.
- Un contenedor empaqueta el programa **y todo lo que hay debajo** —intérprete, librerías del sistema, binarios, sistema de archivos— en un artefacto que se mueve sin abrirse.
- No es un `venv` con esteroides: el `venv` aísla paquetes de Python, el contenedor aísla el sistema entero que rodea a esos paquetes.

## Tres fallas que ya te pasaron en este curso

No son ejemplos inventados: son tres cosas que rompieron en las últimas cuatro unidades — el script de [[bash-scripting]], el patrón de [[taquigrafia-perl]] y el pipeline de [[cuando-se-rompe]].

| Caso | Qué rompió | Qué cambió debajo |
|---|---|---|
| **A** | el script de bash de la **unidad 5** devuelve otra cosa en la máquina del compañero — o nada | su `bash` es el 3.2 que Apple congeló en 2007, o su `date` es el de BSD y no entiende `-d` |
| **B** | el patrón de la **unidad 6** da dos resultados distintos sobre el mismo archivo | `grep -P` no existe en macOS, y `grep -E '\d'` no busca dígitos: busca la letra `d`, sin avisar |
| **C** | el pipeline de la **unidad 2** anda perfecto en tu laptop y muere en el servidor | allá hay Python 3.8 y un `pandas` viejo, o el CSV que leías vivía en `~/datos/` y ese directorio no existe |

**Tu código está bien escrito. Lo que es otro es el intérprete — y en ninguno de los tres casos hay un error que leer.**

> [!NOTE]
> Las tres tienen la misma forma: **el código es idéntico y el resultado no.** Lo que cambió está debajo del código, en la capa que nadie versiona porque nadie la escribió.

## McLean, 1956

El transporte marítimo vivió ese problema durante un siglo. La carga iba suelta —sacos, barriles, cajas—, y en cada trasbordo un equipo de estibadores la bajaba pieza por pieza y la volvía a acomodar.

Estibar carga suelta costaba alrededor de `$5.86` por tonelada; el mismo trabajo con contenedores, `$0.16` (Levinson, *The Box*, 2006, con cifras de 1956).

Malcom McLean era transportista, no naviero, y por eso vio lo que el gremio no veía: **el valor no está en la caja, está en no abrirla.** El 26 de abril de 1956 el *Ideal-X* zarpó de Newark a Houston con 58 contenedores. Nadie tuvo que saber qué llevaban adentro.

::: table {#cont-tabla-intermodal title="El puerto y el software"}

| En el puerto | En tu computadora |
|---|---|
| La carga suelta que hay que estibar en cada trasbordo | Tu programa, sus dependencias y las instrucciones de instalación en un README |
| El contenedor sellado, de medidas estándar | La **imagen**: el programa y su sistema, empaquetados |
| La grúa y el barco no saben qué hay dentro | Tu laptop, la máquina del compañero y el servidor sólo saben arrancarla |
| Lo único que se acuerda es cómo se agarra | Lo único que se acuerda es cómo se arranca |

:::

## «¿Y esto en qué se diferencia de un `venv`?»

Es la pregunta correcta, y la vas a hacer porque ya usas entornos virtuales. La respuesta no es «el contenedor es más grande»: **es que aíslan capas distintas.**

::: table {#cont-tabla-venv title="Qué aísla cada uno"}

| Qué queda aislado | `venv` | conda | Contenedor |
|---|---|---|---|
| Los paquetes de Python | sí | sí | sí |
| El intérprete y las librerías del sistema (`libc`, `libgomp`) | no: usa el Python y las librerías de la máquina | el intérprete sí; las del sistema, a medias | sí |
| Los binarios (`grep`, `bash`, `date`) y el sistema de archivos | no | no | sí |

:::

Lee la tabla contra las tres fallas de arriba. **Un `requirements.txt` arregla la mitad de C y no toca ni A ni B**, por una razón boba: **no tiene renglón para `grep`**. Tampoco para `bash`, ni para `libc`, ni para la versión del kernel. Eso que no tiene renglón es justo lo que rompió en las unidades 5 y 6.

## Y además: mil veces a la vez

Hasta aquí el contenedor parece una herramienta de reproducibilidad, y el mundo no se movió a algo tan grande sólo por eso.

La otra mitad es que un artefacto sellado e idéntico a sí mismo no sólo corre igual **en otra máquina**: corre igual **mil veces a la vez**, en mil máquinas, sin que nadie instale nada. Quién decide esas mil copias tiene nombre —**orquestación**— y es la página 5 de esta sección.

::: problem {#cont-p1-tres-fallas title="¿A cuál le sirve un contenedor?"}
En parejas, dos minutos. Para cada caso decide si empaquetarlo en un contenedor lo resuelve, y di por qué:

1. **A** — el script de bash que devuelve otra cosa en la máquina del compañero.
2. **B** — el patrón que encuentra la letra `d` en vez de dígitos en la laptop de al lado.
3. **C1** — el pipeline que muere en el servidor porque allá `pandas` es de 2019.
4. **C2** — el pipeline que muere en el servidor porque allá no existe `~/datos/ventas.csv`.

Cuando se acabe el tiempo se levanta la mano por opción, **antes** de que nadie diga la respuesta.
:::

::: hint {of="cont-p1-tres-fallas"}
Pregúntate qué viaja dentro de la caja sellada. ¿Viaja el programa? ¿Viajan las herramientas que el programa usa? ¿Viajan **tus datos**?
:::

::: answer {of="cont-p1-tres-fallas"}
**A, B y C1: sí.** En los tres el problema es una pieza de software que en una máquina es una versión y en otra es otra. Todas esas piezas —el `bash`, el `grep`, el intérprete, `pandas`— viajan dentro de la imagen, así que en las dos máquinas se corre exactamente el mismo binario.

**C2: no.** Un contenedor empaqueta **software, no datos**. Tu CSV no está adentro, y meterlo adentro sería peor, no mejor: la imagen se vuelve pesada e intransferible, y el contenedor es desechable.

- **Dónde vive ese archivo** es la pregunta que ordena la sección 2.
- **Por qué no puede vivir adentro** es la de la página 5.

Ése es el corte útil: **el contenedor te quita las diferencias de entorno de encima y te deja, limpia, la única decisión que sí era tuya.**
:::

Sigue con [[que-es-un-contenedor]], donde «proceso aislado» deja de ser una frase hecha.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el contenedor no empaqueta tu programa, empaqueta el sistema donde tu programa funcionaba.
