"""Guardas de las figuras de la unidad de Contenedores.

Mismo molde que test_diagramas.py y test_gen_regex.py: el generador es la unica
fuente de verdad, asi que la prueba regenera y compara en vez de limitarse a
comprobar que el archivo existe. Editar un .svg a mano falla aqui.

Dos diferencias con las guardas hermanas, y las dos son a proposito:

1. Esta prueba NUNCA corre el generador contra course/8_contenedores/_assets/.
   test_gen_regex.py se permite una fixture que reescribe los SVG publicados;
   aqui se rinde a un directorio temporal y se compara byte a byte contra lo
   comiteado. Una prueba que reescribe el artefacto que vigila no puede fallar
   cuando el artefacto esta mal: lo arregla en silencio.

2. La unidad tiene treinta y cuatro figuras de dos clases. Veintinueve son
   conceptuales (gen_contenedores.py) y cinco dibujan un CSV medido
   (gen_contenedores_bench.py). Las cinco llevan guardas extra: que el CSV siga trayendo
   las columnas que declara CSV_DE, que el estadistico siga siendo la mediana
   —cambiarlo a mean() publicaria numeros que contradicen la prosa— y que las
   cifras escritas a mano en la aria-label sigan siendo las que sale del CSV.

No se duplica lo que ya cubre otra guarda: los creditos son de test_creditos.py,
el width/height de la raiz es de test_svg_tamano_intrinseco.py y las seis
ilustraciones ilus-*.jpg —no deterministas, nunca regeneradas— son de
test_ilustraciones.py.

Una convencion de test_diagramas.py NO se hereda: la que prohibe texto de mas de
seis palabras por debajo de 14px. Aquella unidad pinta solo rotulos; esta pinta
bloques de prosa corta con parrafo(), partidos en renglones a 11.5px a
proposito, y la regla marcaria como error el diseno aprobado de la unidad.
"""
import importlib.util
import re
import statistics
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
GENERADOR = RAIZ / "tools/gen_contenedores.py"
GENERADOR_BENCH = RAIZ / "tools/gen_contenedores_bench.py"
UNIDAD = RAIZ / "course/8_contenedores"
ASSETS = UNIDAD / "_assets"
RESULTADOS = ASSETS / "benchmarks/results"
SKIN = RAIZ / "skins/fdd-eva.yaml"

BENCH = (
    "cont-bench-arranque",
    "cont-bench-escala",
    "cont-bench-overhead",
    "cont-bench-anidado",
    "cont-bench-io",
)


def _cargar(nombre, ruta):
    assert ruta.is_file(), (
        f"falta tools/{ruta.name}: las figuras de la unidad deben salir de un "
        "generador determinista, no escribirse a mano"
    )
    # Los generadores hacen `from svg_base import ...`, asi que necesitan
    # tools/ en sys.path. pytest ya lo inserta por rootdir, pero cargar el
    # modulo por ruta no depende de eso.
    if str(RAIZ / "tools") not in sys.path:
        sys.path.insert(0, str(RAIZ / "tools"))
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


GEN = _cargar("gen_contenedores", GENERADOR)
GEN_BENCH = _cargar("gen_contenedores_bench", GENERADOR_BENCH)
SLUGS = list(GEN.DIAGRAMAS)


def svg_de(slug):
    return ASSETS / f"{slug}.svg"


def texto_de(slug):
    return svg_de(slug).read_text(encoding="utf-8")


def raiz_de(slug):
    encontrada = re.match(r"<svg\b[^>]*>", texto_de(slug))
    assert encontrada, f"{slug}.svg: no se encontro la etiqueta <svg>"
    return encontrada.group()


# --------------------------------------------------------------------------
# El catalogo y el disco: ni una figura de mas ni una de menos
# --------------------------------------------------------------------------


def test_el_catalogo_declara_las_treinta_y_cuatro_figuras_de_la_unidad():
    """29 conceptuales + 5 de benchmark. Sumar o quitar una es una decision."""
    assert len(GEN.DIAGRAMAS_CONCEPTUALES) == 29
    assert tuple(GEN_BENCH.DIAGRAMAS) == BENCH
    assert not set(GEN.DIAGRAMAS_CONCEPTUALES) & set(GEN_BENCH.DIAGRAMAS), (
        "una figura declarada en los dos catalogos se pisaria al fusionarlos"
    )
    # Se comparan las claves: GEN importa su propia copia del modulo de
    # benchmark, asi que las funciones son objetos distintos con el mismo
    # nombre. Que el SVG que producen sea el mismo lo dice la comparacion
    # byte a byte contra el disco, que ambas copias tienen que pasar.
    assert set(GEN.DIAGRAMAS) == set(GEN.DIAGRAMAS_CONCEPTUALES) | set(BENCH)
    assert len(GEN.DIAGRAMAS) == 34


@pytest.mark.parametrize("slug", SLUGS)
def test_cada_figura_declarada_existe_en_disco(slug):
    assert svg_de(slug).is_file(), (
        f"falta {slug}.svg: corre `python3 tools/gen_contenedores.py`"
    )


def test_no_sobra_ningun_svg_sin_entrada_en_el_catalogo():
    declarados = {f"{slug}.svg" for slug in SLUGS}
    en_disco = {p.name for p in ASSETS.glob("*.svg")}
    huerfanos = en_disco - declarados
    assert not huerfanos, (
        f"SVG sin entrada en DIAGRAMAS: {sorted(huerfanos)}. El generador es "
        "la unica fuente de verdad de las figuras de esta unidad."
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_el_id_lleva_el_prefijo_de_la_unidad(slug):
    assert slug.startswith("cont-"), (
        f"{slug}: los ids de objeto numerado de Raya son unicos en TODO el "
        "curso, no por pagina; sin el prefijo 'cont-' pueden chocar con una "
        "figura de otra unidad"
    )


# --------------------------------------------------------------------------
# La guarda que de verdad importa: disco == generador, byte a byte
# --------------------------------------------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_el_svg_en_disco_es_exactamente_lo_que_produce_el_generador(slug):
    esperado = GEN.DIAGRAMAS[slug]().encode("utf-8")
    assert svg_de(slug).read_bytes() == esperado, (
        f"{slug}.svg no coincide con lo que el generador produce hoy. Los SVG "
        "no se editan a mano: cambia la funcion del generador y corre "
        "`python3 tools/gen_contenedores.py`."
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_generar_dos_veces_da_lo_mismo(slug):
    """Orden de diccionarios, timestamps o ids aleatorios romperian esto."""
    primera = GEN.DIAGRAMAS[slug]()
    segunda = GEN.DIAGRAMAS[slug]()
    assert primera == segunda
    assert not re.search(r"timestamp|generated-at|uuid", primera, re.I)


def test_regenerar_el_catalogo_completo_a_un_temporal_reproduce_el_disco(tmp_path):
    """El mismo contrato que escribir(), pero sin tocar lo publicado."""
    for slug, funcion in GEN.DIAGRAMAS.items():
        destino = tmp_path / f"{slug}.svg"
        destino.write_text(funcion(), encoding="utf-8")
        assert destino.read_bytes() == svg_de(slug).read_bytes(), slug
    assert {p.name for p in tmp_path.glob("*.svg")} == {
        f"{slug}.svg" for slug in SLUGS
    }


@pytest.mark.parametrize(
    "generador", [GENERADOR, GENERADOR_BENCH], ids=["conceptuales", "bench"]
)
def test_el_generador_rechaza_un_nombre_desconocido(generador):
    """Un slug mal escrito debe abortar, no escribir un archivo huerfano."""
    resultado = subprocess.run(
        [sys.executable, str(generador), "cont-no-existe"],
        capture_output=True, text=True, cwd=RAIZ,
    )
    assert resultado.returncode != 0
    assert "desconocido" in resultado.stderr
    assert not (ASSETS / "cont-no-existe.svg").exists()


# --------------------------------------------------------------------------
# Convenciones del SVG publicado
# --------------------------------------------------------------------------


@pytest.mark.parametrize("slug", SLUGS)
def test_el_svg_es_xml_bien_formado(slug):
    ET.fromstring(texto_de(slug))


@pytest.mark.parametrize("atributo", ["width", "height", "viewBox", "role", "aria-label"])
@pytest.mark.parametrize("slug", SLUGS)
def test_la_raiz_svg_cumple_las_cinco_convenciones(slug, atributo):
    assert f'{atributo}="' in raiz_de(slug), f"{slug}.svg: <svg> sin {atributo}"


@pytest.mark.parametrize("slug", SLUGS)
def test_la_aria_label_describe_la_figura_y_no_solo_la_nombra(slug):
    etiqueta = re.search(r'aria-label="([^"]*)"', raiz_de(slug)).group(1)
    assert len(etiqueta) >= 80, (
        f"{slug}.svg: aria-label demasiado corta ({len(etiqueta)} caracteres) "
        "para describir la figura a quien no la ve"
    )


def test_el_fondo_del_generador_sigue_siendo_el_del_skin():
    fondo = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]["color"]["page"]
    assert GEN.FONDO == fondo, (
        f"gen_contenedores.FONDO ({GEN.FONDO}) ya no es color.page del skin "
        f"({fondo})"
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_cada_svg_hornea_su_propio_fondo(slug):
    """Sin rect de fondo la figura se lee mal en tema claro."""
    assert f'fill="{GEN.FONDO}"' in texto_de(slug), (
        f"{slug}.svg no pinta su propio fondo"
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_todo_texto_lleva_fill_explicito(slug):
    contenido = texto_de(slug)
    assert "<text" in contenido, f"{slug}.svg: sin texto"
    for etiqueta in re.findall(r"<text\b[^>]*>", contenido):
        assert 'fill="' in etiqueta, (
            f"{slug}.svg: <text> sin fill hereda el color del tema y puede "
            f"volverse ilegible -> {etiqueta}"
        )


@pytest.mark.parametrize("slug", SLUGS)
def test_ningun_texto_se_sale_del_lienzo(slug):
    """Una etiqueta fuera del viewBox se recorta en el navegador."""
    raiz = raiz_de(slug)
    ancho = float(re.search(r'\bwidth="([\d.]+)"', raiz).group(1))
    alto = float(re.search(r'\bheight="([\d.]+)"', raiz).group(1))
    for etiqueta in re.findall(r"<text\b[^>]*>", texto_de(slug)):
        x = float(re.search(r'\sx="([-\d.]+)"', etiqueta).group(1))
        y = float(re.search(r'\sy="([-\d.]+)"', etiqueta).group(1))
        assert 0 <= x <= ancho and 0 <= y <= alto, (
            f"{slug}.svg: texto en ({x}, {y}) fuera del lienzo {ancho}x{alto}"
        )


def test_los_colores_del_generador_salen_del_skin():
    tokens = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]
    paleta = set(tokens["color"].values()) | set(tokens["graph"].values())
    usados = {
        GEN.FONDO, GEN.PANEL, GEN.TEXTO, GEN.SUAVE, GEN.LINEA, GEN.ACENTO,
        GEN.TINTE, GEN.AMBAR, GEN.CIAN, GEN.VIOLETA, GEN.ROJO,
    }
    fuera = usados - paleta
    assert not fuera, f"colores que no estan en skins/fdd-eva.yaml: {sorted(fuera)}"


def test_los_textos_van_escapados():
    """Comillas y ampersands en una etiqueta romperian el XML."""
    assert GEN.texto(0, 0, 'a & b "c"').count("&amp;") == 1
    assert escape("<") in GEN.teclado(0, 0, "<a>")


@pytest.mark.parametrize("slug", SLUGS)
def test_cada_figura_esta_referenciada_por_alguna_pagina_de_la_unidad(slug):
    """Una figura que nadie incrusta es peso muerto en el repositorio."""
    paginas = "".join(
        p.read_text(encoding="utf-8") for p in sorted(UNIDAD.rglob("*.md"))
    )
    assert f"{slug}.svg" in paginas, (
        f"{slug}.svg no aparece en ninguna pagina de la unidad"
    )


@pytest.mark.parametrize(
    "generador", [GENERADOR, GENERADOR_BENCH], ids=["conceptuales", "bench"]
)
def test_los_generadores_solo_usan_biblioteca_estandar(generador):
    """CI solo instala pytest, pillow y pyyaml, y esta guarda los IMPORTA."""
    fuente = generador.read_text(encoding="utf-8")
    for paquete in ("matplotlib", "pandas", "numpy", "cairosvg", "requests"):
        assert not re.search(rf"^\s*(import|from)\s+{paquete}\b", fuente, re.M), (
            f"{generador.name} importa {paquete}: la suite se rompe en CI "
            "aunque funcione en la maquina del autor"
        )


# --------------------------------------------------------------------------
# Las cinco graficas de benchmark: dibujan un CSV, no una idea
# --------------------------------------------------------------------------


def test_el_estadistico_de_los_benchmarks_sigue_siendo_la_mediana():
    """Con mean() el baseline a pelo publica 3.1 ms y contradice la prosa."""
    assert GEN_BENCH.ESTADISTICO is statistics.median


def test_cada_grafica_declara_su_csv_y_el_csv_trae_sus_columnas():
    assert tuple(GEN_BENCH.CSV_DE) == BENCH
    for figura, (archivo, columnas) in GEN_BENCH.CSV_DE.items():
        ruta = GEN_BENCH.RESULTADOS / archivo
        assert ruta.is_file(), f"{figura}: falta {ruta}"
        assert ruta.parent == RESULTADOS
        encabezado = ruta.read_text(encoding="utf-8").splitlines()[0]
        presentes = [c.strip() for c in encabezado.split(",")]
        faltan = [c for c in columnas if c not in presentes]
        assert not faltan, f"{archivo}: faltan columnas {faltan}"
        assert len(GEN_BENCH.leer(figura)) > 1, f"{archivo}: sin filas de datos"


@pytest.mark.parametrize("figura", BENCH)
def test_la_grafica_se_regenera_desde_su_csv_y_coincide(figura, tmp_path):
    """Se rinde a un temporal: lo publicado no se toca ni para comprobarlo."""
    destino = tmp_path / f"{figura}.svg"
    destino.write_text(GEN_BENCH.DIAGRAMAS[figura](), encoding="utf-8")
    assert destino.read_bytes() == svg_de(figura).read_bytes(), (
        f"{figura}.svg no coincide con lo que sale de "
        f"{GEN_BENCH.CSV_DE[figura][0]}: corre "
        "`python3 tools/gen_contenedores_bench.py`"
    )


def test_una_columna_ausente_en_el_csv_aborta_en_vez_de_graficar_de_menos(
    tmp_path, monkeypatch
):
    """Sin esto, un CSV mutilado publicaria una grafica con menos series."""
    archivo, columnas = GEN_BENCH.CSV_DE["cont-bench-arranque"]
    original = (RESULTADOS / archivo).read_text(encoding="utf-8").splitlines()
    sobrevive = [c for c in original[0].split(",") if c.strip() != columnas[-1]]
    (tmp_path / archivo).write_text(
        ",".join(sobrevive) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(GEN_BENCH, "RESULTADOS", tmp_path)
    with pytest.raises(SystemExit, match="faltan columnas"):
        GEN_BENCH.leer("cont-bench-arranque")


def test_un_csv_ausente_aborta_con_su_ruta(tmp_path, monkeypatch):
    monkeypatch.setattr(GEN_BENCH, "RESULTADOS", tmp_path)
    with pytest.raises(SystemExit, match="falta"):
        GEN_BENCH.leer("cont-bench-escala")


# Las aria-label de las cinco graficas estan escritas a mano y citan las
# cifras medidas. Nada las ata al CSV: si el experimento se vuelve a correr,
# las barras cambian solas y el texto accesible se queda contando la medicion
# vieja. Esta tabla es esa atadura. La clave es (figura, valor esperado,
# formato); el valor se calcula del CSV con el mismo formato que usa la prosa.
def _mediana(figura, columna, **filtros):
    return GEN_BENCH.resumen(GEN_BENCH.leer(figura), columna, **filtros)


def _serie(figura, columna, **filtros):
    return GEN_BENCH.serie(
        GEN_BENCH.leer(figura), "count", columna, ("1", "5", "10", "20"),
        **filtros
    )


def _cifras_arranque():
    f = "cont-bench-arranque"
    return [
        f"{_mediana(f, 'startup_ms', runtime='docker', image='ubuntu'):.0f}",
        f"{_mediana(f, 'startup_ms', runtime='docker', image='alpine'):.0f}",
        f"{_mediana(f, 'startup_ms', runtime='podman', image='ubuntu'):.0f}",
        f"{_mediana(f, 'startup_ms', runtime='podman', image='alpine'):.0f}",
        f"{_mediana(f, 'startup_ms', runtime='bare', image='none'):.1f}",
    ]


def _cifras_escala():
    f = "cont-bench-escala"
    docker = _serie(f, "launch_time_s", runtime="docker")
    podman = _serie(f, "launch_time_s", runtime="podman")
    mem_d = [v / 1024 for v in _serie(f, "daemon_rss_kb", runtime="docker")]
    mem_p = [v / 1024 for v in _serie(f, "daemon_rss_kb", runtime="podman")]
    return [
        f"{docker[0]:.2f}", f"{docker[-1]:.2f}",
        f"{podman[0]:.2f}", f"{podman[-1]:.2f}",
        f"{mem_d[0]:.0f}", f"{mem_p[0]:.1f}", f"{mem_p[-1]:.1f}",
    ]


def _cifras_overhead():
    f = "cont-bench-overhead"
    return [
        f"{_mediana(f, 'time_s', runtime=r, workload=w):.3f}"
        for w in ("hash", "sort") for r in ("bare", "docker", "podman")
    ]


def _cifras_anidado():
    f = "cont-bench-anidado"
    metodos = ("bare", "docker", "dind", "podman", "podman-nested")
    arranque = [_mediana(f, "value", method=m, metric="startup_ms") for m in metodos]
    cpu = [_mediana(f, "value", method=m, metric="cpu_s") for m in metodos]
    return (
        [f"{v:.1f}" if v < 10 else f"{v:.0f}" for v in arranque]
        + [f"{v:.2f}" for v in cpu]
    )


def _cifras_io():
    f = "cont-bench-io"
    return [
        f"{_mediana(f, 'mb_per_sec', runtime=r, mode=m):.0f}"
        for r, m in (("bare", "direct"), ("docker", "overlay"),
                     ("docker", "volume"), ("podman", "volume"),
                     ("podman", "overlay"))
    ]


@pytest.mark.parametrize("figura, cifras", [
    ("cont-bench-arranque", _cifras_arranque),
    ("cont-bench-escala", _cifras_escala),
    ("cont-bench-overhead", _cifras_overhead),
    ("cont-bench-anidado", _cifras_anidado),
    ("cont-bench-io", _cifras_io),
])
def test_las_cifras_de_la_aria_label_siguen_saliendo_del_csv(figura, cifras):
    etiqueta = re.search(
        r'aria-label="([^"]*)"', GEN_BENCH.DIAGRAMAS[figura]()
    ).group(1)
    faltan = [c for c in cifras() if c not in etiqueta]
    assert not faltan, (
        f"{figura}: la aria-label ya no cita {faltan}, que es lo que hoy sale "
        f"de {GEN_BENCH.CSV_DE[figura][0]}. El texto accesible esta contando "
        "una medicion vieja."
    )


def test_el_brazo_imposible_de_io_no_se_dibuja_como_una_medicion():
    """io.csv trae un resultado y un artefacto, y la figura los separa dibujando.

    El brazo de `podman/overlay` reporta 3.7x el disco a pelo: `fuse-overlayfs`
    midio page cache, no disco. La decision de diseno es que ese brazo se
    publique —esconderlo seria mutilar la tabla— pero **no como una barra**:
    va hueco, con el contorno punteado en rojo, saliendose del eje y roto por
    un corte de sierra. Esta guarda es lo que impide que una edicion futura lo
    convierta en una barra solida mas, que es exactamente el error que la
    pagina 1/9 existe para ensenar a no cometer.
    """
    svg = GEN_BENCH.cont_bench_io()
    filas = GEN_BENCH.leer("cont-bench-io")
    fantasma = GEN_BENCH.resumen(filas, "mb_per_sec", runtime="podman",
                                 mode="overlay")
    a_pelo = GEN_BENCH.resumen(filas, "mb_per_sec", runtime="bare",
                               mode="direct")
    assert fantasma > 2 * a_pelo, (
        "el brazo de podman/overlay dejo de ser fisicamente imposible: si el "
        "CSV se volvio a medir, esta figura y la pagina 1/9 hay que rehacerlas"
    )
    # Ninguna barra solida lo dibuja: los <rect> de color son mediciones.
    rellenos = re.findall(r'<rect\b[^>]*fill="([^"]+)"', svg)
    assert GEN_BENCH.ROJO not in rellenos, (
        "el artefacto se dibujo como barra solida: en esta figura el rojo "
        "solo puede ser contorno y texto"
    )
    # Y si esta dibujado: contorno hueco, punteado y en rojo.
    hueco = re.findall(
        r'<path\b[^>]*fill="none"[^>]*stroke="%s"[^>]*stroke-dasharray'
        % re.escape(GEN_BENCH.ROJO), svg
    )
    assert hueco, (
        "falta el contorno hueco y punteado del brazo que no midio disco"
    )
    assert f'>{fantasma:.0f} MB/s' in svg or f'{fantasma:.0f} MB/s' in svg, (
        "la figura ya no dice cuanto reporto el brazo descartado"
    )
