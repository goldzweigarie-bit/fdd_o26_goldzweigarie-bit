"""Genera los diagramas SVG de la unidad 9 (Python), seccion de ambientes.

Las primitivas y la paleta salen de tools/svg_base.py: un solo lugar declara
los colores de skins/fdd-eva.yaml.

Este archivo es la unica fuente de verdad de esos SVG. Editar un .svg a mano es
un error que tools/test_gen_python.py detecta.

Los ids llevan prefijo "py-" a proposito: los ids de objeto numerado de Raya
son unicos en TODO el curso, no por pagina.
"""
import sys
from pathlib import Path

from svg_base import (
    ACENTO, AMBAR, CIAN, FONDO, LINEA, PANEL, ROJO, SUAVE, TEXTO, TINTE,
    VIOLETA, caja, chip, cierre, flecha, marco, teclado, texto,
)

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/9_python/_assets"


def _punteada(x, y, w, h, color=SUAVE):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-dasharray="8 6"/>')


def py_mapa():
    """Que produce que en un proyecto uv, y que va a git."""
    ancho, alto = 1080, 560
    aria = (
        "Tres cajas en fila. La primera, lo que pides: pyproject.toml, con "
        "rangos como rich mayor o igual a 15, que escribes tu o uv add. Una "
        "flecha rotulada uv lock lleva a la segunda, lo que se resolvio: "
        "uv.lock, con version exacta y hash de cada paquete, tambien las "
        "transitivas, que se bajan de PyPI. Una flecha rotulada uv sync lleva a "
        "la tercera, lo que esta instalado: la carpeta .venv con su python y "
        "su site-packages, desechable. De .venv sale una flecha uv run hacia tu "
        "programa, y uv python install pone el interprete. Abajo: "
        "pyproject.toml y uv.lock van a git; .venv no va a git, se borra y se "
        "recrea con uv sync"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué produce qué en un proyecto uv", TEXTO, 21, peso="600"))

    # PyPI, arriba de la caja del lock.
    p.append(caja(440, 70, 200, 40, PANEL, VIOLETA, radio=8))
    p.append(teclado(540, 96, "PyPI", VIOLETA, 16))
    p.append(flecha(540, 112, 540, 136, VIOLETA, 2))
    p.append(texto(700, 96, "de dónde se bajan", SUAVE, 13, anclaje="start"))

    cajas = (
        (40, AMBAR, "lo que pides", "pyproject.toml", "rangos: rich>=15", "lo escribes tú o uv add"),
        (400, CIAN, "lo que se resolvió", "uv.lock", "versión exacta + hash", "de cada paquete, también las transitivas"),
        (760, ACENTO, "lo que está instalado", ".venv/", "bin/python + site-packages/", "desechable"),
    )
    for x, color, titulo, archivo, linea1, linea2 in cajas:
        p.append(caja(x, 140, 280, 150, PANEL, color))
        p.append(texto(x + 140, 170, titulo, color, 15, peso="600"))
        p.append(teclado(x + 140, 206, archivo, color, 19))
        p.append(texto(x + 140, 240, linea1, TEXTO, 13.5))
        p.append(texto(x + 140, 264, linea2, SUAVE, 12.5))

    p.append(flecha(324, 215, 394, 215, CIAN, 2.5))
    p.append(chip(359, 190, "uv lock", CIAN, tam=13))
    p.append(flecha(684, 215, 754, 215, ACENTO, 2.5))
    p.append(chip(719, 190, "uv sync", ACENTO, tam=13))

    # Tu entrada: uv add escribe el toml (y de paso lock + sync).
    p.append(caja(110, 360, 140, 44, FONDO, AMBAR, radio=8))
    p.append(texto(180, 388, "tú", AMBAR, 15, peso="600"))
    p.append(flecha(180, 356, 180, 296, AMBAR, 2.5))
    p.append(chip(268, 330, "uv add rich", AMBAR, tam=13))

    # El interprete tambien lo pone uv.
    p.append(caja(400, 360, 280, 44, FONDO, SUAVE, radio=8))
    p.append(teclado(540, 387, "uv python install", SUAVE, 14))
    p.append(texto(540, 424, "el intérprete también lo pone uv", SUAVE, 12.5))
    p.append(flecha(684, 382, 790, 296, SUAVE, 1.8))

    # Correr.
    p.append(flecha(900, 296, 900, 356, ACENTO, 2.5))
    p.append(chip(800, 326, "uv run hola.py", ACENTO, tam=13))
    p.append(caja(820, 360, 160, 44, FONDO, ACENTO, radio=8))
    p.append(texto(900, 388, "tu programa", ACENTO, 15, peso="600"))

    # Que va a git.
    p.append(caja(40, 462, 1000, 70, TINTE, LINEA, radio=10))
    p.append(texto(60, 492, "a git:", TEXTO, 15, anclaje="start", peso="600"))
    p.append(teclado(130, 492, "✓ pyproject.toml   ✓ uv.lock", ACENTO, 15, anclaje="start"))
    p.append(teclado(470, 492, "✗ .venv/", ROJO, 15, anclaje="start"))
    p.append(texto(560, 492, "no va a git: se borra y se recrea con uv sync", ROJO, 14, anclaje="start"))
    p.append(texto(60, 518, "Los dos archivos bastan para que otra máquina tenga exactamente tus versiones.", SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_choque():
    """Dos proyectos, un solo site-packages: el ultimo que instala gana."""
    ancho, alto = 1080, 400
    aria = (
        "Dos columnas. A la izquierda, sin ambientes: proyecto-a pide pandas "
        "1.5 y proyecto-b pide pandas 2.2, y los dos apuntan al unico "
        "site-packages del Python del sistema, donde solo cabe una version, la "
        "2.2; la flecha de proyecto-a termina en rojo porque esperaba 1.5. A la "
        "derecha, con un .venv por proyecto: cada proyecto tiene su propio "
        "site-packages con su version, y las dos flechas terminan en verde"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Dos proyectos, un solo Python", TEXTO, 21, peso="600"))
    p.append(texto(270, 86, "sin ambientes", ROJO, 16, peso="600"))
    p.append(texto(810, 86, "con un .venv/ por proyecto", ACENTO, 16, peso="600"))
    p.append(f'<line x1="540" y1="70" x2="540" y2="380" stroke="{LINEA}" stroke-width="1.5" stroke-dasharray="6 6"/>')

    # Izquierda.
    for y, nombre, pide in ((110, "proyecto-a", "pide pandas==1.5"), (200, "proyecto-b", "pide pandas==2.2")):
        p.append(caja(40, y, 190, 64, PANEL, LINEA))
        p.append(teclado(135, y + 28, nombre, TEXTO, 15))
        p.append(texto(135, y + 50, pide, SUAVE, 12.5))
    p.append(caja(300, 120, 210, 150, PANEL, AMBAR))
    p.append(texto(405, 146, "Python del sistema", AMBAR, 14, peso="600"))
    p.append(teclado(405, 176, "site-packages/", SUAVE, 14, peso="normal"))
    p.append(caja(325, 196, 160, 46, FONDO, ROJO, radio=8))
    p.append(teclado(405, 225, "pandas 2.2", ROJO, 15))
    p.append(flecha(234, 142, 320, 210, ROJO, 2.2))
    p.append(flecha(234, 232, 320, 226, ACENTO, 2.2))
    p.append(texto(270, 320, "una sola ranura: el último que instala gana", ROJO, 14))
    p.append(texto(270, 346, "proyecto-a truena sin que nadie tocara su código", SUAVE, 13))

    # Derecha.
    for y, nombre, version in ((110, "proyecto-a", "pandas 1.5"), (230, "proyecto-b", "pandas 2.2")):
        p.append(caja(580, y, 190, 90, PANEL, LINEA))
        p.append(teclado(675, y + 38, nombre, TEXTO, 15))
        p.append(texto(675, y + 62, f"pide pandas=={version.split()[1]}", SUAVE, 12.5))
        p.append(caja(800, y, 230, 90, PANEL, ACENTO))
        p.append(teclado(915, y + 30, ".venv/site-packages/", SUAVE, 13, peso="normal"))
        p.append(teclado(915, y + 62, version, ACENTO, 15))
        p.append(flecha(774, y + 45, 794, y + 45, ACENTO, 2.2))
    p.append(texto(810, 360, "cada proyecto con sus versiones, sin tocarse", ACENTO, 14))
    p.append(cierre())
    return "".join(p)


def py_path():
    """Que python gana: la shell busca en el PATH, en orden."""
    ancho, alto = 1080, 480
    aria = (
        "Dos columnas con las carpetas del PATH en el orden en que la shell "
        "las recorre buscando python. Sin activar: /usr/local/bin, /usr/bin y "
        "/bin; el python3 de /usr/bin gana. Despues de source .venv/bin/activate: "
        "la carpeta .venv/bin del proyecto queda primero y su python gana, "
        "antes que /usr/local/bin y /usr/bin. Al pie: activate no instala nada, "
        "solo pone .venv/bin al frente del PATH, y uv run no necesita activar"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué python gana: la shell busca en orden", TEXTO, 21, peso="600"))
    p.append(texto(270, 90, "sin activar", SUAVE, 16, peso="600"))
    p.append(teclado(810, 90, "source .venv/bin/activate", ACENTO, 15))

    izquierda = (("/usr/local/bin", "no hay python", SUAVE, LINEA),
                 ("/usr/bin", "aquí está python3 → gana", AMBAR, AMBAR),
                 ("/bin", "ya no se busca", SUAVE, LINEA))
    derecha = (("…/09_python/ambientes/demo/.venv/bin", "aquí está python → gana", ACENTO, ACENTO),
               ("/usr/local/bin", "ya no se busca", SUAVE, LINEA),
               ("/usr/bin", "ya no se busca", SUAVE, LINEA))
    for x0, filas in ((50, izquierda), (590, derecha)):
        for i, (carpeta, nota, color, borde) in enumerate(filas):
            y = 116 + i * 82
            p.append(caja(x0, y, 440, 64, PANEL, borde))
            p.append(texto(x0 + 26, y + 39, str(i + 1), SUAVE, 16, peso="600"))
            p.append(teclado(x0 + 50, y + 30, carpeta, color, 15, anclaje="start"))
            p.append(texto(x0 + 50, y + 52, nota, color if borde != LINEA else SUAVE, 12.5, anclaje="start"))
            if i < 2:
                p.append(flecha(x0 + 26, y + 66, x0 + 26, y + 80, LINEA, 1.5))
    p.append(texto(ancho / 2, 400, "activate no instala nada: sólo pone .venv/bin al frente del PATH", TEXTO, 15))
    p.append(texto(ancho / 2, 430, "uv run no necesita activar: usa el .venv del proyecto directamente", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


def py_venv_arbol():
    """Un ambiente es una carpeta: el arbol de .venv/ y que es cada cosa."""
    ancho, alto = 1080, 460
    aria = (
        "El arbol de la carpeta .venv a la izquierda y, a la derecha de cada "
        "rama, que es: bin/python es el interprete, un enlace al Python base; "
        "bin/activate es lo que corre source; lib/python3.13/site-packages "
        "guarda los paquetes de este ambiente y de ningun otro, como rich y "
        "pygments; pyvenv.cfg dice de que Python salio y su version. Al pie: "
        "borrar el ambiente es borrar la carpeta"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Un ambiente es una carpeta", TEXTO, 21, peso="600"))
    p.append(caja(40, 76, 1000, 300, PANEL, LINEA))
    ramas = (
        (".venv/", "", ACENTO),
        ("├── bin/", "los programas del ambiente", TEXTO),
        ("│   ├── python", "el intérprete: un enlace al Python base", CIAN),
        ("│   └── activate", "lo que corre source (sólo cambia el PATH)", CIAN),
        ("├── lib/python3.13/site-packages/", "los paquetes de este ambiente y de ningún otro", AMBAR),
        ("│   └── rich/  pygments/  …", "lo que instaló uv add", AMBAR),
        ("└── pyvenv.cfg", "de qué Python salió y su versión", VIOLETA),
    )
    for i, (rama, nota, color) in enumerate(ramas):
        y = 116 + i * 38
        p.append(teclado(70, y, rama, color, 16, anclaje="start", peso="600" if i == 0 else "normal"))
        if nota:
            p.append(texto(560, y, nota, SUAVE, 14, anclaje="start"))
    p.append(texto(ancho / 2, 414, "borrar el ambiente = borrar la carpeta: rm -rf .venv", TEXTO, 15))
    p.append(texto(ancho / 2, 440, "nada fuera de .venv/ cambia; uv sync la vuelve a crear", SUAVE, 13.5))
    p.append(cierre())
    return "".join(p)


HERRAMIENTAS = (
    # nombre, (instalar, aislar, proyecto+lock, versiones Py, CLIs); 2 = a medias
    ("pip", (1, 0, 0, 0, 0)),
    ("venv", (0, 1, 0, 0, 0)),
    ("pip-tools", (0, 0, 2, 0, 0)),
    ("pipenv", (1, 1, 1, 0, 0)),
    ("poetry", (1, 1, 1, 0, 0)),
    ("pdm", (1, 1, 1, 1, 0)),
    ("hatch", (1, 1, 1, 1, 0)),
    ("conda", (1, 1, 2, 1, 0)),
    ("pixi", (1, 1, 1, 1, 1)),
    ("pyenv", (0, 0, 0, 1, 0)),
    ("pipx", (1, 1, 0, 0, 1)),
    ("uv", (1, 1, 1, 1, 1)),
)
TRABAJOS = ("instalar paquetes", "aislar", "proyecto + lock",
            "versiones de Python", "herramientas de terminal")


def py_trabajos():
    """Matriz: que trabajos hace cada herramienta."""
    ancho, alto = 1080, 640
    aria = (
        "Matriz de herramientas contra cinco trabajos: instalar paquetes, "
        "aislar, proyecto + lock, versiones de Python y herramientas de "
        "terminal. pip solo instala; venv solo aisla; pip-tools solo fija "
        "versiones; pipenv y poetry instalan, aislan y manejan proyecto con "
        "lock; pdm y hatch ademas instalan versiones de Python; conda hace "
        "casi todo y su lock es a medias; pixi y uv hacen los cinco; pyenv solo "
        "versiones de Python; pipx instala herramientas de terminal aisladas. "
        "La fila de uv esta resaltada. Al pie: conda y pixi instalan ademas "
        "paquetes que no son de Python"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Cinco trabajos, doce herramientas", TEXTO, 21, peso="600"))
    x0, y0, col, fila = 200, 110, 172, 38
    for j, trabajo in enumerate(TRABAJOS):
        cx = x0 + j * col + col / 2
        palabras = trabajo.split(" ", 1) if len(trabajo) > 14 else [trabajo]
        for k, w in enumerate(palabras):
            p.append(texto(cx, y0 - 22 + k * 17 - (8 if len(palabras) > 1 else 0), w, SUAVE, 13.5, peso="600"))
    for i, (nombre, hace) in enumerate(HERRAMIENTAS):
        y = y0 + i * fila
        if nombre == "uv":
            p.append(caja(40, y - 2, 1000, fila - 2, TINTE, ACENTO, radio=6, grosor=1.5))
        p.append(teclado(60, y + 22, nombre, ACENTO if nombre == "uv" else TEXTO, 15, anclaje="start"))
        for j, v in enumerate(hace):
            cx = x0 + j * col + col / 2
            if v == 1:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="8" fill="{ACENTO}"/>')
            elif v == 2:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="8" fill="none" stroke="{AMBAR}" stroke-width="2"/>')
            else:
                p.append(f'<circle cx="{cx}" cy="{y + 17}" r="3" fill="{LINEA}"/>')
    yp = y0 + len(HERRAMIENTAS) * fila + 24
    p.append(f'<circle cx="60" cy="{yp - 5}" r="7" fill="{ACENTO}"/>')
    p.append(texto(74, yp, "lo hace", SUAVE, 13, anclaje="start"))
    p.append(f'<circle cx="160" cy="{yp - 5}" r="7" fill="none" stroke="{AMBAR}" stroke-width="2"/>')
    p.append(texto(174, yp, "a medias", SUAVE, 13, anclaje="start"))
    p.append(texto(280, yp, "conda y pixi instalan además paquetes que no son de Python (CUDA, GDAL); uv no.", SUAVE, 13, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_cual_uso():
    """Arbol de decision: que herramienta usar."""
    ancho, alto = 1080, 470
    aria = (
        "Arbol de decision de tres preguntas. Necesitas paquetes que no son de "
        "Python, como CUDA o GDAL? Si: pixi, o conda. No: el proyecto ya usa "
        "poetry, pdm o hatch? Si: usa esa y lee su pyproject.toml. No: es un "
        "script suelto? Si: uv run script.py con sus dependencias dentro, PEP "
        "723. No: uv init y uv add, que es el caso de este curso"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "¿Cuál uso?", TEXTO, 21, peso="600"))
    preguntas = (
        "¿Necesitas paquetes que no son de Python (CUDA, GDAL)?",
        "¿El proyecto ya usa poetry, pdm o hatch?",
        "¿Es un script suelto, de un solo archivo?",
    )
    respuestas = ("pixi (o conda)", "usa esa: lee su pyproject.toml", "uv run script.py (PEP 723)")
    for i, (preg, resp) in enumerate(zip(preguntas, respuestas)):
        y = 84 + i * 110
        p.append(caja(40, y, 560, 60, PANEL, CIAN))
        p.append(texto(320, y + 36, preg, TEXTO, 15))
        p.append(flecha(604, y + 30, 690, y + 30, AMBAR, 2.2))
        p.append(chip(647, y + 10, "sí", AMBAR, tam=13))
        p.append(caja(694, y + 8, 346, 44, FONDO, AMBAR, radio=8))
        p.append(teclado(867, y + 36, resp, AMBAR, 14))
        p.append(flecha(320, y + 64, 320, y + 104, SUAVE, 2))
        p.append(chip(356, y + 84, "no", SUAVE, tam=13))
    p.append(caja(170, 414, 300, 44, TINTE, ACENTO, radio=8, grosor=2.5))
    p.append(teclado(320, 442, "uv init + uv add", ACENTO, 16))
    p.append(texto(500, 442, "← el caso de este curso", ACENTO, 14, anclaje="start"))
    p.append(cierre())
    return "".join(p)


def py_aislamiento():
    """Que capa aisla cada herramienta."""
    ancho, alto = 1080, 480
    aria = (
        "Cuatro capas apiladas de abajo hacia arriba: kernel, librerias y "
        "programas del sistema, interprete de Python y paquetes de Python. A "
        "la derecha, tres barras verticales muestran que cubre cada "
        "herramienta: el .venv de uv cubre los paquetes y el interprete si uv "
        "lo instalo; conda y pixi cubren paquetes, interprete y parte de las "
        "librerias del sistema; Docker cubre todo menos el kernel. Al pie: "
        "ninguno aisla el kernel, eso es una maquina virtual"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué capa aísla cada uno", TEXTO, 21, peso="600"))
    capas = ("paquetes de Python", "intérprete de Python",
             "librerías y programas del sistema", "kernel")
    y0, h = 90, 70
    for i, c in enumerate(capas):
        y = y0 + i * (h + 8)
        p.append(caja(40, y, 420, h, PANEL, LINEA))
        p.append(texto(250, y + h / 2 + 6, c, TEXTO, 15))
    columnas = (
        (".venv (uv)", ACENTO, 0, 1.5),
        ("conda / pixi", CIAN, 0, 2.5),
        ("Docker", VIOLETA, 0, 3.0),
    )
    for k, (nombre, color, desde, hasta) in enumerate(columnas):
        x = 520 + k * 180
        p.append(texto(x + 60, y0 - 14, nombre, color, 14, peso="600"))
        top = y0 + desde * (h + 8)
        alto_barra = hasta * (h + 8) - 8
        p.append(f'<rect x="{x + 30}" y="{top}" width="60" height="{alto_barra}" rx="8" fill="{color}" fill-opacity="0.35" stroke="{color}" stroke-width="2"/>')
    p.append(texto(616, y0 + 1.5 * (h + 8) - 14, "el intérprete,", SUAVE, 11.5, anclaje="start"))
    p.append(texto(616, y0 + 1.5 * (h + 8) + 2, "si uv lo instaló", SUAVE, 11.5, anclaje="start"))
    p.append(texto(796, y0 + 2.5 * (h + 8) - 14, "sólo las que", SUAVE, 11.5, anclaje="start"))
    p.append(texto(796, y0 + 2.5 * (h + 8) + 2, "empaqueta", SUAVE, 11.5, anclaje="start"))
    p.append(texto(ancho / 2, 440, "Ninguno aísla el kernel: eso lo hace una máquina virtual.", SUAVE, 14))
    p.append(cierre())
    return "".join(p)


def py_uv_docker():
    """El orden del Dockerfile de la tarea, sin dar los comandos."""
    ancho, alto = 1080, 520
    aria = (
        "Las cinco etapas del Dockerfile de la entrega, apiladas en orden: una "
        "imagen base que ya trae Python; el binario de uv, copiado de su imagen "
        "oficial; los dos archivos que describen el ambiente; crear el ambiente "
        "desde el lock, sin dejar que cambie; y al final el programa. Una llave "
        "junto a la tercera y la cuarta dice que esa capa queda en cache y solo "
        "se rehace si cambia el lock; junto a la quinta, que cambia cada vez que "
        "editas el codigo. Abajo, en rojo: el .venv de tu maquina se queda "
        "fuera de la imagen"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "El ambiente primero, el código al final", TEXTO, 21, peso="600"))
    pasos = (
        ("1 · una imagen base que ya trae Python", SUAVE),
        ("2 · el binario de uv, de su imagen oficial", SUAVE),
        ("3 · los dos archivos que describen el ambiente", CIAN),
        ("4 · crear el ambiente desde el lock, sin dejar que cambie", CIAN),
        ("5 · el programa", AMBAR),
    )
    for i, (linea, color) in enumerate(pasos):
        y = 80 + i * 66
        p.append(caja(40, y, 640, 52, PANEL, color))
        p.append(texto(60, y + 32, linea, color, 15, anclaje="start"))
    p.append(f'<path d="M 700 214 Q 716 214 716 230 L 716 316 Q 716 332 700 332" fill="none" stroke="{CIAN}" stroke-width="2"/>')
    p.append(texto(732, 262, "capa en caché:", CIAN, 14, anclaje="start", peso="600"))
    p.append(texto(732, 284, "sólo se rehace si cambia el lock", CIAN, 13.5, anclaje="start"))
    p.append(texto(700, 380, "← cambia cada vez que editas el código", AMBAR, 13.5, anclaje="start"))
    p.append(caja(40, 430, 1000, 56, FONDO, ROJO, radio=10))
    p.append(teclado(60, 464, ".venv/", ROJO, 15, anclaje="start"))
    p.append(texto(130, 464, "de tu máquina: nunca entra a la imagen", ROJO, 14, anclaje="start"))
    p.append(cierre())
    return "".join(p)

DIAGRAMAS = {
    "py-mapa": py_mapa,
    "py-choque": py_choque,
    "py-path": py_path,
    "py-venv-arbol": py_venv_arbol,
    "py-trabajos": py_trabajos,
    "py-cual-uso": py_cual_uso,
    "py-aislamiento": py_aislamiento,
    "py-uv-docker": py_uv_docker,
}


def escribir(nombre):
    ASSETS.mkdir(parents=True, exist_ok=True)
    destino = ASSETS / f"{nombre}.svg"
    destino.write_text(DIAGRAMAS[nombre](), encoding="utf-8")
    return destino


def main(argv):
    for nombre in argv[1:] or list(DIAGRAMAS):
        if nombre not in DIAGRAMAS:
            raise SystemExit(f"diagrama desconocido: {nombre}")
        destino = escribir(nombre)
        print(f"{destino.name}  ({destino.stat().st_size / 1000:.1f} KB)")


if __name__ == "__main__":
    main(sys.argv)
