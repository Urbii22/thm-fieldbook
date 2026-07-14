"""Valida metadatos, enlaces, estructura, payloads y PDF del curso."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from scripts.scaffold_course_modules import BY_ID, GROUPS, slug


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REQUIRED_META = {
    "titulo", "categoria", "dificultad", "prerrequisitos", "fuentes_internas",
    "fuentes_externas", "revision", "estado",
}
REQUIRED_MODULE = {
    "## Objetivos de aprendizaje", "## Prerrequisitos", "## Fundamentos técnicos",
    "## Modelo mental", "## Superficie de ataque", "## Cómo identificarla",
    "## Preguntas que debo hacerme", "## Prueba mínima",
    "## Construcción progresiva del payload", "## Anatomía de los payloads",
    "## Variaciones según el contexto", "## Filtros y bypasses",
    "## Evidencias de confirmación", "## Escalado de impacto",
    "## Errores frecuentes", "## Diagnóstico de payloads fallidos", "## Mitigaciones",
    "## Relación con pentesting y certificaciones", "## Caso guiado",
    "## Caso de adaptación", "## Ejercicios", "## Resumen",
    "## Chuleta operativa", "## Referencias",
}


def validate() -> list[str]:
    errors = []
    files = sorted(DOCS.rglob("*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or text.count("---") < 2:
            errors.append(f"{path}: frontmatter ausente")
            continue
        raw = text.split("---", 2)[1]
        keys = {match.group(1) for match in re.finditer(r"^([a-z_]+):", raw, re.MULTILINE)}
        missing = REQUIRED_META - keys
        if missing:
            errors.append(f"{path}: metadatos ausentes {sorted(missing)}")
        if text.count("```") % 2:
            errors.append(f"{path}: bloque de código sin cerrar")
        if re.search(r"\b(TBD|FIXME)\b|<PLACEHOLDER>", text):
            errors.append(f"{path}: marcador sin resolver")
        lines = text.splitlines()
        for index, line in enumerate(lines[:-1]):
            if not line.startswith("|") or not re.match(r"^\|?\s*:?-+", lines[index + 1]):
                continue
            expected = len(re.split(r"(?<!\\)\|", line.strip("|")))
            row = index + 2
            while row < len(lines) and lines[row].startswith("|"):
                actual = len(re.split(r"(?<!\\)\|", lines[row].strip("|")))
                if actual != expected:
                    errors.append(
                        f"{path}:{row + 1}: tabla con {actual} columnas; se esperaban {expected}"
                    )
                row += 1
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            clean = target.split("#", 1)[0]
            if clean and "://" not in clean and not (path.parent / clean).resolve().exists():
                errors.append(f"{path}: enlace roto {target}")
    for folder, identifiers in GROUPS.items():
        for identifier in identifiers:
            path = DOCS / folder / slug(identifier)
            text = path.read_text(encoding="utf-8")
            missing = REQUIRED_MODULE - {line.strip() for line in text.splitlines()}
            if missing:
                errors.append(f"{path}: secciones ausentes {sorted(missing)}")
            for entry in BY_ID[identifier].get("commands", []):
                command = entry.get("cmd", "")
                if command and command not in text:
                    errors.append(f"{path}: payload alterado {command!r}")
    pdfs = list((DOCS / "pdf").glob("*.pdf"))
    markdown_count = len([p for p in files if p.name != "BUILD.md" and "pdf" not in p.parts])
    if len(pdfs) < markdown_count:
        errors.append(f"PDF insuficientes: {len(pdfs)} para {markdown_count} fuentes")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("OK: metadatos, enlaces, estructura, payloads y cobertura PDF")
