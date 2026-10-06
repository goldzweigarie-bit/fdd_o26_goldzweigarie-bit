---
id: ejercicios-arquitectura
title: "Ejercicios extra de arquitectura y SO"
nav_title: "Arquitectura y SO"
summary: "Ejercicios con la forma del parcial 1, cada uno con una pista y su respuesta plegadas: jerarquía de memoria, localidad, CPU contra GPU, FLOPS y tiempos, el techo de la memoria, GHz, ISA y el sistema operativo."
status: ready
estimated_time: 40m
tags: [ejercicios, arquitectura, memoria, cpu, gpu, flops, sistemas-operativos]
---

# Ejercicios extra de arquitectura y SO

Miden lo mismo que el [[parcial-arquitectura|parcial 1]] con casos nuevos. Debajo de cada pregunta hay dos cosas plegadas:

- **la pista**: ábrela sólo si llevas un rato atorado;
- **la respuesta**, con su explicación.

Varias preguntas piden una cuenta. Hazla en papel: son órdenes de magnitud, y lo que importa es el razonamiento.

## Parte 1 · Memoria

::: problem {#xa-1 title="1 · Ordena por velocidad"}
Ordena del más rápido al más lento: SSD, caché L2, registro, RAM, red, caché L1, caché L3. ¿Qué pasa con la capacidad en ese mismo orden?
:::

::: hint {of="xa-1"}
Piensa en la distancia al lugar donde se hace la cuenta. Lo que está dentro del núcleo es lo más rápido.
:::

::: answer {of="xa-1"}
**Registro → L1 → L2 → L3 → RAM → SSD → red.**

La capacidad va **al revés**: los registros guardan bytes, y la red, casi lo que quieras. Al acercarse al cómputo, cada nivel es más rápido, más pequeño y más caro por byte. Por eso existe la jerarquía: no hay una memoria rápida, grande y barata a la vez.
:::

::: problem {#xa-2 title="2 · No cupo"}
Tu laptop tiene 16 GB de RAM. Procesar una tabla de 2 GB tarda 10 segundos. Una tabla de 40 GB, con el mismo procesamiento, tarda mucho más que 20 veces eso. ¿Por qué no escala en proporción?
:::

::: hint {of="xa-2"}
¿Dónde quedan los 40 GB si la RAM tiene 16? ¿Qué nivel de la jerarquía toca entonces cada acceso?
:::

::: answer {of="xa-2"}
Los 40 GB **no caben** en RAM. El sistema operativo manda pedazos al SSD y los vuelve a traer cuando se necesitan, y cada uno de esos accesos es unas mil veces más lento que uno a RAM. Ya no estás haciendo 20 veces el mismo trabajo: estás haciendo el trabajo **un nivel más abajo** en la jerarquía.

Arreglos posibles: procesar por pedazos que quepan, usar sólo las columnas necesarias, o una máquina con más RAM. Es el síntoma «no cabe» del curso: el límite es la **capacidad**.
:::

::: problem {#xa-3 title="3 · En orden o al azar"}
Dos programas leen los mismos 1,000 millones de números de un arreglo en RAM. Uno los recorre **en orden** y el otro **saltando al azar**. Leen la misma cantidad de datos. ¿Cuál termina antes, y por qué?
:::

::: hint {of="xa-3"}
Cuando la CPU trae un dato de la RAM, no trae sólo ese: trae un bloque con sus vecinos. ¿A cuál de los dos programas le sirven los vecinos?
:::

::: answer {of="xa-3"}
**El que va en orden**, por mucho.

- Cada viaje a la RAM trae un **bloque** de datos contiguos a la caché. Si recorres en orden, los siguientes números ya están en la caché, y además el procesador puede adivinar qué vas a pedir y traerlo antes.
- Al azar, casi cada lectura cae en un bloque nuevo: desperdicias el resto del bloque y pagas la **latencia** completa de la RAM en cada número.

Esto es la **localidad**. Un recorrido en orden aprovecha el **ancho de banda**; uno al azar queda dominado por la latencia. Misma cantidad de bytes, métrica distinta.
:::

**Repasa:** [[memoria-y-datos|Memoria y movimiento de datos]].

## Parte 2 · CPU, GPU y FLOPS

::: problem {#xa-4 title="4 · ¿CPU o GPU?"}
Para cada tarea, elige CPU o GPU y di por qué en una frase:

a) Compilar un programa.

b) Multiplicar dos matrices de 10,000 × 10,000.

c) Un servidor web que atiende solicitudes pequeñas, cada una con su lógica.

d) Aplicar el mismo filtro a un millón de imágenes.

e) Leer un JSON con estructura irregular y validar cada campo.
:::

::: hint {of="xa-4"}
Pregúntate en cada caso: ¿es la misma operación sobre muchos datos independientes, o son decisiones distintas paso a paso?
:::

::: answer {of="xa-4"}
| Tarea | Elige | Por qué |
|---|---|---|
| a) Compilar | **CPU** | Lleno de decisiones y ramas; cada paso depende del anterior |
| b) Matrices | **GPU** | Millones de multiplicaciones iguales e independientes |
| c) Servidor web | **CPU** | Solicitudes pequeñas con lógica distinta; importa la latencia de cada una |
| d) Filtro a imágenes | **GPU** | La misma operación sobre muchísimos píxeles |
| e) JSON irregular | **CPU** | Cada campo se valida distinto: control irregular |

En b) y d), la GPU gana si el volumen justifica copiar los datos a su memoria. Con pocas imágenes, la copia puede costar más que el cálculo (ejercicio 7).
:::

::: problem {#xa-5 title="5 · ¿Cuánto tarda el entrenamiento?"}
Entrenar un modelo requiere **6 × 10¹⁸ FLOP**. Tu GPU anuncia **300 TFLOPS**, pero en la práctica tu código aprovecha sólo el **40 %**. ¿Cuánto tarda, en horas?
:::

::: hint {of="xa-5"}
FLOP es trabajo y FLOPS es ritmo: tiempo = trabajo / ritmo. ¿Cuánto vale «tera»? Aplica el 40 % al ritmo.
:::

::: answer {of="xa-5"}
- Ritmo real: 300 × 10¹² × 0.4 = **1.2 × 10¹⁴ FLOPS**.
- Tiempo: 6 × 10¹⁸ / 1.2 × 10¹⁴ = **5 × 10⁴ s ≈ 13.9 horas**.

**Lo que enseña:** el número anunciado es un **pico**. El 40 % es realista, porque el código espera datos, sincroniza y no usa todas las unidades todo el tiempo. Ojo también con la precisión: los 300 TFLOPS suelen estar medidos en una precisión baja, como BF16, y en FP32 serían bastante menos.
:::

::: problem {#xa-6 title="6 · El techo de la memoria"}
Un chip hace **2 TFLOPS** y su memoria entrega **100 GB/s**. Calculas `C[i] = A[i] + B[i]` con números FP32, de 4 bytes. Por cada suma lees A y B y escribes C.

a) ¿Cuántos FLOP haces por byte movido?

b) ¿Cuántos GFLOPS logras como máximo?

c) ¿Ayuda cambiar a un chip con el doble de FLOPS y la misma memoria?
:::

::: hint {of="xa-6"}
Una suma es 1 FLOP. ¿Cuántos bytes mueves por suma? Si cada byte permite tantos FLOP y llegan 100 GB por segundo, ¿cuántos FLOP por segundo alcanzas?
:::

::: answer {of="xa-6"}
- **a)** Mueves 4 + 4 + 4 = 12 bytes por 1 FLOP: **1/12 ≈ 0.083 FLOP/byte**. Es la **intensidad aritmética**.
- **b)** 100 GB/s × 0.083 FLOP/byte ≈ **8.3 GFLOPS**. Es menos del 0.5 % de los 2 TFLOPS: las unidades de cálculo pasan casi todo el tiempo esperando datos.
- **c)** **No.** El límite es la memoria, no el cálculo, y con el doble de FLOPS sigues en 8.3 GFLOPS. Lo que ayuda es más ancho de banda: con 200 GB/s llegas a 16.7.

**La regla:** el rendimiento es el **menor** de dos techos, el de cómputo y el ancho de banda × intensidad. Más FLOPS no ayudan si faltan datos.
:::

::: problem {#xa-7 title="7 · ¿Vale la pena la copia?"}
Tienes 1 GB de datos en RAM. La GPU los procesa en 5 ms, y la CPU en 200 ms. Copiar a la GPU viaja a unos 25 GB/s, y el resultado de vuelta es pequeño.

a) ¿Quién termina antes?

b) ¿Y si la CPU tardara 30 ms?
:::

::: hint {of="xa-7"}
El tiempo de la GPU no es sólo su cálculo: suma lo que tarda el viaje de los datos hasta ella.
:::

::: answer {of="xa-7"}
Copiar 1 GB a 25 GB/s tarda **40 ms**, así que la GPU tarda en total unos 40 + 5 = **45 ms**.

- **a)** **GPU**: 45 ms contra 200 ms.
- **b)** **CPU**: 30 ms contra 45 ms. La copia sola ya tarda más que todo el trabajo en CPU.

Por eso un trabajo corto rara vez conviene en la GPU, y por eso conviene dejar los datos en la GPU entre un paso y el siguiente, en vez de copiarlos ida y vuelta.
:::

::: problem {#xa-8 title="8 · GHz contra trabajo"}
El chip X corre a **5 GHz** y termina en promedio **2 instrucciones por ciclo**. El chip Y corre a **3.5 GHz** y termina **4 instrucciones por ciclo**. Para un programa de un solo hilo que no espera a la memoria, ¿cuál es más rápido?
:::

::: hint {of="xa-8"}
Instrucciones por segundo = ciclos por segundo × instrucciones por ciclo.
:::

::: answer {of="xa-8"}
- X: 5 × 10⁹ × 2 = **10 mil millones** de instrucciones por segundo.
- Y: 3.5 × 10⁹ × 4 = **14 mil millones**.

**Y es 40 % más rápido**, aunque tiene menos GHz. Los GHz miden el ritmo del reloj, no el trabajo que sale de cada tick; eso depende de la microarquitectura. Y esto vale sólo con la condición del enunciado: si el programa espera a la memoria, ninguno de los dos números manda.
:::

**Repasa:** [[paralelismo-performance-energia|Paralelismo, performance y energía]] y [[compute-instrucciones-cpu|Compute, instrucciones y CPU]].

## Parte 3 · ISA y sistema operativo

::: problem {#xa-9 title="9 · El binario que no corre"}
Compilas un programa en C en tu laptop x86-64 y copias el ejecutable a una Raspberry Pi, que es ARM. ¿Corre? ¿Y un script de Python copiado igual?
:::

::: hint {of="xa-9"}
¿En qué está escrito un ejecutable compilado? ¿Y quién lee un script de Python?
:::

::: answer {of="xa-9"}
- **El binario de C no corre.** Está escrito en instrucciones de la **ISA x86-64**, y la Pi entiende las de **ARM**: son contratos distintos. Hay que recompilarlo para ARM.
- **El script de Python sí corre**, si la Pi tiene Python instalado. El script no son instrucciones de máquina: lo lee el **intérprete**, y el intérprete de la Pi ya está compilado para ARM.

Matiz: si el script usa bibliotecas con partes compiladas, como numpy, esas partes deben existir en versión ARM. Por eso a veces `pip install` funciona en una máquina y en otra no.
:::

::: problem {#xa-10 title="10 · ¿Quién habla con el disco?"}
En Python escribes `open("datos/ventas.csv").read()`. ¿Tu programa le habla al disco directamente? Nombra dos cosas que hace el sistema operativo en ese momento.
:::

::: hint {of="xa-10"}
Recuerda la definición del curso: el sistema operativo es el intermediario. ¿Qué traduce, qué controla y qué reparte?
:::

::: answer {of="xa-10"}
**No.** Tu programa **le pide** al sistema operativo que lea el archivo. Mientras tanto, el sistema operativo, entre otras cosas:

- **traduce el nombre** `datos/ventas.csv` a los bloques del disco donde viven esos bytes: es el **sistema de archivos**;
- **revisa los permisos**: si tu usuario puede leer ese archivo;
- **controla el dispositivo** a través de su driver;
- **pone los bytes en la memoria** de tu programa;
- **reparte la CPU**: mientras el disco responde, deja correr a otros programas.

Con dos bien explicadas basta. Por esta mediación, la misma línea de Python puede comportarse distinto en Windows y en Linux: cambian las rutas, los permisos y el sistema de archivos.
:::

::: problem {#xa-11 title="11 · ¿Dónde está el cuello de botella?"}
Un ETL nocturno lee **2 TB** de CSV desde un SSD que entrega unos **2 GB/s**, filtra filas con una condición simple y escribe un resultado pequeño. Alguien propone comprar una GPU para acelerarlo. ¿Ayudaría?
:::

::: hint {of="xa-11"}
Calcula cuánto tarda sólo en **leer** los 2 TB. Luego pregúntate cuánto cálculo hay por cada byte leído.
:::

::: answer {of="xa-11"}
**Casi seguro que no.** Sólo leer 2 TB a 2 GB/s toma 1,000 s, unos 17 minutos, y filtrar con una condición simple es muy poco cálculo por byte. El trabajo está limitado por el **almacenamiento**, no por el cálculo, así que una GPU esperaría datos igual que la CPU, y además habría que copiárselos.

Lo que sí ayuda:

- un formato **columnar** como Parquet, para leer sólo las columnas necesarias;
- comprimir, para leer menos bytes;
- un almacenamiento más rápido;
- repartir la lectura entre varias máquinas.

Antes de comprar hardware, hay que preguntar qué recurso se agota primero: capacidad, latencia, ancho de banda o cálculo.
:::

**Repasa:** [[compute-instrucciones-cpu|Compute, instrucciones y CPU]], [[software-libre-y-sistemas-operativos|Software libre y sistemas operativos]] y [[ia-escala-decision|IA, escala y selección de hardware]].
