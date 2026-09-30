"""Guardas focales de la unidad 8, Contenedores.

Molde: `test_regex_curriculum.py`. Pero es **reescritura, no adaptación**: la
mitad ejecutable de aquella guarda —correr los bloques ```bash exigiendo stderr
vacío— aquí no se puede usar, porque cada bloque de esta unidad necesita un
Docker o un Podman vivos y CI no los tiene. Lo que sí se reaprovecha entero es
la otra mitad: la forma de la página, los topes, el ejercicio único, el cierre,
y sobre todo las **aserciones argumentales**, que son las que de verdad pagan.

La unidad son 30 páginas de lección repartidas en tres secciones, cuatro
índices y cuatro anexos. Hoy cumplen la forma porque se revisaron a mano, una
por una. Sin guarda, la primera edición apurada las erosiona en silencio: el
build no se cae por un «En corto» de cinco viñetas, ni por una página que se
queda sin puente, ni por una cifra que dejó de corresponder a su CSV.

Las reglas están fijadas en
`.superpowers/sdd/2026-09-15-unidad-8-contenedores/reglas-de-escritura.md` y el
porqué de cada una en
`docs/superpowers/specs/2026-09-15-unidad-8-contenedores-design.md`.
"""
import csv
import re
import statistics
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CURSO = RAIZ / "course"
UNIDAD = CURSO / "8_contenedores"
RESULTADOS = UNIDAD / "_assets/benchmarks/results"

INDICE_UNIDAD = UNIDAD / "0_index.md"

# Las tres secciones, en el orden en que se leen, con su índice y sus lecciones.
SECCIONES = ("1_la_idea", "2_manos_a_la_obra", "3_diseno_y_seguridad")


def _lecciones(seccion: str) -> list[Path]:
    """Las páginas de lección de una sección, en orden de autoría.

    `rglob` no, `glob` sí: aquí no hay subsecciones. Y el prefijo numérico se
    ordena como número, no como texto, o la 10 se cuela entre la 1 y la 2.
    """
    paginas = [p for p in (UNIDAD / seccion).glob("*.md") if p.name != "0_index.md"]
    return sorted(paginas, key=lambda p: int(p.name.split("_", 1)[0]))


INDICES = [INDICE_UNIDAD] + [UNIDAD / s / "0_index.md" for s in SECCIONES]
ANEXOS = [
    UNIDAD / "4_A_chuleta.md",
    UNIDAD / "5_B_prompts.md",
    UNIDAD / "6_C_anidar.md",
    UNIDAD / "7_D_entregas.md",
]
CHULETA = ANEXOS[0]

# Las 30 lecciones, en el orden en que se leen: sección 1 entera, luego la 2,
# luego la 3. Ese orden es el que hace decidible «antes de definirse».
LECCIONES: list[Path] = [p for s in SECCIONES for p in _lecciones(s)]
IDS_PYTEST = [f"{p.parent.name.split('_')[0]}-{p.stem}" for p in LECCIONES]

# Topes de longitud (regla 5). El de 160 viene de la unidad 6. Las exentas no
# son un permiso general: cada una es una página que tiene que cubrir las tres
# plataformas o servir de referencia, y está nombrada en el spec.
MAX_LINEAS = 160
MAX_EXENTAS = 260
MAX_CHULETA = 320
# El techo cuenta **líneas de fuente**, y en estas páginas un párrafo ocupa una
# sola por largo que sea: el de 314 palabras de `lo-que-cuesta` costaba 1. Así que
# partir un muro de prosa en tabla, viñetas y avisos **baja las palabras y sube
# las líneas** —ese párrafo pasó a 90 palabras en 14 líneas—, y medido en líneas
# el resultado parece un empeoramiento.
#
# Eso explica a dos de las tres. Dicho sin adorno, porque la diferencia importa:
#   lo-que-cuesta   144 -> 205 líneas, 3613 -> 3264 palabras: reflow puro.
#   docker-y-podman 158 -> 187 líneas, 2930 -> 2905 palabras: reflow puro.
#   capas-y-cache   152 -> 185 líneas, 1745 -> 1814 palabras: **se le añadió**
#     material (la tabla de la clave de caché y el aviso de que ni Git ni Docker
#     guardan diffs). Cabía en 160 antes y no cabe ahora, y no es por reflow.
# Como las de 260, las tres van nombradas de una en una y están en el spec.
MAX_ESTRUCTURADAS = 215
#
# Los dos laboratorios de la clase 2 (2026-09-22) entran por lo mismo, pero al
# revés: no crecieron por reflow sino por **aire**. Cada experimento es
# «Predice / Haz / Deberías ver / Por qué» en líneas propias, con una línea en
# blanco antes de cada encabezado. A 160 hubo que pegar el «Haz» a la pregunta
# y quitar los blancos, y la página dejó de escanearse, que es para lo que
# existe el formato. Partirlos rompería la matriz de ocho casos en dos mitades.
ESTRUCTURADAS = {
    "docker-y-podman",
    "capas-y-cache",
    "lo-que-cuesta",
}

# Las ocho páginas de la clase 2 (2026-09-22). El profesor pidió que cada
# bandera y cada subcomando se explique donde se usa —«los usas pero no
# mencionan qué está pasando»—, así que cada bloque ejecutable lleva debajo su
# «Qué hace cada pieza», una línea por pieza. Eso sube las líneas sin subir la
# prosa. Los dos laboratorios ya estaban en 215 por el aire del formato
# Predice / Haz / Deberías ver; la glosa los empuja más.
MAX_CLASE = 260
CLASE = {
    "repaso-dockerfile-imagen-contenedor",
    "ciclo-de-vida-de-un-contenedor",
    "el-dockerfile-por-dentro",
    "donde-vive-cada-byte",
    "lab-sin-volumen",
    "lab-con-volumen",
    "named-volumes-y-postgres",
    "limpieza-de-docker",
}
EXENTAS_260 = {
    "instalar-docker-y-podman",
    "planes-b-de-instalacion",
    "cuando-se-rompe-el-aislamiento",
    "prompts-contenedores",
    "contenedores-anidados",
    "entregas-contenedores",
}

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_IMAGEN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_OBJETO = re.compile(
    r"::: (figure|table|definition|problem|equation|example|code)\s*\{#([\w-]+)"
)
_WIKILINK = re.compile(r"\[\[([^\]\n|]+)(?:\|([^\]\n]*))?\]\]")
_MARCADOR = re.compile(r"\*\*Página (\d+) de (\d+) · sección (\d+) de 3\*\*")


def lee(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ident(path: Path) -> str:
    """El id estable de la página: lo durable, no el nombre del archivo."""
    encontrado = re.search(r"^id: (\S+)$", lee(path), re.M)
    assert encontrado, f"{path.name} no declara un id en su frontmatter"
    return encontrado.group(1)


def cuerpo(path: Path) -> str:
    """El texto después del `# Título`: sin frontmatter y sin el H1."""
    return lee(path).split("\n# ", 1)[1]


def prosa(texto: str) -> str:
    """Lo que un lector ve como texto corrido.

    Fuera: los bloques cercados, los code spans y el texto alternativo de las
    imágenes. Los tres son sitios donde una palabra puede aparecer sin que sea
    el autor usándola como concepto: `--memory 512m` no «usa» nada, y el alt de
    una figura describe lo que el SVG rotula, no lo que la página enseña.
    """
    fuera, dentro = [], False
    for linea in texto.splitlines():
        if _FENCE.match(linea):
            dentro = not dentro
            continue
        if not dentro:
            fuera.append(_CODE_SPAN.sub(" ", _IMAGEN.sub(" ", linea)))
    return "\n".join(fuera)


def bloques_bash(texto: str) -> list[str]:
    return re.findall(r"```bash\n(.*?)```", texto, re.S)


def _ids_estables() -> set[str]:
    """Todo lo que un wikilink puede resolver: páginas y objetos oficiales."""
    ids = set()
    for pagina in CURSO.glob("**/*.md"):
        encontrado = re.search(r"^id: (\S+)$", lee(pagina), re.M)
        if encontrado:
            ids.add(encontrado.group(1))
    for oficial in CURSO.glob("**/_official/**/*.yaml"):
        documento = yaml.safe_load(lee(oficial))
        if isinstance(documento, dict) and "id" in documento:
            ids.add(str(documento["id"]))
    return ids


IDS_ESTABLES = _ids_estables()
IDS_LECCION = [ident(p) for p in LECCIONES]
# id -> "sección/página", la coordenada con la que se citan entre ellas.
COORDENADA = {}
for _pagina in LECCIONES:
    _marca = _MARCADOR.search(lee(_pagina))
    if _marca:
        COORDENADA[ident(_pagina)] = f"{_marca.group(3)}/{_marca.group(1)}"


def antes_de(identificador: str) -> list[Path]:
    """Las lecciones que se leen antes que ésta."""
    return LECCIONES[: IDS_LECCION.index(identificador)]


# --------------------------------------------------------------------------
# El inventario, antes que nada
# --------------------------------------------------------------------------

def test_la_unidad_tiene_las_30_lecciones_los_4_indices_y_los_4_anexos():
    """Si alguien parte una página en dos, esta guarda deja de cubrirla.

    Las listas de arriba se construyen por `glob`, así que una página nueva
    entra sola a todas las pruebas de forma — pero el reparto por sección es
    una decisión de diseño (9 · 16 · 5) y cambiarlo mueve los marcadores de
    posición, los índices y la chuleta a la vez. Que falle aquí es el aviso.
    """
    assert [len(_lecciones(s)) for s in SECCIONES] == [9, 16, 5]
    assert len(LECCIONES) == 30
    for grupo in (INDICES, ANEXOS):
        for pagina in grupo:
            assert pagina.is_file(), f"falta {pagina.relative_to(RAIZ)}"
    assert len(set(IDS_LECCION)) == 30, "dos lecciones comparten id estable"


# --------------------------------------------------------------------------
# 1. La forma de la página (regla 6), sólo sobre las 30 lecciones
# --------------------------------------------------------------------------

@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_cada_leccion_abre_con_su_posicion_meta_y_figura(pagina):
    """Marcador, meta de una línea, figura, y después el texto. En ese orden.

    El ancla visual va antes de la prosa: es lo que hace que la unidad se pueda
    leer con la atención dispersa, que es la condición real con la que se lee.
    """
    texto = cuerpo(pagina)
    marca = _MARCADOR.search(texto)
    assert marca, (
        f"{pagina.name} no dice en qué punto de la unidad estás; "
        "el marcador es `**Página N de M · sección S de 3**`"
    )
    posicion, total, seccion = (int(g) for g in marca.groups())
    esperada = _lecciones(SECCIONES[seccion - 1]).index(pagina) + 1
    assert seccion == SECCIONES.index(pagina.parent.name) + 1
    assert posicion == esperada, (
        f"{pagina.name} dice ser la {posicion} y es la {esperada} de su sección"
    )
    assert total == len(_lecciones(pagina.parent.name)), (
        f"{pagina.name}: el total del marcador no es el de la sección"
    )

    meta = re.search(r"^Meta: (.+)$", texto, re.M)
    assert meta, f"{pagina.name} no abre con una línea 'Meta:'"
    # «De una línea» es la regla, y una línea de prosa son ~160 caracteres. El
    # tope no es decorativo: la meta se lee antes que nada y compite con la
    # figura por la primera pantalla.
    #
    # Este tope estuvo en 200 durante unas horas, para acomodar la meta de
    # `ciclo-de-vida-de-un-contenedor`, que medía 194 porque tenía dos frases
    # y sobraba una. Aflojar el número era tratar el síntoma: la segunda frase
    # se movió al cuerpo, que es donde el lector la necesita, y el tope volvió
    # a donde tenía que estar. La más larga hoy mide 159.
    assert len(meta.group(1)) <= 160, (
        f"{pagina.name}: la meta mide {len(meta.group(1))} caracteres y debe "
        "caber en una línea; si necesita dos frases, la segunda es cuerpo"
    )

    pos_meta = texto.index("Meta:")
    pos_figura = texto.index("::: figure")
    pos_corto = texto.index("## En corto")
    assert pos_meta < pos_figura < pos_corto, (
        f"{pagina.name}: el orden es meta, figura y después 'En corto'"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_cada_leccion_trae_su_propia_figura_numerada(pagina):
    """Regla 7: sin excepciones y sin lista de exentas.

    Por eso el inventario de SVG de la unidad subió a 29: cada página se ganó
    el suyo en vez de reciclar el del vecino.
    """
    assert "::: figure" in lee(pagina), (
        f"{pagina.name} no tiene figura numerada propia"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_el_en_corto_cabe_en_tres_vinetas(pagina):
    seccion = lee(pagina).split("## En corto", 1)[1].split("\n## ", 1)[0]
    vinetas = [l for l in seccion.splitlines() if l.startswith("- ")]
    assert 1 <= len(vinetas) <= 3, (
        f"{pagina.name}: 'En corto' tiene {len(vinetas)} viñetas; el máximo es 3"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_cada_leccion_trae_un_solo_ejercicio_completo(pagina):
    """Uno, con su pista y su respuesta. Dos seguidos rompen el ritmo."""
    texto = lee(pagina)
    problemas = re.findall(r"::: problem \{#([\w-]+)", texto)
    assert len(problemas) == 1, (
        f"{pagina.name} tiene {len(problemas)} ejercicios; debe tener exactamente 1"
    )
    for directiva in ("hint", "answer"):
        assert f'::: {directiva} {{of="{problemas[0]}"}}' in texto, (
            f"{pagina.name}: al ejercicio {problemas[0]} le falta su {directiva}"
        )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_cada_leccion_cierra_con_una_sola_frase(pagina):
    """El cierre va como callout, no como objeto numerado.

    `note` no es una familia de objeto numerado de Raya —el build falla con
    "Unknown numbered object family"— y además una nota numerada no es lo que
    se quiere aquí: es un recordatorio, no una pieza a la que se referencie.
    """
    texto = lee(pagina)
    nota = re.search(
        r"^> \[!NOTE\]\n> \*\*Si sólo recuerdas una cosa:\*\* (.+)$", texto, re.M
    )
    assert nota, f"{pagina.name} no cierra con 'Si sólo recuerdas una cosa'"
    assert "::: note" not in texto, (
        f"{pagina.name}: `note` no es una familia válida de objeto numerado"
    )


@pytest.mark.parametrize(
    "pagina", INDICES + ANEXOS,
    ids=[f"idx-{p.parent.name}" for p in INDICES] + [p.stem for p in ANEXOS],
)
def test_los_indices_y_los_anexos_quedan_fuera_de_la_forma_de_leccion(pagina):
    """Regla 6, segunda mitad: la forma aplica a las lecciones **y a nada más**.

    Lo que se vigila aquí es el marcador de posición (regla 8): un índice o un
    anexo que diga «Página 3 de 9 · sección 2 de 3» es señal de que alguien
    copió la plantilla equivocada, y además miente — la chuleta no se lee de
    corrido y no ocupa un lugar en ninguna secuencia.

    Y al revés, un índice no lleva ejercicio: es una tabla de contenido. Los
    anexos sí pueden —`C_anidar` cierra con uno, a propósito—, así que la
    regla del ejercicio único no se les aplica ni para exigirlo ni para
    prohibirlo.
    """
    texto = lee(pagina)
    assert not _MARCADOR.search(texto), (
        f"{pagina.name} lleva marcador de posición y no es una lección"
    )
    if pagina in INDICES:
        assert "::: problem" not in texto, (
            f"{pagina.name} es un índice y trae un ejercicio"
        )
        assert "Si sólo recuerdas una cosa" not in texto, (
            f"{pagina.name} es un índice y trae el cierre de una lección"
        )


# --------------------------------------------------------------------------
# 2. Los topes de longitud (regla 5)
# --------------------------------------------------------------------------

def test_los_conjuntos_de_exentas_no_se_solapan():
    """Si un id cae en dos conjuntos gana el techo más flojo, en silencio.

    `test_ninguna_pagina_pasa_su_techo_de_longitud` encadena `elif`, así que un
    id en `EXENTAS_260` y en `ESTRUCTURADAS` se mediría contra 260 y la rama de
    215 quedaría muerta sin que ninguna prueba lo dijera. Hoy son disjuntos por
    suerte, no por construcción; esto lo vuelve construcción.
    """
    solape = (ESTRUCTURADAS & EXENTAS_260) | (CLASE & (ESTRUCTURADAS | EXENTAS_260))
    assert not solape, f"ids en dos conjuntos de exentas a la vez: {sorted(solape)}"
    assert "chuleta-contenedores" not in (ESTRUCTURADAS | EXENTAS_260), (
        "la chuleta tiene su propio techo; no puede estar además en otro conjunto"
    )


@pytest.mark.parametrize(
    "pagina",
    LECCIONES + INDICES + ANEXOS,
    ids=IDS_PYTEST + [f"idx-{p.parent.name}" for p in INDICES] + [p.stem for p in ANEXOS],
)
def test_ninguna_pagina_pasa_su_techo_de_longitud(pagina):
    """Tres pantallas, con las excepciones que el spec nombra una por una.

    Si una página nueva no cabe, la salida por defecto no es agregarla a un
    conjunto de exentas: es partirla, o mandar la referencia larga a la chuleta.
    Los conjuntos existen para los dos casos en que partir empeora la página —
    cubrir las tres plataformas (`EXENTAS_260`) y la prosa ya estructurada en
    tablas y avisos (`ESTRUCTURADAS`)— y cada miembro se nombra y se justifica
    en el spec. Añadir uno es una decisión que se argumenta, no un trámite.
    """
    identificador = ident(pagina)
    if identificador == "chuleta-contenedores":
        techo = MAX_CHULETA
    elif identificador in EXENTAS_260:
        techo = MAX_EXENTAS
    elif identificador in ESTRUCTURADAS:
        techo = MAX_ESTRUCTURADAS
    elif identificador in CLASE:
        techo = MAX_CLASE
    else:
        techo = MAX_LINEAS
    lineas = len(lee(pagina).splitlines())
    assert lineas <= techo, (
        f"{pagina.name} tiene {lineas} líneas y su techo es {techo}: "
        "parte la página o manda la referencia larga a A_chuleta.md"
    )


# --------------------------------------------------------------------------
# 3. El puente
# --------------------------------------------------------------------------

@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_cada_leccion_tiende_el_puente_a_la_siguiente(pagina):
    """`Sigue con [[id]]`, y ese id resuelve.

    Ésta es la aserción con mejor historial: durante la construcción de la
    unidad el puente se perdió **dos veces** —una página quedó sin salida y
    otra apuntó a un id que nadie había creado todavía—. Ninguna de las dos
    rompía nada visible hasta que el lector se quedaba mirando el final.

    El puente va **antes** del callout de cierre: el cierre es lo último que
    se lee, y lo último que se lee no es una instrucción de navegación.
    """
    texto = lee(pagina)
    puente = re.search(r"Sigue con \[\[([\w-]+)(?:\|[^\]]*)?\]\]", texto)
    assert puente, (
        f"{pagina.name} no cierra con 'Sigue con [[id]]': el lector se queda "
        "sin saber a dónde va"
    )
    destino = puente.group(1)
    assert destino in IDS_ESTABLES, (
        f"{pagina.name} apunta a [[{destino}]], que no es un id estable del curso"
    )
    assert destino != ident(pagina), f"{pagina.name} se apunta a sí misma"
    cierre = texto.index("> [!NOTE]\n> **Si sólo recuerdas una cosa:**")
    assert puente.start() < cierre, (
        f"{pagina.name}: el puente va antes del callout de cierre"
    )


def test_el_puente_encadena_las_lecciones_en_el_orden_en_que_se_leen():
    """El puente de la página N apunta a la N+1, no a cualquier lado.

    Dentro de una sección encadena páginas; al final de una sección salta al
    índice de la siguiente; y la última de la unidad manda a los anexos. Un
    puente que apunte hacia atrás o que se salte una página es exactamente el
    modo en que una reordenación deja huérfana a una lección.
    """
    ids_anexos = {ident(p) for p in ANEXOS}
    for indice, pagina in enumerate(LECCIONES):
        destino = re.search(
            r"Sigue con \[\[([\w-]+)(?:\|[^\]]*)?\]\]", lee(pagina)
        ).group(1)
        siguiente = LECCIONES[indice + 1] if indice + 1 < len(LECCIONES) else None
        if siguiente is not None and siguiente.parent == pagina.parent:
            esperado = {ident(siguiente)}
            queja = "debe apuntar a la siguiente página de su sección"
        elif siguiente is not None:
            esperado = {ident(siguiente.parent / "0_index.md")}
            queja = "cierra sección: debe apuntar al índice de la siguiente"
        else:
            esperado = ids_anexos
            queja = "es la última de la unidad: debe apuntar a un anexo"
        assert destino in esperado, (
            f"{pagina.name} apunta a [[{destino}]] y {queja} ({sorted(esperado)})"
        )


# --------------------------------------------------------------------------
# 4. Los ids de objetos numerados, únicos en todo el curso
# --------------------------------------------------------------------------

def test_ningun_id_de_objeto_numerado_se_repite_en_todo_el_curso():
    """El builder guarda **un solo** conjunto de ids vistos para todo el curso.

    No es por página: reusar `#tabla-1` en dos unidades distintas tumba el
    build entero con `Duplicate numbered object ID`. Por eso los de esta
    unidad van prefijados `cont-`, y por eso esta prueba barre `course/`
    completo en vez de mirar sólo la unidad 8.
    """
    vistos: dict[str, list[str]] = {}
    for pagina in sorted(CURSO.glob("**/*.md")):
        for _familia, identificador in _OBJETO.findall(lee(pagina)):
            vistos.setdefault(identificador, []).append(
                str(pagina.relative_to(CURSO))
            )
    repetidos = {k: v for k, v in vistos.items() if len(v) > 1}
    assert not repetidos, (
        "ids de objeto numerado repetidos en el curso (el build falla con "
        f"'Duplicate numbered object ID'): {repetidos}"
    )
    assert any(k.startswith("cont-") for k in vistos), (
        "la unidad 8 no aportó ningún objeto numerado: ¿se movió de sitio?"
    )


def test_los_ids_de_la_unidad_van_prefijados_para_no_chocar():
    """El prefijo no es cosmética: es lo que hace que el choque no ocurra."""
    for pagina in LECCIONES + INDICES + ANEXOS:
        for familia, identificador in _OBJETO.findall(lee(pagina)):
            assert identificador.startswith("cont-"), (
                f"{pagina.name}: el {familia} `{identificador}` no lleva el "
                "prefijo `cont-`; los ids son únicos en todo el curso"
            )


def test_toda_referencia_arroba_apunta_a_un_objeto_que_existe():
    """`@nombre` es una referencia a objeto numerado, no un adorno.

    De ahí salen las dos caras del mismo problema: un `@` suelto en prosa
    tumba el build, y un `@id` que no existe también. Como las referencias de
    esta unidad cruzan de página en página —la 1/6 cita la figura de la 3/5—,
    el conjunto contra el que se resuelven es el del curso entero.
    """
    declarados = {
        identificador
        for pagina in CURSO.glob("**/*.md")
        for _familia, identificador in _OBJETO.findall(lee(pagina))
    }
    rotas = []
    for pagina in LECCIONES + INDICES + ANEXOS:
        for referencia in re.findall(r"(?<![\w`])@([A-Za-z][\w.-]*)", prosa(lee(pagina))):
            if referencia not in declarados:
                rotas.append(f"{pagina.name}: @{referencia}")
    assert not rotas, (
        "referencias `@` que no resuelven a ningún objeto numerado (un `@` "
        "literal en prosa va en code span): " + ", ".join(rotas)
    )


# --------------------------------------------------------------------------
# 5. Las cuatro tablas de contenido
# --------------------------------------------------------------------------

@pytest.mark.parametrize("seccion", SECCIONES)
def test_el_indice_de_cada_seccion_lista_sus_paginas_con_enlace(seccion):
    """La tabla de contenido es la única página que las nombra todas.

    Dos fallas distintas caben aquí y las dos son mudas: una página nueva que
    nadie agregó a la tabla —existe, se construye, y no se llega a ella desde
    ningún lado— y una fila escrita en texto plano, que además se salta la
    validación de enlaces de raya, porque no hay enlace que validar.
    """
    indice = UNIDAD / seccion / "0_index.md"
    texto = lee(indice)
    encabezado = re.search(r"^## Las (\w+) páginas$", texto, re.M)
    assert encabezado, f"{seccion}/0_index.md no tiene su tabla de páginas"

    tabla = texto.split(encabezado.group(0), 1)[1].split("\n## ", 1)[0]
    filas = [
        l for l in tabla.splitlines()
        if l.startswith("|") and not re.fullmatch(r"\|[\s\-:|]+\|", l)
        and not l.lstrip("|").strip().startswith("#")
    ]
    esperadas = [ident(p) for p in _lecciones(seccion)]
    assert len(filas) == len(esperadas), (
        f"{seccion}/0_index.md lista {len(filas)} páginas y la sección tiene "
        f"{len(esperadas)}"
    )
    enlazadas = []
    for numero, fila in enumerate(filas, 1):
        enlaces = _WIKILINK.findall(fila)
        assert enlaces, (
            f"{seccion}/0_index.md: la fila {numero} no lleva wikilink; una "
            "fila en texto plano no la valida nadie"
        )
        enlazadas.append(enlaces[0][0])
    assert enlazadas == esperadas, (
        f"{seccion}/0_index.md lista {enlazadas} y la sección es {esperadas}"
    )


def test_el_indice_de_la_unidad_enlaza_las_tres_secciones_y_los_cuatro_anexos():
    """El índice de la unidad no lista las 30 páginas: lista quién sí las lista.

    Por eso se comprueba distinto: sus dos tablas tienen que cubrir, entre las
    dos, los tres índices de sección y los cuatro anexos, sin sobrar ni faltar.
    """
    texto = lee(INDICE_UNIDAD)
    for encabezado, esperados in (
        ("## Las tres secciones", [ident(UNIDAD / s / "0_index.md") for s in SECCIONES]),
        ("## Los cuatro anexos", [ident(p) for p in ANEXOS]),
    ):
        assert encabezado in texto, f"al índice de la unidad le falta «{encabezado}»"
        tabla = texto.split(encabezado, 1)[1].split("\n## ", 1)[0]
        filas = [
            l for l in tabla.splitlines()
            if l.startswith("|") and not re.fullmatch(r"\|[\s\-:|]+\|", l)
            and not l.lstrip("|").strip().startswith("#")
            and not l.lstrip("|").strip().startswith("Anexo")
        ]
        enlazados = []
        for numero, fila in enumerate(filas, 1):
            enlaces = _WIKILINK.findall(fila)
            assert enlaces, (
                f"índice de la unidad, «{encabezado}»: la fila {numero} no "
                "lleva wikilink"
            )
            enlazados.append(enlaces[0][0])
        assert sorted(enlazados) == sorted(esperados), (
            f"índice de la unidad, «{encabezado}»: enlaza {enlazados}, "
            f"se esperaba {esperados}"
        )


def test_toda_pagina_de_la_unidad_es_alcanzable_desde_un_indice():
    """Cerrar el círculo: ninguna de las 38 páginas queda huérfana."""
    enlazados = {
        destino
        for indice in INDICES
        for destino, _etiqueta in _WIKILINK.findall(lee(indice))
    }
    huerfanas = [
        ident(p) for p in LECCIONES + ANEXOS
        if ident(p) not in enlazados
    ]
    assert not huerfanas, (
        f"páginas que ningún índice enlaza: {huerfanas}"
    )


def test_las_coordenadas_de_seccion_pagina_dicen_la_verdad():
    """`[[id|2/11]]` promete una posición; la página tiene que estar ahí.

    La chuleta cita ~60 veces con esta etiqueta, y las tablas de deuda de los
    índices citan coordenadas sueltas. Mover una página de sitio sin tocar
    ninguna de las dos deja al lector buscando la 2/11 donde ya no está, y
    nada en el build se entera.
    """
    mentiras = []
    for pagina in LECCIONES + INDICES + ANEXOS:
        for destino, etiqueta in _WIKILINK.findall(lee(pagina)):
            if re.fullmatch(r"\d/\d{1,2}", etiqueta or ""):
                if COORDENADA.get(destino) != etiqueta:
                    mentiras.append(
                        f"{pagina.name}: [[{destino}|{etiqueta}]] pero está en "
                        f"{COORDENADA.get(destino)}"
                    )
    assert not mentiras, "\n".join(mentiras)


@pytest.mark.parametrize("seccion", SECCIONES[:2])
def test_las_tablas_de_deuda_apuntan_a_paginas_que_existen(seccion):
    """«Se abre en 1/5, se paga en 3/1» es una promesa comprobable.

    Las dos primeras secciones llevan una tabla de lo que dejan abierto a
    propósito. Es el mecanismo con el que la unidad se permite nombrar algo
    antes de explicarlo, así que una coordenada que no resuelve convierte la
    promesa en una deuda impagable.
    """
    indice = UNIDAD / seccion / "0_index.md"
    texto = lee(indice)
    assert "## Lo que esta sección te debe" in texto, (
        f"{seccion}/0_index.md perdió su tabla de deuda"
    )
    tabla = texto.split("## Lo que esta sección te debe", 1)[1]
    validas = set(COORDENADA.values())
    rotas = [
        f"{s}/{p}" for s, p in re.findall(r"(?<![\w/])(\d)/(\d{1,2})(?![\w/])", tabla)
        if f"{s}/{p}" not in validas
    ]
    assert not rotas, (
        f"{seccion}/0_index.md promete pagar deudas en páginas que no existen: "
        f"{sorted(set(rotas))}"
    )


# --------------------------------------------------------------------------
# 6. Invariantes argumentales
# --------------------------------------------------------------------------

def test_el_microservicio_se_nombra_por_primera_vez_donde_se_define():
    """La palabra que la unidad viene prometiendo se dice una sola vez, y ahí.

    Es la pieza que más fácil se degrada: «microservicio» es una palabra que
    se cuela sola en cualquier párrafo sobre contenedores, y usada antes de su
    página convierte el argumento de `el-contrato-de-un-servicio` en una
    definición tardía de algo que el lector ya creía entender.
    """
    pagina = UNIDAD / "3_diseno_y_seguridad/2_el_contrato_de_un_servicio.md"
    texto = lee(pagina)
    assert "Un **microservicio** no es «un servicio chico»" in texto, (
        "la página del contrato debe definir «microservicio» por contraste, "
        "no darlo por sabido"
    )
    tempranas = [
        p.name for p in antes_de(ident(pagina))
        if re.search(r"microservicio", prosa(lee(p)), re.I)
    ]
    assert not tempranas, (
        f"«microservicio» se usa antes de definirse, en: {tempranas}"
    )


def test_la_palabra_api_no_entra_en_la_prosa_de_la_unidad():
    """Restricción dura del diseño: **los alumnos no saben qué es una API**.

    Ninguna página la define, y ninguna debe apoyarse en ella: la unidad
    explica un servicio por su contrato —puerto, variables, volumen— y nunca
    por «expone una API». La palabra sí aparece como **rótulo de contenedor**
    dentro de dos diagramas (`api` junto a `db`), y ahí es un nombre, no un
    concepto; por eso la prosa se mide sin el texto alternativo ni los code
    spans. En cuanto alguien escriba «la API escucha en el 8000» en un
    párrafo, esta prueba se cae, que es justo lo que se quiere.
    """
    ofensas = []
    for pagina in LECCIONES + ANEXOS:
        for numero, linea in enumerate(prosa(lee(pagina)).splitlines(), 1):
            if re.search(r"\bAPIs?\b", linea):
                ofensas.append(f"{pagina.name}: {linea.strip()[:90]}")
    assert not ofensas, (
        "la unidad usa «API» en prosa sin haberla definido nunca; dilo por su "
        "contrato (puerto, variables, volumen):\n" + "\n".join(ofensas)
    )


def test_puerto_se_glosa_donde_se_adelanta_y_se_define_donde_toca():
    """`puerto` es la única de las nueve palabras que se usa antes de su página.

    La tabla de namespaces de 1/2 no puede explicar `net` sin nombrarlo, así
    que ahí va una glosa de una línea que dice, además, que se está
    adelantando y dónde se paga. La definición completa vive en 3/1 y **sólo**
    ahí: dos bloques `definition` para la misma palabra es el síntoma de que
    alguien resolvió el problema otra vez sin buscar si ya estaba resuelto.
    """
    adelanto = UNIDAD / "1_la_idea/2_que_es_un_contenedor.md"
    completa = UNIDAD / "3_diseno_y_seguridad/1_la_red_y_el_nombre.md"
    texto_adelanto = lee(adelanto)
    assert "se usa aquí antes de tiempo" in texto_adelanto, (
        "1/2 usa `puerto` sin avisar que se está adelantando"
    )
    assert "un **`puerto`** es el número" in texto_adelanto, (
        "1/2 debe glosar `puerto` en una línea"
    )
    assert "[[la-red-y-el-nombre" in texto_adelanto, (
        "la glosa de 1/2 debe decir dónde se paga la deuda"
    )
    assert "::: definition {#cont-s3p1-def-puerto" in lee(completa), (
        "3/1 debe traer la definición completa de `puerto`"
    )
    definiciones = [
        p.name for p in LECCIONES
        if re.search(r"::: definition \{#[\w-]*puerto", lee(p))
    ]
    assert definiciones == [completa.name], (
        f"`puerto` se define en más de un sitio: {definiciones}"
    )
    # Y la única lección anterior a la glosa usa «puerto» en el sentido de
    # McLean, no en el de red: nada de publicar ni de `-p`.
    previa = antes_de(ident(adelanto))
    for pagina in previa:
        assert "-p " not in prosa(lee(pagina)), (
            f"{pagina.name} publica un puerto antes de que exista la palabra"
        )


@pytest.mark.parametrize(
    "palabra,bloque,pagina",
    [
        ("PID", "cont-def-pid", "1_la_idea/2_que_es_un_contenedor.md"),
        ("/proc", "cont-def-pid", "1_la_idea/2_que_es_un_contenedor.md"),
        ("daemon", "cont-def-daemon", "1_la_idea/4_anatomia_de_docker_run.md"),
        ("socket", "cont-def-daemon", "1_la_idea/4_anatomia_de_docker_run.md"),
        ("syscall", "cont-def-syscall", "1_la_idea/4_anatomia_de_docker_run.md"),
        ("réplica", "cont-def-estado", "1_la_idea/5_escalamiento_y_orquestacion.md"),
        ("psql", "cont-def-psql", "2_manos_a_la_obra/7_named_volumes_y_postgres.md"),
    ],
)
def test_las_palabras_que_el_curso_nunca_definio_se_definen_al_usarlas(
    palabra, bloque, pagina
):
    """Regla 11: definición de una línea en la **primera** aparición.

    Son palabras que el curso da por sabidas y nunca enseñó. La prueba no
    comprueba que exista la definición —eso sería fácil de cumplir poniéndola
    al final—: comprueba que **ninguna lección anterior** usa la palabra. Ese
    es el orden que hace que la unidad se pueda leer una sola vez, hacia
    adelante.
    """
    destino = UNIDAD / pagina
    assert f"::: definition {{#{bloque}" in lee(destino), (
        f"{pagina} perdió el bloque de definición `{bloque}`"
    )
    patron = re.compile(re.escape(palabra), re.I if palabra.isalpha() else 0)
    tempranas = [
        p.name for p in antes_de(ident(destino)) if patron.search(prosa(lee(p)))
    ]
    assert not tempranas, (
        f"«{palabra}» se usa antes de definirse en {pagina}, en: {tempranas}"
    )


def test_la_unidad_no_ensena_kubernetes_como_herramienta():
    """Es la deuda que no se paga, y está declarada como tal.

    Enseñar Kubernetes aquí es el error que la unidad existe para no cometer:
    produce gente que copia manifiestos sin saber qué está pegando. La
    declaración vive en 1/5 y en la tabla de deuda de la sección 1; lo que
    esta prueba vigila es que nadie la desmienta metiendo la herramienta por
    la puerta de atrás.
    """
    prohibidos = ("kubectl", "minikube", "apiVersion:", "kind: Deployment", "k8s")
    ofensas = [
        f"{p.name}: {t}"
        for p in LECCIONES + INDICES + ANEXOS
        for t in prohibidos
        if t in lee(p)
    ]
    assert not ofensas, (
        "la unidad empezó a enseñar Kubernetes como herramienta: " + ", ".join(ofensas)
    )
    orquestacion = lee(UNIDAD / "1_la_idea/5_escalamiento_y_orquestacion.md")
    assert "**Es una deuda que no se paga, a propósito.**" in orquestacion, (
        "1/5 nombra Kubernetes: tiene que decir, ahí mismo, que no se enseña"
    )
    deuda = lee(UNIDAD / "1_la_idea/0_index.md")
    fila = re.search(r"\|\s*\*\*Kubernetes como herramienta\*\*\s*\|([^|]*)\|([^|]*)\|", deuda)
    assert fila, "la tabla de deuda de la sección 1 perdió la fila de Kubernetes"
    assert "no se paga" in fila.group(2), (
        "la fila de Kubernetes debe decir que la deuda no se paga, no prometer página"
    )


# --------------------------------------------------------------------------
# 6 bis. Ninguna cifra publicada sin respaldo
# --------------------------------------------------------------------------

def _columna(archivo: str, columna: str, **filtros) -> list[float]:
    ruta = RESULTADOS / archivo
    assert ruta.is_file(), f"falta el CSV {ruta.relative_to(RAIZ)}"
    with ruta.open(encoding="utf-8") as mango:
        return [
            float(fila[columna])
            for fila in csv.DictReader(mango)
            if all(fila[k] == v for k, v in filtros.items())
        ]


def _mediana(archivo: str, columna: str, **filtros) -> float:
    valores = _columna(archivo, columna, **filtros)
    assert valores, f"{archivo}: ninguna fila cumple {filtros}"
    return statistics.median(valores)


# (página, cifra tal como se publica, cómo se calcula desde el CSV)
CIFRAS = [
    # Arranque, tanda 1 (exp1_startup.csv).
    ("lo-que-cuesta", "427.6", lambda: f"{_mediana('exp1_startup.csv', 'startup_ms', runtime='docker', image='ubuntu'):.1f}"),
    ("lo-que-cuesta", "429.8", lambda: f"{_mediana('exp1_startup.csv', 'startup_ms', runtime='docker', image='alpine'):.1f}"),
    ("lo-que-cuesta", "212.7", lambda: f"{_mediana('exp1_startup.csv', 'startup_ms', runtime='podman', image='ubuntu'):.1f}"),
    ("lo-que-cuesta", "193.3", lambda: f"{_mediana('exp1_startup.csv', 'startup_ms', runtime='podman', image='alpine'):.1f}"),
    # El baseline y su media, que es media parte del argumento de la página.
    ("lo-que-cuesta", "1.8", lambda: f"{_mediana('exp1_startup.csv', 'startup_ms', runtime='bare'):.1f}"),
    ("lo-que-cuesta", "3.1", lambda: f"{statistics.mean(_columna('exp1_startup.csv', 'startup_ms', runtime='bare')):.1f}"),
    # Ejecución, tanda 1 (exp3_runtime.csv).
    ("lo-que-cuesta", "1.035", lambda: f"{_mediana('exp3_runtime.csv', 'time_s', runtime='bare', workload='hash'):.3f}"),
    ("lo-que-cuesta", "0.781", lambda: f"{_mediana('exp3_runtime.csv', 'time_s', runtime='docker', workload='hash'):.3f}"),
    ("lo-que-cuesta", "1.416", lambda: f"{_mediana('exp3_runtime.csv', 'time_s', runtime='bare', workload='sort'):.3f}"),
    ("lo-que-cuesta", "1.524", lambda: f"{_mediana('exp3_runtime.csv', 'time_s', runtime='docker', workload='sort'):.3f}"),
    # Escala (exp2_scale.csv): la corrida única, citada como tal.
    ("lo-que-cuesta", "5.52", lambda: f"{_mediana('exp2_scale.csv', 'launch_time_s', runtime='docker', count='20'):.2f}"),
    ("escalamiento-y-orquestacion", "5.5", lambda: f"{_mediana('exp2_scale.csv', 'launch_time_s', runtime='docker', count='20'):.1f}"),
    ("escalamiento-y-orquestacion", "2.7", lambda: f"{_mediana('exp2_scale.csv', 'launch_time_s', runtime='podman', count='20'):.1f}"),
    # Escritura, tanda 1 (io.csv): el brazo bueno y el brazo imposible, en
    # el mismo archivo. Los 1700 MB/s se publican **como artefacto**, así
    # que también son una cifra que tiene que seguir saliendo del CSV: el
    # día que alguien lo vuelva a medir bien, la página cambia de tesis.
    ("lo-que-cuesta", "458", lambda: f"{_mediana('io.csv', 'mb_per_sec', runtime='bare', mode='direct'):.0f}"),
    ("lo-que-cuesta", "380", lambda: f"{_mediana('io.csv', 'mb_per_sec', runtime='docker', mode='overlay'):.0f}"),
    ("lo-que-cuesta", "510", lambda: f"{_mediana('io.csv', 'mb_per_sec', runtime='docker', mode='volume'):.0f}"),
    ("lo-que-cuesta", "1700", lambda: f"{_mediana('io.csv', 'mb_per_sec', runtime='podman', mode='overlay'):.0f}"),
    # Runtimes OCI, tanda 2 (exp5_oci.csv): los tres brazos del mito del 2×.
    ("docker-y-podman", "215", lambda: f"{_mediana('exp5_oci.csv', 'startup_ms', brazo='podman-crun'):.0f}"),
    ("docker-y-podman", "361", lambda: f"{_mediana('exp5_oci.csv', 'startup_ms', brazo='docker-runc'):.0f}"),
    ("docker-y-podman", "373", lambda: f"{_mediana('exp5_oci.csv', 'startup_ms', brazo='podman-runc'):.0f}"),
    # Anidamiento (exp4_nested.csv), el anexo C.
    ("contenedores-anidados", "315", lambda: f"{_mediana('exp4_nested.csv', 'value', method='docker', metric='startup_ms'):.0f}"),
    ("contenedores-anidados", "340", lambda: f"{_mediana('exp4_nested.csv', 'value', method='dind', metric='startup_ms'):.0f}"),
    ("contenedores-anidados", "166", lambda: f"{_mediana('exp4_nested.csv', 'value', method='podman', metric='startup_ms'):.0f}"),
    ("contenedores-anidados", "241", lambda: f"{_mediana('exp4_nested.csv', 'value', method='podman-nested', metric='startup_ms'):.0f}"),
    ("contenedores-anidados", "0.54", lambda: f"{_mediana('exp4_nested.csv', 'value', method='docker', metric='cpu_s'):.2f}"),
    ("contenedores-anidados", "0.58", lambda: f"{_mediana('exp4_nested.csv', 'value', method='dind', metric='cpu_s'):.2f}"),
    ("contenedores-anidados", "0.70", lambda: f"{_mediana('exp4_nested.csv', 'value', method='podman-nested', metric='cpu_s'):.2f}"),
]

_POR_ID = {ident(p): p for p in LECCIONES + INDICES + ANEXOS}


@pytest.mark.parametrize(
    "pagina_id,cifra,calculo", CIFRAS,
    ids=[f"{p}-{c}" for p, c, _ in CIFRAS],
)
def test_cada_cifra_publicada_coincide_con_su_CSV(pagina_id, cifra, calculo):
    """El número del texto y el del CSV son el mismo número.

    Ésta es la mitad dura de «ninguna cifra sin respaldo»: la unidad publica
    sus scripts y sus CSV para que los corras, así que la prosa no puede
    contar otra cosa que los datos. Y no sólo protege de un dedazo al
    teclear: protege de que alguien vuelva a medir, cambie el CSV y deje la
    página contando la corrida vieja.
    """
    calculada = calculo()
    assert calculada == cifra, (
        f"{pagina_id} publica {cifra} y el CSV da {calculada}: o se corrigió "
        "la página, o se volvió a medir y hay que rehacer el pie"
    )
    texto = lee(_POR_ID[pagina_id])
    assert re.search(rf"(?<![\d.]){re.escape(cifra)}(?![\d])", texto), (
        f"{pagina_id} ya no cita {cifra}, que es lo que dice su CSV"
    )


def test_los_incrementos_del_anexo_de_anidamiento_salen_de_su_CSV():
    """Los porcentajes también son cifras, y son las que más se repiten fuera.

    «Anidar cuesta un 8 %» es la frase que sobrevive al anexo; si el CSV
    cambia y el porcentaje no, lo que circula es un número inventado.
    """
    def salto(uno: str, otro: str) -> int:
        a = _mediana("exp4_nested.csv", "value", method=uno, metric="startup_ms")
        b = _mediana("exp4_nested.csv", "value", method=otro, metric="startup_ms")
        return round((b / a - 1) * 100)

    texto = lee(UNIDAD / "6_C_anidar.md")
    assert f"un {salto('docker', 'dind')} %" in texto, (
        "el incremento de Docker dentro de Docker no es el de exp4_nested.csv"
    )
    assert f"**{salto('podman', 'podman-nested')} %**" in texto, (
        "el incremento de Podman anidado no es el de exp4_nested.csv"
    )


def test_los_derivados_de_la_prueba_de_escritura_salen_de_su_CSV():
    """El 34 % y el 3.7× son los dos números que se citan fuera de la gráfica.

    Uno es el resultado que la unidad sí publica —salir del overlay— y el otro
    es la prueba de que el brazo de Podman midió page cache y no disco. Los dos
    son cocientes, así que ninguna de las dos guardas de arriba los cubre: un
    dedazo en cualquiera de ellos pasaría en verde citando cifras correctas.
    """
    overlay = _mediana("io.csv", "mb_per_sec", runtime="docker", mode="overlay")
    volumen = _mediana("io.csv", "mb_per_sec", runtime="docker", mode="volume")
    a_pelo = _mediana("io.csv", "mb_per_sec", runtime="bare", mode="direct")
    fantasma = _mediana("io.csv", "mb_per_sec", runtime="podman", mode="overlay")

    mejora = f"{round((volumen / overlay - 1) * 100)} %"
    for identificador in ("lo-que-cuesta", "donde-vive-cada-byte"):
        assert mejora in lee(_POR_ID[identificador]), (
            f"{identificador} ya no dice que salir del overlay son {mejora} "
            "más rápido, que es lo que da io.csv"
        )

    assert f"{fantasma / a_pelo:.1f}×" in lee(_POR_ID["lo-que-cuesta"]), (
        "lo-que-cuesta perdió el cociente que delata al artefacto: el brazo de "
        "Podman reporta más veces el disco a pelo de lo que la página dice"
    )
    assert "1700" not in lee(_POR_ID["donde-vive-cada-byte"]), (
        "2/4 publica el brazo descartado; ahí no hay espacio para explicar por "
        "qué está mal, y un número malo sin su explicación es peor que ninguno"
    )


_MEDICION = re.compile(r"\bmediana\b|medición propia|\bMedido con\b|\d+(?:\.\d+)?\s*ms\b")


@pytest.mark.parametrize(
    "pagina", LECCIONES + ANEXOS, ids=IDS_PYTEST + [p.stem for p in ANEXOS],
)
def test_ninguna_pagina_publica_una_medicion_sin_su_pie(pagina):
    """Regla 9: un número de benchmark sin su pie no vale nada.

    El pie completo —máquina, kernel, versiones de los dos runtimes **y de las
    herramientas medidas**— vive una sola vez, en `lo-que-cuesta`. Cualquier
    otra página que cite una medición tiene dos salidas legítimas: enlazar a
    esa página, o declarar ahí mismo su propia tanda con sus versiones. Lo que
    no es una salida es soltar el número.

    Que esto importe no es doctrina: media unidad existe porque las cifras
    heredadas venían sin pie y, al buscárselo, tres de ellas resultaron estar
    midiendo otra cosa.
    """
    texto = lee(pagina)
    if ident(pagina) == "lo-que-cuesta" or not _MEDICION.search(prosa(texto)):
        return
    tiene_enlace = "[[lo-que-cuesta" in texto
    tiene_pie_propio = bool(
        re.search(r"Docker \d+\.\d+", texto) and re.search(r"Linux \d+\.\d+", texto)
    )
    assert tiene_enlace or tiene_pie_propio, (
        f"{pagina.name} publica una medición y no dice de dónde sale: enlaza a "
        "[[lo-que-cuesta]] o declara su propia tanda con máquina, kernel y "
        "versiones"
    )


# Qué CSV respalda a cada página que publica milisegundos. Una página que no
# esté aquí no puede publicar ninguno: registrarla es el trámite que obliga a
# decir de qué tanda sale el número antes de escribirlo.
FUENTES_MS = {
    "lo-que-cuesta": ("exp1_startup.csv", "exp5_oci.csv"),
    "docker-y-podman": ("exp1_startup.csv", "exp5_oci.csv"),
    "contenedores-anidados": ("exp4_nested.csv",),
}

_COLUMNA_MS = {
    "exp1_startup.csv": ("startup_ms", ("runtime", "image")),
    "exp5_oci.csv": ("startup_ms", ("brazo",)),
    "exp4_nested.csv": ("value", ("method", "metric")),
}


def _milisegundos_respaldados(archivo: str) -> set[str]:
    """Todas las medianas del CSV, tal como una página puede escribirlas."""
    columna, claves = _COLUMNA_MS[archivo]
    ruta = RESULTADOS / archivo
    series: dict[tuple, list[float]] = {}
    with ruta.open(encoding="utf-8") as mango:
        for fila in csv.DictReader(mango):
            if archivo == "exp4_nested.csv" and fila["metric"] != "startup_ms":
                continue
            series.setdefault(tuple(fila[k] for k in claves), []).append(
                float(fila[columna])
            )
    permitidas = set()
    for valores in series.values():
        for resumen in (statistics.median(valores), statistics.mean(valores)):
            permitidas.update({f"{resumen:.1f}", f"{resumen:.0f}", f"{resumen:.2f}"})
    return permitidas


_MS = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s?ms\b")


@pytest.mark.parametrize(
    "pagina", LECCIONES + ANEXOS, ids=IDS_PYTEST + [p.stem for p in ANEXOS],
)
def test_ningun_milisegundo_publicado_se_sale_de_los_CSV(pagina):
    """El cierre de «ninguna cifra sin respaldo»: no basta con que la buena esté.

    La tabla `CIFRAS` comprueba que cada número que la unidad quiere decir
    sigue siendo el del CSV. Esta prueba cierra el otro lado: que la página no
    diga **además** un número que no está en ningún CSV. Sin ella, cambiar
    «427.6 ms» por «427.9 ms» en el pie de una figura pasa en verde, porque el
    427.6 bueno sigue apareciendo tres párrafos abajo.

    Y vale la pena decir de dónde viene la manía: las cifras que esta unidad
    heredó venían sin pie, y al buscárselo resultó que varias estaban midiendo
    otra cosa. Un número que no se puede rastrear hasta una corrida publicada
    no es un dato, es folclore.
    """
    texto = lee(pagina)
    citadas = set(_MS.findall(texto))
    if not citadas:
        return
    identificador = ident(pagina)
    assert identificador in FUENTES_MS, (
        f"{pagina.name} publica milisegundos ({sorted(citadas)}) y no tiene "
        "CSV declarado en FUENTES_MS: di de qué tanda sale antes de escribirlo"
    )
    respaldadas = set()
    for archivo in FUENTES_MS[identificador]:
        respaldadas |= _milisegundos_respaldados(archivo)
    huerfanas = sorted(citadas - respaldadas)
    assert not huerfanas, (
        f"{pagina.name} publica milisegundos que no salen de "
        f"{FUENTES_MS[identificador]}: {huerfanas}"
    )


def test_los_CSV_que_la_unidad_promete_estan_publicados():
    """«Los scripts y los CSV están publicados para que puedas rehacerlo.»

    Es una promesa explícita de `lo-que-cuesta`, y es lo que sostiene el
    método que enseña la página. Un CSV borrado la convierte en una cita de
    autoridad.
    """
    for archivo in (
        "exp1_startup.csv", "exp2_scale.csv", "exp3_runtime.csv",
        "exp4_nested.csv", "exp5_oci.csv",
    ):
        assert (RESULTADOS / archivo).is_file(), f"falta {archivo}"
    assert "_assets/benchmarks/" in lee(UNIDAD / "1_la_idea/9_lo_que_cuesta.md")


# --------------------------------------------------------------------------
# 7. Higiene del renderizador
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "pagina", LECCIONES + INDICES + ANEXOS,
    ids=IDS_PYTEST + [f"idx-{p.parent.name}" for p in INDICES] + [p.stem for p in ANEXOS],
)
def test_ninguna_linea_de_prosa_lleva_dos_signos_de_pesos(pagina):
    """El renderizador carga `dollarmath`: dos `$` en una línea son MathJax.

    Y lo peor es cómo falla: **sin error y sin warning**. La línea sale
    convertida en una fórmula ilegible y el build pasa en verde. Como
    `$(pwd)`, `$USER` y `$GHUSER` están por toda la unidad, la regla es que
    todo `$` va dentro de code span o de un bloque cercado — por eso aquí se
    quitan los dos antes de contar.
    """
    ofensas = [
        f"  línea {n}: {l.strip()[:90]}"
        for n, l in enumerate(prosa(lee(pagina)).splitlines(), 1)
        if l.count("$") >= 2
    ]
    assert not ofensas, (
        f"{pagina.name} tiene prosa con dos `$`, que dollarmath convierte en "
        "fórmula sin avisar:\n" + "\n".join(ofensas)
    )


_HTML = re.compile(
    r"</?(?:div|br|iframe|details|summary|span|img|p|table|tr|td|th|b|i|u|em|"
    r"strong|a|h[1-6]|script|style)\b[^>]*>",
    re.I,
)


@pytest.mark.parametrize(
    "pagina", LECCIONES + INDICES + ANEXOS,
    ids=IDS_PYTEST + [f"idx-{p.parent.name}" for p in INDICES] + [p.stem for p in ANEXOS],
)
def test_ninguna_pagina_mete_html_crudo(pagina):
    """El renderizador corre con `html: False`.

    Tampoco rompe el build: escapa la etiqueta y la deja **visible** en la
    página publicada. Es el modo de falla más caro de todos, porque sólo se
    ve mirando el sitio con los ojos, y ninguna guarda existente lo detecta.
    """
    ofensas = [
        f"  línea {n}: {m.group(0)}"
        for n, l in enumerate(prosa(lee(pagina)).splitlines(), 1)
        for m in _HTML.finditer(l)
    ]
    assert not ofensas, (
        f"{pagina.name} usa HTML crudo; el renderizador lo escapa y sale "
        "visible:\n" + "\n".join(ofensas)
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_las_paginas_de_laboratorio_alternan_haz_y_deberias_ver(pagina):
    """Regla 10: el dispositivo que hace legible a una página con teclado.

    Es lo que sostiene a la unidad 6, donde aparece entre 9 y 15 veces por
    página. Sin él, el marco de la forma de página envuelve 160 líneas de
    prosa corrida con comandos sueltos adentro, y el lector no sabe cuáles
    teclea ni qué debería pasar cuando lo haga.

    Se exige a la página que tiene **laboratorio** —dos o más bloques
    ejecutables—, no a la que enseña un comando de ejemplo: la sesión 1 es sin
    computadora y cita comandos para leerlos, no para correrlos.
    """
    texto = lee(pagina)
    bloques = bloques_bash(texto)
    if len(bloques) < 2:
        return
    haz = texto.count("**Haz:**")
    ver = texto.count("**Deberías ver:**")
    assert haz >= 3 and ver >= 3, (
        f"{pagina.name} tiene {len(bloques)} bloques ejecutables y sólo "
        f"{haz} «Haz:» / {ver} «Deberías ver:»; el mínimo son 3 tramos"
    )
    assert ver <= haz, (
        f"{pagina.name} promete {ver} salidas para {haz} tramos"
    )
    largo = max(len(b.strip().splitlines()) for b in bloques)
    assert largo <= 15, (
        f"{pagina.name} tiene un bloque de {largo} líneas; el máximo son 15, "
        "o el tramo deja de caber de un vistazo"
    )


@pytest.mark.parametrize("pagina", LECCIONES, ids=IDS_PYTEST)
def test_ningun_bloque_ejecutable_pide_sudo_para_hablar_con_el_runtime(pagina):
    """`sudo docker` es el síntoma de una instalación a medias.

    La sección 2 dedica su página de instalación (2/10) y su plan B a dejar
    los dos runtimes corriendo **sin** `sudo`; un `sudo docker` en un bloque
    que el alumno copia enseña justo el hábito que esa página existe para
    quitar. El `sudo` de
    `apt-get`, `dnf` o `usermod` es otra cosa y sigue siendo legítimo.
    """
    ofensas = [
        f"  {l.strip()[:90]}"
        for bloque in bloques_bash(lee(pagina))
        for l in bloque.splitlines()
        if re.search(r"\bsudo\s+(docker|podman)\b", l)
    ]
    assert not ofensas, (
        f"{pagina.name} pide `sudo` para hablar con el runtime; la instalación "
        "de 2/10 existe para no necesitarlo:\n" + "\n".join(ofensas)
    )
