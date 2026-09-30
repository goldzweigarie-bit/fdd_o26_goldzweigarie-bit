# Reglas 5 y 6 de la revisión de entregas — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que la revisión automática comprueba el nombre de la branch de cada entrega y que un pull request toque una sola carpeta de la unidad.

**Architecture:** Dos reglas bloqueantes nuevas en `.github/scripts/revisa_entrega.py`, que hoy tiene cuatro. El mapa branch→carpeta viaja por el `env` del workflow, como `MANTENEDORES` y `BRANCH_ESTRICTA_DESDE`, para que el script siga sin leer nada del árbol de trabajo — ésa es la propiedad que hace seguro `pull_request_target`. La página del curso que promete estas comprobaciones se actualiza en el mismo commit, porque `CLAUDE.md` obliga a que el contenido y el script se muevan juntos.

**Tech Stack:** Python 3 (sólo biblioteca estándar), pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-15-unidad-8-contenedores-design.md`, sección «Dos reglas nuevas en la revisión automática».

## Global Constraints

- **El script no lee el árbol de trabajo.** Sólo `os.environ` y la API vía `gh`. `tools/test_revisa_entrega.py` lo asserta estructuralmente; no romper eso.
- **Sólo biblioteca estándar.** El runner de `entregas.yml` no instala nada.
- **Mensajes en español, sin acentos en el código fuente** — el script ya está escrito así ("Arreglo:", "Ojo:"), seguir la convención.
- **Todo mensaje de fallo dice qué archivo y qué hacer**, en dos o tres líneas. Es la regla de diseño declarada en el docstring del script.
- **No romper hacia atrás:** las entregas de la unidad 7 (`tarea-07-git` tocando `07_git/`, DataCamp tocando `github/`) tienen que seguir pasando.
- Correr la suite con `python3 -m pytest tools/test_revisa_entrega.py -q` desde `~/itam/fdd_o26`.

---

### Task 1: Regla 5 — el nombre de la branch

**Files:**
- Modify: `.github/scripts/revisa_entrega.py`
- Modify: `.github/workflows/entregas.yml` (bloque `env` del step «Revisar la entrega»)
- Test: `tools/test_revisa_entrega.py`

**Interfaces:**
- Produces: `PATRON_RAMA` (compilado, `re.Pattern`), `_mapa_tareas() -> dict[str, str]` — lee `TAREAS` del entorno y devuelve branch→subcarpeta. La Task 2 consume las dos.

- [ ] **Step 1: Escribe las pruebas que fallan**

Añade al final de la sección «las cuatro reglas, en las dos direcciones» de `tools/test_revisa_entrega.py`. Primero extiende el helper para que acepte el mapa — busca la firma de `_correr` y agrégale el parámetro y el `setenv`:

```python
def _correr(mod, monkeypatch, archivos, autor="ana", rama="tarea-07-git",
            mantenedores="uumami", rama_default="main", declarado=None,
            estricta_desde="", tareas=""):
    monkeypatch.setenv("AUTOR", autor)
    monkeypatch.setenv("RAMA", rama)
    monkeypatch.setenv("RAMA_DEFAULT", rama_default)
    monkeypatch.setenv("PR", "1")
    monkeypatch.setenv("MANTENEDORES", mantenedores)
    monkeypatch.setenv("BRANCH_ESTRICTA_DESDE", estricta_desde)
    monkeypatch.setenv("TAREAS", tareas)
    monkeypatch.setenv("GITHUB_REPOSITORY", "raya-lucaria/fdd_o26")
    monkeypatch.setattr(mod, "archivos_del_pr", lambda pr: archivos)
    n = len(archivos) if declarado is None else declarado
    monkeypatch.setattr(mod, "total_declarado", lambda pr: n)
    return mod.main()
```

Y las pruebas nuevas:

```python
# --- regla 5: el nombre de la branch ----------------------------------------

MAPA = ("tarea-08-datacamp-intro=docker,"
        "tarea-08-imagen=08_contenedores,"
        "tarea-08-datacamp-inter-1=docker,"
        "tarea-08-datacamp-inter-2=docker")


def test_branch_sin_nombre_de_tarea_falla(mod, monkeypatch):
    """Hoy una branch llamada 'x' pasa en verde: nadie mira el nombre."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="x", tareas=MAPA) == 1


def test_branch_con_nombre_de_tarea_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 0


def test_el_mensaje_de_branch_lista_los_nombres_validos(mod, monkeypatch, capsys):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    _correr(mod, monkeypatch, archivos, rama="mi-branch", tareas=MAPA)
    salida = capsys.readouterr().out
    assert "tarea-08-imagen" in salida


def test_la_branch_de_la_unidad_7_sigue_pasando(mod, monkeypatch):
    """No romper hacia atras: tarea-07-git casa con el patron."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="tarea-07-git") == 0


def test_desde_main_no_reporta_dos_veces_la_branch(mod, monkeypatch, capsys):
    """La regla 1 ya cubre main; la 5 no debe duplicar el fallo."""
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md")]
    _correr(mod, monkeypatch, archivos, rama="main", tareas=MAPA)
    salida = capsys.readouterr().out
    assert salida.count("BRANCH:") == 1
```

- [ ] **Step 2: Corre las pruebas y comprueba que fallan**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_revisa_entrega.py -q
```

Esperado: fallan `test_branch_sin_nombre_de_tarea_falla`,
`test_el_mensaje_de_branch_lista_los_nombres_validos` y
`test_desde_main_no_reporta_dos_veces_la_branch` (el script devuelve 0 o
imprime un solo BRANCH que es el de la regla 1). Las otras dos pasan ya.

- [ ] **Step 3: Implementa la regla**

En `.github/scripts/revisa_entrega.py`, agrega `import re` junto a los otros
imports, y debajo de `BASURA_SUFIJOS` estas dos piezas:

```python
# Las branches de entrega se llaman tarea-NN-nombre. El nombre exacto de cada
# una esta escrito en su tarea; aqui solo se comprueba la forma y, si el mapa
# esta disponible, que la carpeta corresponda.
PATRON_RAMA = re.compile(r"^tarea-\d{2}-[a-z0-9-]+$")


def _mapa_tareas():
    """branch -> subcarpeta esperada, tal como lo declara el workflow."""
    mapa = {}
    for par in os.environ.get("TAREAS", "").split(","):
        par = par.strip()
        if "=" in par:
            rama, carpeta = par.split("=", 1)
            mapa[rama.strip()] = carpeta.strip().strip("/")
    return mapa
```

Dentro de `main()`, justo después de la línea
`mio = f"{RAIZ_ESTUDIANTES}{autor}/"`, agrega:

```python
    mapa = _mapa_tareas()
```

Y justo después del bloque de la regla 1 (el `if rama == rama_default:` con su
`else`), agrega la regla 5:

```python
    # 5. El nombre de la branch. Se salta si el pull request sale de la rama
    # default, porque la regla 1 ya lo reporto y dos mensajes confunden.
    if rama != rama_default and not PATRON_RAMA.match(rama):
        nombres = ", ".join(sorted(mapa)) or "tarea-NN-nombre"
        fallos.append(
            f"BRANCH: '{rama}' no es el nombre de una entrega.\n"
            "  Cada tarea se entrega desde su propia branch, y el nombre exacto\n"
            "  esta escrito en la tarea. Los validos ahora mismo son:\n"
            f"    {nombres}\n"
            "  Arreglo: git switch -c <el nombre de tu tarea>, vuelve a\n"
            "  commitear ahi, haz push y abre el pull request desde esa branch."
        )
```

- [ ] **Step 4: Corre las pruebas y comprueba que pasan**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_revisa_entrega.py -q
```

Esperado: todas en verde.

- [ ] **Step 5: Declara `TAREAS` en el workflow**

En `.github/workflows/entregas.yml`, dentro del `env:` del step «Revisar la
entrega», debajo de `MANTENEDORES: uumami`, agrega:

```yaml
          # Mapa branch -> carpeta de cada entrega. El script lo lee de aqui y
          # nunca del arbol de trabajo: con pull_request_target, leer el repo
          # seria darle al pull request una via para reescribir sus propias
          # reglas. Cada unidad agrega sus lineas.
          TAREAS: >-
            tarea-08-datacamp-intro=docker,
            tarea-08-imagen=08_contenedores,
            tarea-08-datacamp-inter-1=docker,
            tarea-08-datacamp-inter-2=docker
```

- [ ] **Step 6: Comprueba que el workflow y el script siguen de acuerdo**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_revisa_entrega.py -q
```

Esperado: `test_el_workflow_exporta_lo_que_el_script_lee` sigue en verde. Si
falla, es porque el script lee una variable que el workflow no exporta o al
revés: revisa que el nombre sea exactamente `TAREAS` en los dos lados.

- [ ] **Step 7: Commit**

```bash
cd ~/itam/fdd_o26
git add .github/scripts/revisa_entrega.py .github/workflows/entregas.yml tools/test_revisa_entrega.py
git commit -m "feat(ci): la revision comprueba el nombre de la branch de cada entrega

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Regla 6 — una entrega, una carpeta

**Files:**
- Modify: `.github/scripts/revisa_entrega.py`
- Test: `tools/test_revisa_entrega.py`

**Interfaces:**
- Consumes: `PATRON_RAMA` y `_mapa_tareas()` de la Task 1.
- Produces: `subcarpeta(ruta, mio) -> str` — devuelve la primera carpeta bajo
  `estudiantes/<login>/`, o `""` si el archivo está suelto en la raíz.

- [ ] **Step 1: Escribe las pruebas que fallan**

```python
# --- regla 6: una entrega, una carpeta --------------------------------------

def test_dos_carpetas_en_un_pull_request_falla(mod, monkeypatch):
    """Las dos entregas del 22 en una sola branch salen hoy en verde."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md"),
                _f("estudiantes/ana/08_contenedores/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1


def test_una_sola_carpeta_pasa(mod, monkeypatch):
    archivos = [_f("estudiantes/ana/08_contenedores/bitacora.md"),
                _f("estudiantes/ana/08_contenedores/roto/Dockerfile")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 0


def test_archivo_suelto_en_la_raiz_no_cuenta_como_carpeta(mod, monkeypatch):
    """El .gitkeep de la primera entrega no debe invalidar nada."""
    archivos = [_f("estudiantes/ana/.gitkeep"),
                _f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-datacamp-intro", tareas=MAPA) == 0


def test_la_carpeta_no_corresponde_a_la_branch_falla(mod, monkeypatch):
    """Branch de la imagen tocando la carpeta de DataCamp."""
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1


def test_el_mensaje_dice_que_carpeta_esperaba(mod, monkeypatch, capsys):
    archivos = [_f("estudiantes/ana/docker/certificaciones.md")]
    _correr(mod, monkeypatch, archivos, rama="tarea-08-imagen", tareas=MAPA)
    salida = capsys.readouterr().out
    assert "08_contenedores" in salida


def test_sin_mapa_basta_con_una_carpeta(mod, monkeypatch):
    """Una branch que el mapa no conoce solo tiene que tocar una carpeta."""
    archivos = [_f("estudiantes/ana/07_git/bitacora.md")]
    assert _correr(mod, monkeypatch, archivos, rama="tarea-07-git") == 0


def test_un_rename_entre_carpetas_falla(mod, monkeypatch):
    """Mover de una entrega a otra toca dos carpetas y cuenta como dos."""
    archivos = [_f("estudiantes/ana/08_contenedores/notas.md",
                   status="renamed", previa="estudiantes/ana/docker/notas.md")]
    assert _correr(mod, monkeypatch, archivos,
                   rama="tarea-08-imagen", tareas=MAPA) == 1
```

- [ ] **Step 2: Corre las pruebas y comprueba que fallan**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_revisa_entrega.py -q
```

Esperado: fallan las cinco que esperan `1` o una cadena en la salida; el script
todavía devuelve `0` porque nadie mira las carpetas.

- [ ] **Step 3: Implementa el helper**

En `.github/scripts/revisa_entrega.py`, junto a `es_basura`:

```python
def subcarpeta(ruta, mio):
    """La carpeta de la entrega dentro de la del estudiante.

    `estudiantes/ana/docker/certificaciones.md` -> `docker`.
    Un archivo suelto en `estudiantes/ana/` devuelve "" y no cuenta: el
    .gitkeep de la primera entrega no puede invalidar la segunda.
    """
    resto = ruta[len(mio):]
    partes = resto.split("/")
    return partes[0] if len(partes) > 1 else ""
```

- [ ] **Step 4: Recoge las rutas propias en el bucle**

En `main()`, donde se declara `fuera, mal_nombre, basura = [], [], []`,
cámbialo por:

```python
    fuera, mal_nombre, basura, mias = [], [], [], []
```

Y dentro del `for ruta in rutas:`, el `if/elif` de ubicación pasa a tener
`else`:

```python
            if not ruta.startswith(RAIZ_ESTUDIANTES):
                fuera.append(ruta)
            elif not ruta.startswith(mio):
                partes = ruta.split("/")
                duenio = partes[1] if len(partes) > 2 else ""
                if duenio and duenio.lower() == autor.lower():
                    mal_nombre.append((ruta, duenio))
                else:
                    fuera.append(ruta)
            else:
                mias.append(ruta)
```

- [ ] **Step 5: Implementa la regla**

Después del bloque `if basura:` y antes del `for a in avisos:`:

```python
    # 6. Una entrega, una carpeta. Cierra tres cosas de un golpe: dos entregas
    # metidas en el mismo pull request, el conflicto add/add cuando las dos
    # agregan el mismo archivo, y el alumno que llena el certificaciones.md de
    # la unidad pasada.
    carpetas = {subcarpeta(r, mio) for r in mias}
    carpetas.discard("")
    esperada = mapa.get(rama)
    if esperada and carpetas and carpetas != {esperada}:
        fallos.append(
            f"CARPETA: la branch '{rama}' entrega en {mio}{esperada}/\n"
            f"  y este pull request toca: {', '.join(sorted(carpetas))}\n"
            "  Cada entrega vive en una sola carpeta. Si juntaste dos tareas,\n"
            "  separalas: una branch y un pull request por cada una, las dos\n"
            "  nacidas de main y no una de la otra."
        )
    elif len(carpetas) > 1:
        fallos.append(
            "CARPETA: este pull request toca mas de una carpeta de entrega.\n"
            f"  Encontre: {', '.join(sorted(carpetas))}\n"
            "  Cada entrega vive en una sola carpeta. Separalas en dos branches\n"
            "  y dos pull requests, las dos nacidas de main."
        )
```

- [ ] **Step 6: Corre las pruebas y comprueba que pasan**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/test_revisa_entrega.py -q
```

Esperado: todas en verde, incluidas las de la unidad 7.

- [ ] **Step 7: Commit**

```bash
cd ~/itam/fdd_o26
git add .github/scripts/revisa_entrega.py tools/test_revisa_entrega.py
git commit -m "feat(ci): una entrega toca una sola carpeta

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: La página del curso promete las seis reglas

**Files:**
- Modify: `course/7_git_y_github/2_github/4_el_flujo_del_curso.md`

`CLAUDE.md` lo pide con todas sus letras: «The content that promises these
checks is `course/7_git_y_github/2_github/4_el_flujo_del_curso.md`, so the two
move together». Un alumno no puede descubrir una regla nueva por un fallo en
rojo.

- [ ] **Step 1: Lee la sección que enumera las reglas**

```bash
cd ~/itam/fdd_o26 && grep -n "revisi" course/7_git_y_github/2_github/4_el_flujo_del_curso.md | head -20
```

Localiza la lista de cuatro reglas y la tabla de mensajes de error, si la hay.

- [ ] **Step 2: Agrega las dos reglas nuevas**

Con el registro de la unidad: qué comprueba, por qué, y qué hacer si sale en
rojo. Texto para insertar al final de la enumeración existente:

```markdown
5. **La branch se llama como la tarea.** Cada entrega trae escrito su nombre,
   con la forma `tarea-NN-nombre`. Una branch con otro nombre se rechaza, y el
   mensaje te dice cuáles son los válidos.
6. **Una entrega, una carpeta.** Un pull request toca **una sola** carpeta
   dentro de la tuya. Si juntas dos tareas en una branch, la revisión lo
   rechaza — y te ahorra el conflicto que se arma cuando las dos agregan el
   mismo archivo.
```

Y en la tabla de errores frecuentes, dos filas:

```markdown
| `BRANCH: '<nombre>' no es el nombre de una entrega` | La branch no se llama como la tarea | `git switch -c <el nombre de tu tarea>`, commitea ahí y abre el pull request desde esa branch |
| `CARPETA: este pull request toca mas de una carpeta` | Juntaste dos entregas | Sepáralas en dos branches, las dos nacidas de `main` |
```

- [ ] **Step 3: Recuerda lo que la revisión NO comprueba**

En el mismo párrafo donde la página ya explica el alcance del check verde,
asegúrate de que diga que **la regla del mirror no es machine-checked**, que es
lo que `CLAUDE.md` exige decir donde se describa. Si no está, agrégalo:

```markdown
> [!NOTE]
> El check verde significa «no rompiste las reglas del repositorio», no «tu
> tarea está completa». Que los archivos sean los que la tarea pide, y que la
> subcarpeta se llame como su espejo, lo reviso yo.
```

- [ ] **Step 4: Valida el curso**

```bash
cd ~/itam/raya_lucaria
UV_PROJECT_ENVIRONMENT=.venv-local uv run raya validate ~/itam/fdd_o26
```

Esperado: sin errores. Si aparece un fallo de MathJax o de objeto numerado,
revisa que ningún `$` ni `@` haya quedado fuera de un code span.

- [ ] **Step 5: Corre la suite completa**

```bash
cd ~/itam/fdd_o26 && python3 -m pytest tools/ -q
```

Esperado: 736 pruebas en verde más las once nuevas de las Tasks 1 y 2. Tarda
unos dos minutos y medio.

- [ ] **Step 6: Commit**

```bash
cd ~/itam/fdd_o26
git add course/7_git_y_github/2_github/4_el_flujo_del_curso.md
git commit -m "docs(unidad-7): el flujo promete las seis reglas de la revision

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Ensayo contra un pull request real

**Files:** ninguno — es una comprobación manual antes de que la regla juzgue a
treinta personas.

- [ ] **Step 1: Abre un pull request de prueba desde una branch mal nombrada**

Desde un fork propio, con una branch llamada `ensayo`, tocando un archivo
dentro de `estudiantes/<tu-login>/`. Comprueba que la revisión sale en rojo y
que el mensaje lista los nombres válidos.

- [ ] **Step 2: Repite con dos carpetas**

Branch `tarea-08-imagen`, tocando `docker/` y `08_contenedores/` a la vez.
Comprueba que el mensaje nombra las dos carpetas y la esperada.

- [ ] **Step 3: Repite con la entrega correcta**

Branch `tarea-08-imagen` tocando sólo `08_contenedores/`. Comprueba que sale en
verde.

- [ ] **Step 4: Cierra los pull requests de prueba y borra las branches**

---

## Self-review

**Cobertura del spec.** La sección «Dos reglas nuevas en la revisión
automática» pide tres cosas: la regla del nombre (Task 1), la regla de una
carpeta con su mapa (Task 2), y que la página del curso se mueva con el script
(Task 3). El mapa en el `env` del workflow está en la Task 1 Step 5, y la
propiedad de no leer el árbol se conserva porque `_mapa_tareas()` sólo toca
`os.environ`.

**Placeholders.** Ninguno: todo paso de código trae el código.

**Consistencia de tipos.** `_mapa_tareas()` devuelve `dict[str, str]` y se
consume como `mapa.get(rama)` en las dos tasks; `subcarpeta(ruta, mio)`
devuelve `str` y se consume dentro de un set comprehension. `PATRON_RAMA` se
usa sólo en la Task 1. `mias` se declara en la Task 2 Step 4 antes de usarse en
el Step 5.

**Riesgo conocido.** Si una unidad futura agrega tareas y nadie actualiza
`TAREAS`, la regla 6 cae al caso genérico («basta con una carpeta») en vez de
fallar: degrada, no bloquea. Es el comportamiento que queremos.
