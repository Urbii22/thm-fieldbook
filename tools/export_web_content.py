from __future__ import annotations

import argparse
import ast
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "web" / "data" / "content.json"


MASTER_SECTION_SLUGS = {
    "ultra-quick-start": "ultra-quick-start",
    "arquetipos-de-rooms": "arquetipos-de-rooms",
    "web-moderna-y-apis": "web-y-apis",
    "metodologia-cve-exploit": "cve-y-exploits",
    "credenciales-cracking-y-loot": "credenciales-y-loot",
    "plantilla-de-room-writeup": "notas-y-cierre",
    "equivalencias-windows-linux": "equivalencias",
    "errores-tipicos": "errores-tipicos",
    "checklist-de-atasco": "checklist-de-atasco",
}


TAG_RULES = {
    "web": ["web", "api", "jwt", "idor", "ssrf", "upload", "wordpress", "sqli", "graphql"],
    "windows": ["windows", "winrm", "powershell", "privilege", "registry", "servicios"],
    "linux": ["linux", "suid", "sudo", "cron", "caps"],
    "credentials": ["cred", "hash", "loot", "john", "hashcat", "password", "keePass"],
    "pivoting": ["pivot", "tunnel", "chisel", "ligolo", "proxychains", "ssh -l"],
    "recon": ["recon", "nmap", "enumer", "servicios", "dns", "smb"],
    "exploit": ["cve", "exploit", "poc", "rce"],
    "workflow": ["quick", "mapa", "arquetipos", "checklist", "notas", "cierre"],
    "active-directory": ["active directory", "kerberos", "ldap", "bloodhound", "dominio"],
}

CURATED_TAGS = {
    "ultra-quick-start": ["recon", "workflow"],
    "mentalidad-y-preparacion": ["recon", "workflow"],
    "mapa-de-decisiones": ["recon", "workflow"],
    "arquetipos-de-rooms": ["recon", "workflow"],
    "recon-y-servicios": ["recon"],
    "web-y-apis": ["web"],
    "wordpress": ["web"],
    "sqli": ["web"],
    "credenciales-y-loot": ["credentials"],
    "acceso-inicial": ["credentials", "exploit", "linux", "windows"],
    "linux-privesc": ["linux"],
    "windows-privesc": ["windows"],
    "active-directory": ["active-directory", "credentials", "windows"],
    "pivoting": ["pivoting"],
    "cve-y-exploits": ["exploit"],
    "errores-tipicos": ["workflow"],
    "checklist-de-atasco": ["workflow"],
    "notas-y-cierre": ["workflow"],
    "equivalencias": ["linux", "windows"],
}

PHASE_RULES = [
    ("privesc", ["privesc", "privilege escalation"]),
    ("pivot", ["pivot"]),
    ("access", ["acceso", "credenciales", "loot", "cve", "exploit"]),
    ("enumeration", ["web", "api", "wordpress", "sqli", "active directory"]),
    ("closeout", ["writeup", "notas", "cierre", "equivalencias", "errores", "checklist"]),
    ("recon", ["quick", "recon", "servicios", "arquetipos", "mentalidad", "mapa"]),
]

SHORTCUTS = [
    {
        "label": "Estoy atascado",
        "query": "checklist atasco errores hipotesis reenumerar",
        "target": "checklist-de-atasco",
    },
    {
        "label": "Tengo credenciales",
        "query": "credenciales loot hash cracking reuse smb ssh winrm",
        "target": "credenciales-y-loot",
    },
    {
        "label": "Tengo shell",
        "query": "acceso inicial shell estabilizar privesc post exploit",
        "target": "acceso-inicial",
    },
    {
        "label": "Veo una web",
        "query": "web api idor jwt upload sqli wordpress discovery",
        "target": "web-y-apis",
    },
    {
        "label": "Necesito pivotar",
        "query": "pivoting tunneling chisel ligolo proxychains ssh tunel",
        "target": "pivoting",
    },
    {
        "label": "Tengo una version/CVE",
        "query": "cve exploit poc version verificar payload",
        "target": "cve-y-exploits",
    },
]


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def slugify(value: str) -> str:
    plain = strip_accents(value).lower()
    plain = re.sub(r"[^a-z0-9]+", "-", plain)
    return plain.strip("-")


def normalize_text(value: Any) -> str:
    text = str(value)
    replacements = {
        "â€”": "-",
        "â€“": "-",
        "â€œ": '"',
        "â€": '"',
        "â€˜": "'",
        "â€™": "'",
        "â†’": "->",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def flatten_block(block: tuple[Any, ...]) -> tuple[list[str], list[str], list[list[str]]]:
    kind = block[0]
    text_parts: list[str] = []
    commands: list[str] = []
    tables: list[list[str]] = []

    if kind in {"p", "h2"}:
        text_parts.append(normalize_text(block[1]))
    elif kind == "code":
        commands.extend(normalize_text(line) for line in block[1])
        text_parts.extend(commands)
    elif kind == "table":
        for row in block[1]:
            cells = [normalize_text(cell) for cell in row]
            tables.append(cells)
            text_parts.append(" ".join(cells))
    elif kind == "bullets":
        text_parts.extend(normalize_text(item) for item in block[1])

    return text_parts, commands, tables


def infer_tags(title: str, summary: str, search_text: str) -> list[str]:
    curated = CURATED_TAGS.get(slugify(title))
    if curated:
        return curated
    haystack = strip_accents(f"{title} {summary} {search_text}").lower()
    tags = []
    for tag, needles in TAG_RULES.items():
        if any(strip_accents(needle).lower() in haystack for needle in needles):
            tags.append(tag)
    return sorted(set(tags or ["workflow"]))


def infer_phase(title: str, summary: str, tags: list[str]) -> str:
    primary = strip_accents(f"{title} {summary}").lower()
    for phase, needles in PHASE_RULES:
        if any(needle in primary for needle in needles):
            return phase
    tag_text = strip_accents(" ".join(tags)).lower()
    if "pivoting" in tag_text:
        return "pivot"
    if "exploit" in tag_text or "credentials" in tag_text:
        return "access"
    return "reference"


def normalize_section(section: dict[str, Any], index: int) -> dict[str, Any]:
    title = normalize_text(section["short"])
    summary = normalize_text(section.get("summary", ""))
    text_parts = [title, summary]
    commands: list[str] = []
    tables: list[list[str]] = []

    for block in section.get("blocks", []):
        block_text, block_commands, block_tables = flatten_block(block)
        text_parts.extend(block_text)
        commands.extend(block_commands)
        tables.extend(block_tables)

    search_text = " ".join(part for part in text_parts if part)
    tags = infer_tags(title, summary, search_text)
    return {
        "id": f"section-{index:02d}",
        "order": index,
        "slug": slugify(title),
        "title": title,
        "summary": summary,
        "phase": infer_phase(title, summary, tags),
        "tags": tags,
        "commands": commands,
        "tables": tables,
        "blocks": section.get("blocks", []),
        "searchText": search_text,
    }


def extract_master_commands(doc: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for section in doc.get("sections", []):
        for key in ("code", "code2"):
            for line in section.get(key, []):
                command = normalize_text(line).strip()
                if command:
                    commands.append(command)
    return commands


def load_master_docs() -> list[dict[str, Any]]:
    source_path = ROOT / "tools" / "generate_thm_playbook.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "GENERATED_DOCS" for target in node.targets):
            expression = ast.Expression(node.value)
            ast.fix_missing_locations(expression)
            return eval(compile(expression, str(source_path), "eval"), {"__builtins__": {}}, {"cm": 1})
    raise RuntimeError("No GENERATED_DOCS assignment found in generate_thm_playbook.py")


def build_master_command_index() -> dict[str, list[str]]:
    command_index: dict[str, list[str]] = {}
    for doc in load_master_docs():
        source_slug = slugify(normalize_text(doc.get("short", "")))
        target_slug = MASTER_SECTION_SLUGS.get(source_slug)
        if not target_slug:
            continue
        command_index[target_slug] = extract_master_commands(doc)
    return command_index


def should_merge_master_commands(sections: list[dict[str, Any]]) -> bool:
    slugs = {section["slug"] for section in sections}
    return len(sections) >= 10 and bool(slugs.intersection(MASTER_SECTION_SLUGS.values()))


def merge_master_commands(sections: list[dict[str, Any]]) -> None:
    if not should_merge_master_commands(sections):
        return

    master_commands = build_master_command_index()
    for section in sections:
        supplemental = master_commands.get(section["slug"], [])
        if not supplemental:
            continue

        seen = set(section["commands"])
        additions = [command for command in supplemental if command not in seen]
        if not additions:
            continue

        section["commands"].extend(additions)
        section["searchText"] = " ".join([section["searchText"], *additions])


def load_guides() -> list[dict[str, Any]]:
    source_path = ROOT / "tools" / "guides.py"
    if not source_path.exists():
        return []
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "GUIDES" for target in node.targets
        ):
            return ast.literal_eval(node.value)
    return []


def build_payload(sections: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_sections = [normalize_section(section, index) for index, section in enumerate(sections, 1)]
    merge_master_commands(normalized_sections)
    all_tags = sorted({tag for section in normalized_sections for tag in section["tags"]})
    phases = sorted({section["phase"] for section in normalized_sections})
    guides = load_guides()

    return {
        "generatedAt": date.today().isoformat(),
        "stats": {
            "totalSections": len(normalized_sections),
            "totalCommands": sum(len(section["commands"]) for section in normalized_sections),
            "totalTags": len(all_tags),
            "totalGuides": len(guides),
        },
        "tags": all_tags,
        "phases": phases,
        "shortcuts": SHORTCUTS,
        "sections": normalized_sections,
        "guides": guides,
    }


def load_source_sections() -> list[dict[str, Any]]:
    source_path = ROOT / "tools" / "generate_structured_playbook.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SECTIONS" for target in node.targets):
            expression = ast.Expression(node.value)
            ast.fix_missing_locations(expression)
            return eval(compile(expression, str(source_path), "eval"), {"__builtins__": {}}, {"cm": 1})
    raise RuntimeError("No SECTIONS assignment found in generate_structured_playbook.py")


def write_payload(output_path: Path = DEFAULT_OUTPUT) -> Path:
    payload = build_payload(load_source_sections())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export THM structured playbook content for the web app.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    path = write_payload(args.output)
    print(path)


if __name__ == "__main__":
    main()
