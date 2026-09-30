---
id: disenar-con-contenedores
title: "Diseño y seguridad"
nav_title: "3. Diseño y seguridad"
summary: "Cómo se reparte una aplicación en servicios, por dónde se rompe el aislamiento, y qué hay más allá del contenedor."
status: ready
tags: [diseno, microservicio, red, seguridad, kata, gvisor]
---

# Diseño y seguridad

**Sección 3 de 3** · 5 páginas · unos 69 min · sesión del jueves 24 de septiembre, 19:00–20:30

Meta: pasar de correr contenedores a diseñar con ellos, y entender que la mayoría de los escapes de aislamiento no son bugs, son decisiones.

## En corto

- Llegan con volúmenes y redes ya practicados en DataCamp: la clase casi no gasta comandos, gasta decisiones.
- Cierra la pregunta que quedó abierta en la primera sesión: qué hay más allá del contenedor cuando compartir el kernel no es aceptable.
- No se usan APIs ni Python.

## Las cinco páginas

| # | Página | Qué agrega | Min |
|---:|---|---|---:|
| 1 | [[la-red-y-el-nombre]] | Que dos contenedores se hablen por nombre, y por qué publicar un puerto es una decisión de diseño | 12 |
| 2 | [[el-contrato-de-un-servicio]] | Qué es un microservicio sin decirlo como si fuera magia: puerto, variables, volumen | 15 |
| 3 | [[disenar-un-sistema]] | Dibujar un pipeline completo como servicios, antes de escribirlo | 15 |
| 4 | [[cuando-se-rompe-el-aislamiento]] | Las fugas reales de contenedor, y por qué casi todas fueron una mala configuración y no un bug | 15 |
| 5 | [[kata-y-el-espectro]] | Dos ejes distintos —dónde aterriza la syscall que no controlas, qué privilegio tiene quien se escapa— y dónde entra un segundo kernel | 12 |

## Qué te llevas

- Saber partir un sistema en servicios con un contrato explícito, y cuándo **no** conviene partirlo.
- Un vocabulario preciso de por dónde se rompe el aislamiento de un contenedor, sin exploits inventados.
- Un mapa de qué hay entre "proceso normal" y "máquina virtual completa", y cuándo cada punto de ese mapa es la respuesta correcta.
