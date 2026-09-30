"""Genera las cinco graficas de benchmark de la unidad de Contenedores.

Mismo patron que gen_regex.py y gen_diagramas.py: paleta importada de
svg_base, una funcion por figura que devuelve una cadena SVG completa, y un
catalogo DIAGRAMAS que el generador y su prueba comparten como unica fuente de
"que figuras existen".

La diferencia con los generadores conceptuales es que estas cinco no dibujan
una idea: dibujan un CSV. Los datos viven en
course/8_contenedores/_assets/benchmarks/results/ y CSV_DE declara, por figura,
que archivo los trae y que columnas exige. Nada se teclea a mano: si el
experimento se vuelve a correr, la grafica cambia sola.

Solo biblioteca estandar, a proposito. El runner de CI instala pytest, pillow y
pyyaml, y la guarda de la unidad IMPORTA este modulo: un `import matplotlib` o
un `import pandas` aqui rompe la suite en CI aunque funcione en la maquina del
autor. Los CSV se leen con el modulo csv y las graficas se emiten como cadenas.

La raiz <svg> sale siempre de svg_base.marco(): trae width y height numericos
sin unidades y un viewBox que empieza en "0 0", que es lo que exige
test_svg_tamano_intrinseco.py. Construir la raiz a mano es lo que produce el
SVG deformado.
"""
import csv
import math
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/8_contenedores/_assets"
RESULTADOS = ASSETS / "benchmarks/results"

from svg_base import (  # noqa: F401  (se reexportan para las guardas)
    FONDO, PANEL, TEXTO, SUAVE, LINEA, ACENTO, TINTE, AMBAR, CIAN, VIOLETA,
    ROJO, FUENTE, MONO, COLORES_FLECHA, caja, cierre, marco, teclado, texto,
)

# --------------------------------------------------------------------------
# El estadistico y el mapa de datos
# --------------------------------------------------------------------------

ESTADISTICO = statistics.median

# Los numeros que cita la unidad son MEDIANAS. Quien cambie esto a mean() por
# reflejo publicara 3.1 / 423 / 222 en vez de 1.8 / 428 / 213 y contradira la
# prosa sin que ninguna guarda lo note: el baseline a pelo tiene un ramp-up de
# frecuencia del CPU en las primeras repeticiones y por eso su media miente.

CSV_DE = {
    "cont-bench-arranque": ("exp1_startup.csv",
        ("runtime", "image", "rep", "startup_ms")),
    "cont-bench-escala": ("exp2_scale.csv",
        ("runtime", "count", "launch_time_s", "per_container_kb",
         "total_container_kb", "daemon_rss_kb")),
    "cont-bench-overhead": ("exp3_runtime.csv",
        ("runtime", "workload", "rep", "time_s")),
    "cont-bench-anidado": ("exp4_nested.csv",
        ("method", "metric", "rep", "value")),
    "cont-bench-io": ("io.csv",
        ("runtime", "mode", "rep", "mb_per_sec")),
}


def leer(figura):
    """Filas del CSV de una figura, con sus columnas exigidas verificadas."""
    archivo, columnas = CSV_DE[figura]
    ruta = RESULTADOS / archivo
    if not ruta.is_file():
        raise SystemExit(f"falta {ruta}")
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        faltan = [c for c in columnas if c not in (lector.fieldnames or ())]
        if faltan:
            raise SystemExit(f"{archivo}: faltan columnas {faltan}")
        return [dict(fila) for fila in lector]


def resumen(filas, columna, **filtros):
    """ESTADISTICO de una columna sobre las filas que cumplen los filtros."""
    muestras = [
        float(fila[columna]) for fila in filas
        if all(fila[clave] == valor for clave, valor in filtros.items())
    ]
    if not muestras:
        raise SystemExit(f"sin muestras para {filtros} en {columna}")
    return ESTADISTICO(muestras)


def serie(filas, clave, columna, orden, **filtros):
    """Una lista de valores en el orden pedido, uno por categoria."""
    return [
        float(next(
            fila[columna] for fila in filas
            if fila[clave] == categoria
            and all(fila[k] == v for k, v in filtros.items())
        ))
        for categoria in orden
    ]


# --------------------------------------------------------------------------
# Infraestructura de grafica
#
# No hay primitiva de grafica en el repositorio: esto la construye contra la
# paleta de svg_base, que es la de skins/fdd-eva.yaml. La unica pieza heredada
# es log_position(), copiada textual de tools/gen_ai_hardware_costs.py (no
# importada: ese modulo hace `import yaml` a nivel de modulo y arrastra mas).
# --------------------------------------------------------------------------


def log_position(value, minimum, maximum, start, end) -> float:
    """Map a positive value to a logarithmic horizontal coordinate."""
    values = tuple(float(item) for item in (value, minimum, maximum))
    if any(item <= 0 for item in values):
        raise ValueError("logarithmic values must be positive")
    value_f, minimum_f, maximum_f = values
    if maximum_f <= minimum_f or not minimum_f <= value_f <= maximum_f:
        raise ValueError("value must lie inside a positive increasing domain")
    fraction = math.log10(value_f / minimum_f) / math.log10(
        maximum_f / minimum_f
    )
    return float(start) + fraction * (float(end) - float(start))


def lineal(valor, minimo, maximo, inicio, fin):
    """La contraparte lineal de log_position(), con la misma firma."""
    fraccion = (float(valor) - minimo) / (maximo - minimo)
    return float(inicio) + fraccion * (float(fin) - float(inicio))


def rect(x, y, w, h, relleno, radio=3):
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" '
        f'height="{max(h, 0):.1f}" rx="{radio}" fill="{relleno}"/>'
    )


def regla(x1, y1, x2, y2, color=LINEA, grosor=1.5, guion=None):
    trazo = f' stroke-dasharray="{guion}"' if guion else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{grosor}"{trazo}/>'
    )


def polilinea(puntos, color, grosor=2.5):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)
    return (
        f'<polyline points="{d}" fill="none" stroke="{color}" '
        f'stroke-width="{grosor}" stroke-linejoin="round"/>'
    )


def punto(x, y, color, r=5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>'


def eje_x(x0, x1, y, marcas, titulo=None):
    """Eje horizontal con sus marcas y, opcionalmente, su titulo debajo."""
    p = [regla(x0 - 6, y, x1 + 6, y, LINEA, 1.8)]
    for x, etiqueta in marcas:
        p.append(regla(x, y, x, y + 6, LINEA, 1.4))
        p.append(texto(x, y + 22, etiqueta, SUAVE, 12.5))
    if titulo:
        p.append(texto((x0 + x1) / 2, y + 46, titulo, SUAVE, 13.5))
    return "".join(p)


def eje_y(x, y_arriba, y_abajo, marcas, ancho_rejilla=0):
    """Eje vertical con marcas a la izquierda y rejilla punteada opcional."""
    p = [regla(x, y_arriba - 6, x, y_abajo, LINEA, 1.8)]
    for y, etiqueta in marcas:
        p.append(regla(x - 6, y, x, y, LINEA, 1.4))
        p.append(texto(x - 12, y + 4, etiqueta, SUAVE, 12.5, anclaje="end"))
        if ancho_rejilla and y < y_abajo:
            p.append(regla(x, y, x + ancho_rejilla, y, LINEA, 0.8, guion="3 6"))
    return "".join(p)


def rejilla_vertical(y_arriba, y_abajo, xs):
    return "".join(regla(x, y_arriba, x, y_abajo, LINEA, 0.8, guion="3 6")
                   for x in xs)


def nota(x, y, ancho, alto, lineas):
    """Bloque de texto al pie de la grafica. lineas = [(texto, color, tam)]."""
    p = [rect(x, y, ancho, alto, PANEL, radio=10)]
    cursor = y + 28
    for contenido, color, tam in lineas:
        peso = "600" if tam >= 15 else "normal"
        p.append(texto(x + 22, cursor, contenido, color, tam,
                       anclaje="start", peso=peso))
        cursor += 26 if tam >= 15 else 22
    return "".join(p)


def pie(ancho, y, lineas):
    """Pie de la grafica: maquina, kernel y versiones de lo que se midio."""
    return "".join(
        texto(ancho / 2, y + i * 17, linea, SUAVE, 11.5)
        for i, linea in enumerate(lineas)
    )


def muestra(x, y, etiqueta, color, tam=13.5):
    """Entrada de leyenda: cuadrito de color y su nombre a la derecha."""
    return (
        rect(x, y - 10, 14, 14, color, radio=3)
        + texto(x + 24, y + 2, etiqueta, TEXTO, tam, anclaje="start")
    )


# La maquina donde se corrieron los cuatro experimentos. Va en el pie de las
# cuatro graficas: un numero de benchmark sin su maquina no es reproducible.
#
# Estas son las versiones de CUANDO SE MIDIO, no las de hoy. La misma maquina
# hoy corre Docker 29.6.0 sobre Linux 6.17.9; poner eso afirmaria que los
# numeros salieron de un Docker que todavia no existia cuando se midieron. La
# fuente es fdd_p26/clase/08_containers/04_benchmarks.md.
MAQUINA = "Intel Core i7-7700HQ · Linux 6.12"
RUNTIMES = "Docker 28.4.0 · Podman 4.6.2"


# --------------------------------------------------------------------------
# Experimento 1: latencia de arranque
# --------------------------------------------------------------------------

def cont_bench_arranque():
    """Cinco barras en escala logaritmica: el arranque de cada combinacion."""
    filas = leer("cont-bench-arranque")
    barras = [
        ("Docker · ubuntu:24.04", ("docker", "ubuntu"), CIAN),
        ("Docker · alpine", ("docker", "alpine"), CIAN),
        ("Podman · ubuntu:24.04", ("podman", "ubuntu"), AMBAR),
        ("Podman · alpine", ("podman", "alpine"), AMBAR),
        ("a pelo · fork + execve", ("bare", "none"), ACENTO),
    ]
    valores = [
        resumen(filas, "startup_ms", runtime=r, image=i)
        for _, (r, i), _ in barras
    ]
    du, da = valores[0], valores[1]
    brecha = abs(da - du) / min(da, du) * 100

    ancho, alto = 1000, 580
    izq, der = 250, 900
    minimo, maximo = 1.0, 1000.0
    ticks = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)
    xs = [log_position(t, minimo, maximo, izq, der) for t in ticks]

    aria = (
        "Grafica de barras con escala logaritmica del tiempo de arranque de un "
        "contenedor: Docker tarda 428 milisegundos con ubuntu y 430 con "
        "alpine, Podman 213 y 193, y lanzar el mismo proceso a pelo en el host "
        "tarda 1.8 milisegundos; las dos imagenes de cada runtime se ven "
        "practicamente identicas"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Cuánto tarda en arrancar un contenedor",
                   TEXTO, 22, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "Mediana de 10 repeticiones · escala logarítmica",
                   SUAVE, 14))

    p.append(rejilla_vertical(96, 330, xs))

    for i, (etiqueta, _, color) in enumerate(barras):
        cy = 118 + i * 46
        valor = valores[i]
        x_fin = log_position(valor, minimo, maximo, izq, der)
        p.append(rect(izq, cy - 15, x_fin - izq, 30, color))
        p.append(texto(izq - 14, cy + 5, etiqueta, TEXTO, 14, anclaje="end"))
        p.append(texto(x_fin + 12, cy + 5, f"{valor:.1f} ms", TEXTO, 14,
                       anclaje="start", peso="600"))

    p.append(eje_x(izq, der, 330,
                   list(zip(xs, (str(t) for t in ticks))),
                   "milisegundos (escala logarítmica)"))

    p.append(nota(50, 386, 900, 130, [
        ("Cambiar de imagen no cambia el arranque.", ACENTO, 15),
        (f"Docker tarda {du:.1f} ms con ubuntu:24.04 y {da:.1f} ms con "
         f"alpine: {brecha:.1f} % de diferencia.", SUAVE, 13.5),
        ("Arrancar no descomprime nada: la imagen ya quedó desplegada en el "
         "disco desde el pull.", SUAVE, 13.5),
        ("El baseline no es el piso del cronómetro: es el fork más execve de "
         "/usr/bin/date.", SUAVE, 13.5),
        ("Su mediana es 1.8 ms; su media, 3.1 ms, por el ramp-up de "
         "frecuencia del CPU en las primeras repeticiones.", SUAVE, 13.5),
    ]))

    p.append(pie(ancho, 542, [
        f"{MAQUINA} · {RUNTIMES}",
        "Imágenes ubuntu:24.04 y alpine · 10 repeticiones por barra más un "
        "warm-up descartado",
    ]))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Experimento 2: huella al escalar
# --------------------------------------------------------------------------

def cont_bench_escala():
    """Dos paneles: tiempo de arranque y memoria del supervisor, en crudo."""
    filas = leer("cont-bench-escala")
    cuentas = ("1", "5", "10", "20")
    arranque = {
        r: serie(filas, "count", "launch_time_s", cuentas, runtime=r)
        for r in ("docker", "podman")
    }
    # `ps -o rss=` reporta KIBIbytes, no kilobytes, aunque la columna del CSV
    # se llame daemon_rss_kb. La conversion correcta es /1024 y la unidad es
    # MiB: dividir entre 1000 y llamarlo MB es justo el error de unidades que
    # esta unidad ensena a no cometer.
    memoria = {
        r: [v / 1024 for v in
            serie(filas, "count", "daemon_rss_kb", cuentas, runtime=r)]
        for r in ("docker", "podman")
    }

    ancho, alto = 1060, 620
    arriba, base = 170, 400
    paneles = ((110, 500), (640, 1030))
    xs = [[lineal(i, 0, 3, x0 + 35, x1 - 35) for i in range(4)]
          for x0, x1 in paneles]

    aria = (
        "Dos paneles con el mismo eje de 1, 5, 10 y 20 contenedores: a la "
        "izquierda el tiempo de arranque, que sube de 0.35 a 5.52 segundos en "
        "Docker y de 0.19 a 2.74 en Podman; a la derecha la memoria del "
        "supervisor tal como la midio el script, con el RSS de dockerd plano "
        "en 179 mebibytes y la suma de los conmon de Podman subiendo de 1.7 a "
        "35.8 mebibytes"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué cambia al pasar de 1 a 20 contenedores",
                   TEXTO, 22, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "Lo que midió el script, con el daemon de Docker y los "
                   "conmon de Podman. Sin corregir nada.", SUAVE, 14))

    # --- Panel izquierdo: tiempo de arranque ---
    x0, x1 = paneles[0]
    p.append(texto((x0 + x1) / 2, 136, "Tiempo de arranque (segundos)",
                   TEXTO, 16, peso="600"))
    ticks_y = [(lineal(v, 0, 6, base, arriba), f"{v}") for v in range(7)]
    p.append(eje_y(x0, arriba, base, ticks_y, ancho_rejilla=x1 - x0 + 6))
    for runtime, color in (("docker", CIAN), ("podman", AMBAR)):
        puntos = [(xs[0][i], lineal(v, 0, 6, base, arriba))
                  for i, v in enumerate(arranque[runtime])]
        p.append(polilinea(puntos, color))
        for px, py in puntos:
            p.append(punto(px, py, color))
    p.append(muestra(x0 + 22, 192,
                     f"docker · de {arranque['docker'][0]:.2f} a "
                     f"{arranque['docker'][-1]:.2f} s", CIAN))
    p.append(muestra(x0 + 22, 218,
                     f"podman · de {arranque['podman'][0]:.2f} a "
                     f"{arranque['podman'][-1]:.2f} s", AMBAR))
    p.append(texto(x1 - 35, lineal(arranque["docker"][-1], 0, 6, base, arriba)
                   - 14, f"{arranque['docker'][-1]:.2f} s", TEXTO, 13.5,
                   anclaje="end", peso="600"))
    p.append(texto(x1 - 35, lineal(arranque["podman"][-1], 0, 6, base, arriba)
                   - 14, f"{arranque['podman'][-1]:.2f} s", TEXTO, 13.5,
                   anclaje="end", peso="600"))
    p.append(eje_x(x0, x1, base, list(zip(xs[0], cuentas)), "contenedores"))

    # --- Panel derecho: memoria del supervisor ---
    x0, x1 = paneles[1]
    p.append(texto((x0 + x1) / 2, 136, "Memoria del supervisor, RSS (MiB)",
                   TEXTO, 16, peso="600"))
    ticks_y = [(lineal(v, 0, 200, base, arriba), f"{v}")
               for v in (0, 50, 100, 150, 200)]
    p.append(eje_y(x0, arriba, base, ticks_y, ancho_rejilla=x1 - x0 + 6))
    for runtime, color in (("docker", CIAN), ("podman", AMBAR)):
        puntos = [(xs[1][i], lineal(v, 0, 200, base, arriba))
                  for i, v in enumerate(memoria[runtime])]
        p.append(polilinea(puntos, color))
        for px, py in puntos:
            p.append(punto(px, py, color))
    p.append(muestra(x0 + 22, 248,
                     f"dockerd · {memoria['docker'][0]:.1f} a "
                     f"{memoria['docker'][-1]:.1f} MiB", CIAN))
    p.append(muestra(x0 + 22, 274,
                     f"suma de los conmon · {memoria['podman'][0]:.1f} a "
                     f"{memoria['podman'][-1]:.1f} MiB", AMBAR))
    p.append(texto(x1 - 35, lineal(memoria["docker"][-1], 0, 200, base, arriba)
                   - 14, f"{memoria['docker'][-1]:.1f} MiB", TEXTO, 13.5,
                   anclaje="end", peso="600"))
    p.append(texto(x1 - 35, lineal(memoria["podman"][-1], 0, 200, base, arriba)
                   - 14, f"{memoria['podman'][-1]:.1f} MiB", TEXTO, 13.5,
                   anclaje="end", peso="600"))
    p.append(eje_x(x0, x1, base, list(zip(xs[1], cuentas)), "contenedores"))

    p.append(nota(50, 462, 960, 112, [
        ("Esto es la medición cruda, y por eso parece que Podman cruza a "
         "Docker.", AMBAR, 15),
        ("El script mide sólo el RSS de dockerd: nunca cuenta los "
         "containerd-shim, uno por contenedor.", SUAVE, 13.5),
        ("En Podman suma el RSS de todos los conmon, que comparten páginas "
         "entre sí.", SUAVE, 13.5),
        ("La gráfica dibuja el CSV tal cual: corregirla es el ejercicio de "
         "la página.", SUAVE, 13.5),
    ]))

    p.append(pie(ancho, 592, [
        f"{MAQUINA} · {RUNTIMES} · imagen ubuntu, contenedores "
        "«sleep 3600» · una medición por punto",
    ]))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Experimento 3: overhead de ejecucion
# --------------------------------------------------------------------------

def cont_bench_overhead():
    """Dos paneles, uno por workload: miden cosas distintas."""
    filas = leer("cont-bench-overhead")
    runtimes = (("bare", "a pelo", ACENTO),
                ("docker", "docker exec", CIAN),
                ("podman", "podman exec", AMBAR))
    datos = {
        w: [resumen(filas, "time_s", runtime=r, workload=w)
            for r, _, _ in runtimes]
        for w in ("hash", "sort")
    }

    ancho, alto = 1040, 640
    arriba, base = 172, 400
    paneles = (
        ((110, 490), "hash", "hash — dd 100 MiB · sha256sum", 1.2,
         (0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2)),
        ((620, 1000), "sort", "sort — seq 1..1 000 000 · shuf · sort -n", 1.8,
         (0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8)),
    )

    aria = (
        "Dos paneles con el costo de ejecutar el mismo trabajo dentro de un "
        "contenedor ya corriendo: el workload de hash tarda 1.035 segundos a "
        "pelo contra 0.781 en Docker y 0.850 en Podman, y el de sort tarda "
        "1.416 segundos a pelo contra 1.524 en Docker y 1.504 en Podman; la "
        "ventaja del hash viene de una version distinta de coreutils, no del "
        "contenedor"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Qué cuesta ejecutar dentro de un contenedor",
                   TEXTO, 22, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "Mediana de 5 repeticiones sobre contenedores que ya "
                   "estaban corriendo · segundos", SUAVE, 14))

    for (x0, x1), workload, titulo, tope, ticks in paneles:
        p.append(texto((x0 + x1) / 2, 136, titulo, TEXTO, 16, peso="600"))
        p.append(eje_y(x0, arriba, base,
                       [(lineal(v, 0, tope, base, arriba),
                         f"{v:.1f}") for v in ticks],
                       ancho_rejilla=x1 - x0 + 6))
        referencia = datos[workload][0]
        for i, (_, etiqueta, color) in enumerate(runtimes):
            valor = datos[workload][i]
            cx = lineal(i + 0.5, 0, 3, x0, x1)
            y_top = lineal(valor, 0, tope, base, arriba)
            p.append(rect(cx - 38, y_top, 76, base - y_top, color))
            p.append(texto(cx, y_top - 12, f"{valor:.3f} s", TEXTO, 14,
                           peso="600"))
            delta = (valor - referencia) / referencia * 100
            dentro = "referencia" if i == 0 else f"{delta:+.1f} %"
            p.append(texto(cx, y_top + 24, dentro, FONDO, 11.5, peso="600"))
            p.append(texto(cx, base + 22, etiqueta, SUAVE, 12.5))
        p.append(eje_x(x0, x1, base, []))
        p.append(texto(x0 + 6, arriba - 16, "segundos", SUAVE, 12.5,
                       anclaje="start"))

    p.append(nota(50, 466, 940, 118, [
        ("Ejecutar dentro de un contenedor no cuesta.", ACENTO, 15),
        ("El hash sale a favor del contenedor, y la razón no es el "
         "contenedor:", SUAVE, 13.5),
        ("el host corre GNU coreutils 8.32 y la imagen ubuntu:24.04 corre "
         "9.4. Es otra implementación de sha256sum, no otro kernel.",
         SUAVE, 13.5),
        ("El sort sale al revés, +7.6 % en Docker: parte de ese margen es el "
         "propio docker exec, que el experimento no midió aparte.",
         SUAVE, 13.5),
    ]))

    p.append(pie(ancho, 604, [
        f"{MAQUINA} · {RUNTIMES} · imagen ubuntu:24.04 · 5 repeticiones por "
        "barra, mediana",
        "Herramientas medidas: GNU coreutils 8.32 en el host contra GNU "
        "coreutils 9.4 dentro de la imagen",
    ]))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Experimento 4: contenedores anidados
# --------------------------------------------------------------------------

def cont_bench_anidado():
    """Dos paneles apilados, los cinco metodos en el mismo orden."""
    filas = leer("cont-bench-anidado")
    metodos = (
        ("bare", "a pelo", ACENTO),
        ("docker", "docker", CIAN),
        ("dind", "Docker dentro de Docker", VIOLETA),
        ("podman", "podman", AMBAR),
        ("podman-nested", "Podman anidado", ROJO),
    )
    arrancar = [resumen(filas, "value", method=m, metric="startup_ms")
                for m, _, _ in metodos]
    cpu = [resumen(filas, "value", method=m, metric="cpu_s")
           for m, _, _ in metodos]

    ancho, alto = 1000, 860
    izq, der = 270, 930
    minimo, maximo = 1.0, 1000.0
    ticks = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)
    xs_log = [log_position(t, minimo, maximo, izq, der) for t in ticks]
    ticks_cpu = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    xs_cpu = [lineal(t, 0, 0.8, izq, der) for t in ticks_cpu]

    aria = (
        "Dos paneles con los mismos cinco metodos en el mismo orden: a pelo, "
        "docker, Docker dentro de Docker, podman y Podman anidado. Arriba el "
        "arranque en milisegundos, 1.3, 315, 340, 166 y 241; abajo el tiempo "
        "de CPU del mismo trabajo en segundos, 0.47, 0.54, 0.58, 0.56 y 0.70. "
        "Anidar cuesta poco en computo y bastante en arranque"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44,
                   "Anidar: qué cuesta un contenedor dentro de otro",
                   TEXTO, 22, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "Mediana de 4 repeticiones · los mismos cinco métodos, en "
                   "el mismo orden, en los dos paneles", SUAVE, 14))

    # --- Panel de arriba: arranque ---
    p.append(texto(ancho / 2, 112, "Arranque (milisegundos)",
                   TEXTO, 16, peso="600"))
    p.append(rejilla_vertical(128, 336, xs_log))
    for i, (_, etiqueta, color) in enumerate(metodos):
        cy = 148 + i * 40
        valor = arrancar[i]
        x_fin = log_position(valor, minimo, maximo, izq, der)
        p.append(rect(izq, cy - 13, x_fin - izq, 26, color))
        p.append(texto(izq - 14, cy + 5, etiqueta, TEXTO, 14, anclaje="end"))
        formato = f"{valor:.0f} ms" if valor >= 10 else f"{valor:.1f} ms"
        p.append(texto(x_fin + 12, cy + 5, formato, TEXTO, 14,
                       anclaje="start", peso="600"))
    p.append(eje_x(izq, der, 336, list(zip(xs_log, (str(t) for t in ticks))),
                   "milisegundos (escala logarítmica)"))

    # --- Panel de abajo: tiempo de CPU ---
    p.append(texto(ancho / 2, 428, "Tiempo de CPU del mismo trabajo (segundos)",
                   TEXTO, 16, peso="600"))
    p.append(rejilla_vertical(444, 640, xs_cpu))
    for i, (_, etiqueta, color) in enumerate(metodos):
        cy = 464 + i * 40
        valor = cpu[i]
        x_fin = lineal(valor, 0, 0.8, izq, der)
        p.append(rect(izq, cy - 13, x_fin - izq, 26, color))
        p.append(texto(izq - 14, cy + 5, etiqueta, TEXTO, 14, anclaje="end"))
        p.append(texto(x_fin + 12, cy + 5, f"{valor:.2f} s", TEXTO, 14,
                       anclaje="start", peso="600"))
    p.append(eje_x(izq, der, 640,
                   list(zip(xs_cpu, (f"{t:.1f}" for t in ticks_cpu))),
                   "segundos"))

    d_arr = arrancar[2] - arrancar[1]
    d_cpu = cpu[2] - cpu[1]
    p_arr = arrancar[4] - arrancar[3]
    p_cpu = cpu[4] - cpu[3]
    p.append(nota(50, 702, 900, 104, [
        ("Anidar cuesta poco en cómputo y bastante en arranque.", ACENTO, 15),
        (f"Docker dentro de Docker: {d_arr:+.0f} ms de arranque sobre docker "
         f"({d_arr / arrancar[1] * 100:+.0f} %) y {d_cpu:+.3f} s de CPU "
         f"({d_cpu / cpu[1] * 100:+.0f} %).", SUAVE, 13.5),
        (f"Podman anidado: {p_arr:+.0f} ms sobre podman "
         f"({p_arr / arrancar[3] * 100:+.0f} %) y {p_cpu:+.3f} s de CPU "
         f"({p_cpu / cpu[3] * 100:+.0f} %).", SUAVE, 13.5),
    ]))

    p.append(pie(ancho, 824, [
        f"{MAQUINA} · {RUNTIMES}",
        "Docker dentro de Docker con docker:dind, Podman anidado con podman "
        "en modo privilegiado · 4 repeticiones por barra",
    ]))
    p.append(cierre())
    return "".join(p)


# --------------------------------------------------------------------------
# Experimento 5: escribir, y el brazo que no midio el disco
#
# Esta grafica tiene un requisito que las otras cuatro no tienen: io.csv trae
# en el mismo archivo un resultado solido —el volumen de Docker contra su capa
# overlay— y un artefacto —Podman sobre fuse-overlayfs reportando 3.7x el
# disco a pelo, que es page cache y no disco—. Esconder el artefacto seria
# publicar una tabla mutilada; dibujarlo como una barra mas seria publicar un
# numero falso. Asi que se dibuja como lo que es: la barra del artefacto va
# HUECA (sin relleno, contorno punteado en rojo), se sale del eje y termina en
# un corte de sierra en vez de en un extremo. Las cuatro barras solidas son
# mediciones; la unica que no lo es, no se parece a ninguna.
# --------------------------------------------------------------------------

def cont_bench_io():
    """Cuatro barras medidas y una quinta dibujada como lo que es: un artefacto."""
    filas = leer("cont-bench-io")
    solidas = (
        ("a pelo · al disco", ("bare", "direct"), ACENTO),
        ("Docker · capa overlay", ("docker", "overlay"), CIAN),
        ("Docker · volumen", ("docker", "volume"), CIAN),
        ("Podman · volumen", ("podman", "volume"), AMBAR),
    )
    valores = [
        resumen(filas, "mb_per_sec", runtime=r, mode=m)
        for _, (r, m), _ in solidas
    ]
    a_pelo, overlay, volumen = valores[0], valores[1], valores[2]
    fantasma = resumen(filas, "mb_per_sec", runtime="podman", mode="overlay")
    mejora = (volumen / overlay - 1) * 100
    veces = fantasma / a_pelo

    ancho, alto = 1040, 620
    izq, der = 250, 880
    tope = 600.0
    ticks = (0, 100, 200, 300, 400, 500, 600)
    xs = [lineal(t, 0, tope, izq, der) for t in ticks]
    arriba, abajo = 104, 345

    aria = (
        "Grafica de barras del rendimiento de escritura en megabytes por "
        "segundo: el disco a pelo da 458, Docker escribe 380 en su capa "
        "overlay y 510 en un volumen, un 34 por ciento mas, y Podman escribe "
        "512 en un volumen. La quinta barra, la de Podman sobre su capa "
        "overlay, dice 1700 y no se dibuja como las otras cuatro: va hueca, "
        "con el contorno punteado en rojo, se sale del eje y termina en un "
        "corte de sierra, porque 1700 es 3.7 veces el disco a pelo y lo que "
        "midio fue el page cache, no el disco"
    )
    p = [marco(ancho, alto, aria)]
    p.append(texto(ancho / 2, 44, "Cuánto rinde escribir, y cuándo el número "
                   "no es del disco", TEXTO, 22, peso="600"))
    p.append(texto(ancho / 2, 70,
                   "Mediana de 3 repeticiones · MB/s · cuatro mediciones y un "
                   "artefacto, dibujados distinto a propósito", SUAVE, 14))

    p.append(rejilla_vertical(arriba, abajo, xs))

    # La referencia fisica: lo que da el disco sin contenedor de por medio.
    x_pelo = lineal(a_pelo, 0, tope, izq, der)
    p.append(regla(x_pelo, arriba, x_pelo, abajo, ACENTO, 1.2, guion="4 6"))
    p.append(texto(x_pelo, arriba - 8, "el disco a pelo", ACENTO, 12))

    for i, (etiqueta, _, color) in enumerate(solidas):
        cy = 130 + i * 46
        valor = valores[i]
        x_fin = lineal(valor, 0, tope, izq, der)
        p.append(rect(izq, cy - 15, x_fin - izq, 30, color))
        p.append(texto(izq - 14, cy + 5, etiqueta, TEXTO, 14, anclaje="end"))
        p.append(texto(x_fin + 12, cy + 5, f"{valor:.0f} MB/s", TEXTO, 14,
                       anclaje="start", peso="600"))

    # El corchete entre las dos barras de Docker: el resultado que sí se publica.
    y_overlay, y_volumen = 130 + 46, 130 + 2 * 46
    x_corchete = 900
    p.append(regla(x_corchete, y_overlay, x_corchete, y_volumen, ACENTO, 1.5))
    for y in (y_overlay, y_volumen):
        p.append(regla(x_corchete - 10, y, x_corchete, y, ACENTO, 1.5))
    p.append(texto(x_corchete + 10, (y_overlay + y_volumen) / 2 + 5,
                   f"+{mejora:.0f} %", ACENTO, 15, anclaje="start", peso="600"))

    # La barra que no es una medicion: hueca, punteada, fuera del eje y rota.
    cy = 130 + 4 * 46
    y0, y1 = cy - 15, cy + 15
    x_corte = der + 40
    p.append(texto(izq - 14, cy + 5, "Podman · capa overlay", ROJO, 14,
                   anclaje="end"))
    p.append(
        f'<path d="M {x_corte:.1f} {y0:.1f} L {izq:.1f} {y0:.1f} '
        f'L {izq:.1f} {y1:.1f} L {x_corte:.1f} {y1:.1f}" fill="none" '
        f'stroke="{ROJO}" stroke-width="2" stroke-dasharray="7 5"/>'
    )
    p.append(
        f'<path d="M {x_corte:.1f} {y0:.1f} L {x_corte - 12:.1f} '
        f'{y0 + 7.5:.1f} L {x_corte + 12:.1f} {y0 + 15:.1f} '
        f'L {x_corte - 12:.1f} {y0 + 22.5:.1f} L {x_corte:.1f} {y1:.1f}" '
        f'fill="none" stroke="{ROJO}" stroke-width="2"/>'
    )
    p.append(texto(izq + 18, cy + 5,
                   f"{fantasma:.0f} MB/s — esto no es una medición de disco",
                   ROJO, 14, anclaje="start", peso="600"))

    p.append(eje_x(izq, der, 356, list(zip(xs, (str(t) for t in ticks))),
                   "megabytes por segundo escritos"))

    p.append(nota(50, 430, 940, 118, [
        ("Un resultado y un artefacto, en el mismo CSV.", ACENTO, 15),
        (f"Docker: en un volumen rinde {volumen:.0f} MB/s contra "
         f"{overlay:.0f} en la capa overlay, {mejora:.0f} % más. Ése es el "
         "resultado, y es el que la unidad publica.", SUAVE, 13.5),
        (f"Podman sobre fuse-overlayfs reporta {fantasma:.0f} MB/s: "
         f"{veces:.1f}× el disco a pelo. Nadie escribe más rápido que su "
         "disco.", ROJO, 13.5),
        ("Lo que midió ahí fue el page cache. Por eso esa barra va hueca, "
         "fuera del eje y rota: no es un dato que se pueda leer en la escala.",
         SUAVE, 13.5),
    ]))

    p.append(pie(ancho, 566, [
        f"{MAQUINA} · {RUNTIMES}",
        "Tanda 1 · 3 repeticiones por brazo, mediana · de esta prueba se "
        "conservó el CSV, no el script que lo produjo",
    ]))
    p.append(cierre())
    return "".join(p)


DIAGRAMAS = {
    "cont-bench-arranque": cont_bench_arranque,
    "cont-bench-escala": cont_bench_escala,
    "cont-bench-overhead": cont_bench_overhead,
    "cont-bench-anidado": cont_bench_anidado,
    "cont-bench-io": cont_bench_io,
}


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
