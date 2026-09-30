---
id: el-archivo-compartido
title: "El archivo compartido"
nav_title: "El archivo compartido"
summary: "El bind mount en las dos direcciones, y de quién queda el archivo que escribe el contenedor: cuatro plataformas y cuatro respuestas distintas."
status: ready
estimated_time: 15m
tags: [bind-mount, uid, permisos, rootless, keep-id, macos, wsl2, solo-lectura]
prerequisites: [rutas-en-docker]
---

# El archivo compartido

**Página 14 de 16 · sección 2 de 3**

Meta: ver el bind mount funcionando en las dos direcciones, y descubrir que la pregunta «¿de quién queda el archivo?» tiene **cuatro** respuestas, no una.

**Página de referencia.** La clase no la recorre: si ya la usaste, sirve para consultar.

::: figure {#cont-uid-plataformas title="El mismo bind mount y el mismo proceso, en cuatro plataformas: cuatro resultados"}
![Cuatro paneles, uno por plataforma, y en todos el mismo proceso de contenedor corriendo con uid 0, es decir root adentro. En el primero, Linux nativo con Docker, no hay user namespace porque Docker no lo activa por omisión, así que el uid 0 de adentro es el uid 0 de afuera, el mismo número sobre el mismo kernel y el mismo inodo: el archivo queda de root y no se borra sin sudo. En el segundo, Linux con Podman rootless, hay un user namespace con tu mapeo y el uid 0 de adentro se mapea a tu uid, y sólo ése, porque el 1000 de adentro cae en tu rango de subuid, que no es ningún usuario real: el archivo queda tuyo, sin sudo en ningún momento. En el tercero, WSL2 sobre una ruta ext4 de tu carpeta personal, es Linux de verdad, mismo kernel y mismo ext4, así que se comporta igual que el primero y el archivo queda de root. En el cuarto, macOS o Windows sobre una ruta del disco del sistema, el bind mount cruza a la máquina virtual por un puente que traduce la propiedad y te devuelve tu uid pase lo que pase adentro: el archivo queda tuyo, no porque esté bien sino porque nadie lo mide. Al pie, dos recuadros con las salidas: en Docker, la bandera user con tu uid y tu gid, con un asterisco que advierte que el proceso deja de ser root también adentro y que ese uid no existe en el archivo de usuarios de la imagen; y en Podman, userns igual a keep id, o el sufijo dos puntos U del volumen, que hace un chown recursivo del origen](../_assets/cont-uid-plataformas.svg)
:::

## En corto

- Un bind mount es **bidireccional**: lo que escribe el contenedor aparece en tu disco, y lo que editas en tu disco lo ve el contenedor **sin reconstruir nada**.
- De quién queda ese archivo **depende de tu plataforma**, y hay cuatro respuestas. No es una curiosidad: decide si puedes borrarlo sin `sudo`.
- En Docker Desktop el archivo queda de **tu** usuario, y no porque ahí haya más aislamiento: es que ahí el bind mount **no es tu disco, es un puente**.

## Las dos direcciones

**Haz:** primero sin volumen, para ver qué ve el contenedor por su cuenta.

```bash
cd ~/fdd/docker-lab
echo "print('version 1')" > app.py
docker run --rm ubuntu:24.04 ls /app
docker run --rm -v "$(pwd)":/app ubuntu:24.04 ls /app
```

**Deberías ver:** primero `ls: cannot access '/app': No such file or directory` —el contenedor no sabe nada de tu carpeta— y después `app.py`. El montaje es lo único que cambió.

**Haz:** ahora que escriba **él**, y busca el resultado en tu carpeta.

```bash
docker run --rm -v "$(pwd)":/app ubuntu:24.04 \
  bash -c 'echo "escrito desde adentro" > /app/salida.txt'
ls -l salida.txt
```

**Deberías ver:** `salida.txt` en **tu** carpeta, con su contenido, aunque el contenedor ya no existe. Mira con cuidado la columna del dueño: es la pregunta de la segunda mitad de esta página.

**Haz:** edita tú, sin reconstruir ni volver a copiar nada.

```bash
echo "print('version 2')" > app.py
docker run --rm -v "$(pwd)":/app ubuntu:24.04 cat /app/app.py
docker run --rm -v "$(pwd)":/app ubuntu:24.04 rm /app/salida.txt
ls salida.txt
```

**Deberías ver:** `version 2` —el contenedor lee lo que acabas de guardar, sin `build` de por medio— y después `No such file or directory` en tu propia terminal: **un `rm` desde adentro borró un archivo de tu disco.** Es el mismo directorio, no una copia.

**Haz:** y la defensa, que es una palabra.

```bash
docker run --rm -v "$(pwd)":/app:ro ubuntu:24.04 bash -c 'rm /app/app.py'
```

**Deberías ver:** `Read-only file system`. El sufijo `:ro` monta de sólo lectura; tu código entra, pero nada de adentro puede tocarlo.

## Y de quién queda el archivo

Aquí es donde un curso normal te promete un resultado y le falla a media clase. La promesa de siempre es «queda de `root`», y es cierta sólo en dos de los cuatro casos:

::: table {#cont-tabla-plataformas title="De quién queda el archivo que escribió el contenedor"}

| Plataforma | De quién queda | Por qué |
|---|---|---|
| Linux nativo, Docker | **`root`** | Docker no activa user namespaces: el uid 0 de adentro **es** el uid 0 de afuera |
| Linux, Podman rootless | **tu usuario** | el uid 0 se mapea al tuyo, y sólo ése |
| WSL2, ruta ext4 (`/home/...`) | **`root`** | es Linux de verdad: mismo kernel, mismo ext4, mismas reglas |
| macOS con Docker Desktop, o Windows con ruta `C:\...` | **tu usuario** | el filesystem compartido **inventa** la propiedad |

:::

La cuarta fila es la contraintuitiva, y conviene decir con todas sus letras por qué **no** es que ahí haya más aislamiento. En macOS y en Windows hay una máquina virtual y un sistema de archivos compartido de por medio, y ese sistema inventa la propiedad para que nada falle: te devuelve tu uid pase lo que pase adentro. **No es que ahí sí haya user namespaces — es que ahí el bind mount no es tu disco, es un puente.** Nadie está midiendo el uid real, así que no hay conflicto que resolver.

Lo que Podman hace en la segunda fila sí es una traducción de verdad, la que quedó explicada en [[docker-y-podman]]: rootless corre dentro de un user namespace donde el uid 0 de adentro es tu uid de afuera. El archivo queda tuyo porque **de verdad lo escribió tu uid**, no porque alguien lo haya adivinado. El precio son los uid altos del resto del rango, que reaparecen en [[named-volumes-y-postgres]].

## Las salidas, cuando el resultado no te sirve

En **Docker** se le dice al contenedor con qué uid correr:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$(pwd)":/app ubuntu:24.04 \
  bash -c 'touch /app/mio.txt'
```

Con su asterisco, porque no es gratis: el proceso **deja de ser `root` también adentro**, así que se rompe si la imagen esperaba escribir en una ruta suya o instalar algo al arrancar. Y ese uid no existe en el `/etc/passwd` de la imagen, así que algunas herramientas se quejan de que no hay usuario.

En **Podman** la primera respuesta para montar tu propio árbol es `--userns=keep-id`, que mapea tu uid al mismo número adentro y quita toda traducción sorpresiva. El sufijo `:U` del volumen —`-v ./app:/app:U`— es otra cosa: hace un `chown` **recursivo** del origen al uid mapeado, o sea le cambia el dueño a tu directorio de verdad. Mídelo antes de usarlo sobre algo que te importe.

Y una aclaración que ahorra una tarde: **`podman unshare` es la herramienta de diagnóstico, no la solución.** Sirve para entrar al namespace y ver los uid como los ve Podman; no arregla el montaje. Y **no existe en macOS**, donde el cliente `podman` es remoto y habla con la máquina virtual.

::: problem {#cont-s2p9-de-quien-queda title="Predice el dueño en TU plataforma, y después bórralo"}
**Antes de correr nada**, escribe en una línea de quién va a quedar el archivo en **tu** máquina, y por qué. Después corre:

```bash
cd ~/fdd/docker-lab
docker run --rm -v "$(pwd)":/app ubuntu:24.04 \
  bash -c 'echo prueba > /app/dueno.txt'
ls -l dueno.txt
```

1. ¿Acertaste? Si no, di cuál de las cuatro filas era la tuya.
2. **Si estás en Linux nativo o en WSL2 sobre ext4**, intenta ahora `echo otra cosa > dueno.txt` con tu usuario. Falla: explica por qué, con el `ls -l` en la mano.
3. Con el mismo archivo, corre `rm dueno.txt`. **Sí puedes.** Explica por qué, y por qué no es una contradicción con la 2.
4. Vuelve a crearlo con la salida que le toque a tu runtime —`--user` en Docker, `--userns=keep-id` en Podman— y comprueba con `ls -l` que ahora sí queda tuyo.
:::

::: hint {of="cont-s2p9-de-quien-queda"}
Para la 2 y la 3, el `ls -l` te está dando dos informaciones distintas: los permisos **del archivo** y, si corres `ls -ld .`, los permisos **del directorio que lo contiene**. Una de las dos operaciones toca el archivo y la otra no toca el archivo en absoluto.
:::

::: answer {of="cont-s2p9-de-quien-queda"}
**1. Las cuatro respuestas.** En **Linux nativo con Docker**, `root`, porque Docker no activa user namespaces y el uid 0 de adentro es el uid 0 de afuera. En **Linux con Podman rootless**, tu usuario, porque el uid 0 se mapea al tuyo. En **WSL2 sobre una ruta ext4**, `root`: es Linux de verdad y se comporta igual que el primer caso. En **macOS con Docker Desktop, o Windows sobre una ruta `C:\...`**, tu usuario, porque el filesystem compartido de la VM inventa la propiedad — no porque ahí haya más aislamiento.

**2. No puedes escribirlo porque no eres el dueño.** El `ls -l` dice `-rw-r--r-- 1 root root`: el permiso de escritura es del dueño, y el dueño es `root`. Tú caes en «otros», que sólo tiene lectura. Con `sudo` funcionaría, y eso mismo es la molestia: un archivo que escribió tu propio laboratorio y que necesitas privilegios para tocar.

**3. Sí puedes borrarlo, y no es contradicción: borrar no toca el archivo.** `rm` quita una entrada del **directorio**, y para eso hacen falta permisos de escritura y ejecución **sobre el directorio**, no sobre el archivo. `~/fdd/docker-lab` es tuyo, así que puedes sacar de ahí lo que sea, aunque sea de `root`. Modificar sí toca el contenido del archivo, y ahí mandan los permisos del archivo. Son dos preguntas distintas y el `ls -l` te da las dos: `ls -l dueno.txt` para la 2, `ls -ld .` para la 3.

**4.** Con `docker run --user "$(id -u):$(id -g)"` el `ls -l` ya muestra tu usuario y tu grupo, porque el proceso de adentro corrió con tu uid. Con `podman run --userns=keep-id` pasa lo mismo por otro camino: tu uid se mapea a sí mismo dentro del namespace. **Y en macOS o Windows no notas ninguna diferencia**, porque ahí el archivo ya era tuyo antes de que hicieras nada.
:::

Sigue con [[los-ocho-casos]], que cierra el modelo: ocho combinaciones de dónde vive el código y dónde lo editas, predichas **antes** de ejecutarlas.

> [!NOTE]
> **Si sólo recuerdas una cosa:** el bind mount va en las dos direcciones y no es una copia — y de quién queda el archivo depende de si hay un kernel compartido o un puente en medio.
