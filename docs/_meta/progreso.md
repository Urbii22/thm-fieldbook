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
revision: 2026-07-15
estado: borrador
---

# Progreso

| Lote | Estado | Archivos | Comprobaciones | Pendientes |
|---|---|---|---|---|
| 01 Auditoría | Completo | `auditoria_repositorio.md` | Árbol, fuentes, datos, pruebas y artefactos revisados | Mantener actualizado |
| 02 Mapa de fuentes | Completo | `mapa_fuentes.md` | Cobertura contrastada con 88 conceptos, 24 secciones y 12 guías | Refinar al crear módulos |
| 03 Programa | Completo | `00_programa_del_curso.md` | Dependencias y planificación de 14 semanas revisadas | Enlazar módulos al existir |
| 04 Estructura e índice | Completo | `../README.md` | Índice exhaustivo generado y carpetas creadas | Mantener con trazabilidad |
| 05 Fundamentos | Completo | `../01_fundamentos/*.md` | Cinco módulos; metadatos y navegación comprobados | Ampliar con ejercicios |
| 06 Metodología | Completo | `../02_metodologia/*.md` | Método general y construcción de payloads | Mantener referencias |
| 07 Seguridad web | Completo | `../03_seguridad_web/*.md` | 20 módulos con estructura obligatoria | Revisión editorial experta recomendada |
| 08 Linux | Completo | `../04_linux/*.md` | 14 módulos con estructura obligatoria | Revisión editorial experta recomendada |
| 09 Windows y AD | Completo | `../05_windows/*.md`, `../06_active_directory/*.md` | 18 módulos con estructura obligatoria | Revisión editorial experta recomendada |
| 10 Redes y pivoting | Completo | `../07_redes_y_pivoting/*.md` | 14 módulos con estructura obligatoria | Revisión editorial experta recomendada |
| 11 Ejercicios y exámenes | Completo | `../08_ejercicios/*.md`, `../09_examenes/*.md` | 20 ejercicios, tipo test y seis exámenes con rúbrica | Aplicar en laboratorio |
| 12 Solucionarios | Completo | `../10_solucionarios/*.md` | Soluciones separadas y razonadas | Ampliar tras pilotaje |
| 13 Chuletas | Completo | `../11_chuletas/*.md` | 14 chuletas generadas desde conceptos reales | Mantener sincronizadas |
| 14 PDF | Completo | `../BUILD.md`, `../../scripts/build_docs.py`, `../pdf/*.pdf` | 113 PDF; 685 páginas; render visual revisado | Manual completo opcional |
| 15 Control de calidad | Completo | `../../scripts/validate_docs.py`, `matriz_de_trazabilidad.md`, `informe_final.md` | Metadatos, enlaces, estructura, payloads, PDF y pruebas de aplicación OK | Revisión editorial experta recomendada |
| 16 Revisión pedagógica profunda | Completo | Fundamentos, metodología, 13 módulos técnicos prioritarios, cuaderno, solucionario e `informe_revision_pedagogica_fase2.md` | Casos A-D, anatomía, enlaces, bloques, exactitud técnica, ejercicios, pistas y PDF verificados | Sin pendientes en el alcance; ampliar otros módulos en una fase futura |

## Registro de decisiones

- Markdown será la fuente de verdad del curso.
- `web/data/content.json` se trata como artefacto generado.
- La lógica de la PWA no se modificará para construir el curso.
- No se crearán módulos vacíos para carencias detectadas.
- Las ampliaciones externas se identificarán por separado de las fuentes internas.
