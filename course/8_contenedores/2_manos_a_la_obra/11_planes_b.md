---
id: planes-b-de-instalacion
title: "Planes B"
nav_title: "Planes B"
summary: "Las cinco trampas de instalación con su síntoma y su causa, la que no existe, y cómo hacer la tarea mientras resuelves la tuya."
status: ready
estimated_time: 12m
tags: [instalacion, wsl2, snap, virtualizacion, secure-boot, disco, diagnostico]
prerequisites: [instalar-docker-y-podman]
---

# Planes B

**Página 11 de 16 · sección 2 de 3**

Meta: que nadie se quede sin poder hacer la tarea mientras resuelve su instalación.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-planes-b title="Síntoma, causa y arreglo: las cinco trampas de instalación, y la que no existe"}
![Tabla de diagnóstico de tres columnas —síntoma, causa y arreglo— con las cinco trampas de instalación: los bind mounts que fallan fuera de tu carpeta personal por el paquete confinado de snap, el WSL1 en vez de WSL2, la integración por distro apagada en Docker Desktop, la virtualización desactivada en el firmware y el disco sin espacio que delata df -h en la raíz. Una sexta fila, tachada, dice que Secure Boot no tiene nada que ver con Docker. Al pie, la fecha de reporte anticipada: si el sábado 19 no te funciona, dilo el sábado 19](../_assets/cont-planes-b.svg)
:::

## En corto

- Entre el jueves y el martes hay **cinco días sin ningún contacto humano**: si algo se atora, esta página es la que tienes a mano.
- Casi todo lo que falla el día de la instalación son **cinco trampas conocidas**, y cada una tiene un síntoma que la delata.
- **Si el sábado 19 no te funciona, dilo el sábado 19.** No el lunes a medianoche.

## Primero: no te quedes sin poder trabajar

La instalación y la tarea son dos problemas distintos, y conviene no dejar que el primero se coma al segundo.

**Podman solo te alcanza para toda la unidad.** Los dos CLI son compatibles comando por comando: si Docker se te atoró y Podman corre, trabaja con Podman y sigue leyendo Docker en las páginas. Casi todo lo de este curso funciona con `alias docker=podman`, y las tres diferencias que sí importan están en [[docker-y-podman|la página 7 de la sección anterior]].

**Si no corre ninguno de los dos**, hay dos salidas que bastan para la entrega, porque lo que se entrega es una imagen publicada y una URL, no un archivo:

| Salida | Qué es | El pero |
|---|---|---|
| [Play with Docker](https://labs.play-with-docker.com/) | una terminal con Docker en el navegador, gratis con tu cuenta de Docker Hub | la sesión dura unas horas y **se borra entera**: el `docker push` va antes de cerrar |
| GitHub Codespaces | la máquina de la nube que ya usaste en el curso, con Docker adentro | consume tus horas gratuitas del mes |

Las dos son **un puente, no un destino**: el laboratorio de volúmenes de esta sección enseña cosas sobre *tu* disco y *tu* usuario que en una máquina prestada no se ven. Vuelve a tu instalación el fin de semana.

## Las cinco trampas

### 1. `snap install docker`, en Ubuntu

Es el primer resultado de la búsqueda y es el que más caro sale. El paquete de `snap` está **confinado**: sólo ve una parte de tu disco. Instala bien, arranca bien, y un `docker run hello-world` funciona perfecto — así que parece que terminaste.

El síntoma aparece después, en la página 6 de esta sección, cuando montes una carpeta: **los bind mounts fuera de tu carpeta personal fallan**, con un `no such file or directory` sobre una ruta que existe y que puedes ver con `ls`. Es media clase del martes, y perdida de una forma especialmente difícil de diagnosticar, porque el error miente.

**Haz:** averigua si lo tuyo es el paquete de `snap`.

```bash
snap list docker 2>/dev/null
type -a docker
```

**Deberías ver:** `error: no matching snaps installed`, y una ruta que **no** empieza con `/snap/`. Si sale lo contrario, el arreglo es `sudo snap remove docker` y volver a la página anterior, a instalar desde el repositorio oficial.

### 2. WSL1 en vez de WSL2

WSL1 no es una máquina virtual con kernel de Linux: es una capa de traducción de llamadas al sistema. Docker Desktop **necesita WSL2**, y una distribución creada hace años puede seguir en la versión 1 sin decírtelo.

**Haz:** en **PowerShell**, no dentro de la distribución.

```powershell
wsl -l -v
```

**Deberías ver:** una tabla con una columna `VERSION` y un `2` en tu distribución. Si dice `1`, el arreglo es `wsl --set-version Ubuntu 2` —tarda unos minutos y no borra nada— y después `wsl --set-default-version 2` para que la próxima nazca bien.

### 3. La integración por distro, apagada

Docker Desktop corriendo, el ícono en verde, y dentro de tu Ubuntu de WSL2 el comando `docker` no existe. No está roto: el interruptor de **Settings → Resources → WSL integration** para *esa* distribución viene apagado.

Enciéndelo, aplica, y abre una terminal nueva. Si tienes más de una distribución, el interruptor es **uno por distribución**.

### 4. La virtualización, desactivada en el firmware

Sin virtualización no hay WSL2 y no hay VM de Docker Desktop. El síntoma es un `wsl --install` que falla, o un Docker Desktop que arranca y se queda dando vueltas. Se activa en el firmware —la tecla para entrar depende del modelo— y la opción se llama distinto según el fabricante: **Intel VT-x**, **AMD-V** o **SVM Mode**.

Si no la encuentras, ésta es la pregunta que vale la pena hacerle a un modelo de lenguaje, con tu modelo exacto escrito:

> **Prompt:** «Tengo una `[modelo exacto]` con Windows `[10 u 11, versión]`. Quiero activar la virtualización para WSL2. ¿Con qué tecla entro al firmware en este modelo, cómo se llama ahí la opción de virtualización, y cómo verifico desde Windows que quedó activada?»

### 5. El disco lleno

Las imágenes de esta unidad pesan varios gigabytes, y quien instaló en dual boot pudo haberle dado a Linux una partición chica. Un disco lleno a media clase se ve como un `pull` que falla con `no space left on device`, lo cual es honesto, o como cosas raras que no lo parecen.

**Haz:** míralo antes, no durante.

```bash
df -h /
docker system df
```

**Deberías ver:** al menos **10 GB** libres en la columna `Avail`. El segundo comando te dice cuánto de lo ocupado es de Docker; qué se borra con cada `prune` es [[limpieza-de-docker|la página 8 de esta sección]].

## Y la trampa que no existe: Secure Boot

**Secure Boot no tiene nada que ver con Docker.** Ni con WSL2, ni con Docker Desktop, ni con Podman.

Vale la pena decirlo con todas sus letras porque [[planes-b|la unidad 4]] te enseñó a desactivarlo para instalar Linux, y es la primera palanca que uno recuerda cuando algo no arranca. Aquí no aplica: Docker no carga módulos de kernel sin firmar. Desactivarlo no va a arreglar nada, y si tienes arranque dual puede dejarte con el otro sistema sin arrancar. Si alguien en el chat del grupo lo sugiere, éste es el párrafo que le mandas.

El pariente cercano que **sí** existe es el número 4: la virtualización, que se activa en la misma pantalla del firmware. Son dos opciones distintas, en el mismo menú, y confundirlas cuesta la tarde.

## La fecha de reporte anticipada

Una instalación atorada que se reporta el **sábado 19** se arregla en veinte minutos. La misma atorada que aparece el lunes a medianoche te cuesta la clase del martes y las dos entregas que vencen esa mañana.

Así que la regla es de fecha, no de esfuerzo: **si el sábado 19 no te funciona, dilo el sábado 19.** Y dilo con las cuatro cosas que hacen que se pueda contestar en dos minutos: qué sistema operativo tienes, qué comando corriste, qué esperabas, y qué salió — pegado tal cual, no descrito.

::: problem {#cont-s2p2-tres-sintomas title="Tres síntomas, tres causas"}
Tres personas del grupo escriben esto el domingo. Para cada una: **qué trampa es, qué comando le pides para confirmarlo, y cuál es el arreglo.**

**Ana.** «Docker funciona perfecto, `hello-world` sale bien. Pero cuando monto mi carpeta de proyecto me dice `no such file or directory`, y la carpeta existe, la estoy viendo con `ls`. Estoy en Ubuntu.»

**Beto.** «Docker Desktop está corriendo, el ícono está en verde. Abro mi terminal de Ubuntu y me dice `docker: command not found`. Ya lo reinicié tres veces.»

**Caro.** «`wsl --install` me falla. Leí que es por Secure Boot y lo desactivé, pero sigue igual. ¿Lo vuelvo a activar?»
:::

::: hint {of="cont-s2p2-tres-sintomas"}
Las tres están en la figura de arriba — dos como fila normal y una como la fila tachada. Para cada una, la pregunta útil no es «¿qué le falta?» sino **«¿qué parte sí le funciona?»**: lo que ya funciona te dice dónde *no* está el problema, y eso descarta media tabla.

Y en la tercera, fíjate en cuál de los dos ajustes del firmware es el que sí importa.
:::

::: answer {of="cont-s2p2-tres-sintomas"}
**Ana — el paquete de `snap`.** El detalle que lo delata es que `hello-world` funcione: el runtime está bien, lo que falla es *ver el disco*. Eso es confinamiento, no permisos. **Comando:** `snap list docker` y `type -a docker`; si la ruta empieza con `/snap/`, ya está. **Arreglo:** `sudo snap remove docker` y reinstalar desde el repositorio oficial.

**Beto — la integración de WSL apagada.** El ícono verde sólo dice que Docker Desktop corre en Windows; no dice nada sobre si tu distribución lo ve. **Comando:** `wsl -l -v` en PowerShell, para saber qué distribución es y confirmar que está en versión 2, y `type -a docker` dentro de ella. **Arreglo:** encender el interruptor de esa distribución en Settings → Resources → WSL integration, y abrir una terminal nueva. Reiniciar Docker Desktop no podía arreglarlo: el interruptor no se toca solo.

**Caro — la trampa que no existe.** Secure Boot no tiene nada que ver, así que **vuelve a activarlo**, sobre todo si tiene arranque dual. Lo que probablemente falta es la **virtualización**, que se activa en la misma pantalla del firmware y se llama `Intel VT-x`, `AMD-V` o `SVM Mode`. **Comando:** en PowerShell, `systeminfo` y leer la línea de Hyper-V, o abrir el Administrador de tareas y mirar si dice «Virtualización: habilitada».

Lo que tienen en común las tres: **ninguna se diagnostica con la frase «no me funciona Docker»**. Se diagnostican con qué sí funciona y qué exactamente no.
:::

Sigue con [[a-docker-hub]], que es la primera cosa que vas a publicar.

> [!NOTE]
> **Si sólo recuerdas una cosa:** Secure Boot no tiene nada que ver con Docker, y una instalación atorada se reporta el sábado, no el lunes a medianoche.
