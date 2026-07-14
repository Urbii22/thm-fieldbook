"""Materializa módulos Markdown desde los conceptos editoriales de Fieldbook.

El resultado es un punto de partida versionado: después de generarlo, Markdown
es la fuente editorial del curso y este script no participa en la aplicación.
"""
from __future__ import annotations

import re
import json
from pathlib import Path

from tools.concepts import CONCEPTS


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BY_ID = {item["id"]: item for item in CONCEPTS}

GROUPS = {
    "03_seguridad_web": [
        "enum-wildcard-responses", "auth-session-security", "mfa-otp-bypass",
        "client-side-controls", "idor-bola", "sqli", "lfi", "lfi-a-rce",
        "file-upload", "ssrf", "command-injection", "argument-injection",
        "xss", "ssti", "xxe", "jwt-security", "api-testing-model",
        "graphql-security", "oauth-oidc-cors", "wordpress",
    ],
    "04_linux": [
        "enum-privesc-linux", "sudo-abuse", "suid", "capabilities",
        "cron-abuse", "path-hijacking", "wildcard-injection",
        "sudo-ld-preload", "python-library-hijacking", "writable-sensitive-files",
        "group-abuse-linux", "nfs-no-root-squash", "docker-container-escape",
        "kernel-exploits-linux",
    ],
    "05_windows": [
        "enum-privesc-windows", "service-misconfig-windows",
        "always-install-elevated", "stored-credentials-windows",
        "registry-autoruns", "token-impersonation", "dll-hijacking",
        "sebackup-serestore", "uac-bypass", "kernel-exploits-windows",
    ],
    "06_active_directory": [
        "ad-modelo", "ldap-enum", "kerberos", "asrep-kerberoast", "ntlm-pth",
        "bloodhound", "ad-cs", "ad-tickets-trusts",
    ],
    "07_redes_y_pivoting": [
        "recon-metodologia", "fingerprinting-servicios", "tcp-vs-udp", "dns-enum",
        "smb-enum", "ftp-enum", "smtp-enum", "snmp-enum", "nfs-enum",
        "packet-analysis", "network-segmentation-firewalls", "pivoting-tunel",
        "pivot-troubleshooting", "network-traffic-mitm",
    ],
}

CHEATS = {
    "enumeracion_inicial": ["recon-metodologia", "fingerprinting-servicios", "dns-enum", "smb-enum"],
    "http_y_burp": ["burp-manual-testing", "api-testing-model", "auth-session-security"],
    "sql_injection": ["sqli"],
    "lfi_y_path_traversal": ["lfi", "lfi-a-rce"],
    "ssrf": ["ssrf"],
    "file_upload": ["file-upload"],
    "command_y_argument_injection": ["command-injection", "argument-injection"],
    "reverse_shells": ["reverse-vs-bind"],
    "escalada_linux": ["enum-privesc-linux", "sudo-abuse", "suid", "capabilities", "cron-abuse"],
    "windows": ["enum-privesc-windows", "service-misconfig-windows", "token-impersonation"],
    "active_directory": ["ad-modelo", "ldap-enum", "asrep-kerberoast", "bloodhound"],
    "redes_y_pivoting": ["network-segmentation-firewalls", "pivoting-tunel", "pivot-troubleshooting"],
    "interpretacion_de_puertos": ["fingerprinting-servicios", "tcp-vs-udp"],
    "estabilizacion_de_shells": ["tty-stabilization", "shell-troubleshooting"],
}

EXTERNAL = {
    "03_seguridad_web": "https://portswigger.net/web-security/all-materials",
    "04_linux": "https://man7.org/linux/man-pages/",
    "05_windows": "https://learn.microsoft.com/en-us/windows/security/",
    "06_active_directory": "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/",
    "07_redes_y_pivoting": "https://www.rfc-editor.org/",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") + ".md"


def bullets(values: list[str]) -> str:
    return "\n".join(f"- {clean(value)}" for value in values) if values else "- No aplica según la fuente interna."


def clean(value: str) -> str:
    """Convierte los enlaces wiki de la PWA en referencias legibles en Markdown."""
    return re.sub(r"\[\[([^]]+)\]\]", r"`\1`", value)


def command_blocks(item: dict) -> str:
    commands = item.get("commands", [])
    if not commands:
        return "La fuente interna no fija una cadena universal. Construye la prueba desde la observación y la documentación de la versión detectada."
    parts = []
    for index, entry in enumerate(commands, 1):
        command = entry.get("cmd", "").rstrip()
        parts.append(
            f"### Capa {index}: prueba documentada\n\n"
            f"```text\n{command}\n```\n\n"
            f"**Objetivo y contexto:** {clean(entry.get('why', 'Aplicar solo cuando coincidan los prerrequisitos descritos.'))}\n\n"
            f"**Resultado esperado:** {clean(entry.get('out', item.get('resultado', 'Una diferencia reproducible.')))}"
        )
    return "\n\n".join(parts)


def anatomy(item: dict) -> str:
    commands = item.get("commands", [])
    if not commands:
        return "Identifica herramienta, subcomando, opciones, operandos y variables antes de ejecutar. Consulta la ayuda de la versión presente."
    cmd = commands[0].get("cmd", "")
    return (
        f"La primera prueba es `{cmd}`. Separa sus delimitadores, operadores, opciones, operandos "
        "y variables; algunos elementos no estarán presentes según el contexto. Las comillas, "
        "barras y separadores pertenecen a una capa concreta. Usa la explicación de cada capa "
        "para determinar qué símbolo altera sintaxis y cuál transporta datos."
    )


def render(item: dict, folder: str) -> str:
    title = item["title"]
    source = f"../../tools/concepts.py#{item['id']}"
    commands = item.get("commands", [])
    minimal = item.get("confirmacion", "Diseña una prueba mínima que produzca evidencia inequívoca y un control negativo.")
    result = item.get("resultado", "Una diferencia reproducible atribuible a la entrada.")
    no_apply = item.get("no_aplica", [])
    steps = item.get("pasos", [])
    return f"""---
titulo: {json.dumps(title, ensure_ascii=False)}
categoria: {folder}
dificultad: Intermedia
prerrequisitos:
  - ../01_fundamentos/encoding_normalizacion_y_parsers.md
  - ../02_metodologia/construccion_y_adaptacion_de_payloads.md
fuentes_internas:
  - {source}
fuentes_externas:
  - {EXTERNAL[folder]}
revision: 2026-07-14
estado: borrador
---

# {title}

## Objetivos de aprendizaje

Identificar la superficie, explicar la causa, diseñar una confirmación mínima, interpretar evidencia y proponer una mitigación causal.

## Prerrequisitos

Flujo source-transformación-validación-sink, parsers, permisos y metodología de hipótesis. Revisa los prerrequisitos declarados en los metadatos.

## Fundamentos técnicos

{clean(item.get('que', item.get('summary', '')))}

{clean(item.get('porque', ''))}

## Modelo mental

```text
Entrada controlada -> transformaciones -> validación -> componente final
                  -> sink -> efecto observable -> decisión
```

El paso crítico es demostrar qué componente consume el valor y con qué identidad o privilegios.

## Superficie de ataque

{clean(item.get('cuando', 'Busca funcionalidades que entreguen datos controlables al componente descrito.'))}

## Cómo identificarla

{bullets(item.get('senales', []))}

## Preguntas que debo hacerme

- ¿Qué dato controlo exactamente y en qué formato viaja?
- ¿Qué transformaciones y normalizaciones ocurren antes del sink?
- ¿Qué identidad ejecuta la operación y qué permisos tiene?
- ¿Qué otra explicación produciría la misma señal?
- ¿Cuál es la prueba de menor riesgo que separa ambas explicaciones?

## Prueba mínima

{clean(minimal)}

Evidencia esperada: {clean(result)}

## Construcción progresiva del payload

1. Reproduce una entrada válida.
2. Aísla un único valor controlable.
3. Define la primitiva mínima indicada por la fuente.
4. Predice resultado y control negativo.
5. Aplica una sola adaptación cuando haya evidencia de restricción.
6. Confirma de forma reproducible antes de ampliar impacto.

{command_blocks(item)}

## Anatomía de los payloads

{anatomy(item)}

## Variaciones según el contexto

No traslades una prueba entre sistemas operativos, motores, frameworks o versiones sin revisar sintaxis y comportamiento. Conserva la primitiva y vuelve a serializarla para el parser real.

## Filtros y bypasses

No existe un bypass universal. Registra la forma enviada, la forma decodificada, la comparación, la normalización y la forma consumida. Una adaptación es válida solo si demuestra una discrepancia concreta; si la validación ocurre sobre la forma canónica y expresa la propiedad correcta, la variante no debe funcionar.

## Evidencias de confirmación

{clean(result)}

Usa además una entrada inocua y un control negativo. No confundas reflexión, error genérico o demora aislada con confirmación.

## Escalado de impacto

{bullets(steps)}

Amplía únicamente dentro del laboratorio y cuando cada salto aporte una capacidad nueva demostrable.

## Errores frecuentes

{bullets(no_apply)}

- Ejecutar la prueba sin adaptar variables ni versión.
- Cambiar varias capas a la vez.
- Omitir el control negativo o no guardar evidencia.

## Diagnóstico de payloads fallidos

| Síntoma | Posible causa | Prueba de diagnóstico | Adaptación |
|---|---|---|---|
| Rechazo inmediato | Formato o precondición | Repetir entrada válida | Corregir transporte |
| Sin diferencia | Entrada ignorada o canal ciego | Marcador y control negativo | Buscar evidencia adecuada |
| Error del componente | Contexto o versión | Reducir a prueba mínima | Consultar manual detectado |
| Resultado parcial | Permisos/restricción | Comprobar identidad y alcance | Reducir primitiva |

## Mitigaciones

Eliminar el dato controlable del sink cuando sea posible; usar APIs estructuradas, allowlists sobre valores canónicos, privilegio mínimo, autorización en servidor y registros que permitan detectar abuso. La defensa concreta debe impedir la causa explicada en Fundamentos técnicos.

## Relación con pentesting y certificaciones

Se espera reconocer la señal, justificar la prueba elegida, adaptar variables, interpretar salida y documentar impacto y mitigación. La puntuación debe premiar razonamiento y evidencia, no memoria literal.

## Caso guiado

Parte de una señal de la lista anterior. Escribe observación e hipótesis, ejecuta la prueba mínima, compara con el control y clasifica el resultado como no confirmado, indicio o confirmación. Solo entonces sigue los pasos de escalado relevantes.

## Caso de adaptación

Si la prueba básica falla, no cambies caracteres al azar. Comprueba primero transporte, parser, versión, permisos y canal de evidencia. Diseña una segunda prueba que discrimine entre las dos causas más probables.

## Ejercicios

1. Señala source, transformaciones y sink en el caso guiado.
2. Explica qué evidencia refutaría la hipótesis.
3. Descompón la primera prueba documentada por opciones y argumentos.
4. Propón un control negativo y una mitigación causal.

## Resumen

{clean(item.get('summary', title))} La técnica queda confirmada solo cuando una prueba mínima produce la evidencia prevista y descarta explicaciones alternativas.

## Chuleta operativa

1. Confirmar alcance y precondiciones.
2. Identificar entrada, componente y permisos.
3. Ejecutar prueba mínima y control.
4. Interpretar señal antes de escalar.
5. Guardar evidencia y mitigación.

## Referencias

- [Concepto fuente de THM Fieldbook]({source.split('#')[0]}) (`{item['id']}`)
- [Referencia técnica externa]({EXTERNAL[folder]})

## Navegación

Anterior: [Construcción de payloads](../02_metodologia/construccion_y_adaptacion_de_payloads.md). Índice: [curso](../README.md). Ejercicios y chuleta se enlazarán desde la matriz de trazabilidad.
"""


def render_cheat(name: str, identifiers: list[str]) -> str:
    items = [BY_ID[value] for value in identifiers]
    rows = []
    signals = []
    for item in items:
        signals.extend(item.get("senales", [])[:2])
        for entry in item.get("commands", [])[:2]:
            cmd = entry.get("cmd", "").replace("|", "\\|")
            why = clean(entry.get("why", "Prueba documentada.")).replace("|", "\\|")
            out = clean(entry.get("out", "Evidencia reproducible.")).replace("|", "\\|")
            rows.append(f"| `{cmd}` | {why} | {out} |")
    title = name.replace("_", " ").title()
    table = "\n".join(rows) if rows else "| Consultar módulo | No hay comando universal | Evidencia definida en el módulo |"
    return f"""---
titulo: {json.dumps(title, ensure_ascii=False)}
categoria: Chuletas
dificultad: Operativa
prerrequisitos:
  - ../02_metodologia/construccion_y_adaptacion_de_payloads.md
fuentes_internas:
  - ../../tools/concepts.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# {title}

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

{bullets(signals)}

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
{table}

## Diagnóstico

| Síntoma | Comprobar |
|---|---|
| Sin respuesta | ruta, DNS, puerto, listener y firewall |
| Rechazo | sintaxis, credenciales, permisos y versión |
| Salida distinta | control negativo, caché y estado |
| Resultado parcial | identidad efectiva y precondiciones |

## Cierre

- Guardar comando adaptado y salida.
- Anotar qué confirma y qué no.
- No persistir secretos en notas compartidas.
- Restaurar cambios del laboratorio.

Fuente operativa: [conceptos de Fieldbook](../../tools/concepts.py). Método: [construcción de payloads](../02_metodologia/construccion_y_adaptacion_de_payloads.md).
"""


def main() -> None:
    for folder, identifiers in GROUPS.items():
        target = DOCS / folder
        target.mkdir(parents=True, exist_ok=True)
        for identifier in identifiers:
            item = BY_ID[identifier]
            path = target / slug(identifier)
            path.write_text(render(item, folder), encoding="utf-8", newline="\n")
            print(path.relative_to(ROOT))
    cheat_dir = DOCS / "11_chuletas"
    cheat_dir.mkdir(parents=True, exist_ok=True)
    for name, identifiers in CHEATS.items():
        path = cheat_dir / f"{name}.md"
        path.write_text(render_cheat(name, identifiers), encoding="utf-8", newline="\n")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
