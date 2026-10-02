# Créditos de materiales de la unidad

Procedencia, ruta y condición de uso de cada material del directorio.

Los SVG salen de `tools/gen_python.py`, que es su única fuente de verdad. No se
editan a mano, se regeneran. La guarda `tools/test_gen_python.py` falla si un
archivo del disco deja de coincidir con lo que produce el generador.

| Archivo | Descripción y prompt resumido | Autor / origen | Fecha | Licencia |
|---|---|---|---|---|
| py-mapa.svg | Ruta: `course/9_python/_assets/py-mapa.svg`. Qué produce qué en un proyecto uv: `pyproject.toml` → `uv lock` → `uv.lock` → `uv sync` → `.venv/` → `uv run`, con PyPI, `uv python install` y la franja de qué va a git y qué no. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-choque.svg | Ruta: `course/9_python/_assets/py-choque.svg`. Dos proyectos que piden versiones distintas de pandas: sin ambientes comparten un solo `site-packages/` y el último que instala gana; con un `.venv/` por proyecto cada uno guarda la suya. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-path.svg | Ruta: `course/9_python/_assets/py-path.svg`. Las carpetas del `PATH` en el orden en que la shell busca `python`, sin activar y después de `source .venv/bin/activate`. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-venv-arbol.svg | Ruta: `course/9_python/_assets/py-venv-arbol.svg`. El árbol de `.venv/` (`bin/python`, `bin/activate`, `site-packages/`, `pyvenv.cfg`) con qué es cada rama. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-trabajos.svg | Ruta: `course/9_python/_assets/py-trabajos.svg`. Matriz de doce herramientas (pip, venv, pip-tools, pipenv, poetry, pdm, hatch, conda, pixi, pyenv, pipx, uv) contra cinco trabajos: instalar paquetes, aislar, proyecto + lock, versiones de Python, herramientas de terminal. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-cual-uso.svg | Ruta: `course/9_python/_assets/py-cual-uso.svg`. Árbol de decisión de tres preguntas que termina en pixi/conda, la herramienta que ya usa el proyecto, `uv run` con PEP 723, o `uv init` + `uv add`. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-aislamiento.svg | Ruta: `course/9_python/_assets/py-aislamiento.svg`. Cuatro capas (paquetes, intérprete, librerías del sistema, kernel) y qué cubre un `.venv` de uv, conda/pixi y Docker. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
| py-uv-docker.svg | Ruta: `course/9_python/_assets/py-uv-docker.svg`. Las cinco etapas del Dockerfile de la entrega en orden —base, uv, archivos del ambiente, crear el ambiente desde el lock, el programa— con la capa en caché señalada, sin las instrucciones literales. | Generado por `tools/gen_python.py`; obra propia | 2026-10-01 | Uso docente del curso |
