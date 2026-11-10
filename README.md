# THM Fieldbook

> Consola de campo para rooms de TryHackMe y CTF: de una evidencia (un puerto, un error, una credencial) a la siguiente comprobación concreta.

**Web:** <https://urbii22.github.io/thm-fieldbook/>

THM Fieldbook es una web estática (sin backend) que reúne playbooks, comandos comentados, guías y conceptos de pentesting ofensivo. No ejecuta nada: adapta los comandos a tu objetivo (`$IP`, `$USER`, `$PASS`…), explica para qué sirven y te los deja copiados para que los revises antes de lanzarlos.

## Qué incluye

| Bloque | Contenido |
| --- | --- |
| **Secciones** | 24 áreas prácticas: recon, web discovery, APIs, inyecciones, SQLi, WordPress, hashes y cracking, acceso inicial, privesc Linux/Windows, Active Directory, pivoting, CVE, checklist de atasco… |
| **Comandos** | ~440 comandos; los más importantes con ficha (objetivo, requisitos, salida esperada, riesgos, errores comunes). |
| **Aprender** | Guías paso a paso y una wiki de conceptos enlazados entre sí, organizados en rutas de aprendizaje. |
| **Room** | IP objetivo, puertos, dominio y usuario; notas, progreso y exportación del writeup en Markdown. |
| **Extras** | Generador de reverse shells, favoritos, recientes y funcionamiento offline (PWA). |

### Ejemplos de búsqueda

| Escribe | Qué obtienes |
| --- | --- |
| `445` o `tengo smb 445` | Playbook SMB: usuarios y shares. |
| `tengo credenciales` | Cómo validar y reutilizar credenciales. |
| `web 403` | Discovery, vhosts, autenticación y autorización. |
| `sudo NOPASSWD vim` | Escalada por sudo y GTFOBins. |
| `shell muere` | Diagnóstico de listener, TTY y red. |

Más detalle del flujo de uso en [GUIA_DE_USO.md](GUIA_DE_USO.md).

## Privacidad

Todo vive en tu navegador. Las credenciales, hashes y claves se guardan solo durante la sesión (`sessionStorage`) salvo que actives explícitamente la persistencia local. La exportación de una room excluye los secretos.

## Estructura del repositorio

```text
tools/                         Fuente del contenido y exportador
  generate_structured_playbook.py   SECTIONS: secciones y comandos (+ PDF por sección)
  generate_thm_playbook.py          Guías PDF temáticas (output/pdf/)
  guides.py                         GUIDES: guías del modo Aprender
  concepts.py                       CONCEPTS y rutas de aprendizaje
  command_metadata.py               Fichas verificables de comandos
  export_web_content.py             Genera web/data/content.json
web/                           App estática publicada en GitHub Pages
  index.html, app.mjs, styles.css, sw.js, manifest.webmanifest
  js/                               Módulos (búsqueda, ranking, rooms, notas, progreso) con sus tests
  data/content.json                 Contenido exportado (se commitea)
  data/revshells.json               Plantillas de reverse shells
tests/                         Tests del exportador (unittest)
output/                        PDFs y capturas generadas (no es fuente)
```

## Desarrollo local

Requisitos: Python 3.13+ y Node 24+. Para generar PDFs, además `pypdf` y `reportlab`.

Servir la web en <http://localhost:4599>:

```bash
python -m http.server 4599 --directory web
```

### Editar contenido

1. Edita la fuente en `tools/` (secciones, guías, conceptos o metadata de comandos), nunca `web/data/content.json` a mano.
2. Regenera el JSON:

   ```bash
   python tools/export_web_content.py
   ```

3. Si cambias `app.mjs` o `styles.css`, actualiza el parámetro `?v=` de `index.html` para invalidar la caché del service worker.
4. Commitea la fuente **y** el `content.json` regenerado: la CI comprueba que coinciden.

### Tests

```bash
python -m unittest discover -s tests
```

```bash
node --test web/app.test.mjs web/js/*.test.mjs
```

### PDFs (opcional)

```bash
python tools/generate_structured_playbook.py
```

```bash
python tools/generate_thm_playbook.py
```

Los PDFs se escriben en `output/pdf/` (temporales en `tmp/`).

## Despliegue

[`.github/workflows/pages.yml`](.github/workflows/pages.yml) se ejecuta en cada push y PR a `main`:

1. Tests de Python y de JavaScript.
2. Re-exporta el contenido y lo compara con `web/data/content.json`.
3. En `main`, publica la carpeta `web/` en GitHub Pages.

## Uso responsable

El contenido está pensado para laboratorios (TryHackMe, HackTheBox, CTF) y auditorías autorizadas. Lanza cada comando solo dentro del alcance que tengas permitido.
