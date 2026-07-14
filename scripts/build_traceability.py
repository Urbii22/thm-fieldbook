"""Regenera la matriz de trazabilidad a partir de los frontmatter Markdown."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "_meta" / "matriz_de_trazabilidad.md"
README = DOCS / "README.md"


def metadata(text: str) -> tuple[str, list[str]]:
    raw = text.split("---", 2)[1]
    title = re.search(r"^titulo:\s*[\"']?(.+?)[\"']?$", raw, re.MULTILINE)
    sources = []
    in_sources = False
    for line in raw.splitlines():
        if line == "fuentes_internas:":
            in_sources = True; continue
        if in_sources and line.startswith("  - "):
            sources.append(line[4:])
        elif in_sources and line and not line.startswith(" "):
            break
    return (title.group(1) if title else "Sin título"), sources


def main() -> None:
    rows = []
    for path in sorted(DOCS.rglob("*.md")):
        if path in {OUT, DOCS / "BUILD.md"} or "pdf" in path.parts:
            continue
        title, sources = metadata(path.read_text(encoding="utf-8"))
        rel = path.relative_to(DOCS).as_posix()
        pdf = "__".join(path.relative_to(DOCS).with_suffix("").parts) + ".pdf"
        exercise = "08_ejercicios/cuaderno_de_ejercicios.md" if path.parent.name not in {"08_ejercicios", "09_examenes", "10_solucionarios", "11_chuletas", "_meta"} else "Según bloque"
        cheat = "11_chuletas/" if path.parent.name in {"03_seguridad_web", "04_linux", "05_windows", "06_active_directory", "07_redes_y_pivoting"} else "No aplica"
        rows.append(f"| [{title}](../{rel}) | {'<br>'.join(sources) or 'Documento editorial'} | Estructura didáctica y referencias declaradas | {exercise} | {cheat} | `../pdf/{pdf}` |")
    text = """---
titulo: Matriz de trazabilidad
categoria: Meta
dificultad: Inicial
prerrequisitos:
  - auditoria_repositorio.md
fuentes_internas:
  - ../../scripts/build_traceability.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# Matriz de trazabilidad

| Documento | Contenido de origen | Ampliaciones | Ejercicios | Chuleta | PDF |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    readme = README.read_text(encoding="utf-8")
    marker = "## Índice completo"
    if marker in readme:
        readme = readme.split(marker, 1)[0].rstrip() + "\n\n"
    index = [marker, ""]
    for folder in ["01_fundamentos", "02_metodologia", "03_seguridad_web", "04_linux", "05_windows", "06_active_directory", "07_redes_y_pivoting", "08_ejercicios", "09_examenes", "10_solucionarios", "11_chuletas"]:
        index.extend([f"### {folder}", ""])
        for path in sorted((DOCS / folder).glob("*.md")):
            title, _ = metadata(path.read_text(encoding="utf-8"))
            index.append(f"- [{title}]({path.relative_to(DOCS).as_posix()})")
        index.append("")
    index.extend(["### Trazabilidad y compilación", "", "- [Matriz de trazabilidad](_meta/matriz_de_trazabilidad.md)", "- [Compilar PDF](BUILD.md)", "- [Informe de progreso](_meta/progreso.md)", ""])
    README.write_text(readme + "\n".join(index), encoding="utf-8", newline="\n")
    print(f"{OUT}: {len(rows)} documentos")


if __name__ == "__main__":
    main()
