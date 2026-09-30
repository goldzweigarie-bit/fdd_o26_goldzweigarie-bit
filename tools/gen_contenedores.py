"""Genera las figuras conceptuales SVG de la unidad de Contenedores.

Mismo patron que gen_regex.py y gen_git.py: paleta importada de svg_base, una
funcion por figura que devuelve una cadena SVG completa, y un catalogo
DIAGRAMAS que el generador y su prueba comparten como unica fuente de "que
figuras existen".

El catalogo de este modulo FUSIONA las veintinueve figuras conceptuales con
las cinco graficas de benchmark de gen_contenedores_bench.py, que dibujan CSV
en vez de ideas. Quien importe DIAGRAMAS de aqui ve las treinta y cuatro
figuras de la unidad.

Solo biblioteca estandar, a proposito: la guarda de la unidad IMPORTA este
modulo y el runner de CI solo instala pytest, pillow y pyyaml.

La raiz <svg> sale siempre de svg_base.marco(): trae width y height numericos
sin unidades y un viewBox que empieza en "0 0", que es lo que exige
test_svg_tamano_intrinseco.py. Cada SVG hornea su fondo y usa `fill` explicito
en todo texto, para que se lea igual en tema claro y en tema oscuro.

Los ids llevan prefijo "cont-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/8_contenedores/_assets"

from svg_base import (  # noqa: F401  (se reexportan para las guardas)
    FONDO, PANEL, TEXTO, SUAVE, LINEA, ACENTO, TINTE, AMBAR, CIAN, VIOLETA,
    ROJO, FUENTE, MONO, COLORES_FLECHA, arco, bucle, caja, celda, chip,
    cierre, cima_arco, curva, estado, flecha, marco, teclado, texto, _marca,
)

from gen_contenedores_bench import DIAGRAMAS as DIAGRAMAS_BENCH


# --------------------------------------------------------------------------
# Primitivas locales
#
# svg_base.py no se toca: modificarla regenera y revalida los 32 SVG de las
# unidades 6 y 7. Lo que falta aqui —trazos punteados, circulos, elipses— se
# construye sobre su paleta y sobre sus markers de punta de flecha.
# --------------------------------------------------------------------------


def linea(x1, y1, x2, y2, color=LINEA, grosor=2, guion=None):
    trazo = f' stroke-dasharray="{guion}"' if guion else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{grosor}"{trazo}/>'
    )


def flecha_punteada(x1, y1, x2, y2, color=SUAVE, grosor=2, guion="6 6"):
    """flecha() de svg_base, pero con el trazo cortado."""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{grosor}" stroke-dasharray="{guion}" '
        f'marker-end="url(#{_marca(color)})"/>'
    )


def caja_punteada(x, y, w, h, borde=SUAVE, radio=10, grosor=1.5, guion="7 7"):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radio}" '
        f'fill="none" stroke="{borde}" stroke-width="{grosor}" '
        f'stroke-dasharray="{guion}"/>'
    )


def relleno(x, y, w, h, color, radio=3):
    """Rectangulo macizo sin borde: barras, medidores, iconos."""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" '
        f'height="{max(h, 0):.1f}" rx="{radio}" fill="{color}"/>'
    )


def circulo(cx, cy, r, color, borde="none", grosor=2):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" '
        f'stroke="{borde}" stroke-width="{grosor}"/>'
    )


def elipse(cx, cy, rx, ry, color, borde=LINEA, grosor=2):
    return (
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" '
        f'stroke="{borde}" stroke-width="{grosor}"/>'
    )


def tachado(x1, y, x2, color=ROJO, grosor=2):
    """Raya encima de algo: lo que se escribe para decir que NO va."""
    return linea(x1, y, x2, y, color, grosor)


def cruz(cx, cy, r=9, color=ROJO, grosor=2.5):
    """Marca de no: dos trazos cruzados, sin texto que traducir."""
    return (linea(cx - r, cy - r, cx + r, cy + r, color, grosor)
            + linea(cx - r, cy + r, cx + r, cy - r, color, grosor))


def palomita(cx, cy, r=8, color=ACENTO, grosor=2.5):
    """Marca de si, del mismo tamano que cruz()."""
    return (linea(cx - r, cy, cx - r * 0.25, cy + r * 0.7, color, grosor)
            + linea(cx - r * 0.25, cy + r * 0.7, cx + r, cy - r * 0.8, color,
                    grosor))


def pastilla(x, y, w, h, etiqueta, color, encendida=True, tam=12.5):
    """Casilla chica que se prende o se apaga: alcance, cobertura, estado."""
    relleno_caja = TINTE if encendida else FONDO
    borde = color if encendida else LINEA
    return (caja(x, y, w, h, relleno_caja, borde, radio=7,
                 grosor=2 if encendida else 1.2)
            + teclado(x + w / 2, y + h / 2 + 4.5, etiqueta,
                      color if encendida else SUAVE, tam,
                      peso="600" if encendida else "normal"))


def parrafo(x, y, renglones, color=SUAVE, tam=12.5, paso=18,
            anclaje="start", peso="normal"):
    """Varias lineas de texto con el mismo tabulado."""
    return "".join(texto(x, y + i * paso, r, color, tam, anclaje, peso)
                   for i, r in enumerate(renglones))


def bloque(x, y, w, h, titulo, glosa, color, relleno_caja=PANEL,
           tam_titulo=15, mono=True, grosor=2):
    """Caja de cadena: un nombre arriba y su papel en una linea chica."""
    p = [caja(x, y, w, h, relleno_caja, color, radio=10, grosor=grosor)]
    escribir_titulo = teclado if mono else texto
    p.append(escribir_titulo(x + w / 2, y + h / 2 - 4, titulo, color,
                             tam_titulo))
    if glosa:
        p.append(texto(x + w / 2, y + h / 2 + 20, glosa, SUAVE, 11.5))
    return "".join(p)


def cadena(x0, y, alto_caja, piezas, sep=60, color_flecha=SUAVE):
    """Fila de cajas unidas por flechas. piezas = [(ancho, nombre, papel, color)]."""
    p = []
    x = x0
    centros = []
    for i, (ancho, nombre, papel, color) in enumerate(piezas):
        if i:
            p.append(flecha(x - sep + 4, y + alto_caja / 2, x - 6,
                            y + alto_caja / 2, color_flecha))
        p.append(bloque(x, y, ancho, alto_caja, nombre, papel, color))
        centros.append((x + ancho / 2, x, x + ancho))
        x += ancho + sep
    return "".join(p), centros


# --------------------------------------------------------------------------
# 1/1 · En mi maquina si funciona: el contenedor intermodal
# --------------------------------------------------------------------------

def _bultos(cx, cy):
    """Carga suelta: un barril, un saco y una caja, de tres tamanos."""
    return "".join((
        relleno(cx - 40, cy - 14, 20, 28, AMBAR, radio=6),
        relleno(cx - 13, cy - 9, 22, 22, VIOLETA, radio=10),
        relleno(cx + 15, cy - 16, 26, 32, ROJO, radio=3),
    ))


def _contenedor_icono(cx, cy):
    """El bulto sellado: una caja con corrugado y su precinto."""
    p = [caja(cx - 42, cy - 17, 84, 34, TINTE, ACENTO, radio=4, grosor=2.5)]
    for i in range(1, 4):
        p.append(linea(cx - 42 + i * 21, cy - 15, cx - 42 + i * 21, cy + 15,
                       ACENTO, 1.2))
    p.append(circulo(cx + 42, cy, 5, FONDO, ACENTO, 2))
    return "".join(p)


def cont_intermodal():
    """El mismo recorrido, con la carga suelta y con la caja sellada."""
    ancho, alto = 1240, 560
    aria = (
        "Dos recorridos paralelos del mismo muelle a la misma bodega pasando "
        "por camion, barco y tren. Arriba, la carga suelta de antes de 1956 se "
        "descarga y se vuelve a cargar en cada trasbordo, con su costo "
        "marcado; abajo, el contenedor sellado pasa de vehiculo en vehiculo "
        "sin abrirse. A la derecha, las equivalencias con el software: la "
        "carga es tu programa con sus dependencias, el contenedor es la "
        "imagen y los tres vehiculos son tu laptop, la maquina del companero "
        "y el servidor"
    )
    nodos = ("muelle", "camión", "barco", "tren", "bodega")
    w, sep, x0 = 108, 63, 40
    centros = [x0 + i * (w + sep) + w / 2 for i in range(5)]
    huecos = [x0 + i * (w + sep) + w + sep / 2 for i in range(4)]

    p = [marco(ancho, alto, aria)]
    p.append(texto(620, 42, "Del muelle a la bodega, dos maneras", TEXTO, 21, peso="600"))
    p.append(texto(620, 68, "el contenedor intermodal de McLean, 1956 — y el mismo truco en software", SUAVE, 14))

    # Recorrido de arriba: carga suelta.
    p.append(texto(x0, 104, "antes de 1956 · carga suelta", ROJO, 15, anclaje="start", peso="600"))
    for i, nombre in enumerate(nodos):
        x = x0 + i * (w + sep)
        p.append(caja(x, 118, w, 88, PANEL, ROJO))
        p.append(texto(x + w / 2, 140, nombre, TEXTO, 13.5))
        p.append(_bultos(x + w / 2, 176))
        if i:
            p.append(flecha(x - sep + 4, 162, x - 6, 162, ROJO))
    for hx in huecos:
        p.append(texto(hx, 228, "descargar y recargar", ROJO, 12))
        p.append(texto(hx, 246, "+ tiempo + costo", AMBAR, 12, peso="600"))

    # Recorrido de abajo: el bulto sellado.
    p.append(texto(x0, 284, "desde 1956 · el contenedor intermodal", ACENTO, 15, anclaje="start", peso="600"))
    for i, nombre in enumerate(nodos):
        x = x0 + i * (w + sep)
        p.append(caja(x, 298, w, 88, PANEL, ACENTO))
        p.append(texto(x + w / 2, 320, nombre, TEXTO, 13.5))
        p.append(_contenedor_icono(x + w / 2, 356))
        if i:
            p.append(flecha(x - sep + 4, 342, x - 6, 342, ACENTO))
    p.append(texto(436, 412, "en ningún trasbordo se abre la caja: se mueve entera, sellada", ACENTO, 13))
    for i, maquina in enumerate(("tu laptop", "la máquina del compañero", "el servidor")):
        p.append(texto(centros[i + 1], 442, maquina, CIAN, 12.5))

    # La columna de equivalencias.
    p.append(caja(880, 100, 320, 348, PANEL, CIAN))
    p.append(texto(1040, 130, "lo mismo, en software", CIAN, 16, peso="600"))
    p.append(linea(900, 252, 1180, 252, LINEA, 1))
    p.append(linea(900, 340, 1180, 340, LINEA, 1))
    p.append(texto(1040, 168, "la carga suelta", SUAVE, 13))
    p.append(texto(1040, 190, "≡", SUAVE, 15))
    p.append(texto(1040, 214, "tu programa, con todas", TEXTO, 14, peso="600"))
    p.append(texto(1040, 234, "sus dependencias", TEXTO, 14, peso="600"))
    p.append(texto(1040, 274, "el contenedor sellado", SUAVE, 13))
    p.append(texto(1040, 296, "≡", SUAVE, 15))
    p.append(teclado(1040, 322, "la imagen", ACENTO, 18))
    p.append(texto(1040, 362, "los tres vehículos", SUAVE, 13))
    p.append(texto(1040, 384, "≡", SUAVE, 15))
    p.append(texto(1040, 408, "tu laptop, la máquina del", CIAN, 13.5, peso="600"))
    p.append(texto(1040, 428, "compañero y el servidor", CIAN, 13.5, peso="600"))

    p.append(texto(620, 500, "McLean no inventó la caja: inventó que nadie tuviera que abrirla. En cada trasbordo se mueve el bulto entero, sellado.", SUAVE, 14))
    p.append(texto(620, 526, "Una imagen es eso. La máquina que la recibe no la abre para acomodar lo de adentro: la corre tal cual llegó.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/2 · Namespaces y cgroups: dos preguntas distintas
# --------------------------------------------------------------------------

def _medidor(x, y, w, etiqueta, limite, fraccion, color, glosa):
    """Un cgroup: cuanto de un recurso puede usar el proceso."""
    return "".join((
        texto(x, y - 10, etiqueta, TEXTO, 14, anclaje="start", peso="600"),
        texto(x + w, y - 10, limite, color, 13, anclaje="end"),
        caja(x, y, w, 24, PANEL, LINEA, radio=6, grosor=1.5),
        relleno(x + 2, y + 2, (w - 4) * fraccion, 20, color, radio=5),
        texto(x, y + 44, glosa, SUAVE, 11.5, anclaje="start"),
    ))


def cont_ns_cgroups():
    """Namespaces = que puede ver. cgroups = cuanto puede usar."""
    ancho, alto = 1180, 700
    aria = (
        "Un proceso partido en dos mitades. A la izquierda, bajo el rotulo que "
        "puede ver, seis cajas de namespace etiquetadas pid, net, mnt, user, "
        "uts e ipc, con cgroup y time al pie como los dos tipos que faltan "
        "para llegar a ocho. A la derecha, bajo cuanto puede usar, tres "
        "medidores de cgroup para CPU, memoria y numero de procesos. La caja "
        "user va resaltada y unida por una linea continua al kernel del host, "
        "porque es el unico de los diez enlaces que no difiere del host"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(590, 42, "Namespaces y cgroups: dos preguntas distintas", TEXTO, 21, peso="600"))
    p.append(texto(590, 68, "no son dos mitades de lo mismo", SUAVE, 14))

    p.append(caja(40, 92, 1100, 356, "none", LINEA))
    p.append(texto(60, 116, "el proceso del contenedor", SUAVE, 13.5, anclaje="start"))
    p.append(linea(600, 100, 600, 440, LINEA, 1.5, "6 6"))

    p.append(texto(320, 152, "qué puede VER", CIAN, 18, peso="600"))
    p.append(texto(320, 174, "namespaces", SUAVE, 13))
    p.append(texto(870, 152, "cuánto puede USAR", AMBAR, 18, peso="600"))
    p.append(texto(870, 174, "cgroups", SUAVE, 13))

    ns = (
        ("pid", "qué procesos ve", CIAN, False),
        ("net", "su propia red", CIAN, False),
        ("mnt", "qué archivos ve", CIAN, False),
        ("user", "qué UID es adentro", AMBAR, True),
        ("uts", "su propio hostname", CIAN, False),
        ("ipc", "memoria compartida", CIAN, False),
    )
    for i, (nombre, glosa, color, resaltado) in enumerate(ns):
        x = 60 + (i % 3) * 180
        y = 196 + (i // 3) * 82
        p.append(caja(x, y, 160, 66, PANEL, color, grosor=3 if resaltado else 2))
        p.append(teclado(x + 80, y + 28, nombre, color, 17))
        p.append(texto(x + 80, y + 50, glosa, SUAVE, 11.5))

    p.append(caja_punteada(200, 360, 380, 56, SUAVE))
    p.append(texto(212, 392, "y dos tipos más, para ocho:", SUAVE, 12.5, anclaje="start"))
    p.append(chip(462, 388, "cgroup", SUAVE, tam=13))
    p.append(chip(548, 388, "time", SUAVE, tam=13))

    p.append(_medidor(660, 220, 440, "CPU", "--cpus=0.5", 0.5, AMBAR,
                      "ve todos los núcleos; sólo no puede usarlos todos"))
    p.append(_medidor(660, 300, 440, "memoria", "--memory=512m", 0.35, VIOLETA,
                      "pasarse no da un error: da un OOM kill"))
    p.append(_medidor(660, 380, 440, "procesos", "--pids-limit=100", 0.2, CIAN,
                      "el tope de PIDs: lo que frena una bomba de forks"))

    # El unico enlace que no difiere del host baja hasta el kernel compartido.
    p.append(flecha(140, 344, 140, 562, AMBAR, 2.5))

    p.append(caja(40, 496, 1100, 56, TINTE, ACENTO, grosor=2.5))
    p.append(texto(590, 530, "kernel del host — uno solo, compartido", TEXTO, 16, peso="600"))

    p.append(caja(40, 566, 520, 60, PANEL, AMBAR))
    p.append(texto(300, 590, "user es el único de los diez enlaces que NO difiere del host", AMBAR, 13, peso="600"))
    p.append(texto(300, 610, "Docker no activa user namespaces por omisión: root adentro es root afuera", SUAVE, 12))

    p.append(texto(590, 656, "ls /proc/1/ns/ imprime DIEZ enlaces y aquí hay OCHO tipos: pid y time salen además en su variante _for_children,", SUAVE, 13.5))
    p.append(texto(590, 678, "el namespace que heredarán los hijos. De esos diez, nueve difieren del host.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/3 · Receta, congelado, servido
# --------------------------------------------------------------------------

def cont_tres_abstracciones():
    """Dockerfile, imagen y contenedor como receta, congelado y servido."""
    ancho, alto = 1160, 520
    aria = (
        "Tres paneles en fila con su analogia arriba y su termino abajo: la "
        "receta escrita es el Dockerfile, el platillo congelado es la imagen y "
        "el platillo servido es el contenedor, unidos por las flechas docker "
        "build y docker run. Del platillo congelado salen tres platos servidos "
        "identicos; bajo la imagen dice inmutable y bajo los contenedores dice "
        "efimeros"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(580, 42, "Receta, congelado, servido", TEXTO, 21, peso="600"))
    p.append(texto(580, 68, "las tres cosas que todo el mundo confunde", SUAVE, 14))

    p.append(caja(40, 96, 280, 330, PANEL, CIAN))
    p.append(texto(180, 128, "la receta escrita", SUAVE, 14))
    p.append(caja(100, 150, 160, 170, FONDO, CIAN, radio=8, grosor=1.5))
    for i, linea_df in enumerate(("FROM python:3.12", "WORKDIR /app", "COPY . .",
                                  "RUN pip install", "CMD [\"python\"]")):
        p.append(teclado(112, 178 + i * 24, linea_df, SUAVE, 11.5,
                         anclaje="start", peso="normal"))
    p.append(teclado(180, 368, "Dockerfile", CIAN, 20))
    p.append(texto(180, 396, "texto, y va en git", SUAVE, 12.5))

    p.append(caja(440, 96, 280, 330, PANEL, VIOLETA))
    p.append(texto(580, 128, "el platillo congelado", SUAVE, 14))
    for dx, dy in ((-40, 202), (0, 190), (40, 202)):
        p.append(teclado(580 + dx, dy, "❄", CIAN, 17))
    p.append(elipse(580, 248, 88, 30, PANEL, VIOLETA, 2.5))
    p.append(elipse(580, 242, 54, 18, FONDO, VIOLETA, 1.5))
    p.append(teclado(580, 300, "sha256:6a2f…", SUAVE, 12.5, peso="normal"))
    p.append(teclado(580, 368, "imagen", VIOLETA, 20))
    p.append(texto(580, 396, "inmutable", VIOLETA, 13, peso="600"))

    p.append(caja(840, 96, 280, 330, PANEL, ACENTO))
    p.append(texto(980, 128, "el platillo servido", SUAVE, 14))
    for cy in (180, 236, 292):
        p.append(elipse(980, cy, 70, 22, PANEL, ACENTO, 2))
        p.append(elipse(980, cy - 4, 42, 13, FONDO, ACENTO, 1.5))
    p.append(texto(980, 332, "tres, de la misma imagen", SUAVE, 12))
    p.append(teclado(980, 368, "contenedor", ACENTO, 20))
    p.append(texto(980, 396, "efímeros", ACENTO, 13, peso="600"))

    p.append(teclado(380, 150, "docker build", ACENTO, 15))
    p.append(flecha(326, 246, 434, 246, ACENTO))
    p.append(teclado(780, 150, "docker run", ACENTO, 15))
    for cy in (186, 240, 292):
        p.append(flecha(726, 246, 834, cy, ACENTO))

    p.append(texto(580, 468, "De una receta salen muchos congelados idénticos; de un congelado, muchos platos servidos.", SUAVE, 14))
    p.append(texto(580, 492, "Borrar el plato no toca el congelado. Cambiar la receta tampoco: para eso hay que volver a construir.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/4 · Que pasa cuando escribes `docker run`
# --------------------------------------------------------------------------

def cont_anatomia_run():
    """La cadena real, con quien sostiene al proceso y quien ya se fue."""
    ancho, alto = 1280, 730
    aria = (
        "Cadena de cinco cajas: docker CLI, dockerd, containerd, "
        "containerd-shim-runc-v2 y runc, con el socket rotulado sobre la "
        "primera flecha. El proceso del contenedor cuelga del shim y no del "
        "daemon, y una flecha punteada sube del shim a PID 1 porque se "
        "desacopla con un doble fork. runc va en gris con marca de salida: "
        "corre en create y en start y sale las dos veces. Dos llamadas "
        "corrigen que el rootfs lo monta dockerd con overlay2 y que el cgroup "
        "lo crea systemd por D-Bus. Al pie, el orden real: proceso, cgroup, "
        "namespaces"
    )
    piezas = (
        (150, "docker", "lo que tecleas", CIAN),
        (150, "dockerd", "el daemon (root)", ROJO),
        (170, "containerd", "imágenes y tareas", VIOLETA),
        (236, "containerd-shim-runc-v2", "el supervisor del contenedor", ACENTO),
        (130, "runc", "crea y se va", SUAVE),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(640, 42, "Qué pasa cuando escribes docker run", TEXTO, 21, peso="600"))
    p.append(texto(640, 68, "la cadena real, y qué queda de ella cuando el contenedor ya corre", SUAVE, 14))

    p.append(caja(770, 110, 200, 46, PANEL, SUAVE, radio=10, grosor=1.5))
    p.append(texto(870, 139, "PID 1 — systemd", TEXTO, 15, peso="600"))
    p.append(flecha_punteada(870, 196, 870, 162, SUAVE))
    p.append(texto(986, 130, "doble fork: el shim se desacopla", SUAVE, 12.5, anclaje="start"))
    p.append(texto(986, 148, "y queda reparentado a systemd", SUAVE, 12.5, anclaje="start"))

    x = 102
    bordes = []
    for i, (w, nombre, papel, color) in enumerate(piezas):
        if i:
            p.append(flecha(x - 56, 243, x - 6, 243, SUAVE))
        p.append(caja(x, 200, w, 86, PANEL, color))
        p.append(teclado(x + w / 2, 234, nombre, color, 14))
        p.append(texto(x + w / 2, 258, papel, SUAVE, 11.5))
        bordes.append((x, x + w, x + w / 2))
        x += w + 60
    p.append(teclado(282, 182, "/var/run/docker.sock", CIAN, 12.5, peso="normal"))

    # El proceso cuelga del shim, no del daemon.
    p.append(flecha(870, 290, 870, 348, ACENTO, 2.5))
    p.append(texto(744, 322, "cuelga del shim,", ACENTO, 12.5, anclaje="end", peso="600"))
    p.append(texto(744, 340, "no del daemon", ACENTO, 12.5, anclaje="end", peso="600"))
    p.append(caja(752, 352, 236, 92, TINTE, ACENTO))
    p.append(texto(870, 378, "el proceso del contenedor", TEXTO, 14, peso="600"))
    p.append(teclado(870, 404, "sleep 300", ACENTO, 15))
    p.append(texto(870, 426, "PID 1 dentro del contenedor", SUAVE, 11.5))

    # runc ya salio.
    p.append(chip(1113, 312, "sale ✗", SUAVE, tam=13))
    p.append(texto(1113, 346, "corre dos veces:", SUAVE, 11.5))
    p.append(texto(1113, 362, "create y start", SUAVE, 11.5))
    p.append(texto(1113, 378, "y sale las dos", SUAVE, 11.5))

    p.append(caja(50, 470, 596, 130, PANEL, AMBAR))
    p.append(texto(66, 498, "Dos cosas que se enseñan mal — y que runc NO hace", AMBAR, 14.5, anclaje="start", peso="600"))
    p.append(texto(66, 526, "· el rootfs ya está en disco desde el pull; lo monta dockerd con el", SUAVE, 12.5, anclaje="start"))
    p.append(texto(80, 544, "graphdriver overlay2 (o el shim, con el image store de containerd)", SUAVE, 12.5, anclaje="start"))
    p.append(texto(66, 570, "· el cgroup lo crea systemd: runc le pide una unidad scope por D-Bus", SUAVE, 12.5, anclaje="start"))
    p.append(texto(80, 588, "y sólo escribe los knobs que systemd no expone", SUAVE, 12.5, anclaje="start"))

    p.append(caja(680, 470, 550, 130, PANEL, ACENTO))
    p.append(texto(696, 498, "El árbol de procesos, con el contenedor ya corriendo", ACENTO, 14.5, anclaje="start", peso="600"))
    p.append(teclado(696, 524, "systemd", TEXTO, 13, anclaje="start", peso="normal"))
    p.append(teclado(712, 544, "└─ containerd-shim-runc-v2", TEXTO, 13, anclaje="start", peso="normal"))
    p.append(teclado(744, 564, "└─ sleep 300", ACENTO, 13, anclaje="start", peso="normal"))
    p.append(texto(696, 588, "ni dockerd ni containerd aparecen — y runc tampoco: ya salió", SUAVE, 12, anclaje="start"))

    p.append(texto(50, 646, "el orden real, dentro de runc:", SUAVE, 13, anclaje="start"))
    for cx, etiqueta in ((336, "1 · el proceso"), (556, "2 · el cgroup"),
                         (800, "3 · los namespaces")):
        p.append(chip(cx, 640, etiqueta, ACENTO, tam=13.5))
    p.append(flecha(426, 640, 471, 640, SUAVE))
    p.append(flecha(640, 640, 688, 640, SUAVE))
    p.append(texto(925, 636, "primero el PID, después el cgroup —", SUAVE, 12, anclaje="start"))
    p.append(texto(925, 654, "para que ningún hijo escape— y al final los namespaces", SUAVE, 12, anclaje="start"))

    p.append(texto(640, 706, "El camino de ejecución ya no pasa por Docker: cada syscall va directo al kernel. Lo que queda es un supervisor sosteniendo la salida y el código de salida.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/5 · De uno a mil: escalamiento y orquestacion
# --------------------------------------------------------------------------

def cont_escalamiento():
    """Una copia funciona; cinco replicas con el estado adentro, no."""
    ancho, alto = 1220, 870
    aria = (
        "Dos escenarios. A la izquierda, una sola copia del servicio con su "
        "archivo de sesiones guardado adentro y funcionando. A la derecha, "
        "cinco replicas identicas de la misma imagen detras de un repartidor "
        "de carga, cada una con su propio archivo de sesiones marcado en rojo, "
        "y tres peticiones del mismo usuario que caen en replicas distintas y "
        "encuentran archivos distintos. Abajo, el mismo dibujo corregido: el "
        "estado sacado a una caja compartida fuera de los contenedores y el "
        "orquestador, que decide cuantas replicas hay y repone la que muere"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(610, 42, "De uno a mil: qué se rompe al escalar", TEXTO, 21, peso="600"))
    p.append(texto(610, 68, "el mismo servicio, una copia y cinco réplicas", SUAVE, 14))

    # Una copia.
    p.append(texto(60, 108, "una copia", ACENTO, 16, anclaje="start", peso="600"))
    p.append(caja(60, 150, 110, 60, PANEL, CIAN))
    p.append(texto(115, 176, "usuario", CIAN, 13))
    p.append(texto(115, 194, "una sesión", SUAVE, 11))
    p.append(flecha(176, 180, 246, 180, CIAN))
    p.append(caja(252, 130, 280, 150, PANEL, ACENTO))
    p.append(texto(392, 158, "el servicio", TEXTO, 14, peso="600"))
    p.append(texto(392, 178, "una sola copia", SUAVE, 11.5))
    p.append(caja(282, 196, 220, 60, TINTE, ACENTO, radio=8))
    p.append(teclado(392, 222, "sesiones.db", ACENTO, 14))
    p.append(texto(392, 244, "adentro del contenedor", SUAVE, 11))
    p.append(texto(296, 318, "Funciona. El usuario siempre vuelve", SUAVE, 13))
    p.append(texto(296, 338, "al mismo proceso y al mismo archivo.", SUAVE, 13))

    p.append(linea(570, 130, 570, 460, LINEA, 1.5, "6 6"))

    # Cinco replicas.
    p.append(texto(600, 108, "cinco réplicas de la misma imagen", ROJO, 16, anclaje="start", peso="600"))
    p.append(caja(600, 240, 100, 60, PANEL, CIAN))
    p.append(texto(650, 266, "el mismo", CIAN, 12.5))
    p.append(texto(650, 284, "usuario", CIAN, 12.5))
    p.append(flecha(706, 270, 724, 270, CIAN))
    p.append(caja(730, 140, 90, 310, PANEL, VIOLETA))
    p.append(texto(775, 286, "repartidor", VIOLETA, 12.5))
    p.append(texto(775, 304, "de carga", VIOLETA, 12.5))
    for i in range(5):
        y = 140 + i * 64
        golpeada = i in (0, 2, 4)
        color = ROJO if golpeada else LINEA
        p.append(caja(870, y, 310, 52, PANEL, color))
        p.append(texto(884, y + 22, f"réplica {i + 1}", TEXTO, 13, anclaje="start"))
        p.append(teclado(1166, y + 22, "sesiones.db", ROJO, 12, anclaje="end", peso="normal"))
        nota = "no te conoce: su archivo está vacío" if golpeada else "su propio archivo, con otra cosa adentro"
        p.append(texto(884, y + 40, nota, SUAVE, 10.5, anclaje="start"))
    for k, i in enumerate((0, 2, 4)):
        y = 140 + i * 64 + 26
        p.append(flecha(824, y, 864, y, CIAN))
        p.append(texto(844, y - 12, f"{k + 1}ª", CIAN, 11))
    p.append(texto(890, 494, "Cada petición cae en una réplica distinta y encuentra otro archivo.", SUAVE, 13))
    p.append(texto(890, 514, "La sesión se pierde: el estado adentro rompe el escalamiento.", ROJO, 13))

    p.append(linea(40, 548, 1180, 548, LINEA, 1.5, "6 6"))

    # El mismo dibujo, corregido.
    p.append(texto(610, 584, "lo mismo, corregido", ACENTO, 17, peso="600"))
    p.append(caja(40, 616, 230, 96, PANEL, VIOLETA))
    p.append(texto(155, 644, "el orquestador", VIOLETA, 14, peso="600"))
    p.append(texto(155, 666, "decide cuántas réplicas hay", SUAVE, 11.5))
    p.append(texto(155, 684, "y repone la que muere", SUAVE, 11.5))
    p.append(flecha_punteada(274, 656, 294, 656, VIOLETA))
    for i in range(5):
        x = 300 + i * 182
        p.append(caja(x, 616, 152, 80, PANEL, ACENTO))
        p.append(texto(x + 76, 644, "réplica", TEXTO, 13))
        p.append(texto(x + 76, 666, "sin estado", ACENTO, 12, peso="600"))
        p.append(texto(x + 76, 686, "desechable", SUAVE, 10.5))
        p.append(flecha(x + 76, 700, 505 + i * 88, 720, CIAN, 1.4))
    p.append(caja(470, 724, 420, 66, PANEL, CIAN))
    p.append(texto(680, 752, "el estado, afuera", CIAN, 15, peso="600"))
    p.append(texto(680, 774, "una base o un caché de sesiones, compartido por las cinco", SUAVE, 12))

    p.append(texto(610, 826, "Sacar el estado afuera es lo que hace intercambiables a las réplicas: matar una deja de ser un problema.", SUAVE, 13.5))
    p.append(texto(610, 848, "Quién decide cuántas hay y repone la que muere es el orquestador. Kubernetes es el nombre, y en este curso queda como deuda.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/6 · VM contra contenedor
# --------------------------------------------------------------------------

def cont_vm_vs_contenedor():
    """Dos pilas sobre el mismo hardware: donde ocurre el aislamiento."""
    ancho, alto = 1180, 820
    aria = (
        "Dos pilas lado a lado sobre el mismo hardware y el mismo kernel del "
        "host. A la izquierda, el hipervisor y tres maquinas virtuales, cada "
        "una con su kernel invitado y su sistema operativo completo; a la "
        "derecha, tres contenedores que comparten el kernel del host y solo "
        "llevan su rootfs y su proceso. La frontera del aislamiento va "
        "resaltada en cada pila y una franja al pie compara arranque, tamano "
        "en disco y que le pasa a cada pila con un bug del kernel"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(590, 42, "Máquina virtual contra contenedor", TEXTO, 21, peso="600"))
    p.append(texto(590, 68, "dónde ocurre el aislamiento", SUAVE, 14))
    p.append(texto(310, 104, "tres máquinas virtuales", AMBAR, 17, peso="600"))
    p.append(texto(870, 104, "tres contenedores", ACENTO, 17, peso="600"))

    for i in range(3):
        x = 60 + i * 172
        p.append(caja(x, 140, 156, 270, PANEL, AMBAR))
        p.append(texto(x + 78, 164, "VM", AMBAR, 13, peso="600"))
        p.append(caja(x + 12, 176, 132, 46, FONDO, ACENTO, radio=6, grosor=1.5))
        p.append(texto(x + 78, 204, "tu proceso", ACENTO, 12.5))
        p.append(caja(x + 12, 230, 132, 92, FONDO, SUAVE, radio=6, grosor=1.5))
        p.append(texto(x + 78, 258, "sistema operativo", SUAVE, 11.5))
        p.append(texto(x + 78, 276, "completo", SUAVE, 11.5))
        p.append(texto(x + 78, 300, "init, libs, paquetes", SUAVE, 10.5))
        p.append(caja(x + 12, 330, 132, 66, FONDO, AMBAR, radio=6, grosor=1.5))
        p.append(texto(x + 78, 358, "kernel", AMBAR, 12.5, peso="600"))
        p.append(texto(x + 78, 378, "invitado", AMBAR, 12.5))

    p.append(caja(60, 428, 500, 66, TINTE, AMBAR, grosor=3.5))
    p.append(texto(310, 456, "hipervisor (KVM, QEMU, Hyper-V)", AMBAR, 15, peso="600"))
    p.append(texto(310, 478, "la frontera del aislamiento está aquí", AMBAR, 12.5))

    p.append(caja_punteada(620, 150, 500, 156, SUAVE))
    p.append(texto(870, 186, "lo que el contenedor NO lleva", SUAVE, 15, peso="600"))
    p.append(texto(870, 216, "· ningún kernel invitado", SUAVE, 13))
    p.append(texto(870, 240, "· ningún sistema operativo completo", SUAVE, 13))
    p.append(texto(870, 264, "· ningún hipervisor", SUAVE, 13))
    p.append(texto(870, 292, "por eso arranca en milisegundos y pesa megabytes", SUAVE, 12))

    for i in range(3):
        x = 620 + i * 172
        p.append(caja(x, 330, 156, 164, PANEL, ACENTO))
        p.append(texto(x + 78, 354, "contenedor", ACENTO, 13, peso="600"))
        p.append(caja(x + 12, 366, 132, 54, FONDO, ACENTO, radio=6, grosor=1.5))
        p.append(texto(x + 78, 398, "tu proceso", ACENTO, 12.5))
        p.append(caja(x + 12, 428, 132, 54, FONDO, SUAVE, radio=6, grosor=1.5))
        p.append(texto(x + 78, 450, "rootfs", SUAVE, 12.5))
        p.append(texto(x + 78, 468, "sólo lo que pediste", SUAVE, 10.5))

    p.append(caja(60, 508, 1060, 62, TINTE, ACENTO, grosor=3.5))
    p.append(texto(590, 534, "kernel del host (Linux) — uno solo", TEXTO, 16, peso="600"))
    p.append(texto(590, 558, "del lado del contenedor la frontera está aquí: es el mismo kernel para los tres", ACENTO, 12))

    p.append(caja(60, 584, 1060, 50, PANEL, LINEA))
    p.append(texto(590, 614, "hardware — CPU, memoria, disco, red", SUAVE, 15))

    p.append(caja(40, 656, 1100, 136, PANEL, LINEA))
    p.append(texto(360, 684, "máquina virtual", AMBAR, 13.5, anclaje="start", peso="600"))
    p.append(texto(760, 684, "contenedor", ACENTO, 13.5, anclaje="start", peso="600"))
    filas = (
        ("arranque", "decenas de segundos", "cientos de milisegundos"),
        ("tamaño en disco", "gigabytes", "decenas o cientos de MB"),
        ("un bug del kernel", "cae el invitado; el host sigue", "cae el kernel de todos: no hay un segundo kernel"),
    )
    for k, (criterio, vm, cont) in enumerate(filas):
        y = 716 + k * 28
        p.append(texto(70, y, criterio, TEXTO, 13, anclaje="start", peso="600"))
        p.append(texto(360, y, vm, SUAVE, 13, anclaje="start"))
        p.append(texto(760, y, cont, SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/6 y 3/5 · El espectro no es una linea: son dos ejes
# --------------------------------------------------------------------------

def cont_espectro():
    """Donde aterriza la syscall, contra que privilegio tiene quien se escapa."""
    ancho, alto = 1200, 800
    aria = (
        "No es una linea, son dos ejes cruzados. El eje horizontal, donde "
        "aterriza la syscall que no controlas, ordena proceso suelto, "
        "contenedor, gVisor, Kata y VM completa. El eje vertical, que "
        "privilegio tiene quien se escapa, va de root en el host abajo a un "
        "usuario sin privilegios con su rango de subuid arriba. Contenedor "
        "rootful y rootless caen en la misma columna y se separan solo en el "
        "eje vertical; gVisor aparece dos veces, una a cada altura, porque "
        "tiene su propio modo rootless: los ejes se componen, no se ordenan"
    )
    columnas = (
        (386, "proceso suelto", SUAVE,
         ("la syscall va directo", "al kernel del host")),
        (558, "contenedor", ACENTO,
         ("la syscall va directo", "al kernel del host —", "el mismo kernel")),
        (730, "gVisor", CIAN,
         ("a un núcleo en espacio", "de usuario que reimplementa", "la interfaz de syscalls")),
        (902, "Kata", VIOLETA,
         ("a un segundo kernel real,", "dentro de una VM ligera")),
        (1074, "VM completa", AMBAR,
         ("a un kernel invitado,", "detrás del hipervisor")),
    )
    ARRIBA, ABAJO = 270, 480

    p = [marco(ancho, alto, aria)]
    p.append(texto(600, 42, "El aislamiento no es una línea: son dos ejes", TEXTO, 21, peso="600"))
    p.append(texto(600, 68, "y rootless sólo mueve uno de los dos", SUAVE, 14))

    p.append(flecha(300, 566, 300, 174, AMBAR))
    p.append(flecha(294, 560, 1166, 560, CIAN))
    for y in (ARRIBA, ABAJO):
        p.append(linea(300, y, 1160, y, LINEA, 1, "4 7"))

    p.append(texto(170, 126, "qué privilegio tiene", AMBAR, 14, peso="600"))
    p.append(texto(170, 146, "quien se escapa", AMBAR, 14, peso="600"))
    p.append(texto(730, 126, "Son dos preguntas independientes. Cada runtime ocupa una casilla de la rejilla:", SUAVE, 13))
    p.append(texto(730, 148, "una respuesta en el eje de abajo y otra en el de la izquierda.", SUAVE, 13))
    p.append(texto(288, 264, "un usuario sin privilegios,", SUAVE, 12.5, anclaje="end"))
    p.append(texto(288, 282, "con su rango de subuid", SUAVE, 12.5, anclaje="end"))
    p.append(texto(288, 484, "root en el host", SUAVE, 12.5, anclaje="end"))

    for cx, nombre, color, glosa in columnas:
        p.append(texto(cx, 592, nombre, color, 14, peso="600"))
        for k, renglon in enumerate(glosa):
            p.append(texto(cx, 614 + k * 16, renglon, SUAVE, 11))
    p.append(texto(730, 700, "dónde aterriza la syscall que no controlas   →", CIAN, 14, peso="600"))

    # Proceso suelto: no hay frontera que romper.
    p.append(circulo(386, ABAJO, 9, SUAVE))
    p.append(texto(386, 508, "nada que romper", SUAVE, 11.5))

    # El contenedor: misma columna, dos alturas.
    p.append(flecha(558, ABAJO - 18, 558, ARRIBA + 20, ACENTO, 2.5))
    p.append(texto(544, 374, "rootless", ACENTO, 12.5, anclaje="end", peso="600"))
    p.append(texto(544, 392, "sube sólo aquí", SUAVE, 11.5, anclaje="end"))
    p.append(circulo(558, ABAJO, 10, ROJO))
    p.append(texto(558, 508, "rootful", ROJO, 13, peso="600"))
    p.append(circulo(558, ARRIBA, 10, ACENTO))
    p.append(texto(558, 246, "rootless", ACENTO, 13, peso="600"))

    # gVisor, dos veces: tiene su propio modo rootless.
    p.append(linea(730, ABAJO - 18, 730, ARRIBA + 18, CIAN, 1.5, "5 6"))
    p.append(circulo(730, ABAJO, 10, CIAN))
    p.append(texto(730, 508, "gVisor", CIAN, 13, peso="600"))
    p.append(circulo(730, ARRIBA, 10, CIAN))
    p.append(texto(730, 246, "gVisor rootless", CIAN, 13, peso="600"))
    p.append(texto(746, 374, "su propio modo", CIAN, 11.5, anclaje="start"))
    p.append(texto(746, 390, "rootless", CIAN, 11.5, anclaje="start"))

    # Kata y VM: el eje horizontal los fija; el vertical no lo dice esta figura.
    for cx, nombre, color in ((902, "Kata", VIOLETA), (1074, "VM completa", AMBAR)):
        p.append(caja(cx - 30, 252, 60, 246, PANEL, color, radio=30, grosor=2.5))
        p.append(texto(cx, 232, nombre, color, 13, peso="600"))
        p.append(texto(cx, 520, "el eje vertical", SUAVE, 10.5))
        p.append(texto(cx, 534, "depende de cómo lo corras", SUAVE, 10.5))

    p.append(texto(600, 728, "Rootless no añade ninguna frontera: mismo kernel, misma superficie de syscalls. Mueve el eje vertical y no el horizontal.", SUAVE, 13.5))
    p.append(texto(600, 750, "Por eso gVisor tiene su propio modo rootless: los dos ejes se componen, no se ordenan.", SUAVE, 13.5))
    p.append(texto(600, 772, "Y rootless no sale gratis: habilitar user namespaces no privilegiados abre interfaces del kernel que normalmente están restringidas.", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/7 · Docker y Podman
# --------------------------------------------------------------------------

def cont_docker_vs_podman():
    """Con daemon y sin daemon, y el mito del 2x desarmado con los datos."""
    ancho, alto = 1260, 770
    aria = (
        "Las dos cadenas, una sobre otra. Arriba, docker CLI hablando por un "
        "socket con dockerd, marcado como proceso privilegiado siempre "
        "encendido, y de ahi containerd, el shim y runc. Abajo, podman, que "
        "hace fork-exec directo de conmon y de crun o runc y no deja nada "
        "permanente, con su caja de lo que si necesita rootless: rango en "
        "subuid y subgid y los binarios newuidmap y newgidmap. Un recuadro "
        "desarma el mito del doble de velocidad con tres barras medidas"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(630, 42, "Docker y Podman: la diferencia es arquitectónica", TEXTO, 21, peso="600"))
    p.append(texto(630, 68, "qué compra exactamente no tener daemon", SUAVE, 14))

    p.append(texto(50, 106, "Docker — con daemon", ROJO, 17, anclaje="start", peso="600"))
    p.append(teclado(209, 134, "/var/run/docker.sock", CIAN, 12.5, peso="normal"))
    docker = (
        (130, "docker", "lo que tecleas", CIAN),
        (150, "dockerd", "root · siempre encendido", ROJO),
        (165, "containerd", "imágenes y tareas", VIOLETA),
        (226, "containerd-shim-runc-v2", "supervisor", ACENTO),
        (120, "runc", "crea y se va", SUAVE),
    )
    x = 50
    for i, (w, nombre, papel, color) in enumerate(docker):
        if i:
            p.append(flecha(x - 54, 187, x - 6, 187, SUAVE))
        p.append(caja(x, 148, w, 78, PANEL, color))
        p.append(teclado(x + w / 2, 180, nombre, color, 13.5))
        p.append(texto(x + w / 2, 202, papel, SUAVE, 11))
        x += w + 58
    p.append(chip(313, 252, "proceso privilegiado", ROJO, tam=13))
    p.append(flecha(782, 228, 782, 246, ACENTO, 2))
    p.append(caja(669, 250, 226, 62, TINTE, ACENTO, radio=8))
    p.append(texto(782, 274, "el proceso del contenedor", TEXTO, 12.5))
    p.append(texto(782, 294, "cuelga del shim", ACENTO, 12))

    p.append(linea(40, 330, 1220, 330, LINEA, 1.5, "6 6"))

    p.append(texto(50, 366, "Podman — sin daemon, rootless", ACENTO, 17, anclaje="start", peso="600"))
    podman = ((50, 150, "podman", "tu propio proceso", ACENTO),
              (258, 165, "conmon", "supervisor, como el shim", ACENTO),
              (481, 200, "crun (o runc)", "crea y se va", SUAVE))
    for i, (px, w, nombre, papel, color) in enumerate(podman):
        if i:
            p.append(flecha(px - 54, 435, px - 6, 435, ACENTO))
            p.append(texto(px - 30, 382, "fork-exec", ACENTO, 11.5))
        p.append(caja(px, 396, w, 78, PANEL, color))
        p.append(teclado(px + w / 2, 428, nombre, color, 13.5))
        p.append(texto(px + w / 2, 450, papel, SUAVE, 11))
    p.append(chip(125, 502, "nada permanente", SUAVE, tam=13))
    p.append(flecha(340, 476, 340, 494, ACENTO, 2))
    p.append(caja(258, 498, 165, 62, TINTE, ACENTO, radio=8))
    p.append(texto(340, 522, "el proceso", TEXTO, 12.5))
    p.append(texto(340, 542, "cuelga de conmon", ACENTO, 11.5))

    p.append(caja(730, 380, 500, 175, PANEL, VIOLETA))
    p.append(texto(750, 410, "lo que rootless SÍ necesita", VIOLETA, 15, anclaje="start", peso="600"))
    p.append(texto(750, 440, "· un rango propio en /etc/subuid y /etc/subgid", SUAVE, 13, anclaje="start"))
    p.append(texto(750, 466, "· los binarios newuidmap y newgidmap", SUAVE, 13, anclaje="start"))
    p.append(texto(766, 490, "en Debian y Ubuntu vienen en el paquete uidmap,", SUAVE, 11.5, anclaje="start"))
    p.append(texto(766, 508, "que es Recommends y falta en instalaciones mínimas", SUAVE, 11.5, anclaje="start"))
    p.append(texto(750, 536, "sin eso:", SUAVE, 12, anclaje="start"))
    p.append(teclado(806, 536, "cannot find UID in /etc/subuid", ROJO, 12, anclaje="start", peso="normal"))

    p.append(caja(50, 580, 1180, 118, PANEL, AMBAR))
    p.append(texto(70, 608, "El mito del 2×, desarmado: fijando todo menos el runtime", AMBAR, 14.5, anclaje="start", peso="600"))
    barras = (("podman --runtime crun", 215, ACENTO),
              ("docker (runtime runc)", 361, CIAN),
              ("podman --runtime runc", 373, ROJO))
    tope = max(ms for _, ms, _ in barras)
    for k, (etiqueta, ms, color) in enumerate(barras):
        y = 626 + k * 24
        p.append(teclado(70, y + 4, etiqueta, SUAVE, 12, anclaje="start", peso="normal"))
        p.append(relleno(310, y - 9, ms / tope * 700, 17, color, radio=4))
        p.append(texto(320 + ms / tope * 700, y + 4, f"{ms} ms", color, 12.5, anclaje="start", peso="600"))

    p.append(texto(630, 722, "Con el runtime igualado, Podman rootless no gana: sale ~3 % detrás de Docker. Lo que compra la ausencia de daemon no es velocidad:", SUAVE, 13.5))
    p.append(texto(630, 744, "es rootless, integración con systemd y ningún proceso privilegiado siempre encendido.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 1/8 · Capas y cache
# --------------------------------------------------------------------------

def _pila_de_capas(y0, instrucciones, estados, hashes, paso=38):
    """Dockerfile a la izquierda, su pila de capas a la derecha."""
    p = []
    for i, instruccion in enumerate(instrucciones):
        y = y0 + i * paso
        tocada = estados[i][2]
        p.append(caja(58, y, 544, 32, FONDO, ROJO if tocada else "none",
                      radio=6, grosor=2 if tocada else 0))
        p.append(teclado(72, y + 21, instruccion, ROJO if tocada else TEXTO, 14,
                         anclaje="start", peso="normal"))
        if tocada:
            p.append(texto(596, y + 21, "← tocaste una línea", ROJO, 11.5,
                           anclaje="end"))
        p.append(flecha(616, y + 16, 684, y + 16, SUAVE, 1.5))
        etiqueta, color, _ = estados[i]
        p.append(caja(690, y, 440, 32, PANEL, color, radio=6, grosor=2))
        p.append(teclado(704, y + 21, hashes[i], SUAVE, 11.5, anclaje="start",
                         peso="normal"))
        p.append(texto(910, y + 21, f"capa {i + 1}", SUAVE, 11.5))
        p.append(texto(1116, y + 21, etiqueta, color, 12, anclaje="end",
                       peso="600"))
    return "".join(p)


def cont_capas_cache():
    """El cache es secuencial: una capa invalidada tumba las de abajo."""
    ancho, alto = 1300, 760
    aria = (
        "Un Dockerfile a la izquierda y su pila de capas a la derecha, cada "
        "capa con su hash truncado. Arriba, con COPY punto punto antes del RUN "
        "pip install, tocar una linea de codigo invalida esa capa y todas las "
        "de abajo, que caen en domino aunque su contenido no haya cambiado. "
        "Abajo, con COPY requirements.txt primero y el codigo despues, las "
        "capas de instalacion quedan rotuladas CACHED y solo se rehacen las "
        "dos ultimas"
    )
    CACHED = ("CACHED", ACENTO, False)
    INVAL = ("INVALIDADA", ROJO, False)
    TOCADA = ("INVALIDADA", ROJO, True)

    p = [marco(ancho, alto, aria)]
    p.append(texto(650, 42, "El caché de capas cae en dominó", TEXTO, 21, peso="600"))
    p.append(texto(650, 68, "el mismo cambio en una línea de código, con dos Dockerfiles", SUAVE, 14))

    p.append(texto(50, 104, "mal ordenado", ROJO, 16, anclaje="start", peso="600"))
    p.append(teclado(200, 104, "COPY . .  antes del  RUN pip install", SUAVE, 12.5, anclaje="start", peso="normal"))
    p.append(caja(50, 124, 560, 220, PANEL, LINEA))
    p.append(_pila_de_capas(
        144,
        ("FROM python:3.12-slim", "WORKDIR /app", "COPY . .",
         "RUN pip install -r requirements.txt", "CMD [\"python\", \"app.py\"]"),
        (CACHED, CACHED, TOCADA, INVAL, INVAL),
        ("sha256:6a2f…", "sha256:c81d…", "sha256:4be9…", "sha256:07ac…",
         "sha256:d5f1…"),
    ))
    p.append(flecha(1168, 236, 1168, 324, ROJO, 2.5))
    p.append(texto(1184, 262, "caen", ROJO, 12, anclaje="start", peso="600"))
    p.append(texto(1184, 280, "en dominó", ROJO, 12, anclaje="start", peso="600"))
    p.append(texto(1184, 302, "pip vuelve a", SUAVE, 10.5, anclaje="start"))
    p.append(texto(1184, 316, "correr entero,", SUAVE, 10.5, anclaje="start"))
    p.append(texto(1184, 330, "sin haber", SUAVE, 10.5, anclaje="start"))
    p.append(texto(1184, 344, "cambiado nada", SUAVE, 10.5, anclaje="start"))

    p.append(linea(40, 368, 1260, 368, LINEA, 1.5, "6 6"))

    p.append(texto(50, 400, "bien ordenado", ACENTO, 16, anclaje="start", peso="600"))
    p.append(teclado(200, 400, "COPY requirements.txt .  antes, y el código después", SUAVE, 12.5, anclaje="start", peso="normal"))
    p.append(texto(580, 400, "— reordenar parte el COPY en dos: una instrucción más", SUAVE, 12, anclaje="start"))
    p.append(caja(50, 420, 560, 258, PANEL, LINEA))
    p.append(_pila_de_capas(
        440,
        ("FROM python:3.12-slim", "WORKDIR /app", "COPY requirements.txt .",
         "RUN pip install -r requirements.txt", "COPY . .",
         "CMD [\"python\", \"app.py\"]"),
        (CACHED, CACHED, CACHED, CACHED, TOCADA, INVAL),
        ("sha256:6a2f…", "sha256:c81d…", "sha256:9d30…", "sha256:b17e…",
         "sha256:4be9…", "sha256:d5f1…"),
    ))
    p.append(texto(1184, 570, "pip no vuelve", ACENTO, 10.5, anclaje="start"))
    p.append(texto(1184, 584, "a correr", ACENTO, 10.5, anclaje="start"))
    p.append(flecha(1168, 596, 1168, 658, ROJO, 2.5))
    p.append(texto(1184, 614, "sólo estas", ROJO, 12, anclaje="start", peso="600"))
    p.append(texto(1184, 632, "dos se rehacen", ROJO, 12, anclaje="start", peso="600"))

    p.append(texto(650, 714, "El caché es secuencial: una capa sólo se reusa si TODAS las de arriba se reusaron. Por eso una capa invalidada tumba todo lo que sigue,", SUAVE, 13.5))
    p.append(texto(650, 738, "aunque su propio contenido no haya cambiado. La regla práctica: lo que cambia poco, arriba; lo que cambia en cada commit, hasta abajo.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/10 · Las ocho formas de creer que corres sin sudo
# --------------------------------------------------------------------------

def _trampa(x, y, w, h, titulo, delator, tachada=False):
    """Tarjeta de trampa: como se llama arriba, que la delata abajo."""
    p = [caja(x, y, w, h, PANEL, ROJO, radio=8, grosor=1.8)]
    for i, renglon in enumerate(titulo):
        p.append(texto(x + w / 2, y + 26 + i * 18, renglon, TEXTO, 12.5,
                       peso="600"))
    if tachada:
        p.append(tachado(x + 18, y + 22, x + w - 18, ROJO, 2.5))
    p.append(linea(x + 14, y + 56, x + w - 14, y + 56, LINEA, 1))
    for i, renglon in enumerate(delator):
        p.append(texto(x + w / 2, y + 76 + i * 16, renglon, SUAVE, 11))
    return "".join(p)


def cont_sin_sudo():
    """La cadena de comprobacion, y las ocho trampas colgadas de su delator."""
    ancho, alto = 1360, 700
    aria = (
        "Arbol de comprobacion de que de verdad corres sin sudo. Arriba, seis "
        "comandos en fila con lo que cada uno debe imprimir: whoami, id -u, "
        "type -a docker, docker context ls, docker version y docker run --rm "
        "hello-world. Abajo, las ocho formas de creer que corres sin sudo sin "
        "correr sin sudo, cada tarjeta colgada del comando que la delata: el "
        "alias con sudo adentro y la funcion de shell bajo type, ser root en "
        "WSL2 bajo whoami, el sudo -i olvidado bajo id -u, el DOCKER_HOST "
        "remoto bajo docker context ls, Podman diciendose Docker bajo docker "
        "version, y bajo la prueba final el newgrp de una sola ventana y el "
        "chmod 666 del socket, tachado en rojo. Al pie, la advertencia que se "
        "cobra en la seccion 3: estar en el grupo docker es ser root"
    )
    comandos = (
        (("whoami",), ("debe decir tu usuario,", "nunca root")),
        (("id -u",), ("debe decir un número", "distinto de 0")),
        (("type -a docker",), ("debe decir un binario,", "no un alias ni una función")),
        (("docker context ls",), ("el contexto activo debe", "ser default, y local")),
        (("docker version",), ("debe traer Client y Server,", "y decir Docker Engine")),
        (("docker run --rm", "hello-world"), ("la prueba de verdad:", "si esto corre, corres")),
    )
    trampas = {
        0: [(("ser root en WSL2",), ("whoami dice root: ahí no",
                                     "hay sudo que quitar,", "ya eres root."), False)],
        1: [(("el sudo -i olvidado",), ("llevas media hora en una",
                                        "shell de root y el prompt", "ya no te lo recuerda."), False)],
        2: [(("un alias con sudo", "adentro"),
             ("docker is aliased to", "'sudo docker'"), False),
            (("una función de shell",),
             ("docker is a function", "— y adentro dice sudo"), False)],
        3: [(("un DOCKER_HOST a", "otra máquina"),
             ("corres sin sudo, sí:", "pero en un servidor",
              "que no es el tuyo."), False)],
        4: [(("Podman diciendo", "que es Docker"),
             ("docker version dice", "Podman Engine: es el",
              "paquete podman-docker."), False)],
        5: [(("el newgrp que sólo", "valía en esa ventana"),
             ("funciona aquí y falla en", "la terminal nueva: falta",
              "cerrar sesión y volver."), False),
            (("chmod 666 del socket",),
             ("funciona, y por eso es peor:", "se lo abriste a todos",
              "los usuarios de la máquina."), True)],
    }

    p = [marco(ancho, alto, aria)]
    p.append(texto(680, 42, "Correr sin sudo, y creer que corres sin sudo", TEXTO, 21, peso="600"))
    p.append(texto(680, 68, "seis comandos que lo comprueban, y las ocho maneras de fallar la comprobación sin notarlo", SUAVE, 14))
    p.append(texto(48, 112, "la cadena, en orden", ACENTO, 15, anclaje="start", peso="600"))
    p.append(texto(1320, 112, "y abajo, las ocho trampas: cada una cuelga del comando que la delata", ROJO, 14, anclaje="end", peso="600"))

    for i, (cmd, glosa) in enumerate(comandos):
        x = 40 + i * 216
        cx = x + 100
        p.append(caja(x, 132, 200, 116, PANEL, CIAN))
        for k, renglon in enumerate(cmd):
            p.append(teclado(cx, 162 + k * 18, renglon, CIAN, 13))
        p.append(linea(x + 14, 190, x + 186, 190, LINEA, 1))
        for k, renglon in enumerate(glosa):
            p.append(texto(cx, 212 + k * 18, renglon, SUAVE, 11))
        if i:
            p.append(flecha(x - 14, 190, x - 4, 190, SUAVE, 1.5))

        for k, (titulo, delator, tachada) in enumerate(trampas[i]):
            y = 300 + k * 136
            p.append(flecha_punteada(cx, y - 20 if k else y - 48, cx, y - 6,
                                     ROJO, 1.6))
            p.append(_trampa(x, y, 200, 116, titulo, delator, tachada))

    p.append(texto(680, 578, "Son ocho, no nueve: el chmod 666 del socket y «dejar el socket suelto» son la misma trampa con dos nombres.", SUAVE, 13))

    p.append(caja(40, 596, 1280, 84, PANEL, ROJO))
    p.append(texto(680, 626, "Y la que se cobra en la sección 3: estar en el grupo docker ES ser root.", ROJO, 15, peso="600"))
    p.append(texto(680, 652, "Quien le puede hablar al socket puede montar / del host dentro de un contenedor. No hay privilegio que escalar: ya lo tiene.", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/11 · Planes B: sintoma, causa, arreglo
# --------------------------------------------------------------------------

def cont_planes_b():
    """Las cinco trampas de instalacion, y el mito que no es una de ellas."""
    ancho, alto = 1320, 730
    aria = (
        "Tabla de diagnostico de tres columnas —sintoma, causa y arreglo— con "
        "las cinco trampas de instalacion: los bind mounts que fallan fuera de "
        "tu carpeta personal porque el paquete de snap esta confinado, la "
        "distro corriendo en WSL1 en vez de WSL2, la integracion por distro "
        "apagada en Docker Desktop, la virtualizacion desactivada en el "
        "firmware, y el disco lleno que delata df -h barra. Una sexta fila va "
        "tachada y en gris: Secure Boot no tiene nada que ver con Docker y no "
        "hay que apagarlo por esto. Al pie, la fecha de reporte anticipada: si "
        "el sabado 19 no te funciona, dilo el sabado 19, no el lunes a "
        "medianoche"
    )
    filas = (
        (ROJO,
         ("bind mount fuera de tu home:", "no such file or directory"),
         ("instalaste Docker desde snap y el paquete", "está confinado: no ve fuera de tu home"),
         ("desinstala el snap e instala desde el", "repositorio oficial de Docker")),
        (ROJO,
         ("System has not been booted with systemd", "y el servicio de docker no arranca"),
         ("tu distro corre en WSL1, no en WSL2",),
         ("wsl -l -v para verlo, y luego", "wsl --set-version <distro> 2")),
        (ROJO,
         ("docker existe en PowerShell", "y no existe en la terminal de Ubuntu"),
         ("la integración por distro está apagada", "en Docker Desktop"),
         ("Settings → Resources → WSL integration,", "y enciende tu distro")),
        (ROJO,
         ("WSL2 o Docker Desktop no levantan:", "la máquina virtual nunca arranca"),
         ("la virtualización está desactivada", "en el firmware de la máquina"),
         ("enciéndela en la BIOS/UEFI:", "VT-x, AMD-V o SVM Mode")),
        (ROJO,
         ("no space left on device", "a media descarga de la imagen"),
         ("el disco está lleno:", "df -h / lo delata en una línea"),
         ("docker system df y después prune:", "la página 8 dice qué se lleva cada uno")),
        (SUAVE,
         ("Secure Boot está encendido",),
         ("ninguna: no es una causa",),
         ("no tiene nada que ver con Docker;", "no lo apagues por esto")),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(660, 42, "Planes B: qué hacer cuando la instalación no salió", TEXTO, 21, peso="600"))
    p.append(texto(660, 68, "las cinco trampas que se repiten, con el síntoma exacto que las delata", SUAVE, 14))

    for x, etiqueta, color in ((66, "síntoma", ROJO), (446, "causa", AMBAR),
                               (866, "arreglo", ACENTO)):
        p.append(texto(x, 116, etiqueta, color, 14.5, anclaje="start", peso="600"))
    p.append(linea(50, 128, 1270, 128, LINEA, 1.5))

    for k, (color, sintoma, causa, arreglo) in enumerate(filas):
        y = 140 + k * 86
        mito = color is SUAVE
        if mito:
            p.append(caja_punteada(50, y, 1220, 78, SUAVE, radio=8))
        else:
            p.append(caja(50, y, 1220, 78, PANEL, LINEA, radio=8, grosor=1.5))
        p.append(linea(430, y + 10, 430, y + 68, LINEA, 1))
        p.append(linea(850, y + 10, 850, y + 68, LINEA, 1))
        for i, renglon in enumerate(sintoma):
            p.append(teclado(66, y + 34 + i * 22, renglon, color, 12,
                             anclaje="start", peso="normal"))
        if mito:
            p.append(tachado(64, y + 30, 262, SUAVE, 2))
        for i, renglon in enumerate(causa):
            p.append(texto(446, y + 34 + i * 22, renglon,
                           SUAVE if mito else TEXTO, 12.5, anclaje="start"))
        for i, renglon in enumerate(arreglo):
            p.append(texto(866, y + 34 + i * 22, renglon,
                           SUAVE if mito else ACENTO, 12.5, anclaje="start"))

    p.append(texto(660, 684, "La fecha de reporte va anticipada a propósito: si el sábado 19 no te funciona, dilo el sábado 19.", SUAVE, 13.5))
    p.append(texto(660, 708, "No el lunes a medianoche, con la clase del martes encima.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/12 · El nombre de una imagen, y el viaje al registro
# --------------------------------------------------------------------------

def cont_registro():
    """Las cuatro piezas del nombre, y login-tag-push-pull."""
    ancho, alto = 1340, 790
    aria = (
        "A la izquierda, el nombre de una imagen desarmado en sus cuatro "
        "piezas rotuladas registro, usuario, nombre y tag: lo que tecleas es "
        "ubuntu y lo que Docker entiende es docker.io diagonal library "
        "diagonal ubuntu dos puntos latest, con la aclaracion de que library "
        "no es un usuario sino el namespace reservado de las imagenes "
        "oficiales, donde no puedes hacer push, y el aviso de que los nombres "
        "van en minusculas siempre. A la derecha, el viaje de tu propia "
        "imagen: docker login, docker tag y docker push hacia el registro, y "
        "docker pull de vuelta desde otra maquina, con el digest sha256 "
        "colgando de la imagen como su nombre verdadero e inmutable, y el "
        "aviso de que la URL publica de la imagen no es la de administracion"
    )
    piezas = (
        (112, "docker.io", "registro", CIAN),
        (94, "library", "usuario", VIOLETA),
        (85, "ubuntu", "nombre", ACENTO),
        (85, "latest", "tag", AMBAR),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "El nombre de una imagen es una dirección", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "cuatro piezas, tres de ellas con valor por omisión — y el viaje de la tuya", SUAVE, 14))
    p.append(linea(680, 96, 680, 700, LINEA, 1.5, "6 6"))

    # -- izquierda: el nombre desarmado ------------------------------------
    p.append(texto(60, 122, "el nombre, desarmado", CIAN, 16, anclaje="start", peso="600"))
    p.append(texto(60, 156, "lo que tecleas", SUAVE, 12.5, anclaje="start"))
    p.append(teclado(60, 192, "ubuntu", ACENTO, 26, anclaje="start"))
    p.append(flecha(90, 208, 90, 246, SUAVE, 1.8))
    p.append(texto(114, 232, "lo que Docker entiende", SUAVE, 12.5, anclaje="start"))

    x = 60
    separadores = ("/", "/", ":")
    for i, (w, pieza, etiqueta, color) in enumerate(piezas):
        if i:
            p.append(teclado(x + 11, 292, separadores[i - 1], SUAVE, 19))
            x += 22
        p.append(caja(x, 258, w, 52, PANEL, color, radio=8))
        p.append(teclado(x + w / 2, 291, pieza, color, 15))
        p.append(texto(x + w / 2, 332, etiqueta, color, 12, peso="600"))
        x += w

    p.append(caja(60, 356, 580, 106, PANEL, VIOLETA))
    p.append(texto(80, 386, "library no es un usuario", VIOLETA, 14.5, anclaje="start", peso="600"))
    p.append(parrafo(80, 412, (
        "Es el namespace reservado de las imágenes oficiales.",
        "Ahí no puedes hacer push: la tuya va a tu-usuario/nombre.",
    )))

    p.append(caja(60, 480, 580, 88, PANEL, ROJO))
    p.append(texto(80, 510, "los nombres van en minúsculas, siempre", ROJO, 14, anclaje="start", peso="600"))
    p.append(teclado(80, 538, "docker.io/TuUsuario/Mi-Imagen", SUAVE, 12, anclaje="start", peso="normal"))
    p.append(teclado(324, 538, "→  invalid reference format", ROJO, 12, anclaje="start", peso="normal"))

    p.append(caja(60, 586, 580, 88, PANEL, AMBAR))
    p.append(texto(80, 616, "latest tampoco es «la más nueva»", AMBAR, 14, anclaje="start", peso="600"))
    p.append(parrafo(80, 642, (
        "Es sólo el tag por omisión, y se mueve. Pinea un tag concreto.",
    )))

    # -- derecha: el viaje del artefacto -----------------------------------
    p.append(texto(716, 122, "el viaje de tu propia imagen", ACENTO, 16, anclaje="start", peso="600"))
    p.append(caja(716, 146, 260, 88, PANEL, ACENTO))
    p.append(texto(846, 176, "tu máquina", TEXTO, 14, peso="600"))
    p.append(teclado(846, 202, "mi-imagen:v1", ACENTO, 14))
    p.append(texto(846, 222, "recién construida con docker build", SUAVE, 11))

    p.append(flecha(846, 238, 846, 336, ACENTO, 2.5))
    p.append(parrafo(880, 266, (
        "docker login",
        "docker tag mi-imagen tu-usuario/mi-imagen:v1",
        "docker push tu-usuario/mi-imagen:v1",
    ), CIAN, 12, 22))
    p.append(texto(880, 332, "sube sólo las capas que al registro le falten", SUAVE, 11, anclaje="start"))

    p.append(caja(716, 344, 584, 130, PANEL, VIOLETA))
    p.append(texto(1008, 374, "el registro — Docker Hub", VIOLETA, 15, peso="600"))
    p.append(teclado(1008, 406, "docker.io/tu-usuario/mi-imagen:v1", TEXTO, 14))
    p.append(teclado(1008, 434, "sha256:9b2fa1c0e7…", AMBAR, 13))
    p.append(texto(1008, 456, "el digest es su nombre verdadero: el tag se mueve, el digest no", SUAVE, 11))

    p.append(flecha(846, 478, 846, 566, CIAN, 2.5))
    p.append(teclado(880, 514, "docker pull tu-usuario/mi-imagen:v1", CIAN, 12, anclaje="start", peso="normal"))
    p.append(texto(880, 534, "otra máquina, sin tu código y sin tus dependencias", SUAVE, 11, anclaje="start"))

    p.append(caja(716, 574, 260, 88, PANEL, CIAN))
    p.append(texto(846, 604, "la máquina de alguien más", TEXTO, 13, peso="600"))
    p.append(texto(846, 628, "no construyó nada:", SUAVE, 12))
    p.append(texto(846, 648, "sólo hizo pull", CIAN, 12, peso="600"))

    p.append(caja(1010, 574, 290, 88, PANEL, AMBAR))
    p.append(texto(1030, 602, "la URL pública no es la tuya", AMBAR, 13, anclaje="start", peso="600"))
    p.append(teclado(1030, 626, "pública: hub.docker.com/r/tu-usuario/…", SUAVE, 10, anclaje="start", peso="normal"))
    p.append(teclado(1030, 646, "admin: hub.docker.com/repository/docker/…", SUAVE, 10, anclaje="start", peso="normal"))

    p.append(texto(670, 726, "Las tres piezas que no escribes tienen valor por omisión, y por eso ubuntu y docker.io/library/ubuntu:latest son la misma imagen.", SUAVE, 13.5))
    p.append(texto(670, 750, "Publicar no es «subirla a internet»: es darle un nombre que otra máquina pueda resolver. El digest es el que no miente.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/2 · El ciclo de vida de un contenedor
# --------------------------------------------------------------------------

def cont_ciclo_de_vida():
    """Tres casillas, y que alcanza cada comando de las tres."""
    ancho, alto = 1400, 700
    aria = (
        "Maquina de estados de tres casillas —created, running y exited— con "
        "cada transicion etiquetada por lo que la provoca: docker run, que es "
        "create mas start; docker start; la salida del proceso PID 1, que es "
        "la unica razon por la que un contenedor se detiene; y docker rm, que "
        "saca la casilla del dibujo junto con su capa de escritura. A la "
        "derecha, que alcanza cada comando: docker ps solo ve running, docker "
        "ps -a ve las tres, docker logs ve running y exited, y docker exec -it "
        "entra a running y aparece tachado contra exited. Al pie, el caso del "
        "exited con codigo 127: docker run --name roto ubuntu:24.04 sh -c "
        "comando-que-no-existe, cuya shell no encuentra el comando, y docker "
        "logs roto trae la linea sh: 1: comando-que-no-existe: not found"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(700, 42, "El ciclo de vida de un contenedor", TEXTO, 21, peso="600"))
    p.append(texto(700, 68, "un contenedor vive exactamente lo que vive su proceso PID 1", SUAVE, 14))

    # -- la maquina de estados ---------------------------------------------
    p.append(linea(60, 164, 480, 164, CIAN, 1.5))
    p.append(linea(60, 164, 60, 178, CIAN, 1.5))
    p.append(linea(480, 164, 480, 178, CIAN, 1.5))
    p.append(teclado(270, 152, "docker run  =  create + start", CIAN, 13.5))

    estados = ((60, "created", "existe, y nunca corrió", SUAVE),
               (300, "running", "su PID 1 está vivo", ACENTO),
               (540, "exited", "su PID 1 ya salió", ROJO))
    for x, nombre, glosa, color in estados:
        p.append(caja(x, 220, 180, 96, PANEL, color, grosor=2.5))
        p.append(teclado(x + 90, 262, nombre, color, 18))
        p.append(texto(x + 90, 288, glosa, SUAVE, 11.5))

    p.append(flecha(246, 268, 294, 268, ACENTO, 2.5))
    p.append(chip(270, 196, "docker start", ACENTO, tam=12.5))
    p.append(flecha(486, 268, 534, 268, ROJO, 2.5))
    p.append(chip(510, 196, "el PID 1 sale", ROJO, tam=12.5))

    p.append(arco(612, 320, 408, 320, 72, ACENTO, 2))
    p.append(chip(510, 376, "docker start", ACENTO, tam=12.5))

    p.append(flecha(660, 320, 660, 424, ROJO, 2.5))
    p.append(teclado(676, 356, "docker rm", ROJO, 13, anclaje="start"))
    p.append(caja_punteada(500, 428, 260, 76, SUAVE, radio=8))
    p.append(texto(630, 456, "fuera del dibujo", SUAVE, 13, peso="600"))
    p.append(texto(630, 480, "y con él, su capa de escritura", SUAVE, 11.5))

    p.append(texto(60, 348, "Detenerse es siempre lo mismo:", TEXTO, 13, anclaje="start", peso="600"))
    p.append(parrafo(60, 370, (
        "que el PID 1 salga. docker stop se lo pide",
        "con SIGTERM y espera 10 s; docker kill manda",
        "SIGKILL. No hay una tercera manera.",
    )))

    p.append(caja(40, 516, 700, 124, PANEL, AMBAR))
    p.append(texto(60, 544, "El caso que vas a ver: Exited (127)", AMBAR, 14.5, anclaje="start", peso="600"))
    p.append(teclado(60, 568, "docker run --name roto ubuntu:24.04 sh -c comando-que-no-existe", TEXTO, 11.5, anclaje="start", peso="normal"))
    p.append(parrafo(60, 589, (
        "127 es «command not found»: la shell arrancó, no halló el comando y salió.",
        "docker ps no lo muestra; docker ps -a sí, y docker logs roto trae la línea:",
    ), SUAVE, 12.5, 18))
    p.append(teclado(60, 629, "sh: 1: comando-que-no-existe: not found", AMBAR, 11.5, anclaje="start", peso="normal"))

    # -- que alcanza cada comando ------------------------------------------
    p.append(caja(780, 130, 580, 428, PANEL, LINEA))
    p.append(texto(1070, 160, "qué alcanza cada comando", CIAN, 16, peso="600"))
    alcances = (
        ("docker ps", (False, True, False), "sólo lo que está corriendo", CIAN),
        ("docker ps -a", (True, True, True), "las tres: created y exited también", CIAN),
        ("docker logs", (False, True, True), "lo que escribió ese proceso, vivo o muerto", CIAN),
        ("docker exec -it", (False, True, False), "sólo se entra a un proceso vivo", ACENTO),
    )
    for k, (cmd, prendidas, nota, color) in enumerate(alcances):
        y = 186 + k * 90
        p.append(teclado(802, y, cmd, color, 13.5, anclaje="start"))
        for i, (etiqueta, prendida) in enumerate(zip(("created", "running", "exited"), prendidas)):
            px = 1002 + i * 116
            p.append(pastilla(px, y - 16, 104, 34, etiqueta,
                              (ROJO if i == 2 else ACENTO) if prendida else SUAVE,
                              prendida, tam=11.5))
        p.append(texto(802, y + 44, nota, SUAVE, 11.5, anclaje="start"))
        if k == 3:
            p.append(flecha(1170, y + 46, 1170, y + 22, ACENTO, 2.5))
            p.append(tachado(1242, y + 2, 1330, ROJO, 2.5))

    p.append(texto(700, 668, "Nada de esto es una regla aparte: created es antes del primer arranque, exited es después de que su PID 1 salió, y docker rm borra la casilla entera.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/3 · El contexto de build
# --------------------------------------------------------------------------

def cont_build_contexto():
    """Que se lleva exactamente el punto final de docker build."""
    ancho, alto = 1300, 830
    aria = (
        "Que significa el punto final de docker build -t mi-imagen punto: el "
        "directorio que hace de contexto, el unico lugar de donde el build "
        "puede leer. Con BuildKit no viaja la carpeta entera: viaja lo que "
        "piden los COPY, y con COPY punto punto eso es todo, menos lo que "
        ".dockerignore recorta. A la izquierda, la carpeta en disco con app.py "
        "y requirements.txt livianos y el .git, el entorno virtual y los datos "
        "crudos pesando gigabytes; en medio, .dockerignore como un colador; a "
        "la derecha, lo que llega al daemon. Un COPY de fuera del contexto "
        "falla con failed to compute cache key, not found. Abajo, tres notas: "
        "-f cambia que Dockerfile se lee pero no el contexto, --no-cache solo "
        "ignora las capas previas, y el error de escribir la ruta del "
        "Dockerfile donde va el contexto: unable to prepare context, path not "
        "found"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(650, 42, "El punto final de docker build no es «aquí»", TEXTO, 21, peso="600"))
    p.append(texto(650, 68, "es «el build sólo puede leer de este directorio»", SUAVE, 14))

    p.append(teclado(472, 152, "docker build -t mi-imagen", TEXTO, 22, anclaje="start"))
    p.append(caja(818, 128, 34, 34, TINTE, ROJO, radio=6, grosor=2.5))
    p.append(teclado(835, 152, ".", ROJO, 22))
    p.append(flecha(835, 166, 835, 196, ROJO, 2))
    p.append(texto(858, 192, "esto es el CONTEXTO, no «aquí»", ROJO, 13.5, anclaje="start", peso="600"))

    # La carpeta en disco.
    p.append(caja(50, 224, 350, 286, PANEL, CIAN))
    p.append(texto(225, 252, "tu carpeta, en disco", CIAN, 14, peso="600"))
    p.append(teclado(225, 274, "~/fdd/docker-lab", SUAVE, 12, peso="normal"))
    arbol = (
        ("app.py", "4 KB", TEXTO, False),
        ("requirements.txt", "1 KB", TEXTO, False),
        ("Dockerfile", "1 KB", TEXTO, False),
        (".git/", "182 MB", ROJO, True),
        (".venv/", "310 MB", ROJO, True),
        ("crudos/", "1.2 GB", ROJO, True),
    )
    for i, (nombre, peso, color, pesado) in enumerate(arbol):
        y = 306 + i * 28
        p.append(teclado(74, y, nombre, color, 12.5, anclaje="start", peso="normal"))
        p.append(teclado(376, y, peso, color, 12.5, anclaje="end", peso="600" if pesado else "normal"))
    p.append(linea(74, 486, 376, 486, LINEA, 1))
    p.append(teclado(376, 504, "1.5 GB en total", ROJO, 12.5, anclaje="end"))

    # El colador.
    p.append(flecha(404, 360, 436, 360, SUAVE, 2))
    p.append(caja_punteada(442, 250, 86, 220, AMBAR, radio=10, grosor=2))
    p.append(texto(485, 236, ".dockerignore", AMBAR, 12.5, peso="600"))
    for i in range(6):
        p.append(linea(452, 274 + i * 32, 518, 274 + i * 32, AMBAR, 1.5, "5 5"))
    p.append(flecha(534, 360, 566, 360, ACENTO, 2))

    # Lo que se cae del colador.
    p.append(flecha_punteada(485, 474, 485, 502, ROJO, 1.6))
    p.append(texto(452, 524, "lo que .dockerignore recorta antes del envío:", ROJO, 12, anclaje="start", peso="600"))
    for i, recortado in enumerate((".git/  ·  182 MB", ".venv/  ·  310 MB",
                                   "crudos/  ·  1.2 GB")):
        p.append(cruz(468, 548 + i * 24, 7, ROJO, 2))
        p.append(teclado(488, 553 + i * 24, recortado, SUAVE, 11.5, anclaje="start", peso="normal"))

    # El contexto y el daemon.
    p.append(caja(572, 300, 250, 124, PANEL, ACENTO))
    p.append(texto(697, 330, "el contexto", ACENTO, 15, peso="600"))
    p.append(texto(697, 354, "lo que piden los COPY", SUAVE, 11.5))
    p.append(teclado(697, 388, "6 KB", ACENTO, 20))
    p.append(texto(697, 410, "con COPY . . y el colador", SUAVE, 11))

    p.append(flecha(826, 362, 878, 362, ACENTO, 2.5))
    p.append(caja(884, 300, 366, 124, PANEL, VIOLETA))
    p.append(texto(1067, 330, "el daemon (BuildKit)", VIOLETA, 15, peso="600"))
    p.append(parrafo(908, 356, (
        "Pide sólo lo que nombran los COPY:",
        "con COPY . . es todo el «.», menos",
        "lo que .dockerignore recorta.",
    )))

    p.append(caja(884, 448, 366, 124, PANEL, ROJO))
    p.append(texto(1067, 478, "y por eso esto falla", ROJO, 14, peso="600"))
    p.append(teclado(908, 506, "COPY ../datos .", SUAVE, 12, anclaje="start", peso="normal"))
    p.append(teclado(908, 530, "failed to compute cache key:", ROJO, 11.5, anclaje="start", peso="normal"))
    p.append(teclado(908, 550, "... \"/datos\": not found", ROJO, 11.5, anclaje="start", peso="normal"))

    # Las tres notas del pie.
    notas = (
        (40, 400, AMBAR, "-f cambia el Dockerfile, no el contexto",
         ("docker build -f otro/Dockerfile .",
          "lee ese archivo; el contexto sigue siendo el «.».",
          "Son dos argumentos distintos y se confunden todo el tiempo.")),
        (460, 380, CIAN, "--no-cache no toca el contexto",
         ("Sólo ignora las capas ya construidas.",
          "Lo que piden los COPY se lee igual,",
          "del mismo contexto.")),
        (860, 400, ROJO, "el error más común",
         ("docker build -t mi-imagen ./Dockerfile",
          "unable to prepare context: path \"./Dockerfile\"",
          "not found  — ahí va el contexto, no el archivo.")),
    )
    for x, w, color, titulo, renglones in notas:
        p.append(caja(x, 616, w, 136, PANEL, color))
        p.append(texto(x + 20, 646, titulo, color, 14, anclaje="start", peso="600"))
        for i, renglon in enumerate(renglones):
            escribir = teclado if (i == 0 and color is not CIAN) else texto
            p.append(escribir(x + 20, 676 + i * 22, renglon, SUAVE, 11.5,
                              anclaje="start", peso="normal"))

    p.append(texto(650, 790, "El contexto es lo que el daemon puede ver: si tu archivo no entró en el bulto, para el build no existe.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/9 · Los tres defectos del Dockerfile de roto/
# --------------------------------------------------------------------------

def _insignia(cx, cy, numero, color=ROJO, r=13):
    return (circulo(cx, cy, r, FONDO, color, 2)
            + texto(cx, cy + 5, numero, color, 14, peso="600"))


def cont_dockerfile_roto():
    """Tres defectos, cada uno con su consecuencia medible y su arreglo."""
    ancho, alto = 1340, 800
    aria = (
        "El Dockerfile de la carpeta roto con sus cinco lineas a la izquierda "
        "y sus tres defectos senalados con insignias numeradas: FROM "
        "python:latest sin pinear, el COPY punto punto antes del RUN pip "
        "install, y la ausencia de una instruccion USER. A la derecha, una "
        "tarjeta por defecto con su consecuencia, con la medicion real que la "
        "hace visible —el segundo build baja de 6.53 a 0.41 segundos al "
        "reordenar, con una sola dependencia— y con el arreglo concreto: FROM python:3.12-slim, partir el "
        "COPY dejando requirements.txt primero, y RUN useradd mas USER. Abajo "
        "a la izquierda, el mismo Dockerfile ya arreglado, entero, con las "
        "ocho instrucciones en el orden correcto"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "Los tres defectos del Dockerfile de roto/", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "cada uno con la medición que lo hace visible, no con una opinión", SUAVE, 14))

    # El archivo roto.
    p.append(caja(50, 104, 470, 258, PANEL, ROJO))
    p.append(texto(285, 134, "roto/Dockerfile", ROJO, 15, peso="600"))
    lineas_rotas = (
        ("FROM python:latest", "1"),
        ("WORKDIR /app", None),
        ("COPY . .", "2"),
        ("RUN pip install -r requirements.txt", None),
        ("CMD [\"python\", \"app.py\"]", None),
    )
    for i, (instruccion, insignia) in enumerate(lineas_rotas):
        y = 168 + i * 30
        color = ROJO if insignia else TEXTO
        p.append(teclado(74, y, instruccion, color, 12.5, anclaje="start", peso="normal"))
        if insignia:
            p.append(_insignia(496, y - 5, insignia))
    p.append(caja_punteada(70, 302, 398, 40, ROJO, radio=6))
    p.append(teclado(84, 328, "(aquí no hay ningún USER)", ROJO, 12.5, anclaje="start", peso="normal"))
    p.append(_insignia(496, 322, "3"))

    # El archivo arreglado.
    p.append(caja(50, 392, 470, 306, PANEL, ACENTO))
    p.append(texto(285, 422, "el mismo archivo, arreglado", ACENTO, 15, peso="600"))
    arregladas = (
        ("FROM python:3.12-slim", ACENTO),
        ("WORKDIR /app", TEXTO),
        ("COPY requirements.txt .", ACENTO),
        ("RUN pip install -r requirements.txt", TEXTO),
        ("COPY . .", ACENTO),
        ("RUN useradd -m app && chown -R app /app", ACENTO),
        ("USER app", ACENTO),
        ("CMD [\"python\", \"app.py\"]", TEXTO),
    )
    for i, (instruccion, color) in enumerate(arregladas):
        p.append(teclado(74, 456 + i * 30, instruccion, color, 12.5,
                         anclaje="start", peso="normal"))

    # Las tres tarjetas.
    tarjetas = (
        ("1", "FROM python:latest — sin pinear",
         "la imagen de hoy no es la de mañana: latest se mueve",
         "construye hoy y dentro de un mes: otro digest y otro Python", (),
         ("FROM python:3.12-slim",)),
        ("2", "COPY . .  antes del  RUN pip install",
         "cada cambio de una línea de código tira el caché de instalación",
         "el segundo build tras tocar app.py: 6.53 s contra 0.41 s",
         ("medido con una sola dependencia pequeña, requests: la brecha crece con",
          "el número de paquetes — con pandas y compañía son minutos contra segundos"),
         ("COPY requirements.txt .", "RUN pip install -r requirements.txt",
          "COPY . .")),
        ("3", "no hay ninguna instrucción USER",
         "el proceso corre como root, y lo que escribe en el bind mount queda de root",
         "ls -l del archivo que escribió: owner root, y no lo puedes borrar", (),
         ("RUN useradd -m app && chown -R app /app", "USER app")),
    )
    for k, (num, titulo, consecuencia, medicion, matiz, arreglo) in enumerate(tarjetas):
        y = 104 + k * 220
        p.append(caja(560, y, 740, 208, PANEL, ROJO))
        p.append(_insignia(590, y + 30, num))
        p.append(texto(616, y + 35, titulo, ROJO, 14.5, anclaje="start", peso="600"))
        p.append(linea(580, y + 52, 1280, y + 52, LINEA, 1))
        p.append(texto(580, y + 76, "consecuencia", SUAVE, 11, anclaje="start"))
        p.append(texto(704, y + 76, consecuencia, TEXTO, 12.5, anclaje="start"))
        p.append(texto(580, y + 102, "cómo se mide", SUAVE, 11, anclaje="start"))
        p.append(texto(704, y + 102, medicion, AMBAR, 12.5, anclaje="start"))
        for i, renglon in enumerate(matiz):
            p.append(texto(704, y + 122 + i * 17, renglon, SUAVE, 11, anclaje="start"))
        y_arreglo = y + (156 if matiz else 130)
        p.append(texto(580, y_arreglo, "el arreglo", SUAVE, 11, anclaje="start"))
        for i, renglon in enumerate(arreglo):
            p.append(teclado(704, y_arreglo + i * 20, renglon, ACENTO, 12,
                             anclaje="start", peso="normal"))

    p.append(texto(670, 776, "Ninguno de los tres es una cuestión de gusto: los tres se comprueban con un comando, y por eso se pueden corregir sin discutir.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/4 · Donde vive cada byte
# --------------------------------------------------------------------------

def cont_overlay_volumen():
    """Las cuatro capas donde puede vivir un byte, y cuando muere cada una."""
    ancho, alto = 1300, 970
    aria = (
        "Corte de un contenedor por capas. Abajo del todo, las capas de solo "
        "lectura de la imagen, que las escribe docker build y mueren con "
        "docker rmi; encima, la capa de escritura, que la escribe el proceso "
        "de adentro y muere con docker rm; entre las dos, la flecha de copy-up "
        "que marca que la primera escritura sobre un archivo que venia de una "
        "capa inferior lo copia entero hacia arriba. Entrando de lado, un bind "
        "mount montado en barra app que sale al disco del host, lo escriben "
        "los dos lados y no muere nunca porque es tu disco, y un named volume "
        "montado en el directorio de datos de Postgres que vive en el area de "
        "Docker, lo escribe el contenedor y muere con docker volume rm. Al "
        "pie, la tabla de las cuatro: donde vive el byte, quien lo escribe, "
        "que lo borra y si sobrevive a un docker rm"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(650, 42, "Dónde vive cada byte que escribe un contenedor", TEXTO, 21, peso="600"))
    p.append(texto(650, 68, "cuatro lugares posibles, y cada uno muere con un comando distinto", SUAVE, 14))

    # La vista del proceso.
    p.append(caja(340, 108, 520, 512, "none", LINEA))
    p.append(texto(600, 138, "lo que el proceso ve colgando de  /", TEXTO, 15, peso="600"))

    p.append(texto(370, 172, "overlayfs", SUAVE, 12, anclaje="start"))
    p.append(caja(370, 182, 460, 62, TINTE, ACENTO, grosor=2.5))
    p.append(texto(600, 208, "la capa de escritura", ACENTO, 14.5, peso="600"))
    p.append(texto(600, 230, "la escribe el proceso  ·  muere con docker rm", SUAVE, 11))

    p.append(flecha(430, 306, 430, 250, AMBAR, 2.5))
    p.append(texto(452, 274, "copy-up: la primera vez que escribes un", AMBAR, 11, anclaje="start"))
    p.append(texto(452, 292, "archivo que venía de abajo, se copia entero", SUAVE, 11, anclaje="start"))

    for i, etiqueta in enumerate(("COPY . .", "RUN pip install -r requirements.txt",
                                  "FROM python:3.12-slim")):
        y = 310 + i * 44
        p.append(caja(370, y, 460, 38, PANEL, VIOLETA, radio=8, grosor=1.8))
        p.append(teclado(600, y + 25, etiqueta, VIOLETA, 12, peso="normal"))
    p.append(linea(356, 310, 356, 436, VIOLETA, 2.5))
    p.append(linea(356, 310, 366, 310, VIOLETA, 2.5))
    p.append(linea(356, 436, 366, 436, VIOLETA, 2.5))
    p.append(texto(600, 456, "las capas de la imagen  ·  sólo lectura", VIOLETA, 12.5, peso="600"))
    p.append(texto(600, 474, "las escribe docker build  ·  mueren con docker rmi", SUAVE, 11))

    p.append(linea(360, 494, 840, 494, LINEA, 1, "6 6"))
    p.append(texto(600, 514, "y colgando aparte, dos rutas montadas:", SUAVE, 12))

    p.append(caja(370, 526, 460, 40, PANEL, CIAN, radio=8, grosor=1.8))
    p.append(teclado(600, 552, "/app", CIAN, 14))
    p.append(caja(370, 574, 460, 40, PANEL, AMBAR, radio=8, grosor=1.8))
    p.append(teclado(600, 600, "/var/lib/postgresql/data", AMBAR, 13))

    # El disco del host.
    p.append(caja(40, 464, 276, 156, PANEL, CIAN))
    p.append(texto(178, 494, "tu disco, el del host", CIAN, 14, peso="600"))
    p.append(teclado(178, 518, "~/fdd/docker-lab/app", SUAVE, 11.5, peso="normal"))
    p.append(texto(178, 544, "bind mount", CIAN, 15, peso="600"))
    p.append(parrafo(58, 570, (
        "lo escriben los dos lados",
        "no muere nunca: es tu disco",
        "docker rm no lo toca",
    ), SUAVE, 11.5, 17))
    p.append(flecha(320, 546, 366, 546, CIAN, 2.5))

    # El area de Docker.
    p.append(caja(884, 512, 296, 156, PANEL, AMBAR))
    p.append(texto(1032, 542, "el área de Docker", AMBAR, 14, peso="600"))
    p.append(teclado(1032, 566, "/var/lib/docker/volumes/", SUAVE, 11, peso="normal"))
    p.append(texto(1032, 592, "named volume", AMBAR, 15, peso="600"))
    p.append(parrafo(902, 618, (
        "lo escribe el contenedor",
        "sobrevive a docker rm",
        "muere con docker volume rm",
    ), SUAVE, 11.5, 17))
    p.append(flecha(880, 594, 834, 594, AMBAR, 2.5))

    # La tabla que ordena la clase.
    p.append(texto(650, 700, "la tabla que ordena toda la clase", TEXTO, 16, peso="600"))
    columnas = ((70, "dónde vive el byte"), (420, "quién lo escribe"),
                (740, "qué lo borra"), (1040, "¿sobrevive a docker rm?"))
    for x, etiqueta in columnas:
        p.append(texto(x, 738, etiqueta, SUAVE, 12.5, anclaje="start", peso="600"))
    p.append(linea(50, 750, 1250, 750, LINEA, 1.5))
    tabla = (
        (VIOLETA, "capas de la imagen", "docker build", "docker rmi", "sí", ACENTO),
        (ACENTO, "la capa de escritura", "el proceso de adentro", "docker rm", "NO", ROJO),
        (CIAN, "bind mount", "el host y el contenedor", "tú, borrando el archivo", "sí", ACENTO),
        (AMBAR, "named volume", "el contenedor", "docker volume rm", "sí", ACENTO),
    )
    for k, (color, donde, quien, borra, sobrevive, color_s) in enumerate(tabla):
        y = 784 + k * 38
        p.append(relleno(50, y - 16, 8, 22, color, radio=3))
        p.append(texto(70, y, donde, color, 13, anclaje="start", peso="600"))
        p.append(texto(420, y, quien, TEXTO, 12.5, anclaje="start"))
        p.append(teclado(740, y, borra, SUAVE, 12, anclaje="start", peso="normal"))
        p.append(texto(1040, y, sobrevive, color_s, 13, anclaje="start", peso="600"))

    p.append(texto(650, 944, "La pregunta nunca es «¿se guardó?»: es «¿en cuál de estos cuatro se guardó?». De ahí sale, sin adivinar, qué comando se lo lleva.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/13 · Cuatro maneras de escribir el origen de un -v
# --------------------------------------------------------------------------

def cont_rutas():
    """Absoluta, relativa, portable — y la que no es una ruta."""
    ancho, alto = 1300, 830
    aria = (
        "Cuatro maneras de escribir el origen de un -v y que hace cada una. La "
        "ruta absoluta monta ese directorio y nunca es portable. La ruta "
        "relativa con -v punto barra app dos puntos barra app funciona desde "
        "Docker CLI 23 y tambien en Podman. La forma portable usa -v con "
        "pwd entre comillas. Y -v app dos puntos barra app, sin el punto "
        "barra, no es una ruta: Docker crea un named volume vacio con ese "
        "nombre y lo monta en silencio, sin error y sin aviso, y el codigo no "
        "aparece por ningun lado. Abajo, un recuadro dibuja por que en macOS y "
        "en Windows el bind mount cruza la frontera de una maquina virtual, y "
        "por eso ahi es mas lento y los permisos se comportan distinto"
    )
    casos = (
        (ACENTO, "-v /home/tu/app:/app", "la ruta absoluta",
         ("Monta ese directorio y nada más. Siempre funciona y nunca es portable:",
          "esa ruta no existe en la máquina de nadie más.")),
        (ACENTO, "-v ./app:/app", "la ruta relativa",
         ("El ./ es lo que la vuelve ruta. Funciona desde Docker CLI 23 (2023)",
          "y también en Podman. Se resuelve contra tu directorio actual.")),
        (CIAN, "-v \"$(pwd)/app\":/app", "la forma portable",
         ("El shell la vuelve absoluta antes de que Docker la vea, así que",
          "funciona con cualquier versión. Las comillas son por los espacios.")),
        (ROJO, "-v app:/app", "esto NO es una ruta",
         ("Le falta el ./ , y sin él Docker no ve una ruta: ve un nombre.",
          "Crea un named volume vacío llamado app y lo monta en silencio.")),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(650, 42, "Cuatro maneras de escribir el origen de un -v", TEXTO, 21, peso="600"))
    p.append(texto(650, 68, "y una de las cuatro no es una ruta", SUAVE, 14))

    for k, (color, cadena, nombre, renglones) in enumerate(casos):
        y = 108 + k * 96
        p.append(caja(50, y, 420, 76, PANEL, color))
        p.append(teclado(260, y + 34, cadena, color, 15))
        p.append(texto(260, y + 58, nombre, SUAVE, 12))
        p.append(flecha(476, y + 38, 516, y + 38, color, 2))
        p.append(caja(522, y, 728, 76, PANEL, LINEA, grosor=1.5))
        for i, renglon in enumerate(renglones):
            p.append(texto(544, y + 32 + i * 22, renglon,
                           ROJO if (color is ROJO and i == 0) else SUAVE,
                           12.5, anclaje="start"))

    p.append(texto(650, 512, "Sin error y sin aviso: docker volume ls lo delata, y tu código no aparece por ningún lado dentro del contenedor.", ROJO, 13, peso="600"))

    p.append(linea(40, 540, 1260, 540, LINEA, 1.5, "6 6"))
    p.append(texto(650, 574, "y en macOS y en Windows, el bind mount cruza una frontera más", AMBAR, 16, peso="600"))

    p.append(caja(70, 600, 300, 96, PANEL, CIAN))
    p.append(texto(220, 630, "tu disco", CIAN, 14, peso="600"))
    p.append(texto(220, 654, "APFS en macOS,", SUAVE, 11.5))
    p.append(texto(220, 672, "NTFS en Windows", SUAVE, 11.5))

    p.append(flecha(376, 648, 418, 648, SUAVE, 2))
    p.append(caja_punteada(426, 600, 96, 96, AMBAR, radio=10, grosor=2))
    p.append(texto(474, 640, "la frontera", AMBAR, 12.5, peso="600"))
    p.append(texto(474, 660, "de la VM", AMBAR, 12.5))
    p.append(flecha(528, 648, 558, 648, SUAVE, 2))

    p.append(caja(566, 600, 300, 96, PANEL, VIOLETA))
    p.append(texto(716, 630, "la VM de Linux", VIOLETA, 14, peso="600"))
    p.append(texto(716, 654, "la que Docker Desktop", SUAVE, 11.5))
    p.append(texto(716, 672, "enciende sin decírtelo", SUAVE, 11.5))

    p.append(flecha(872, 648, 920, 648, SUAVE, 2))
    p.append(caja(928, 600, 300, 96, PANEL, ACENTO))
    p.append(texto(1078, 630, "el contenedor", ACENTO, 14, peso="600"))
    p.append(texto(1078, 654, "que cree estar leyendo", SUAVE, 11.5))
    p.append(texto(1078, 672, "un disco normal", SUAVE, 11.5))

    p.append(texto(650, 730, "Cada lectura y cada escritura del bind mount cruzan ese puente: por eso ahí es más lento que en Linux nativo,", SUAVE, 13.5))
    p.append(texto(650, 752, "y por eso los permisos los inventa el filesystem compartido en vez de salir de tu disco.", SUAVE, 13.5))
    p.append(texto(650, 794, "En Linux no hay puente: el bind mount es el mismo inodo del mismo kernel, y por eso ahí el dueño del archivo sí es una pregunta con respuesta.", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/14 · De quien queda el archivo, en cuatro plataformas
# --------------------------------------------------------------------------

def cont_uid_plataformas():
    """Cuatro plataformas, cuatro resultados — y la frontera que explica cada uno."""
    ancho, alto = 1340, 830
    aria = (
        "Cuatro plataformas en cuatro paneles y, en cada uno, de quien queda "
        "el archivo que el contenedor acaba de escribir en el bind mount. "
        "Linux nativo con Docker: queda de root, porque Docker no activa user "
        "namespaces y el uid 0 de adentro es el uid 0 de afuera. Linux con "
        "Podman rootless: queda de tu usuario, porque el uid 0 se mapea al "
        "tuyo y solo ese. WSL2 en una ruta ext4 de tu carpeta personal: queda "
        "de root, igual que en Linux, porque es Linux de verdad. Y macOS con "
        "Docker Desktop o Windows con una ruta del disco de Windows: queda de "
        "tu usuario, porque el filesystem compartido de la maquina virtual "
        "inventa la propiedad. Cada panel dibuja la frontera que explica su "
        "resultado, y al pie van las salidas: --user en Docker con su "
        "asterisco, y --userns=keep-id o el sufijo dos puntos U del volumen en "
        "Podman"
    )
    paneles = (
        (ROJO, "Linux nativo", "Docker", "no hay user namespace",
         ("Docker no lo activa por omisión.",
          "El uid 0 de adentro es el uid 0",
          "de afuera: el mismo número, el",
          "mismo kernel, el mismo inodo."),
         ("-rw-r--r-- 1 root root", "app/salida.txt"),
         "queda de root", "y no lo borras sin sudo"),
        (ACENTO, "Linux", "Podman rootless", "user namespace, con tu mapeo",
         ("El uid 0 de adentro se mapea a TU",
          "uid. Sólo ése: el 1000 de adentro",
          "cae en tu rango de /etc/subuid,",
          "que no es ningún usuario real."),
         ("-rw-r--r-- 1 tu tu", "app/salida.txt"),
         "queda tuyo", "sin sudo en ningún momento"),
        (ROJO, "WSL2", "ruta ext4, en tu home de Linux", "es Linux de verdad",
         ("Mismo kernel, mismo ext4, mismas",
          "reglas: se comporta igual que el",
          "primer panel. Guardar el proyecto",
          "en /mnt/c es otra historia."),
         ("-rw-r--r-- 1 root root", "app/salida.txt"),
         "queda de root", "es el caso 1, con otro nombre"),
        (ACENTO, "macOS o Windows", "ruta del disco de Windows o de macOS",
         "el filesystem compartido lo inventa",
         ("El bind mount cruza a la VM por un",
          "puente que traduce la propiedad:",
          "te devuelve tu uid pase lo que",
          "pase adentro. No lo negocia nadie."),
         ("-rw-r--r-- 1 tu staff", "app/salida.txt"),
         "queda tuyo", "no porque esté bien: nadie lo mide"),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "De quién queda el archivo que escribe el contenedor", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "el mismo bind mount y el mismo proceso, en cuatro plataformas — y cuatro resultados, no dos", SUAVE, 14))

    for i, (color, plataforma, runtime, frontera, explica, archivo,
            resultado, matiz) in enumerate(paneles):
        x = 40 + i * 320
        cx = x + 152
        p.append(caja(x, 110, 305, 486, PANEL, color))
        p.append(texto(cx, 142, plataforma, TEXTO, 16, peso="600"))
        p.append(texto(cx, 164, runtime, SUAVE, 12))
        p.append(linea(x + 18, 178, x + 287, 178, LINEA, 1))

        p.append(caja(x + 24, 194, 257, 62, TINTE, LINEA, radio=8, grosor=1.5))
        p.append(texto(cx, 218, "el proceso del contenedor", SUAVE, 11.5))
        p.append(teclado(cx, 242, "uid 0  (root adentro)", TEXTO, 12.5))
        p.append(flecha(cx, 258, cx, 288, SUAVE, 2))

        p.append(caja_punteada(x + 16, 292, 273, 122, color, radio=10, grosor=2))
        p.append(texto(cx, 314, frontera, color, 12.5, peso="600"))
        for k, renglon in enumerate(explica):
            p.append(texto(cx, 338 + k * 18, renglon, SUAVE, 10.5))
        p.append(flecha(cx, 416, cx, 446, SUAVE, 2))

        p.append(caja(x + 24, 450, 257, 66, FONDO, LINEA, radio=8, grosor=1.5))
        p.append(teclado(cx, 476, archivo[0], color, 11.5, peso="normal"))
        p.append(teclado(cx, 496, archivo[1], SUAVE, 11.5, peso="normal"))

        p.append(texto(cx, 550, resultado, color, 19, peso="600"))
        p.append(texto(cx, 576, matiz, SUAVE, 11))

    # Las salidas.
    p.append(texto(670, 638, "las salidas, cuando el resultado no te sirve", TEXTO, 16, peso="600"))
    p.append(caja(40, 656, 630, 128, PANEL, CIAN))
    p.append(texto(60, 686, "en Docker", CIAN, 14.5, anclaje="start", peso="600"))
    p.append(teclado(180, 686, "docker run --user $(id -u):$(id -g) …", TEXTO, 13, anclaje="start"))
    p.append(texto(468, 682, "*", ROJO, 18, anclaje="start", peso="600"))
    p.append(parrafo(60, 714, (
        "* el proceso deja de ser root DENTRO también: si la imagen esperaba escribir",
        "en /app o instalar un paquete al arrancar, se rompe. Y ese uid no existe en el",
        "/etc/passwd de la imagen, así que algunas herramientas se quejan del usuario.",
    ), SUAVE, 11.5, 20))

    p.append(caja(690, 656, 630, 128, PANEL, ACENTO))
    p.append(texto(710, 686, "en Podman", ACENTO, 14.5, anclaje="start", peso="600"))
    p.append(teclado(830, 686, "--userns=keep-id", TEXTO, 13, anclaje="start"))
    p.append(teclado(985, 686, "o bien", SUAVE, 12, anclaje="start", peso="normal"))
    p.append(teclado(1040, 686, "-v ./app:/app:U", TEXTO, 13, anclaje="start"))
    p.append(parrafo(710, 714, (
        "keep-id mapea tu uid al mismo número adentro, y ya no hay traducción que",
        "sorprenda. El sufijo :U es otra cosa: hace un chown recursivo del origen al uid",
        "mapeado — cámbiale el dueño a tu directorio de verdad, así que mídelo antes.",
    ), SUAVE, 11.5, 20))

    p.append(texto(670, 812, "No son dos casos con excepciones: son cuatro respuestas distintas, y cuál te toca depende de dónde corre el kernel y de quién inventa la propiedad.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/15 · La matriz de ocho casos
# --------------------------------------------------------------------------

def cont_matriz_volumen():
    """Tres decisiones binarias, ocho hojas, dos preguntas por hoja."""
    ancho, alto = 1400, 830
    aria = (
        "La matriz de ocho casos del laboratorio, dibujada como un arbol de "
        "tres decisiones binarias: el codigo dentro de la imagen o montado por "
        "volumen, la edicion hecha en el host o dentro del contenedor, y con "
        "docker build de por medio o sin el. Cada una de las ocho hojas dice "
        "si el cambio se ve al correr y si sobrevive a un docker rm. Las "
        "cuatro hojas de la rama del volumen van resaltadas y agrupadas bajo "
        "la conclusion que cierra la pagina: con volumen, editar fuera y ver "
        "dentro no necesita ningun rebuild"
    )
    hojas = (
        (False, False, True, "El rebuild mete tu cambio en una capa nueva.",
         "Hay que reconstruir Y volver a correr: dos pasos."),
        (False, False, False, "La imagen sigue siendo la de antes: el contenedor corre",
         "el código viejo. Tu edición existe, pero sólo en tu disco."),
        (False, True, False, "El build lee el contexto del host, no la capa de escritura:",
         "tu edición de adentro no entra nunca a la imagen nueva."),
        (False, True, False, "Se ve ya, en ese contenedor. Vive en la capa de escritura,",
         "y docker rm se la lleva entera sin preguntar."),
        (True, False, True, "Se ve al instante — y el build sobró: el volumen tapa",
         "lo que la imagen traiga en ese path, sea nuevo o viejo."),
        (True, False, True, "La que usas todo el día: guardas el archivo y ya está.",
         "Ni rebuild, ni reinicio, ni docker nada."),
        (True, True, True, "Escribir en /app es escribir en tu disco. El build, otra",
         "vez, no cambió nada que se llegue a ver."),
        (True, True, True, "Escribes en el bind mount: el archivo cambia en tu carpeta",
         "del host, con el dueño que diga tu plataforma."),
    )
    ve = (True, False, False, True, True, True, True, True)
    sobrevive = (True, True, False, False, True, True, True, True)
    centros = [155 + i * 70 for i in range(8)]

    p = [marco(ancho, alto, aria)]
    p.append(texto(700, 42, "Los ocho casos, como tres decisiones", TEXTO, 21, peso="600"))
    p.append(texto(700, 68, "predice antes de ejecutar: el árbol da las ocho respuestas sin correr nada", SUAVE, 14))
    p.append(texto(1240, 94, "¿se ve", SUAVE, 11.5, peso="600"))
    p.append(texto(1240, 110, "al correr?", SUAVE, 11.5, peso="600"))
    p.append(texto(1332, 94, "¿sobrevive", SUAVE, 11.5, peso="600"))
    p.append(texto(1332, 110, "a docker rm?", SUAVE, 11.5, peso="600"))

    # La raiz.
    p.append(caja(50, 369, 170, 62, PANEL, LINEA))
    p.append(texto(135, 396, "cambias una línea", TEXTO, 13, peso="600"))
    p.append(texto(135, 416, "de app.py", SUAVE, 12))

    # Nivel 1: donde vive el codigo.
    p.append(linea(220, 400, 240, 400, LINEA, 2))
    p.append(linea(240, 260, 240, 540, LINEA, 2))
    nivel1 = ((260, VIOLETA, "en la IMAGEN", "el Dockerfile hace COPY . ."),
              (540, CIAN, "por VOLUMEN", "-v \"$(pwd)\":/app"))
    for cy, color, titulo, glosa in nivel1:
        p.append(linea(240, cy, 258, cy, LINEA, 2))
        p.append(caja(262, cy - 34, 190, 68, PANEL, color))
        p.append(texto(357, cy - 4, titulo, color, 14, peso="600"))
        p.append(teclado(357, cy + 18, glosa, SUAVE, 10.5, peso="normal"))

    # Nivel 2: donde editas.
    nivel2 = ((260, 190, 330), (540, 470, 610))
    for cy, a, b in nivel2:
        p.append(linea(452, cy, 470, cy, LINEA, 2))
        p.append(linea(470, a, 470, b, LINEA, 2))
    for cy, etiqueta in ((190, "editas en el HOST"), (330, "editas DENTRO"),
                         (470, "editas en el HOST"), (610, "editas DENTRO")):
        p.append(linea(470, cy, 488, cy, LINEA, 2))
        p.append(caja(492, cy - 26, 172, 52, PANEL, LINEA, grosor=1.5))
        p.append(texto(578, cy + 5, etiqueta, TEXTO, 12.5, peso="600"))

    # Nivel 3: con build o sin build, y las hojas.
    for k, cy in enumerate((190, 330, 470, 610)):
        p.append(linea(664, cy, 682, cy, LINEA, 2))
        p.append(linea(682, centros[2 * k], 682, centros[2 * k + 1], LINEA, 2))
    for i, cy in enumerate(centros):
        volumen, adentro, _ = hojas[i][0], hojas[i][1], None
        p.append(linea(682, cy, 700, cy, LINEA, 2))
        p.append(chip(750, cy, "con build" if i % 2 == 0 else "sin build",
                      AMBAR if i % 2 == 0 else SUAVE, tam=12))
        p.append(flecha(806, cy, 830, cy, SUAVE, 1.8))

        color = ACENTO if volumen else LINEA
        p.append(caja(836, cy - 29, 524, 58, TINTE if volumen else PANEL,
                      color, radio=8, grosor=2 if volumen else 1.5))
        p.append(texto(852, cy - 4, hojas[i][3], TEXTO, 11.5, anclaje="start"))
        p.append(texto(852, cy + 15, hojas[i][4], SUAVE, 11.5, anclaje="start"))
        for cxm, bandera in ((1240, ve[i]), (1332, sobrevive[i])):
            if bandera:
                p.append(palomita(cxm, cy, 9, ACENTO, 3))
            else:
                p.append(cruz(cxm, cy, 9, ROJO, 3))

    p.append(linea(1376, 406, 1376, 674, ACENTO, 3))
    p.append(caja(40, 700, 1320, 62, TINTE, ACENTO, grosor=2.5))
    p.append(texto(700, 727, "Con volumen, editar fuera y ver dentro no necesita ningún rebuild: las cuatro hojas de esa rama se ven y sobreviven.", ACENTO, 15, peso="600"))
    p.append(texto(700, 750, "En la rama de la imagen, en cambio, la respuesta cambia en cada hoja — y eso es exactamente lo que se practica.", SUAVE, 12.5))

    p.append(texto(700, 800, "La segunda columna no pregunta si el archivo existe: pregunta dónde vive. Un cambio en la capa de escritura se ve igual de bien… hasta el docker rm.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/16 · Tapar contra copiar
# --------------------------------------------------------------------------

def _contenido_imagen(x, y, w, entradas, color=VIOLETA, apagado=False):
    """Lo que la imagen trae en ese path, como una lista de binarios."""
    p = [caja(x, y, w, 140, PANEL, SUAVE if apagado else color, radio=8,
              grosor=1.5 if apagado else 2)]
    p.append(texto(x + w / 2, y + 26, "lo que la imagen trae en /bin",
                   SUAVE if apagado else color, 12.5, peso="600"))
    for i, entrada in enumerate(entradas):
        ey = y + 52 + i * 21
        p.append(teclado(x + 24, ey, entrada, SUAVE if apagado else TEXTO, 12,
                         anclaje="start", peso="normal"))
        if apagado:
            p.append(tachado(x + 22, ey - 4, x + 24 + 9 * len(entrada), SUAVE, 1.5))
    return "".join(p)


def cont_tapar():
    """Un bind mount siempre tapa; un named volume vacio copia. Lado a lado."""
    ancho, alto = 1340, 880
    aria = (
        "La diferencia que medio internet cuenta al reves, en dos casos sobre "
        "el mismo path de una imagen que ya traia archivos. Arriba, un bind "
        "mount de un directorio vacio sobre barra bin: siempre tapa, no copia "
        "nada nunca, ni en Docker ni en Podman, y el dibujo deja lo de la "
        "imagen abajo, intacto e inalcanzable, con ls desaparecido y el error "
        "command not found. Abajo, un named volume vacio, que hace lo "
        "contrario: la primera vez que se monta copia al volumen lo que la "
        "imagen tenia en ese path, con la flecha de copia dibujada "
        "explicitamente, y si el volumen ya trae algo entonces si tapa, como "
        "el bind mount. Al margen, la opcion que apaga la copia —nocopy con -v "
        "y volume-nocopy con --mount— y la consecuencia que explica el "
        "laboratorio de Postgres"
    )
    binarios = ("ls", "cat", "sh", "bash")
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "Tapar y copiar no son lo mismo", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "el mismo path, la misma imagen, dos montajes — y resultados opuestos", SUAVE, 14))

    # -- caso 1: el bind mount siempre tapa --------------------------------
    p.append(caja(40, 100, 940, 330, "none", CIAN))
    p.append(texto(60, 132, "1 · un bind mount de un directorio vacío, sobre /bin", CIAN, 16, anclaje="start", peso="600"))
    p.append(_contenido_imagen(60, 156, 250, binarios))
    p.append(flecha(318, 226, 372, 226, SUAVE, 2))
    p.append(caja(378, 156, 250, 140, PANEL, CIAN, radio=8))
    p.append(texto(503, 182, "lo que montas", CIAN, 12.5, peso="600"))
    p.append(teclado(503, 216, "-v ./vacio:/bin", CIAN, 14))
    p.append(texto(503, 248, "un directorio de tu disco,", SUAVE, 11.5))
    p.append(texto(503, 268, "y está vacío", SUAVE, 11.5))
    p.append(flecha(634, 226, 696, 226, ROJO, 2.5))

    p.append(caja(702, 156, 270, 246, PANEL, ROJO))
    p.append(texto(837, 182, "lo que ves en /bin adentro", ROJO, 12.5, peso="600"))
    p.append(texto(837, 216, "(nada)", SUAVE, 16))
    p.append(linea(722, 240, 952, 240, LINEA, 1, "5 5"))
    p.append(texto(837, 260, "debajo del montaje, intacto", SUAVE, 10.5))
    p.append(texto(837, 276, "e inalcanzable:", SUAVE, 10.5))
    for i_b, entrada in enumerate(binarios):
        ey = 300 + i_b * 19
        p.append(teclado(800, ey, entrada, SUAVE, 11.5, anclaje="start", peso="normal"))
        p.append(tachado(798, ey - 4, 802 + 9 * len(entrada), SUAVE, 1.5))
    p.append(teclado(837, 388, "bash: ls: command not found", ROJO, 12))

    p.append(caja(60, 320, 568, 88, PANEL, ROJO))
    p.append(texto(344, 352, "SIEMPRE tapa", ROJO, 18, peso="600"))
    p.append(texto(344, 378, "El bind mount no copia nada, nunca: ni en Docker ni en Podman.", SUAVE, 12.5))
    p.append(texto(344, 398, "Lo de la imagen sigue ahí abajo, intacto, y nadie lo alcanza.", SUAVE, 12.5))

    # -- caso 2: el named volume vacio copia -------------------------------
    p.append(caja(40, 450, 940, 360, "none", AMBAR))
    p.append(texto(60, 482, "2 · un named volume VACÍO, sobre ese mismo /bin", AMBAR, 16, anclaje="start", peso="600"))
    p.append(_contenido_imagen(60, 506, 250, binarios))
    p.append(texto(345, 556, "COPIA", AMBAR, 13.5, peso="600"))
    p.append(flecha(318, 576, 372, 576, AMBAR, 3))
    p.append(caja(378, 506, 250, 140, PANEL, AMBAR, radio=8))
    p.append(texto(503, 532, "lo que montas", AMBAR, 12.5, peso="600"))
    p.append(teclado(503, 566, "-v midata:/bin", AMBAR, 14))
    p.append(texto(503, 598, "un volumen nuevo,", SUAVE, 11.5))
    p.append(texto(503, 618, "y vacío", SUAVE, 11.5))
    p.append(flecha(634, 576, 696, 576, ACENTO, 2.5))

    p.append(caja(702, 506, 270, 190, PANEL, ACENTO))
    p.append(texto(837, 532, "lo que ves en /bin adentro", ACENTO, 12.5, peso="600"))
    for i_b, entrada in enumerate(binarios):
        p.append(teclado(800, 560 + i_b * 21, entrada, ACENTO, 12, anclaje="start", peso="normal"))
    p.append(linea(722, 646, 952, 646, LINEA, 1, "5 5"))
    p.append(texto(837, 666, "y midata ahora los guarda:", SUAVE, 10.5))
    p.append(texto(837, 684, "sobreviven al docker rm", SUAVE, 10.5))

    p.append(caja(60, 662, 568, 74, PANEL, AMBAR))
    p.append(texto(344, 694, "COPIA la primera vez que se monta", AMBAR, 17, peso="600"))
    p.append(texto(344, 720, "Docker copia al volumen lo que la imagen traía en ese path.", SUAVE, 12.5))

    p.append(caja(60, 748, 912, 50, PANEL, ROJO))
    p.append(texto(516, 779, "¿Y si el volumen YA trae algo? Entonces tapa, igual que el bind mount: la copia ocurre una sola vez.", ROJO, 13.5, peso="600"))

    # -- el margen ---------------------------------------------------------
    p.append(caja(1000, 100, 300, 330, PANEL, VIOLETA))
    p.append(texto(1150, 132, "cómo se apaga la copia", VIOLETA, 14.5, peso="600"))
    p.append(teclado(1020, 172, "-v midata:/bin:nocopy", TEXTO, 12, anclaje="start", peso="normal"))
    p.append(texto(1020, 196, "con la sintaxis corta", SUAVE, 11, anclaje="start"))
    p.append(teclado(1020, 234, "--mount type=volume,", TEXTO, 12, anclaje="start", peso="normal"))
    p.append(teclado(1036, 254, "volume-nocopy=true,…", TEXTO, 12, anclaje="start", peso="normal"))
    p.append(texto(1020, 278, "con la sintaxis larga", SUAVE, 11, anclaje="start"))
    p.append(linea(1020, 298, 1280, 298, LINEA, 1))
    p.append(parrafo(1020, 324, (
        "Son la misma opción con dos",
        "nombres. Sin ella, copiar ES el",
        "comportamiento por omisión del",
        "named volume — no una rareza.",
    ), SUAVE, 11.5, 19))

    p.append(caja(1000, 450, 300, 360, PANEL, CIAN))
    p.append(texto(1150, 482, "y por eso el laboratorio", CIAN, 14.5, peso="600"))
    p.append(texto(1150, 502, "de Postgres funciona", CIAN, 14.5, peso="600"))
    p.append(parrafo(1020, 538, (
        "postgres:16 trae vacío su",
        "/var/lib/postgresql/data y lo",
        "inicializa al arrancar.",
        "",
        "El named volume nuevo se lleva",
        "esa inicialización, y el",
        "contenedor siguiente la",
        "encuentra hecha.",
        "",
        "Con un bind mount a un directorio",
        "vacío saldría igual —pero por",
        "otra razón: porque la imagen",
        "también traía ese path vacío.",
    ), SUAVE, 11.5, 19))

    p.append(texto(670, 840, "La regla no es «el volumen copia y el bind mount no»: es que el bind mount NUNCA copia, y el named volume copia UNA vez, y sólo si está vacío.", SUAVE, 13.5))
    p.append(texto(670, 864, "Medio internet lo cuenta al revés. Compruébalo con ls, no con un blog.", SUAVE, 13))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/7 · El estado que sobrevive a su contenedor
# --------------------------------------------------------------------------

def _tabla_pg(x, y, w, apagada=False):
    """La tabla con su fila recien insertada, dentro del volumen."""
    color = SUAVE if apagada else ACENTO
    p = [teclado(x + w / 2, y, "id │ nombre", SUAVE, 11.5, peso="normal"),
         linea(x + 24, y + 8, x + w - 24, y + 8, LINEA, 1),
         teclado(x + w / 2, y + 28, "1  │ ada", color, 12.5)]
    if apagada:
        p.append(tachado(x + 40, y + 24, x + w - 40, ROJO, 2))
    return "".join(p)


def cont_estado_postgres():
    """Cuatro tiempos: el dato sobrevive al contenedor y muere con el volumen."""
    ancho, alto = 1340, 750
    aria = (
        "Cuatro tiempos de la misma linea, de izquierda a derecha. Primero, un "
        "contenedor postgres:16 con un named volume llamado pgdata montado en "
        "/var/lib/postgresql/data y una tabla con su fila recien insertada. "
        "Despues, el contenedor destruido con docker rm -f y el volumen "
        "quedando solo en el dibujo, con los datos adentro. Luego, un "
        "contenedor nuevo montando el mismo volumen y leyendo la misma fila, "
        "sin inicializar nada. Y al final, docker volume rm pgdata, donde los "
        "datos si mueren. Un recuadro marca dos decisiones de la pagina: aqui "
        "no se publica puerto, se entra con docker exec, y el volumen es named "
        "y no bind mount por los permisos del uid 999 y por la portabilidad"
    )
    tiempos = (
        (ACENTO, "1 · corriendo, con su volumen",
         "-v pgdata:/var/lib/postgresql/data", "postgres:16", "el contenedor pg",
         False, False,
         ("INSERT y COMMIT. La fila no vive",
          "en el contenedor: vive en el",
          "volumen, que es otra cosa.")),
        (ROJO, "2 · se destruye el contenedor",
         "docker rm -f pg", "postgres:16", "el contenedor pg",
         True, False,
         ("Se va su capa de escritura y se",
          "va su nombre. El volumen sigue",
          "entero, con la fila adentro.")),
        (ACENTO, "3 · otro contenedor, mismo volumen",
         "docker run --name pg2 -v pgdata:…", "postgres:16", "el contenedor pg2",
         False, False,
         ("SELECT devuelve la misma fila.",
          "Postgres no inicializó nada: el",
          "volumen ya venía inicializado.")),
        (ROJO, "4 · y aquí sí mueren los datos",
         "docker volume rm pgdata", "", "(ya no hay contenedor)",
         True, True,
         ("Es el único de los cuatro",
          "comandos que se lleva el dato.",
          "Y no hay deshacer.")),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "El estado sobrevive a su contenedor", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "cuatro tiempos de la misma línea, con un named volume de por medio", SUAVE, 14))

    for i, (color, titulo, cmd, imagen, etiqueta, muerto, volumen_muerto,
            glosa) in enumerate(tiempos):
        x = 40 + i * 326
        cx = x + 143
        p.append(caja(x, 128, 286, 412, PANEL, color))
        p.append(texto(cx, 158, titulo, color, 13.5, peso="600"))
        p.append(teclado(cx, 182, cmd, SUAVE, 10.5, peso="normal"))

        if muerto and volumen_muerto:
            p.append(caja_punteada(x + 22, 200, 242, 78, SUAVE, radio=8))
            p.append(texto(cx, 244, etiqueta, SUAVE, 12))
        elif muerto:
            p.append(caja_punteada(x + 22, 200, 242, 78, SUAVE, radio=8))
            p.append(teclado(cx, 232, imagen, SUAVE, 13, peso="normal"))
            p.append(texto(cx, 254, etiqueta, SUAVE, 11))
            p.append(tachado(x + 42, 228, x + 244, ROJO, 2.5))
            p.append(cruz(x + 250, 214, 10, ROJO, 3))
        else:
            p.append(caja(x + 22, 200, 242, 78, TINTE, ACENTO, radio=8))
            p.append(teclado(cx, 232, imagen, ACENTO, 14))
            p.append(texto(cx, 254, etiqueta, SUAVE, 11))

        if not muerto:
            p.append(flecha_punteada(cx, 282, cx, 314, ACENTO, 2))
            p.append(texto(cx + 14, 304, "monta", SUAVE, 10.5, anclaje="start"))

        borde = ROJO if volumen_muerto else AMBAR
        p.append(caja(x + 22, 320, 242, 132, PANEL, borde))
        p.append(teclado(cx, 348, "pgdata", borde, 15))
        p.append(texto(cx, 368, "named volume", SUAVE, 10.5))
        p.append(_tabla_pg(x + 22, 398, 242, volumen_muerto))
        if volumen_muerto:
            p.append(cruz(x + 250, 334, 10, ROJO, 3))

        for k, renglon in enumerate(glosa):
            p.append(texto(cx, 480 + k * 19, renglon, SUAVE, 11.5))

        if i:
            p.append(flecha(x - 34, 334, x - 6, 334, SUAVE, 2))

    p.append(caja(40, 572, 630, 122, PANEL, CIAN))
    p.append(texto(60, 602, "aquí no se publica ningún puerto", CIAN, 14.5, anclaje="start", peso="600"))
    p.append(teclado(60, 630, "docker exec -it pg psql -U postgres", TEXTO, 12.5, anclaje="start", peso="normal"))
    p.append(parrafo(60, 654, (
        "Un -p 5432:5432 pondría Postgres en tu red local sin que nadie lo",
        "necesite. Entrar por exec es entrar por la puerta que ya existe.",
    ), SUAVE, 12))

    p.append(caja(690, 572, 630, 122, PANEL, AMBAR))
    p.append(texto(710, 602, "y el volumen es named, no bind mount", AMBAR, 14.5, anclaje="start", peso="600"))
    p.append(parrafo(710, 630, (
        "Postgres corre como el uid 999, y un bind mount a tu carpeta le negaría",
        "el permiso de escribir en su propio directorio de datos. El named volume",
        "además es el mismo comando en Linux, en macOS y en Windows.",
    ), SUAVE, 12))

    p.append(texto(670, 726, "Un contenedor es desechable porque el dato no vive en él. Cuál de los dos borras no es un detalle: es la diferencia entre rehacer y perder.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/8 · Qué se lleva exactamente cada prune
# --------------------------------------------------------------------------

def _monton(x, y, w, h, bloques, color):
    """Un monton del disco: bloques apilados dentro de su recuadro."""
    p = [caja(x, y, w, h, FONDO, color, radio=8, grosor=1.5)]
    for i in range(bloques):
        p.append(relleno(x + 14, y + h - 14 - (i + 1) * 17, w - 28, 13, color))
    return "".join(p)


def cont_prune():
    """Una brocha por comando: exactamente que monton se lleva cada uno."""
    ancho, alto = 1360, 800
    aria = (
        "El mismo disco dibujado como cuatro montones: las imagenes, partidas "
        "en las que tienen un contenedor corriendo y las que no usa nadie; los "
        "contenedores detenidos; las capas huerfanas; y los volumenes sin "
        "dueno. Debajo, una brocha por comando marca exactamente que se lleva "
        "cada uno: docker container prune solo los contenedores detenidos, "
        "docker image prune las capas huerfanas, docker image prune -a ademas "
        "las imagenes que nadie usa, y docker system prune -a todo lo "
        "anterior. Resaltado en rojo, el aviso de que los volumenes no entran "
        "en ninguno y se piden aparte: docker volume prune y docker system "
        "prune --volumes solo borran los anonimos, y los que tienen nombre "
        "piden docker volume prune -a. Arriba a la izquierda, docker system df "
        "como el comando que mide antes de borrar, con sus columnas TYPE, SIZE "
        "y RECLAIMABLE. Abajo a la derecha, que una imagen con un contenedor "
        "corriendo no es candidata para ningun prune, y que si el contenedor "
        "esta detenido image prune -a la respeta pero system prune -a borra "
        "primero el contenedor y despues se la lleva"
    )
    montones = (
        (ACENTO, 4, "2.1 GB", "con un contenedor", "corriendo"),
        (VIOLETA, 6, "4.8 GB", "que nadie usa", "—"),
        (CIAN, 3, "380 MB", "contenedores", "detenidos"),
        (AMBAR, 4, "1.9 GB", "capas huérfanas", "(dangling)"),
        (ROJO, 4, "3.4 GB", "volúmenes", "sin dueño"),
    )
    comandos = (
        ("docker container prune", (2,), CIAN),
        ("docker image prune", (3,), AMBAR),
        ("docker image prune -a", (1, 3), VIOLETA),
        ("docker system prune -a", (1, 2, 3), TEXTO),
    )
    col = [270 + i * 212 for i in range(5)]

    p = [marco(ancho, alto, aria)]
    p.append(texto(680, 42, "Qué se lleva exactamente cada prune", TEXTO, 21, peso="600"))
    p.append(texto(680, 68, "cuatro montones en el disco, y una brocha por comando", SUAVE, 14))

    # Mide antes de borrar.
    p.append(caja(40, 150, 210, 170, PANEL, CIAN))
    p.append(texto(145, 178, "mide antes de borrar", CIAN, 13, peso="600"))
    p.append(teclado(145, 204, "docker system df", TEXTO, 12.5))
    p.append(linea(58, 218, 232, 218, LINEA, 1))
    for i, (tipo, tam, libre) in enumerate((("TYPE", "SIZE", "RECLAIMABLE"),
                                            ("Images", "8.8G", "6.7G"),
                                            ("Containers", "380M", "380M"),
                                            ("Local Volumes", "3.4G", "3.4G"))):
        y = 240 + i * 22
        color = SUAVE if i == 0 else TEXTO
        p.append(teclado(52, y, tipo, color, 10, anclaje="start", peso="normal"))
        p.append(teclado(166, y, tam, color, 10, anclaje="end", peso="normal"))
        p.append(teclado(240, y, libre, color, 10, anclaje="end", peso="normal"))

    # Los montones.
    p.append(linea(270, 136, 674, 136, VIOLETA, 1.5))
    p.append(linea(270, 136, 270, 148, VIOLETA, 1.5))
    p.append(linea(674, 136, 674, 148, VIOLETA, 1.5))
    p.append(texto(472, 128, "imágenes", VIOLETA, 13, peso="600"))
    for i, (color, bloques, tam, n1, n2) in enumerate(montones):
        x = col[i]
        p.append(_monton(x, 152, 192, 118, bloques, color))
        p.append(teclado(x + 96, 292, tam, color, 14))
        p.append(texto(x + 96, 314, n1, TEXTO, 12, peso="600"))
        p.append(texto(x + 96, 332, n2, SUAVE, 11))

    # Una brocha por comando.
    for k, (cmd, alcanza, color) in enumerate(comandos):
        y = 356 + k * 60
        p.append(teclado(40, y + 28, cmd, color, 13, anclaje="start"))
        p.append(linea(40, y + 44, 1310, y + 44, LINEA, 1))
        for i in range(5):
            if i in alcanza:
                p.append(relleno(col[i] + 6, y + 6, 180, 30, color, radio=15))
                p.append(texto(col[i] + 96, y + 26, "se lo lleva", FONDO, 12.5, peso="600"))
            else:
                p.append(texto(col[i] + 96, y + 26, "—", SUAVE, 13))
    p.append(texto(40, 618, "sin el -a, docker system prune se salta las imágenes que nadie usa: de ese lado sólo se lleva las capas huérfanas.", SUAVE, 12.5, anclaje="start"))

    p.append(caja(40, 640, 640, 122, PANEL, ROJO))
    p.append(texto(60, 670, "los volúmenes NO entran en ninguno de los cuatro", ROJO, 14.5, anclaje="start", peso="600"))
    p.append(teclado(60, 696, "docker volume prune · system prune --volumes", TEXTO, 12, anclaje="start", peso="normal"))
    p.append(texto(660, 696, "sólo los anónimos", AMBAR, 12, anclaje="end", peso="600"))
    p.append(teclado(60, 720, "docker volume prune -a", TEXTO, 12, anclaje="start", peso="normal"))
    p.append(texto(660, 720, "también los que tienen nombre", ROJO, 12, anclaje="end", peso="600"))
    p.append(texto(60, 746, "Se piden aparte, a propósito: aquí borrar es perder un dato, no rehacer un build.", SUAVE, 12, anclaje="start"))

    p.append(caja(700, 640, 620, 122, PANEL, ACENTO))
    p.append(texto(720, 670, "y nada de esto toca lo que está en uso", ACENTO, 14.5, anclaje="start", peso="600"))
    p.append(parrafo(720, 698, (
        "Una imagen con un contenedor corriendo no es candidata para ningún prune.",
        "Si el contenedor está detenido, image prune -a la respeta, pero system",
        "prune -a borra primero el contenedor y después se la lleva.",
    ), SUAVE, 12))

    p.append(texto(680, 786, "Cada montón tiene su columna, y docker system df te dice antes cuánto vas a recuperar.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 3/1 · La red y el nombre
# --------------------------------------------------------------------------

def cont_red_y_pod():
    """La misma pareja de contenedores, en tres redes distintas."""
    ancho, alto = 1360, 720
    aria = (
        "Tres escenarios con la misma pareja de contenedores, un servicio web y una "
        "base. En la red bridge por omision se alcanzan por IP pero no hay "
        "resolucion por nombre, y el intento por nombre aparece tachado. En "
        "una red creada por ti se alcanzan por nombre, y la IP va tachada "
        "porque cambia en cada arranque. En un pod de Podman comparten "
        "localhost y se hablan por puerto, sin nombre de por medio. Alrededor "
        "de los tres, la linea del host, con la unica flecha que la atraviesa "
        "rotulada -p 5432:5432 y etiquetada como lo que es: superficie "
        "expuesta y decision de diseno"
    )
    escenarios = (
        (ROJO, "la red bridge por omisión", "docker run  (sin --network)",
         "psql -h 172.17.0.3", "por IP sí llega",
         "psql -h db", "could not translate host name",
         ("No hay DNS en la bridge por omisión.",
          "Y esa IP cambia en cada arranque.")),
        (ACENTO, "una red creada por ti", "docker network create datos",
         "psql -h db", "por nombre: hay DNS embebido",
         "psql -h 172.18.0.3", "funciona hoy, falla mañana",
         ("El DNS resuelve el nombre del contenedor.",
          "La IP es justo lo que no debes escribir.")),
        (CIAN, "un pod de Podman", "podman pod create --name app",
         "psql -h localhost -p 5432", "mismo netns: se hablan por puerto",
         "psql -h db", "no hay ningún nombre que resolver",
         ("Comparten el network namespace, como",
          "dos procesos de la misma máquina.")),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(680, 42, "Que dos contenedores se hablen", TEXTO, 21, peso="600"))
    p.append(texto(680, 68, "tres redes, y sólo en una de ellas el nombre significa algo", SUAVE, 14))

    p.append(caja_punteada(40, 168, 1280, 448, SUAVE, radio=14, grosor=2))
    p.append(texto(66, 194, "el host", SUAVE, 13.5, anclaje="start", peso="600"))

    for i, (color, titulo, cmd, bueno, glosa_b, malo, glosa_m, nota) in enumerate(escenarios):
        x = 70 + i * 386
        cx = x + 175
        p.append(caja(x, 212, 350, 384, PANEL, color))
        p.append(texto(cx, 244, titulo, color, 15, peso="600"))
        p.append(teclado(cx, 266, cmd, SUAVE, 10.5, peso="normal"))

        p.append(caja(x + 20, 292, 130, 66, TINTE, ACENTO, radio=8))
        p.append(teclado(x + 85, 322, "api", ACENTO, 14))
        p.append(texto(x + 85, 342, "sin estado", SUAVE, 10))
        p.append(caja(x + 200, 292, 130, 66, TINTE, AMBAR, radio=8))
        p.append(teclado(x + 265, 322, "db", AMBAR, 14))
        p.append(texto(x + 265, 342, "postgres:16", SUAVE, 10))
        p.append(flecha(x + 156, 325, x + 194, 325, color, 2))

        p.append(palomita(x + 34, 392, 8, ACENTO, 2.5))
        p.append(texto(x + 52, 397, "así sí se hablan", ACENTO, 12, anclaje="start", peso="600"))
        p.append(teclado(x + 24, 424, bueno, TEXTO, 12, anclaje="start", peso="normal"))
        p.append(texto(x + 24, 446, glosa_b, SUAVE, 11, anclaje="start"))

        p.append(cruz(x + 34, 480, 8, ROJO, 2.5))
        p.append(texto(x + 52, 485, "y así no", ROJO, 12, anclaje="start", peso="600"))
        p.append(teclado(x + 24, 512, malo, SUAVE, 12, anclaje="start", peso="normal"))
        p.append(tachado(x + 22, 508, x + 26 + 7.3 * len(malo), ROJO, 2))
        p.append(texto(x + 24, 534, glosa_m, ROJO, 11, anclaje="start"))

        for k, renglon in enumerate(nota):
            p.append(texto(cx, 562 + k * 17, renglon, SUAVE, 10.5))

    # La unica flecha que cruza la linea del host.
    p.append(texto(1250, 122, "desde tu máquina", SUAVE, 12))
    p.append(linea(1250, 130, 1250, 154, AMBAR, 2.5))
    p.append(chip(1250, 168, "-p 5432:5432", AMBAR, tam=12.5))
    p.append(linea(1250, 182, 1250, 325, AMBAR, 2.5))
    p.append(flecha(1250, 325, 1178, 325, AMBAR, 2.5))
    p.append(texto(1250, 372, "la única flecha", AMBAR, 11.5, peso="600"))
    p.append(texto(1250, 390, "que cruza la línea", AMBAR, 11.5, peso="600"))
    p.append(texto(1250, 416, "superficie expuesta,", SUAVE, 11))
    p.append(texto(1250, 434, "y decisión de diseño", SUAVE, 11))

    p.append(texto(680, 660, "Publicar un puerto no es «conectar»: los tres escenarios ya conectan el servicio con la base sin publicar nada.", SUAVE, 13.5))
    p.append(texto(680, 684, "Un -p abre la base al resto de tu red local, y eso se decide a propósito o no se decide.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 3/2 · El contrato de un servicio
# --------------------------------------------------------------------------

def cont_contrato():
    """Puerto, variables y volumen: lo que un servicio promete por escrito."""
    ancho, alto = 1340, 800
    aria = (
        "Tres cajas colgando de un mismo contenedor, etiquetadas el puerto que "
        "escucha, las variables de entorno que espera y el volumen que "
        "necesita, y a la derecha, por cada una, lo que le permite a quien lo "
        "consume: por donde hablarle, como configurarlo sin reconstruir la "
        "imagen, y que sobrevive a un docker rm. Debajo, el mismo servicio con "
        "las tres cajas en blanco y la etiqueta monolito repartido, que es lo "
        "que queda cuando el contrato no esta escrito, y una linea que separa "
        "el servicio con estado del servicio sin estado, con el aviso de que "
        "partir cuesta red, despliegue y depuracion"
    )
    clausulas = (
        (CIAN, "el puerto que escucha", ("8000/tcp",),
         "por dónde hablarle",
         ("Desde la misma red: http://api:8000 — sin saber su IP,",
          "sin publicar nada y sin que a nadie le importe dónde corre.")),
        (AMBAR, "las variables que espera", ("DB_URL", "LOG_LEVEL"),
         "cómo configurarlo sin reconstruir",
         ("La misma imagen en desarrollo y en producción: lo que cambia",
          "es el entorno, no el artefacto. Sin rebuild de por medio.")),
        (VIOLETA, "el volumen que necesita", ("/data",),
         "qué sobrevive a un docker rm",
         ("Lo que está en /data, y sólo eso. Todo lo demás que el",
          "proceso escriba se va con la capa de escritura.")),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(670, 42, "El contrato de un servicio", TEXTO, 21, peso="600"))
    p.append(texto(670, 68, "tres cosas escritas, y lo que cada una le permite a quien lo consume", SUAVE, 14))

    p.append(caja(50, 150, 220, 316, PANEL, ACENTO, grosor=2.5))
    p.append(texto(160, 186, "un servicio", ACENTO, 16, peso="600"))
    p.append(teclado(160, 214, "mi-api:v1", TEXTO, 15))
    p.append(parrafo(72, 250, (
        "Lo que promete es",
        "exactamente esto, y",
        "nada más. Lo que no",
        "está escrito no es",
        "parte del trato.",
    ), SUAVE, 12, 20))
    p.append(texto(160, 400, "y las tres cosas", SUAVE, 12))
    p.append(texto(160, 420, "caben en un README", SUAVE, 12))
    p.append(texto(160, 446, "de diez líneas", SUAVE, 12))

    for k, (color, titulo, valores, permite, renglones) in enumerate(clausulas):
        y = 150 + k * 108
        p.append(flecha(274, y + 42, 316, y + 42, color, 2))
        p.append(caja(322, y, 260, 84, PANEL, color))
        p.append(texto(452, y + 28, titulo, color, 13, peso="600"))
        p.append(teclado(452, y + 58, "   ".join(valores), TEXTO, 13.5))
        p.append(flecha(586, y + 42, 628, y + 42, SUAVE, 2))
        p.append(caja(634, y, 656, 84, PANEL, LINEA, grosor=1.5))
        p.append(texto(652, y + 26, permite, color, 13, anclaje="start", peso="600"))
        for i, renglon in enumerate(renglones):
            p.append(texto(652, y + 48 + i * 18, renglon, SUAVE, 11.5, anclaje="start"))

    # Sin contrato escrito.
    p.append(caja(50, 500, 600, 228, PANEL, ROJO))
    p.append(texto(350, 532, "el mismo servicio, sin contrato escrito", ROJO, 15, peso="600"))
    p.append(caja(76, 558, 160, 140, PANEL, SUAVE, grosor=1.5))
    p.append(texto(156, 600, "un servicio", SUAVE, 13, peso="600"))
    p.append(teclado(156, 626, "mi-api:v1", SUAVE, 13, peso="normal"))
    p.append(texto(156, 656, "el mismo de arriba", SUAVE, 10.5))
    for k in range(3):
        y = 562 + k * 46
        p.append(flecha(240, y + 18, 272, y + 18, SUAVE, 1.6))
        p.append(caja_punteada(278, y, 200, 36, SUAVE, radio=8))
    p.append(chip(378, 706, "monolito repartido", ROJO, tam=13))
    p.append(parrafo(496, 578, (
        "Quien lo consume",
        "tiene que leer tu",
        "código para saber",
        "por dónde entrarle,",
        "y cualquier cambio",
        "tuyo lo rompe sin",
        "avisar a nadie.",
    ), SUAVE, 11.5, 18))

    # Con estado y sin estado.
    p.append(caja(670, 500, 620, 228, PANEL, AMBAR))
    p.append(texto(980, 532, "y la línea que sí importa al partir", AMBAR, 15, peso="600"))
    p.append(linea(980, 556, 980, 692, AMBAR, 1.5, "6 6"))
    p.append(texto(824, 582, "servicio SIN estado", ACENTO, 13, peso="600"))
    p.append(parrafo(700, 606, (
        "Desechable y replicable.",
        "Lo matas y lo repones",
        "sin pensarlo: partirlo",
        "cuesta poco.",
    ), SUAVE, 11.5, 18))
    p.append(texto(1136, 582, "servicio CON estado", VIOLETA, 13, peso="600"))
    p.append(parrafo(1000, 606, (
        "Uno solo, con su volumen.",
        "Partirlo cuesta red,",
        "despliegue y depuración",
        "— y casi nunca se parte.",
    ), SUAVE, 11.5, 18))

    p.append(texto(670, 762, "Un microservicio no es «un servicio chico»: es un servicio cuyo contrato cabe en tres líneas y no obliga a nadie a leer su código.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 3/3 · El pipeline de la unidad 2, repartido en servicios
# --------------------------------------------------------------------------

def cont_pipeline_servicios():
    """Cinco servicios en una red propia, y la unica flecha que cruza al host."""
    ancho, alto = 1360, 780
    aria = (
        "El pipeline de la unidad 2 repartido en servicios dentro de una red "
        "propia: extraccion, transformacion y carga como tres contenedores sin "
        "estado, la base de datos con su named volume como el unico que guarda "
        "algo, y el tablero que la lee. Cada flecha lleva rotulado el contrato "
        "por el que pasa —nombre y puerto, o variable de entorno— y solo una "
        "cruza la linea del host, la del tablero, porque la base no publica "
        "puerto. Al margen, por que la base casi nunca se parte, y que "
        "sobrevive a un docker rm de cada pieza"
    )
    servicios = (
        (90, ACENTO, "extracción", "descarga el crudo", "sin estado"),
        (280, ACENTO, "transformación", "limpia y normaliza", "sin estado"),
        (470, ACENTO, "carga", "escribe en la base", "sin estado"),
        (660, AMBAR, "db", "postgres:16", "el único con estado"),
        (850, CIAN, "tablero", "streamlit", "sin estado"),
    )
    contratos = (
        (260, VIOLETA, "RAW_DIR", "variable de entorno"),
        (455, VIOLETA, "CLEAN_DIR", "variable de entorno"),
        (645, AMBAR, "db:5432", "nombre y puerto"),
        (835, AMBAR, "db:5432", "nombre y puerto"),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(680, 42, "El pipeline de la unidad 2, repartido en servicios", TEXTO, 21, peso="600"))
    p.append(texto(680, 68, "cada flecha es un contrato, y sólo una cruza la línea del host", SUAVE, 14))

    p.append(caja_punteada(60, 170, 970, 330, ACENTO, radio=14, grosor=2))
    p.append(teclado(80, 196, "docker network create pipeline", ACENTO, 12.5, anclaje="start", peso="normal"))

    for cx, color, etiqueta, glosa in contratos:
        p.append(chip(cx, 226, etiqueta, color, tam=12))
        p.append(texto(cx, 250, glosa, SUAVE, 10))

    for i, (x, color, nombre, glosa, estado) in enumerate(servicios):
        p.append(caja(x, 266, 150, 110, PANEL, color))
        p.append(texto(x + 75, 300, nombre, color, 14.5, peso="600"))
        p.append(texto(x + 75, 322, glosa, SUAVE, 11))
        p.append(texto(x + 75, 350, estado, TEXTO if color is AMBAR else SUAVE,
                       10.5, peso="600" if color is AMBAR else "normal"))
        if i:
            p.append(flecha(x - 34, 321, x - 6, 321, contratos[i - 1][1], 2))

    p.append(flecha(735, 376, 735, 404, AMBAR, 2.5))
    p.append(caja(660, 410, 150, 62, PANEL, AMBAR))
    p.append(teclado(735, 438, "pgdata", AMBAR, 14))
    p.append(texto(735, 458, "named volume", SUAVE, 10.5))
    p.append(texto(640, 434, "el único que guarda algo", AMBAR, 12, anclaje="end", peso="600"))
    p.append(texto(640, 454, "de todo el dibujo", SUAVE, 11, anclaje="end"))

    # La linea del host, y la unica flecha que la cruza.
    p.append(linea(40, 536, 1330, 536, SUAVE, 2, "9 7"))
    p.append(texto(60, 560, "la línea del host", SUAVE, 13, anclaje="start", peso="600"))
    p.append(linea(925, 376, 925, 522, CIAN, 2.5))
    p.append(chip(925, 536, "-p 8501:8501", CIAN, tam=12.5))
    p.append(flecha(925, 550, 925, 598, CIAN, 2.5))
    p.append(caja(820, 602, 210, 66, PANEL, CIAN))
    p.append(texto(925, 630, "tu navegador", CIAN, 13.5, peso="600"))
    p.append(texto(925, 652, "la única pieza que se publica", SUAVE, 10.5))
    p.append(texto(1046, 630, "la base no publica puerto:", AMBAR, 12, anclaje="start", peso="600"))
    p.append(texto(1046, 650, "sólo el tablero la alcanza,", SUAVE, 11, anclaje="start"))
    p.append(texto(1046, 668, "y por nombre", SUAVE, 11, anclaje="start"))

    p.append(caja(1050, 170, 280, 150, PANEL, VIOLETA))
    p.append(texto(1190, 200, "por qué la base", VIOLETA, 14, peso="600"))
    p.append(texto(1190, 220, "casi nunca se parte", VIOLETA, 14, peso="600"))
    p.append(parrafo(1068, 248, (
        "Partir un servicio con",
        "estado obliga a repartir",
        "el dato, y eso cuesta",
        "más que lo que compra.",
    ), SUAVE, 11.5, 18))

    p.append(caja(1050, 340, 280, 160, PANEL, ACENTO))
    p.append(texto(1190, 370, "qué sobrevive a", ACENTO, 14, peso="600"))
    p.append(texto(1190, 390, "un docker rm", ACENTO, 14, peso="600"))
    p.append(parrafo(1068, 418, (
        "De las cinco piezas: sólo",
        "lo que hay en pgdata.",
        "Las otras cuatro se",
        "reponen con un run, y por",
        "eso pueden morir.",
    ), SUAVE, 11.5, 17))

    p.append(texto(680, 718, "Dibujar los contratos antes de escribir el código es lo que convierte «lo parto en servicios» en una decisión que se puede discutir.", SUAVE, 13.5))
    p.append(texto(680, 742, "Si una flecha no se puede rotular, esa pieza todavía no es un servicio.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 3/4 · Por dónde se sale
# --------------------------------------------------------------------------

def _brecha(x, y, w, h):
    """Borra un tramo del borde de un anillo: la brecha que abre una bandera."""
    return relleno(x, y, w, h, FONDO, radio=0)


def cont_superficie_ataque():
    """Las cuatro capas por omision, y las cuatro decisiones que las abren."""
    ancho, alto = 1400, 870
    aria = (
        "El contenedor rodeado de sus capas de defensa por omision —seccomp, "
        "AppArmor o SELinux, capabilities recortadas y usuario no root— y, "
        "atravesandolas, las decisiones que abren un agujero en cada una, "
        "dibujadas como brechas rotuladas: --privileged, que abre las cuatro "
        "de un golpe, --security-opt seccomp=unconfined, --cap-add SYS_ADMIN, "
        "y el socket de Docker montado, que no es un exploit sino entregar el "
        "host. Dos casos marcados sostienen la tesis: CVE-2022-0492 "
        "funcionaba sin privilegios y aun asi la configuracion por defecto lo "
        "tapaba, y Dirty Pipe atraviesa todas las capas porque usa splice y "
        "write, que todo contenedor necesita"
    )
    anillos = (
        (200, 240, 560, 400, ROJO, 268, 220, 740,
         "seccomp", "el perfil por omisión bloquea unas 44 syscalls"),
        (246, 286, 468, 308, VIOLETA, 314, 266, 694,
         "AppArmor / SELinux", "qué del filesystem puede tocar"),
        (292, 332, 376, 216, AMBAR, 360, 312, 648,
         "capabilities recortadas", "le quedan unas 14 de las 38"),
        (338, 378, 284, 124, CIAN, 404, 358, 602,
         "usuario no root", "si la imagen trae USER"),
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(700, 42, "Por dónde se sale de un contenedor", TEXTO, 21, peso="600"))
    p.append(texto(700, 68, "un mapa de decisiones mal tomadas: casi ninguna fuga real fue un bug del kernel", SUAVE, 14))

    p.append(caja(200, 720, 560, 56, TINTE, ACENTO, grosor=2.5))
    p.append(texto(480, 754, "el kernel del host — uno solo, el mismo para todos", TEXTO, 13.5, peso="600"))

    for x, y, w, h, color, ty, tx_izq, tx_der, nombre, glosa in anillos:
        p.append(caja(x, y, w, h, "none", color, radio=24, grosor=2.5))
        p.append(texto(tx_izq, ty, nombre, color, 12.5, anclaje="start", peso="600"))
        p.append(texto(tx_der, ty, glosa, SUAVE, 10.5, anclaje="end"))

    p.append(caja(384, 416, 192, 48, TINTE, ACENTO, radio=10, grosor=2.5))
    p.append(texto(480, 446, "tu proceso, adentro", ACENTO, 13, peso="600"))

    # Brecha 1: --privileged abre las cuatro de un golpe.
    for bx in (338, 292, 246, 200):
        p.append(_brecha(bx - 5, 422, 10, 36))
    p.append(flecha(380, 440, 152, 440, ROJO, 3))
    p.append(teclado(40, 416, "--privileged", ROJO, 14, anclaje="start"))
    p.append(parrafo(40, 474, (
        "Abre las cuatro a la vez:",
        "es correr como si no",
        "hubiera contenedor.",
        "No es «un poco menos",
        "seguro»: es ninguna capa.",
    ), SUAVE, 11, 18))

    # Brecha 2: --cap-add SYS_ADMIN abre solo el anillo de capabilities.
    p.append(_brecha(320, 543, 120, 10))
    p.append(linea(380, 548, 380, 562, ROJO, 2))
    p.append(teclado(380, 578, "--cap-add SYS_ADMIN", ROJO, 12.5))

    # Brecha 3: seccomp=unconfined abre solo el anillo de fuera.
    p.append(_brecha(645, 635, 110, 10))
    p.append(linea(700, 640, 700, 654, ROJO, 2))
    p.append(teclado(700, 670, "--security-opt seccomp=unconfined", ROJO, 11.5))
    p.append(texto(586, 690, "y las otras tres siguen en pie:", SUAVE, 10.5, anclaje="start"))
    p.append(texto(586, 706, "una brecha abre su capa, no el host", SUAVE, 10.5, anclaje="start"))

    # Brecha 4: el socket montado no rompe ninguna capa. Las rodea.
    p.append(flecha_punteada(580, 440, 892, 440, ROJO, 2.5, "7 6"))
    p.append(chip(825, 440, "el socket", ROJO, tam=12))
    p.append(texto(825, 414, "montado por ti", ROJO, 11, peso="600"))

    # Dirty Pipe atraviesa las cuatro sin abrir ninguna.
    p.append(flecha(500, 470, 500, 700, VIOLETA, 3))
    p.append(chip(500, 676, "Dirty Pipe", VIOLETA, tam=12))

    # CVE-2022-0492 no llego: la configuracion por omision lo tapo.
    p.append(flecha(478, 410, 478, 262, AMBAR, 2.5))
    p.append(cruz(478, 242, 11, ROJO, 3))
    p.append(chip(478, 212, "CVE-2022-0492", AMBAR, tam=12))

    p.append(caja(900, 150, 440, 190, PANEL, AMBAR))
    p.append(texto(922, 182, "CVE-2022-0492", AMBAR, 15, anclaje="start", peso="600"))
    p.append(parrafo(922, 212, (
        "Funcionaba SIN privilegios: bastaba un user",
        "namespace no privilegiado para llegar al",
        "release_agent de cgroup v1.",
        "",
        "Y aun así, la configuración por omisión lo",
        "tapaba. Quien lo sufrió había apagado algo.",
    ), SUAVE, 11.5, 20))

    p.append(caja(900, 360, 440, 190, PANEL, ROJO))
    p.append(texto(922, 392, "el socket de Docker montado", ROJO, 15, anclaje="start", peso="600"))
    p.append(teclado(922, 418, "-v /var/run/docker.sock:/var/run/…", TEXTO, 11.5, anclaje="start", peso="normal"))
    p.append(parrafo(922, 444, (
        "No rompe ninguna de las cuatro capas: las",
        "rodea. Quien habla con ese socket le pide al",
        "daemon —que es root— que monte / y corra",
        "otro contenedor con --privileged.",
        "No es un exploit: es entregar el host.",
    ), SUAVE, 11.5, 19))

    p.append(caja(900, 570, 440, 190, PANEL, VIOLETA))
    p.append(texto(922, 602, "Dirty Pipe (CVE-2022-0847)", VIOLETA, 15, anclaje="start", peso="600"))
    p.append(parrafo(922, 632, (
        "Atraviesa las cuatro capas sin abrir ninguna,",
        "porque usa splice() y write(): dos syscalls",
        "que todo contenedor necesita y que ningún",
        "perfil razonable puede prohibir.",
        "",
        "Contra esto no hay bandera: hay parchar el kernel.",
    ), SUAVE, 11.5, 19))

    p.append(texto(700, 812, "Las capas por omisión son buenas: el catálogo de fugas reales está lleno de configuraciones apagadas a mano, no de bugs del kernel.", SUAVE, 13.5))
    p.append(texto(700, 836, "Y cuando sí es un bug del kernel, ninguna de las cuatro ayuda — porque el kernel es uno solo y es el mismo para todos.", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/1 · Repaso: Dockerfile, imagen, contenedor
# --------------------------------------------------------------------------

def _ficha(x, y, w, nombre, que_es, rasgo, color, filas):
    """Una de las tres cosas: nombre, que es, y tres preguntas con respuesta."""
    alto = 300
    p = [caja(x, y, w, alto, PANEL, color, grosor=2.5)]
    p.append(teclado(x + w / 2, y + 38, nombre, color, 21))
    p.append(texto(x + w / 2, y + 66, que_es, TEXTO, 13.5))
    p.append(texto(x + w / 2, y + 88, rasgo, color, 13, peso="600"))
    p.append(linea(x + 20, y + 106, x + w - 20, y + 106, LINEA, 1))
    for i, (pregunta, respuesta) in enumerate(filas):
        fy = y + 134 + i * 56
        p.append(texto(x + 24, fy, pregunta, SUAVE, 11.5, anclaje="start"))
        p.append(teclado(x + 24, fy + 22, respuesta, TEXTO, 13.5,
                         anclaje="start", peso="normal"))
    return "".join(p)


def cont_repaso_triada():
    """Las tres cosas, el comando que lleva de una a otra y lo que no regresa."""
    ancho, alto = 1240, 720
    aria = (
        "Tres cajas en fila. Dockerfile: la receta, texto en tu carpeta; lo "
        "cambia tu editor, lo ves con cat y lo borra rm. Una flecha docker "
        "build lleva a la imagen: capas de solo lectura, inmutable; no "
        "cambia, otro docker build hace otra imagen; se lista con docker images y se borra "
        "con docker rmi. Una flecha docker run lleva al contenedor: un proceso "
        "mas su capa de escritura, efimero; lo cambia el proceso o docker "
        "exec, se lista con docker ps -a y se borra con docker rm. Del "
        "contenedor regresa a la imagen una flecha punteada, docker commit, "
        "que existe y no se usa, y al Dockerfile una flecha tachada: nunca "
        "desde su capa de escritura: solo un bind mount escribe en tu carpeta. "
        "Colgando del contenedor, dos cajas externas, bind mount (tu carpeta) "
        "y named volume (area de Docker), que no pasan por la imagen"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(620, 42, "Dockerfile → imagen → contenedor", TEXTO, 21, peso="600"))
    p.append(texto(620, 68, "tres cosas distintas: cada una cambia con su propia herramienta", SUAVE, 14))

    y, w = 96, 300
    xs = (40, 470, 900)
    p.append(_ficha(xs[0], y, w, "Dockerfile", "la receta", "texto en tu carpeta", CIAN, (
        ("lo cambia", "tu editor"),
        ("lo ves con", "cat Dockerfile"),
        ("lo borra", "rm Dockerfile"),
    )))
    p.append(_ficha(xs[1], y, w, "imagen", "capas de sólo lectura", "inmutable", VIOLETA, (
        ("no cambia:", "otro build hace otra"),
        ("la ves con", "docker images"),
        ("la borra", "docker rmi"),
    )))
    p.append(_ficha(xs[2], y, w, "contenedor", "un proceso + su capa de escritura", "efímero", ACENTO, (
        ("lo cambia", "el proceso · docker exec"),
        ("lo ves con", "docker ps -a"),
        ("lo borra", "docker rm"),
    )))

    # Hacia adelante: los dos comandos que si se usan.
    for x_de, etiqueta in ((xs[0] + w, "docker build"), (xs[1] + w, "docker run")):
        p.append(teclado(x_de + 65, 176, etiqueta, ACENTO, 13.5))
        p.append(flecha(x_de + 6, 192, x_de + 124, 192, ACENTO, 2.5))

    # Hacia atras, a la imagen: existe, no se usa.
    p.append(teclado(835, 296, "docker commit", AMBAR, 12.5))
    p.append(flecha_punteada(894, 312, 776, 312, AMBAR, 2))
    p.append(texto(835, 334, "existe, no se usa", AMBAR, 11.5))

    # Hacia atras, al Dockerfile: nunca.
    p.append(linea(930, 396, 930, 440, ROJO, 2, "6 6"))
    p.append(linea(930, 440, 190, 440, ROJO, 2, "6 6"))
    p.append(flecha_punteada(190, 440, 190, 402, ROJO, 2))
    p.append(caja(482, 427, 256, 26, FONDO, FONDO, radio=6, grosor=0))
    p.append(cruz(504, 440, 9, ROJO, 3))
    p.append(texto(524, 445, "nunca desde su capa", ROJO, 13, anclaje="start", peso="600"))
    p.append(texto(560, 470, "sólo un bind mount escribe en tu carpeta", SUAVE, 11.5))

    # Colgando del contenedor: los dos montajes.
    for cx, color, nombre, glosa in ((985, CIAN, "bind mount", "tu carpeta"),
                                     (1135, AMBAR, "named volume", "área de Docker")):
        p.append(linea(cx, 396, cx, 492, color, 2, "5 5"))
        p.append(caja(cx - 68, 492, 136, 62, PANEL, color))
        p.append(texto(cx, 518, nombre, color, 13.5, peso="600"))
        p.append(texto(cx, 540, glosa, SUAVE, 11.5))
    p.append(texto(1060, 582, "no pasan por la imagen", AMBAR, 13, peso="600"))
    p.append(texto(1060, 600, "ni build ni rm los tocan", SUAVE, 11.5))

    p.append(texto(620, 650, "Cada flecha es un comando: si no lo corriste, la caja de la derecha no se enteró.", SUAVE, 14))
    p.append(texto(620, 676, "Las flechas que se usan van hacia la derecha: lo que pasa adentro no regresa solo a la imagen ni al Dockerfile.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# 2/5 y 2/6 · Los dos laboratorios de «¿que cambia que?»
# --------------------------------------------------------------------------

PREDICE = "Predice cada celda antes de correrla; las respuestas están en la tabla del final"


def _celda_pregunta(cx, cy):
    """Una casilla por llenar: el alumno escribe ahi su prediccion."""
    return (caja_punteada(cx - 26, cy - 20, 52, 40, SUAVE, radio=8, grosor=1.5,
                          guion="5 5")
            + texto(cx, cy + 7, "?", AMBAR, 20, peso="600"))


def _matriz_predecir(aria, titulo, columnas, filas, ancho=880):
    """Filas = lo que haces; columnas = tres preguntas; cada celda, un «?».

    La matriz va arriba de la pagina, antes de cada «Predice»: no lleva
    respuestas a proposito. Las respuestas viven en la tabla del final.

    filas = [(color, accion, comando)]
    """
    alto_fila, y0 = 64, 150
    alto = y0 + alto_fila * len(filas) + 34
    xs = (490, 630, 770)
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 42, titulo, TEXTO, 21, peso="600"))
    p.append(texto(ancho / 2, 68, PREDICE, SUAVE, 14))

    p.append(texto(64, 124, "lo que haces", SUAVE, 12.5, anclaje="start", peso="600"))
    for cx, (arriba, abajo) in zip(xs, columnas):
        p.append(texto(cx, 112, arriba, SUAVE, 12, peso="600"))
        p.append(texto(cx, 130, abajo, SUAVE, 12, peso="600"))
    p.append(linea(40, 140, ancho - 40, 140, LINEA, 1.5))

    for k, (color, accion, comando) in enumerate(filas):
        y = y0 + k * alto_fila
        cy = y + alto_fila / 2 - 3
        if k % 2 == 0:
            p.append(relleno(40, y, ancho - 80, alto_fila - 6, PANEL, radio=8))
        p.append(relleno(46, y + 12, 7, alto_fila - 30, color, radio=3))
        p.append(texto(64, cy - 4, accion, TEXTO, 14, anclaje="start", peso="600"))
        p.append(teclado(64, cy + 17, comando, color, 12.5, anclaje="start", peso="normal"))
        for cx in xs:
            p.append(_celda_pregunta(cx, cy))
    p.append(cierre())
    return "".join(p)


def cont_lab_sin_volumen():
    """Ocho cosas que puedes hacer sin volumen, para predecir antes de correr."""
    aria = (
        "Matriz para predecir, sin respuestas, del laboratorio sin volumen. "
        "Ocho filas, lo que haces: editar app.py en el host sin build, "
        "editarlo en el host y hacer docker build, editar el Dockerfile sin "
        "build, editar adentro con docker exec, editar adentro y luego stop y "
        "start, editar adentro y luego docker rm, editar adentro y luego "
        "docker build, y editar adentro y luego docker commit. Tres columnas: "
        "si lo ve el contenedor que ya corria, si lo ve un contenedor nuevo de "
        "la imagen y si cambio la imagen. Cada celda lleva un signo de "
        "interrogacion: se predice antes de correrla, y las respuestas estan "
        "en la tabla del final de la pagina"
    )
    host, dentro = CIAN, ACENTO
    filas = (
        (host, "editas app.py en el host", "sin build"),
        (host, "editas app.py en el host", "+ docker build"),
        (host, "editas el Dockerfile", "sin build"),
        (dentro, "editas app.py adentro", "docker exec"),
        (dentro, "editas adentro y reinicias", "docker stop · docker start"),
        (dentro, "editas adentro y borras", "docker rm"),
        (dentro, "editas adentro y reconstruyes", "docker build"),
        (dentro, "editas adentro y congelas", "docker commit"),
    )
    return _matriz_predecir(
        aria,
        "Sin volumen: ¿qué cambia qué?",
        (("¿lo ve el que", "ya corría?"), ("¿lo ve uno nuevo", "de la imagen?"),
         ("¿cambió", "la imagen?")),
        filas,
    )


def cont_lab_con_volumen():
    """Ocho casos con montaje, para predecir antes de correr."""
    aria = (
        "Matriz para predecir, sin respuestas, del laboratorio con volumen. "
        "Ocho filas: bind mount editando en el host, bind mount editando "
        "adentro, bind mount editando adentro y luego docker build, bind "
        "mount mas rebuild corriendo con el montaje, bind mount de solo lectura escribiendo adentro, "
        "named volume sobre barra app la primera vez, named volume sobre barra "
        "app tras un rebuild con codigo nuevo, y named volume de datos tras "
        "docker rm. Tres columnas: si se ve adentro, si cambia tu disco y si "
        "cambia la imagen. Cada celda lleva un signo de interrogacion: se "
        "predice antes de correrla, y las respuestas estan en la tabla del "
        "final de la pagina"
    )
    bind, named = CIAN, AMBAR
    filas = (
        (bind, "bind mount: editas en el host", "-v \"$PWD\":/app"),
        (bind, "bind mount: editas adentro", "docker exec"),
        (bind, "bind mount: editas adentro + build", "docker exec · docker build"),
        (bind, "bind mount + rebuild, con montaje", "docker build · docker run -v"),
        (bind, "bind mount :ro, escribes adentro", "-v \"$PWD\":/app:ro"),
        (named, "named volume en /app, 1.ª vez", "-v codigo:/app"),
        (named, "named volume en /app, tras rebuild", "docker build + run"),
        (named, "volumen de datos, tras docker rm", "-v datos:/datos"),
    )
    return _matriz_predecir(
        aria,
        "Con volumen: ¿qué cambia qué?",
        (("¿se ve", "adentro?"), ("¿cambia", "tu disco?"), ("¿cambia", "la imagen?")),
        filas,
    )


DIAGRAMAS_CONCEPTUALES = {
    "cont-intermodal": cont_intermodal,
    "cont-ns-cgroups": cont_ns_cgroups,
    "cont-tres-abstracciones": cont_tres_abstracciones,
    "cont-anatomia-run": cont_anatomia_run,
    "cont-escalamiento": cont_escalamiento,
    "cont-vm-vs-contenedor": cont_vm_vs_contenedor,
    "cont-espectro": cont_espectro,
    "cont-docker-vs-podman": cont_docker_vs_podman,
    "cont-capas-cache": cont_capas_cache,
    "cont-sin-sudo": cont_sin_sudo,
    "cont-planes-b": cont_planes_b,
    "cont-registro": cont_registro,
    "cont-ciclo-de-vida": cont_ciclo_de_vida,
    "cont-build-contexto": cont_build_contexto,
    "cont-dockerfile-roto": cont_dockerfile_roto,
    "cont-overlay-volumen": cont_overlay_volumen,
    "cont-rutas": cont_rutas,
    "cont-uid-plataformas": cont_uid_plataformas,
    "cont-matriz-volumen": cont_matriz_volumen,
    "cont-tapar": cont_tapar,
    "cont-estado-postgres": cont_estado_postgres,
    "cont-prune": cont_prune,
    "cont-red-y-pod": cont_red_y_pod,
    "cont-contrato": cont_contrato,
    "cont-pipeline-servicios": cont_pipeline_servicios,
    "cont-superficie-ataque": cont_superficie_ataque,
    "cont-repaso-triada": cont_repaso_triada,
    "cont-lab-sin-volumen": cont_lab_sin_volumen,
    "cont-lab-con-volumen": cont_lab_con_volumen,
}

# Las cinco graficas de benchmark viven en su propio modulo porque dibujan un
# CSV y no una idea. El catalogo se fusiona aqui para que quien importe
# DIAGRAMAS vea todas las figuras de la unidad.
DIAGRAMAS = {**DIAGRAMAS_CONCEPTUALES, **DIAGRAMAS_BENCH}


def escribir(nombre):
    ASSETS.mkdir(parents=True, exist_ok=True)
    destino = ASSETS / f"{nombre}.svg"
    destino.write_text(DIAGRAMAS[nombre](), encoding="utf-8")
    return destino


def main(argv):
    nombres = argv[1:] or list(DIAGRAMAS)
    for nombre in nombres:
        if nombre not in DIAGRAMAS:
            raise SystemExit(f"diagrama desconocido: {nombre}")
        destino = escribir(nombre)
        print(f"{destino.name}  ({destino.stat().st_size / 1000:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv)
