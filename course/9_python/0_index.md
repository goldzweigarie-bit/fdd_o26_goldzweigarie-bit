---
id: python
title: "Python"
nav_title: "Python"
summary: "Python para trabajar con datos de forma profesional. Empieza por lo que todo proyecto necesita antes de su primera línea: un ambiente."
status: ready
estimated_time: 120m
tags: [python, uv, ambientes, venv, pip]
prerequisites: [contenedores]
---

# Python

**Una sección por ahora** · 12 páginas · unos 120 min

## En corto

- La unidad es Python para trabajar con datos de forma profesional: código que corre igual en tu máquina, en la de otra persona y en un contenedor.
- **Empieza por los ambientes**: dónde viven tus paquetes, qué versión de cada uno usa tu proyecto, y cómo se manejan con **uv**.
- Las demás secciones se agregan aquí cuando llega su clase.

## Las secciones

| # | Sección | Qué contesta | Sesión | Páginas | Min |
|---:|---|---|---|---:|---:|
| 1 | [[ambientes-python]] | Dónde viven tus paquetes, y cómo hacer que tu proyecto corra igual en otra máquina | jueves 1 de octubre, 19:00–20:00 | 12 | 120 |

## Antes de empezar

**uv** es un programa de terminal, publicado en 2024 por la empresa Astral, que hace con un solo comando lo que antes pedía cuatro herramientas: crear el ambiente, instalar paquetes, fijar sus versiones e instalar Python mismo.

Necesitas **uv instalado antes de clase**, en la terminal donde trabajas el repo: Linux, WSL2 o macOS, la misma donde instalaste Docker en la unidad 8.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Qué hace cada pieza:**

- `curl -LsSf <url>` — descarga el instalador oficial de uv (`-L` sigue redirecciones, `-sS` sin barra de progreso pero con errores, `-f` falla si el servidor responde con error).
- `| sh` — se lo pasa a la shell, que lo ejecuta: instala `uv` en `~/.local/bin` y agrega esa carpeta a tu `PATH`.

El `PATH` es la lista de carpetas donde la shell busca un programa cuando escribes su nombre. El instalador lo cambia en el archivo de configuración de tu shell, y ese archivo sólo se lee al abrir una terminal. Por eso: cierra la terminal, abre otra y comprueba:

```bash
uv --version
```

**Qué hace cada pieza:**

- `uv --version` — `--version` le pide a uv que imprima su versión y salga. Si responde, uv está instalado y la shell lo encuentra.

**Deberías ver** una línea `uv 0.12.…` o más nueva. Docker, de la unidad anterior, lo necesitas para una de las entregas.
