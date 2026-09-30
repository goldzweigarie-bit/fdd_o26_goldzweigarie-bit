"""Guarda: ningun marcador de callout sale impreso como texto.

El renderizador de Raya convierte en callout **solo** la linea que casa entera
con este patron (`packages/static/src/raya_static/rendering.py`, verificado
contra el SHA pineado en `.github/workflows/pages.yml`):

    _CALLOUT_MARKER_RE = re.compile(
        r"^\\s{0,3}>\\s*\\[!(NOTE|TIP|WARNING|CAUTION)\\]\\s*$", re.IGNORECASE
    )

Lo que no casa **no falla el build**: cae al camino de blockquote normal y el
marcador sale impreso como texto, de modo que el lector ve un parrafo citado que
empieza con un literal `[!IMPORTANT]`. Ni `raya validate` ni `raya build` dicen
una palabra. Es un fallo mudo, y por eso necesita guarda.

Hay **cinco** formas de caerse, no una, y las cinco se han escrito de verdad.
Las cuatro de sintaxis:

1. clase que el renderizador no conoce — `[!IMPORTANT]` estuvo publicado en
   `7_git_y_github/2_github/2_el_fork.md` y en
   `3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md`;
2. **texto en la misma linea** que el marcador (`> [!NOTE] Cuerpo aqui`) — es la
   forma que el spec de la unidad 8 escribia al citar el cierre de pagina, asi
   que estaba a un copiar-y-pegar de entrar;
3. **indentacion de mas de tres espacios** antes del `>`;
4. **blockquote anidado** (`> > [!NOTE]`).

Por eso esta guarda NO pregunta "¿la clase es valida?". Pregunta "¿esta linea
parece un marcador y no lo es?", que es la pregunta cuya respuesta el lector ve.

Y hay una quinta forma, que no es de sintaxis sino de sitio: un marcador
**perfectamente valido dentro de un bloque `::: ...`** (`problem`, `answer`,
`hint`, `definition`, `table`, `figure`) tampoco renderiza — el cuerpo de la
directiva se procesa aparte y el marcador sale impreso. Pasó de verdad, en el
`::: answer` de `1_la_idea/3_receta_imagen_contenedor.md`, y no lo detectaba
ninguna guarda porque la sintaxis era correcta. Dentro de una directiva, el
enfasis va en prosa con negritas.

Los bloques cercados se saltan: una pagina tiene derecho a mostrar un marcador
roto como contraejemplo dentro de un fence. (Aviso: `_extract_callouts` del
framework corre sobre el cuerpo entero **antes** de `_md.parse` y tampoco es
fence-aware, asi que un marcador *valido* dentro de un fence si lo arranca del
bloque de codigo. Es un bug de Raya, no de esta guarda; no escribas marcadores
validos dentro de fences.)
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
CURSO = RAIZ / "course"

# Las cuatro clases que el renderizador reconoce, en el orden en que las declara.
RECONOCIDAS = ("NOTE", "TIP", "WARNING", "CAUTION")

# Copia verbatim de `_CALLOUT_MARKER_RE`. Si Raya cambia, esto cambia con el SHA
# pineado en `pages.yml` y no antes.
_MARCADOR_VALIDO = re.compile(
    r"^\s{0,3}>\s*\[!(" + "|".join(RECONOCIDAS) + r")\]\s*$",
    re.IGNORECASE,
)

# Deliberadamente mas ancho que el del framework: cualquier cosa que un autor
# escribiria creyendo que abre un callout. Lo que caiga aqui y no en el de
# arriba es, exactamente, lo que sale impreso.
_PARECE_MARCADOR = re.compile(r"^\s*>[\s>]*\[!")

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")
_ABRE_DIRECTIVA = re.compile(r"^::: \w+")
_CIERRA_DIRECTIVA = re.compile(r"^:::\s*$")

PAGINAS = sorted(CURSO.glob("**/*.md"))


def _por_que_no_renderiza(linea: str) -> str:
    """El diagnostico concreto, para que el mensaje diga que arreglar."""
    clase = re.search(r"\[!([^\]]*)\]", linea)
    nombre = clase.group(1) if clase else ""
    if re.match(r"^\s*>\s*>", linea):
        return "es un blockquote anidado (`> >`); el marcador va en el primer nivel"
    if re.match(r"^\s{4,}>", linea):
        return "lleva mas de tres espacios de indentacion antes del `>`"
    if nombre.upper() not in RECONOCIDAS:
        return (
            f"`[!{nombre}]` no es una clase que Raya renderice; "
            f"las validas son {', '.join(RECONOCIDAS)}"
        )
    return "lleva texto en la misma linea; el cuerpo va en la linea siguiente"


def test_el_curso_tiene_paginas_que_revisar():
    """Si el glob se queda vacio, la guarda pasa sin haber mirado nada."""
    assert PAGINAS, f"no se encontro ninguna pagina bajo {CURSO}"


def test_la_guarda_distingue_lo_que_renderiza_de_lo_que_no():
    """La guarda se comprueba a si misma contra los casos que persigue.

    Sin esto, un cambio que afloje `_PARECE_MARCADOR` dejaria de detectar y
    ningun test lo diria: la suite seguiria verde porque el curso esta limpio.
    """
    for bueno in ("> [!NOTE]", ">[!warning]", "   > [!TIP]", "> [!CAUTION]  "):
        assert _MARCADOR_VALIDO.match(bueno), bueno
        assert not (_PARECE_MARCADOR.match(bueno) and not _MARCADOR_VALIDO.match(bueno))
    for malo in (
        "> [!IMPORTANT]",
        "> [!NOTE] Cuerpo en la misma linea.",
        "> [!IMPORTANT!]",
        "> [!NOTA IMPORTANTE]",
        "> [!TIP-2]",
        "    > [!NOTE]",
        "> > [!NOTE]",
    ):
        assert _PARECE_MARCADOR.match(malo), f"no se detecta como marcador: {malo}"
        assert not _MARCADOR_VALIDO.match(malo), f"no deberia renderizar: {malo}"
        assert _por_que_no_renderiza(malo), malo


@pytest.mark.parametrize(
    "pagina", PAGINAS, ids=[str(p.relative_to(CURSO)) for p in PAGINAS]
)
def test_ningun_marcador_de_callout_sale_como_texto_literal(pagina):
    rotos, dentro_de_fence, dentro_de_directiva = [], False, False
    for numero, linea in enumerate(
        pagina.read_text(encoding="utf-8").splitlines(), 1
    ):
        if _FENCE.match(linea):
            dentro_de_fence = not dentro_de_fence
            continue
        if dentro_de_fence:
            continue
        if _ABRE_DIRECTIVA.match(linea):
            dentro_de_directiva = True
            continue
        if _CIERRA_DIRECTIVA.match(linea):
            dentro_de_directiva = False
            continue
        if not _PARECE_MARCADOR.match(linea):
            continue
        if dentro_de_directiva:
            rotos.append((
                numero, linea.strip(),
                "esta dentro de un bloque `::: ...`, donde ningun callout "
                "renderiza aunque la sintaxis sea correcta: usa negritas en prosa",
            ))
        elif not _MARCADOR_VALIDO.match(linea):
            rotos.append((numero, linea.strip(), _por_que_no_renderiza(linea)))
    assert not rotos, (
        f"{pagina.relative_to(CURSO)} escribe marcadores de callout que Raya no "
        "renderiza: saldran impresos como texto y ningun build lo dira.\n"
        + "\n".join(f"  linea {n}: {t}\n    -> {d}" for n, t, d in rotos)
    )
