---
titulo: Compilación de la documentación
categoria: Construcción
dificultad: Inicial
prerrequisitos: []
fuentes_internas:
  - ../scripts/build_docs.py
fuentes_externas:
  - https://www.reportlab.com/docs/reportlab-userguide.pdf
revision: 2026-07-14
estado: revisado
---

# Compilación de la documentación

Markdown bajo `docs/` es la fuente de verdad. Los PDF de `docs/pdf/` no se editan manualmente.

## Requisitos

- Python 3.11 o posterior.
- ReportLab.
- PyPDF y Poppler para validación.

En Codex Desktop puede usarse el Python incluido:

```powershell
& "$HOME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" scripts\build_docs.py --clean
```

Con un entorno propio:

```powershell
python -m pip install reportlab pypdf
python scripts\build_docs.py --clean
```

## Salidas

- Un PDF por Markdown.
- Un PDF agregado por bloque.
- Cuaderno, exámenes, solucionario y chuletas dentro de sus bloques.
- Manual completo opcional con `--manual-completo`.

```powershell
python scripts\build_docs.py --clean --manual-completo
```

El generador añade índice de bloque, numeración, encabezado/pie, tipografía Unicode, tablas con cabecera repetida y bloques de código mantenidos juntos cuando caben en una página.

## Revisión visual

```powershell
pdftoppm -f 1 -singlefile -png docs\pdf\bloque__01_fundamentos.pdf tmp\pdfs\fundamentos
```

Revisa índice, acentos, tablas, bloques, márgenes y pie. La validación automática complementa, pero no sustituye, esta inspección.
