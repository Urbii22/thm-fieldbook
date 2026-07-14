---
titulo: Progreso de construcción del curso
categoria: Meta
dificultad: Inicial
prerrequisitos: Ninguno
fuentes_internas:
  - auditoria_repositorio.md
  - mapa_fuentes.md
  - ../00_programa_del_curso.md
fuentes_externas: []
revision: 2026-07-14
estado: borrador
---

# Progreso

| Lote | Estado | Archivos | Comprobaciones | Pendientes |
|---|---|---|---|---|
| 01 Auditoría | Completo | `auditoria_repositorio.md` | Árbol, fuentes, datos, pruebas y artefactos revisados | Mantener actualizado |
| 02 Mapa de fuentes | Completo | `mapa_fuentes.md` | Cobertura contrastada con 88 conceptos, 24 secciones y 12 guías | Refinar al crear módulos |
| 03 Programa | Completo | `00_programa_del_curso.md` | Dependencias y planificación de 14 semanas revisadas | Enlazar módulos al existir |
| 04 Estructura e índice | Pendiente | - | - | Carpetas, README y navegación |
| 05 Fundamentos | Pendiente | - | - | Módulos de semanas 1 y 2 |
| 06 Metodología | Pendiente | - | - | Método general y construcción de payloads |
| 07 Seguridad web | Pendiente | - | - | Módulos con cobertura interna |
| 08 Linux | Pendiente | - | - | Módulos con cobertura interna |
| 09 Windows y AD | Pendiente | - | - | Módulos con cobertura interna |
| 10 Redes y pivoting | Pendiente | - | - | Módulos con cobertura interna |
| 11 Ejercicios y exámenes | Pendiente | - | - | Cuaderno, seis exámenes y rúbricas |
| 12 Solucionarios | Pendiente | - | - | Soluciones razonadas y separadas |
| 13 Chuletas | Pendiente | - | - | 14 chuletas operativas |
| 14 PDF | Pendiente | - | - | Generador, PDF por módulo/bloque y BUILD |
| 15 Control de calidad | Pendiente | - | Línea base: Python 20/20; Node 7/7; diff limpio | Enlaces, payloads, PDF e informe final |

## Registro de decisiones

- Markdown será la fuente de verdad del curso.
- `web/data/content.json` se trata como artefacto generado.
- La lógica de la PWA no se modificará para construir el curso.
- No se crearán módulos vacíos para carencias detectadas.
- Las ampliaciones externas se identificarán por separado de las fuentes internas.

