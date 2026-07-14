---
titulo: Informe final de transformación documental
categoria: Meta
dificultad: Inicial
prerrequisitos:
  - auditoria_repositorio.md
  - mapa_fuentes.md
fuentes_internas:
  - ../../tools/concepts.py
  - ../../tools/guides.py
  - ../../tools/generate_structured_playbook.py
  - ../../scripts/validate_docs.py
fuentes_externas:
  - https://www.rfc-editor.org/rfc/rfc9110.html
  - https://owasp.org/www-project-web-security-testing-guide/
  - https://portswigger.net/web-security/all-materials
  - https://www.gnu.org/software/bash/manual/bash.html
revision: 2026-07-14
estado: revisado
---

# Informe final

## Documentos creados

- Auditoría, mapa de fuentes, programa de 14 semanas, progreso y matriz de trazabilidad.
- Índice general con enlaces a todos los módulos.
- 5 módulos de fundamentos y 2 documentos centrales de metodología.
- 20 módulos web, 14 Linux, 10 Windows, 8 Active Directory y 14 de redes/pivoting.
- Cuaderno con 20 ejercicios y preguntas tipo test.
- 6 exámenes con rúbricas y un solucionario razonado separado.
- 14 chuletas operativas.
- Instrucciones, generador PDF y validador automático.

## Temas cubiertos

HTTP, sesiones, formularios, URL/DNS/IP, encoding, parsers, Linux/shell, SQL y flujo de datos; metodología de evidencia y payloads; web, Linux, Windows, AD, servicios de red, pivoting, reporting y mitigación. La matriz enlaza cada documento con su fuente interna y PDF.

## Carencias detectadas

La aplicación no contiene soporte interno suficiente para RFI, CSRF, deserialización insegura, request smuggling/desync, WebSocket smuggling, race conditions, prototype pollution, NoSQLi, systemd o Golden/Silver Tickets. No se crearon módulos vacíos. Podrán añadirse como ampliaciones externas con fuentes primarias y trazabilidad separada.

## Fuentes

La fuente principal sigue siendo `tools/concepts.py`, `tools/guides.py`, las secciones de los generadores y `command_metadata.py`. Las ampliaciones usan RFC Editor, OWASP, PortSwigger, GNU y documentación de Microsoft/man pages según bloque. `web/data/content.json` se trata como artefacto generado.

## Decisiones técnicas

- No se modificó la lógica de la aplicación.
- Markdown es la fuente del curso; PDF se regenera.
- Los módulos temáticos se materializaron por bloques desde 68 conceptos cubiertos y se validó la preservación literal de sus comandos.
- ReportLab evita añadir Pandoc/WeasyPrint y reutiliza el runtime disponible.
- Arial/Consolas de Windows preservan español y bloques técnicos.
- Los PDF agregados tienen índice de módulos, cabecera, pie y paginación.

## Generación de PDF

```powershell
& "$HOME\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" scripts\build_docs.py --clean
```

Manual opcional:

```powershell
python scripts\build_docs.py --clean --manual-completo
```

## Comprobaciones

- Frontmatter y campos obligatorios.
- Enlaces Markdown locales.
- Cercas de código equilibradas.
- Secciones obligatorias de cada técnica.
- Ausencia de marcadores editoriales temporales y valores genéricos sin resolver.
- Preservación literal de comandos/payloads de los conceptos fuente.
- PDF por fuente y PDF por bloque.
- Extracción de texto: ningún PDF o página vacíos en la comprobación inicial.
- Revisión visual de portadas, fundamentos y SQLi: sin solapamientos, recortes ni glifos ilegibles.

## Limitaciones y pendientes

- Los módulos materializados conservan estado `borrador` hasta una revisión editorial técnica individual; las comprobaciones automáticas no sustituyen esa revisión.
- El manual completo es opcional y no se genera en la compilación predeterminada para evitar un artefacto muy pesado.
- El wrapper `pdftoppm.cmd` del runtime local apunta a una ruta defectuosa; el ejecutable Poppler subyacente sí funciona y permitió la revisión visual.
- Las dos modificaciones ajenas detectadas en `PT1_COBERTURA.md` y `PT1_REVISION_TEORICA.md` no se tocaron ni se incluyeron en el trabajo documental.
