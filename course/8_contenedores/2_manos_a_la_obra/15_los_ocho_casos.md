---
id: los-ocho-casos
title: "Los ocho casos"
nav_title: "Los ocho casos"
summary: "Código en la imagen o por volumen, editado dentro o fuera, con o sin rebuild: predecir las ocho respuestas antes de ejecutar una."
status: ready
estimated_time: 15m
tags: [volumen, bind-mount, imagen, build, rebuild, capa-de-escritura]
prerequisites: [el-archivo-compartido]
---

# Los ocho casos

**Página 15 de 16 · sección 2 de 3**

Meta: cerrar el modelo con una predicción por caso, antes de tocar el teclado.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-matriz-volumen title="Los ocho casos, como tres decisiones"}
![Árbol de tres decisiones binarias con ocho hojas. La primera partición es dónde está el código: en la imagen, con un Dockerfile que hace COPY punto punto, o por volumen, con la bandera -v del directorio actual a /app. La segunda es dónde editas: en el host o dentro del contenedor. La tercera es si hay build de por medio o no. Cada hoja responde dos preguntas rotuladas arriba —si el cambio se ve al correr y si sobrevive a docker rm— y lleva una línea con la razón. Las cuatro hojas de la rama del volumen quedan agrupadas bajo la conclusión de que ahí editar fuera y ver dentro no necesita ningún rebuild, mientras que en la rama de la imagen la respuesta cambia en cada hoja](../_assets/cont-matriz-volumen.svg)
:::

## En corto

- Tres decisiones binarias —el código **en la imagen** o **por volumen**, editas **en el host** o **dentro**, **con** o **sin** rebuild— dan ocho casos, y cada uno tiene una sola respuesta.
- Se predicen **las ocho antes de ejecutar ninguna**, en `volumenes/predicciones.md`. Si aciertas las ocho, entendiste volúmenes.
- Con volumen las cuatro respuestas colapsan en una: se ve al instante y el rebuild sobra. Ésa es la razón de montar el código mientras desarrollas.

## Detente aquí

Abre tu copia de `volumenes/predicciones.md` y **llena la columna «Predicción» de los ocho renglones**. Cada celda contesta dos cosas: **¿se ve el cambio al correr?** y **¿sobrevive a un `docker rm`?**

El archivo no se entrega y no se califica. Su único valor es que lo llenes antes de leer el resto de la página, porque un modelo que sólo confirma lo que ya viste no es un modelo. Lo que sigue es la verificación.

## El montaje

**Haz:**

```bash
mkdir -p ~/fdd/docker-lab/ocho && cd ~/fdd/docker-lab/ocho
cp ~/fdd/fdd_o26/codigo/08_contenedores/volumenes/app.py .
printf '%s\n' 'FROM python:3.12-slim' 'WORKDIR /app' 'COPY . .' \
  'CMD ["python", "app.py"]' > Dockerfile
docker build -t ocho:1 .
docker run --rm ocho:1 | head -3
```

**Deberías ver:** la cabecera `Lab 1: Bind Mounts` entre dos filas de signos de igual. Ésa es la línea que vas a cambiar ocho veces; lo que cambia en cada caso es **dónde** la cambias y **qué** corres después.

## Casos 1 y 2: el código en la imagen, editas en el host

**Haz:** abre `app.py` en tu editor y cambia `Lab 1: Bind Mounts` por `Lab 1: HOST`. Guarda. Después:

```bash
docker run --rm ocho:1 | head -3                 # caso 1: sin rebuild
docker build -t ocho:1 . >/dev/null
docker run --rm ocho:1 | head -3                 # caso 2: con rebuild
```

**Deberías ver:** primero `Bind Mounts`, después `HOST`. El primero no es un error de guardado: la imagen que corriste se construyó **antes** de tu edición y sigue teniendo la copia vieja adentro.

## Casos 3 y 4: el código en la imagen, editas dentro

**Haz:**

```bash
docker run -d --name c3 ocho:1 sleep 300
docker exec c3 sed -i 's/HOST/DENTRO/' /app/app.py
docker exec c3 python /app/app.py | head -3      # caso 3
docker build -t ocho:1 . >/dev/null
docker run --rm ocho:1 | head -3                 # caso 4
docker rm -f c3
```

**Deberías ver:** `DENTRO` **sólo** en la salida del `exec`. El contenedor nuevo dice `HOST`, y después del `rm -f` no queda rastro de la edición en ninguna parte. Vivía en la capa de escritura de `c3` y se fue con él.

## Casos 5 a 8: el código por volumen

**Haz:** vuelve a tu editor, cambia `Lab 1: HOST` por `Lab 1: VOLUMEN` y guarda. Después:

```bash
docker run --rm -v "$(pwd)":/app ocho:1 | head -3                    # caso 5
docker build -t ocho:1 . >/dev/null
docker run --rm -v "$(pwd)":/app ocho:1 | head -3                    # caso 6
docker run --rm -v "$(pwd)":/app ocho:1 \
  sh -c 'sed -i s/VOLUMEN/ADENTRO/ /app/app.py; python /app/app.py' | head -3
grep -n 'Lab 1' app.py                                               # caso 7, visto desde tu disco
docker build -t ocho:1 . >/dev/null
docker run --rm -v "$(pwd)":/app ocho:1 | head -3                    # caso 8
```

**Deberías ver:** `VOLUMEN` en los casos 5 y 6, `ADENTRO` en el 7 — y el `grep` demuestra que **el archivo de tu carpeta también dice `ADENTRO`**. El caso 8 no aporta nada nuevo, y ése es justo el resultado: con volumen, el `build` dejó de decidir.

En Linux y en WSL2 el contenedor corrió como `root`, pero **tu `app.py` sigue siendo tuyo**: `sed -i` conserva el dueño del archivo que ya existía. Lo que sí queda de `root` es lo **nuevo**: el `output.txt` que escribe `app.py`, exactamente como en [[el-archivo-compartido]]. No hace falta `sudo`: `rm output.txt` funciona, porque el directorio es tuyo.

## El bucle de trabajo diario

Sin volumen, cada cambio cuesta tres pasos, y el de en medio crece con el proyecto:

```bash
vim app.py
docker build -t ocho:1 .
docker run --rm ocho:1
```

Con volumen cuesta dos, porque el paso de en medio desaparece:

```bash
vim app.py
docker run --rm -v "$(pwd)":/app ocho:1
```

Eso es todo lo que compra montar el código: **quitar el `build` del ciclo de edición**. No lo quita de tu vida — la imagen que publicas se sigue construyendo con el código adentro, y por qué tiene que ser así es el cierre de [[las-cuatro-trampas]].

::: problem {#cont-p10-matriz title="Las ocho, antes de correr ninguna"}
Ésta es la tabla de `predicciones.md`, en su orden. Para cada renglón contesta **¿se ve el cambio al correr?** y **¿sobrevive a `docker rm`?**

| # | El código está | Editas en | ¿Rebuild? |
|---|---|---|---|
| 1 | en la imagen | el host | no |
| 2 | en la imagen | el host | sí |
| 3 | en la imagen | el contenedor | no |
| 4 | en la imagen | el contenedor | sí |
| 5 | por volumen | el host | no |
| 6 | por volumen | el host | sí |
| 7 | por volumen | el contenedor | no |
| 8 | por volumen | el contenedor | sí |

Si acertaste las ocho, entendiste volúmenes.
:::

::: hint {of="cont-p10-matriz"}
Dos preguntas bastan para las ocho. **¿Qué archivo lee el proceso?** El de la imagen, el de tu disco, o uno de la capa de escritura. Y **¿de dónde lee el `build`?** Del contexto que le pasas —tu carpeta—, nunca de un contenedor vivo.
:::

::: answer {of="cont-p10-matriz"}

| # | ¿Se ve? | ¿Sobrevive al `rm`? | Por qué |
|---|---|---|---|
| 1 | **no** | sí | La imagen sigue siendo la de antes. Tu edición existe, pero sólo en tu disco |
| 2 | **sí** | sí | El rebuild mete tu cambio en una capa nueva. Son dos pasos: reconstruir **y** volver a correr |
| 3 | **sí** | **no** | Se ve ya, en ese contenedor. Vive en la capa de escritura, y `docker rm` se la lleva entera |
| 4 | **no** | sí | El `build` lee el contexto del host, no la capa de escritura: tu edición de adentro no entra nunca |
| 5 | **sí** | sí | La que usas todo el día: guardas el archivo y ya está. Ni rebuild, ni reinicio |
| 6 | **sí** | sí | Se ve al instante — y el build sobró: el volumen tapa lo que la imagen traiga en ese path |
| 7 | **sí** | sí | Escribir en `/app` es escribir en tu disco, con el dueño que diga tu plataforma |
| 8 | **sí** | sí | El build, otra vez, no cambió nada que se llegue a ver |

**Sólo el caso 3 muere con el contenedor.** La segunda columna no pregunta si el archivo existe: pregunta **dónde vive**. Un cambio en la capa de escritura se ve igual de bien que cualquier otro… hasta el `docker rm`.

Y las cuatro filas del volumen contestan lo mismo, con el `build` dando igual en las cuatro. Eso no es redundancia: es el resultado.
:::

Sigue con [[las-cuatro-trampas]], donde el montaje deja de portarse bien.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el `build` lee tu carpeta y el contenedor lee lo que le montaste; nada de lo que escribas dentro de un contenedor llega jamás a una imagen nueva.
