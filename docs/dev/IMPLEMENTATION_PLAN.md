# Plan de implementacion

## 1. Objetivo

- Resultado tecnico: completar los huecos teoricos y de flujo que siguen siendo reales en THM Fieldbook, reorganizar la teoria de APIs sin crear nuevas secciones practicas, anadir una guia de auditoria de APIs, corregir la redaccion visible, proteger la coherencia fuente-exportacion en CI y publicar la iteracion con una unica version PWA alineada.
- Resultado visible para el usuario: las rutas cortas dejan de sentirse incompletas, Web APIs dispone de un recorrido coherente desde el mapeo hasta la autorizacion, las busquedas por situaciones nuevas encuentran contenido util, y la interfaz/textos usan espanol correcto sin perder comandos, profundidad ni acceso rapido.
- Definicion de terminado: la app conserva 24 secciones y 441 comandos practicos, exporta 66 conceptos, 10 guias y 14 rutas; `web/data/content.json` coincide byte a byte con una regeneracion; las pruebas Python y Node pasan; GitHub Pages solo despliega despues de validar; los marcadores PWA usan una misma version; los recorridos manuales de escritorio, movil, teclado, hashes antiguos y busqueda quedan verificados.

## 2. Estado actual verificado

- Rama actual: `main`.
- Commit analizado: `908a4479d5539c1b6a06b301ecfbd9c78275d6e6` (`908a447`).
- Estado de Git: limpio y sincronizado con `origin/main`; no habia cambios sin commit al comenzar el analisis.
- Arquitectura relevante: aplicacion estatica/PWA sin build ni backend. `tools/generate_structured_playbook.py` define `SECTIONS`; `tools/concepts.py` define `CONCEPTS` y `PATHS`; `tools/guides.py` define `GUIDES`; `tools/export_web_content.py` carga, normaliza, fusiona comandos maestros y genera `web/data/content.json`; `web/app.mjs` renderiza Practica/Aprender, busqueda, rutas, guias, hashes, favoritos y estado local; `web/sw.js` gestiona cache/offline; `.github/workflows/pages.yml` publica `web/` en GitHub Pages.
- Flujo de ejecucion actual: fuentes Python -> `python tools/export_web_content.py` -> `web/data/content.json` -> `web/app.mjs` carga `content.json` y `revshells.json` usando `APP_VERSION` -> render en Practica o Aprender -> service worker cachea los activos versionados -> Pages publica el directorio `web`.
- Estado de contenido verificado: 24 secciones, 441 comandos, 55 conceptos, 9 guias y 13 rutas. Todos los conceptos actuales tienen `necesitas`, `no_aplica`, `confirmacion`, `resultado`, `senales` y `pasos`; todos pertenecen a alguna ruta y todas las guias apuntan a secciones existentes.
- Huecos verificados: `web-apis-y-autorizacion` solo tiene teoria propia para IDOR/BOLA; `shells-y-acceso` tiene 2 conceptos; `credenciales-ruta` tiene 2; `recon-red-ruta` tiene 1; `pivoting-ruta` tiene 1; falta teoria especifica de bases de datos aunque `recon-y-servicios` ya contiene comandos para MySQL, MSSQL, PostgreSQL y Redis.
- Decision verificada sobre `cve-ruta`: permanece con un solo concepto porque `explotar-cve` y la guia `cve-metodologia` ya cubren aplicabilidad, lectura del PoC, confirmacion minima y ejecucion; dividirlo ahora duplicaria contenido.
- Decision verificada sobre densidad: `sectionBodyHtml` abre solo el primer grupo y mantiene cerrados grupos posteriores y `Mas comandos`; `web-discovery` abre 7 comandos, no los 27 totales. No necesita otra capa de colapsado.
- Archivos y simbolos relevantes: `tools/concepts.py` — `CONCEPTS`, `PATHS`; `tools/guides.py` — `GUIDES`; `tools/export_web_content.py` — `MASTER_SECTION_SLUGS`, `build_payload`, `write_payload`; `web/app.mjs` — `APP_VERSION`, `SLUG_REDIRECTS`, `ALIASES`, `filterSections`, `sectionBodyHtml`, `conceptPageHtml`, `renderConcepts`, `renderGuides`, `applyHashToState`; `web/sw.js` — `VERSION`; `web/index.html` — referencias versionadas; `web/app.test.mjs` — contratos de integridad, aliases, version y mojibake; `tests/test_export_web_content.py` — exportacion e integridad; `.github/workflows/pages.yml` — despliegue.
- Pruebas y comandos existentes: `python -m unittest discover -s tests -v` (13 pruebas, todas verdes); `node --test web/app.test.mjs` (verde); `python tools/export_web_content.py --output <TEMP>` seguido de comparacion SHA-256 con `web/data/content.json` (coincidencia exacta); `git diff --check` (verde).
- Restricciones comprobadas: no hay `package.json`, bundler, linter, type checker ni framework frontend; el pipeline debe seguir funcionando solo con Python 3.13, Node 24, Git y archivos estaticos. La workflow actual despliega sin ejecutar tests ni comprobar que `content.json` este actualizado.
- Herramientas locales verificadas: Python `3.13.13`, Node `v24.15.0`, Git `2.54.0.windows.1` y GitHub CLI `2.92.0`.

## 3. Alcance

### Incluido

- Anadir exactamente 11 conceptos de alto valor: `api-testing-model`, `auth-session-security`, `jwt-security`, `graphql-security`, `tcp-vs-udp`, `database-enumeration`, `file-transfer`, `shell-troubleshooting`, `secrets-and-loot`, `credential-reuse` y `pivot-troubleshooting`.
- Separar la ruta mixta `web-inyecciones-y-autorizacion-ruta` en una ruta de inyecciones y otra de autorizacion/APIs, sin crear nuevas secciones practicas.
- Anadir una guia `api-paso-a-paso` asociada a `web-apis-y-autorizacion`.
- Ampliar aliases para bases de datos, transferencia, problemas de shell, reutilizacion de credenciales, sesiones, JWT y GraphQL.
- Corregir acentos y redaccion en textos visibles, titulos, resumenes, etiquetas y prosa; conservar literales de comandos, IDs, slugs, variables y placeholders.
- Actualizar `PLAN_IMPLEMENTACION_CONTENIDOS.md` para reflejar el estado ya ejecutado y las cifras reales.
- Anadir validacion previa al despliegue dentro de `.github/workflows/pages.yml`.
- Regenerar `web/data/content.json` y alinear una unica version PWA en `web/index.html`, `web/app.mjs`, `web/sw.js` y `web/app.test.mjs`.
- Verificar escritorio, movil, teclado, hashes antiguos, favoritos, busqueda y actualizacion PWA.

### Fuera de alcance

- Nuevas secciones practicas; las 24 actuales se conservan.
- Nuevos filtros, facetas, backend, telemetria, cuentas, sincronizacion o gamificacion.
- Plantilla editorial extensa, fuentes por comando, estados, fechas de revision o cadencias de mantenimiento.
- OAuth, deserializacion, race conditions, request smuggling, cache poisoning, prototype pollution y WebSockets.
- Cloud, SOC/SIEM, forense, malware, reversing, wireless, movil o desarrollo de exploits.
- Cambiar el esquema de almacenamiento local, las claves `localStorage`, el manifest o el origen de despliegue.
- Reescribir conceptos de privesc/AD ya completos o dividir `cve-ruta` solo para aumentar su contador.
- Introducir dependencias npm/Python nuevas o un sistema de build.

## 4. Requisitos y criterios de aceptacion

- La exportacion final contiene exactamente 24 secciones, 441 comandos, 66 conceptos, 10 guias y 14 rutas.
- Los 11 conceptos nuevos usan el esquema actual completo: `id`, `title`, `phase`, `section`, `summary`, `que`, `porque`, `cuando`, `necesitas`, `no_aplica`, `confirmacion`, `resultado`, `senales`, `pasos` y `commands`.
- Cada concepto nuevo incluye entre 1 y 4 prerrequisitos, entre 1 y 3 comandos de ejemplo y una confirmacion inocua adecuada a un laboratorio autorizado.
- `web-inyecciones-ruta` contiene: `ssti`, `ssrf`, `xxe`, `xss`, `file-upload`, `command-injection`.
- `web-autorizacion-apis-ruta` contiene: `api-testing-model`, `auth-session-security`, `idor-bola`, `jwt-security`, `graphql-security`.
- `shells-y-acceso` contiene 4 conceptos; `credenciales-ruta`, 4; `recon-red-ruta`, 2; `pivoting-ruta`, 2; `enumeracion-servicios-ruta`, 8.
- La guia `api-paso-a-paso` tiene 5 pasos, maximo 3 comandos por paso, y cada paso incluye idea, resultado que buscar y decision posterior.
- Las consultas `3306`, `1433`, `5432`, `6379`, `transferir archivo`, `shell no conecta`, `reutilizar credencial`, `cookie`, `jwt` y `graphql` devuelven una seccion pertinente.
- Ningun cambio de acentos altera un `id`, `slug`, hash, clave de almacenamiento, variable como `$IP`/`$URL`, placeholder como `ATTACKER_IP`, comando o expresion regular funcional.
- `SLUG_REDIRECTS` sigue resolviendo `web-y-apis` y `credenciales-y-loot`.
- Los favoritos, recientes, notas, variables de room, progreso e IP persistidos siguen cargando.
- `.github/workflows/pages.yml` ejecuta tests y compara la exportacion antes de permitir el job de Pages; en pull requests solo valida y no despliega.
- Los cuatro marcadores de version PWA usan el mismo valor nuevo y el test lo exige.
- La regeneracion del JSON no deja diferencias pendientes despues de incluir el archivo exportado en el commit correspondiente.
- No se introducen errores de mojibake; la busqueda conserva equivalencia con/sin tildes.

## 5. Archivos, modulos y simbolos relevantes

| Ruta | Simbolo o seccion | Responsabilidad actual | Cambio previsto | Motivo |
|---|---|---|---|---|
| `tools/concepts.py` | `CONCEPTS` | Teoria estructurada y comandos explicados | Anadir 11 conceptos completos | Cubrir huecos reales sin ampliar areas avanzadas |
| `tools/concepts.py` | `PATHS` | Orden y agrupacion del modo Aprender | Separar inyecciones de autorizacion/APIs y completar rutas cortas | Mejorar coherencia y continuidad |
| `tools/guides.py` | `GUIDES` | Flujos paso a paso | Anadir `api-paso-a-paso` | Convertir la teoria de APIs en procedimiento util |
| `tools/generate_structured_playbook.py` | `SECTIONS` | Fuente de secciones y comandos practicos | Solo correcciones editoriales; no cambiar estructura ni comandos | Pulir contenido conservando 24 secciones/441 comandos |
| `tools/generate_thm_playbook.py` | `GENERATED_DOCS` | Fuente maestra de comandos suplementarios | Solo correcciones editoriales fuera de literales de comandos | Evitar divergencia de textos sin alterar merge |
| `tools/export_web_content.py` | `build_payload`, `write_payload` | Exportacion a JSON | Mantener logica; usarla en CI para detectar artefacto obsoleto | Garantizar reproducibilidad |
| `web/data/content.json` | artefacto generado | Datos consumidos por la PWA | Regenerar tras cada bloque de contenido y version final | Mantener fuente y app alineadas |
| `web/app.mjs` | `ALIASES` | Expansion de busqueda | Anadir aliases de los conceptos/situaciones nuevos | Encontrar contenido sin conocer el nombre tecnico |
| `web/app.mjs` | `conceptPageHtml`, `renderConcepts`, `renderGuides` | Render de teoria y guias | Solo correcciones de copy; no cambiar flujo | El esquema actual ya soporta el contenido nuevo |
| `web/app.mjs` | `APP_VERSION` | Version de datos y activos | Actualizar una vez al cierre | Forzar actualizacion PWA coherente |
| `web/index.html` | etiquetas y query strings | Shell HTML y version de CSS/JS | Corregir copy y actualizar version | Pulido visible y cache coherente |
| `web/sw.js` | `VERSION` | Cache offline | Actualizar al mismo valor | Evitar servir activos antiguos |
| `web/app.test.mjs` | integridad, aliases, version, mojibake | Pruebas JS/datos reales | Anadir contratos de conceptos/rutas/guia/aliases y copy | Prevenir regresiones |
| `tests/test_export_web_content.py` | `ExportWebContentTests` | Pruebas del exportador | Anadir expectativas de IDs, rutas, guia y cifras | Validar la fuente antes del navegador |
| `.github/workflows/pages.yml` | jobs `validate` y `deploy` | Publicacion Pages | Insertar gate de validacion y limitar permisos | No desplegar datos rotos/obsoletos |
| `PLAN_IMPLEMENTACION_CONTENIDOS.md` | linea base/objetivos | Plan anterior ya ejecutado | Marcar estado ejecutado y corregir 11 -> 13 rutas | Evitar documentacion contradictoria |

## 6. Decisiones arquitectonicas

### Decision: ampliar contenido usando el esquema y render actuales

- Decision seleccionada: anadir contenido en `CONCEPTS`, `PATHS` y `GUIDES`; no crear componentes, filtros ni vistas nuevas.
- Justificacion: `conceptPageHtml`, `renderConcepts` y `renderGuides` ya renderizan todos los campos necesarios y tienen pruebas de integridad.
- Alternativas consideradas: nuevo modelo de datos, nueva vista de aprendizaje o mas metadatos.
- Razones para descartarlas: aumentan coste y mantenimiento sin resolver un hueco observado.
- Impacto en compatibilidad: aditivo; IDs existentes se conservan.
- Impacto en seguridad: sin nuevos canales de entrada ni persistencia.
- Impacto en rendimiento: crecimiento pequeno del JSON; sin nuevas peticiones ni dependencias.

### Decision: separar APIs/autorizacion de inyecciones solo en PATHS

- Decision seleccionada: sustituir `web-inyecciones-y-autorizacion-ruta` por `web-inyecciones-ruta` y `web-autorizacion-apis-ruta`.
- Justificacion: IDOR, sesiones, JWT y GraphQL comparten el eje identidad/objeto/autorizacion y no son una secuencia natural con SSTI/SSRF/XXE.
- Alternativas consideradas: conservar la ruta mixta de 7 y agregar los nuevos conceptos al final; crear nuevas secciones practicas.
- Razones para descartarlas: la primera superaria una longitud razonable y mezclaria modelos mentales; la segunda reintroduciria fragmentacion ya resuelta.
- Impacto en compatibilidad: los hashes usan IDs de concepto, no IDs de ruta; se conservan los conceptos y sus IDs.
- Impacto en seguridad: ninguno.
- Impacto en rendimiento: una agrupacion adicional en el indice de Aprender, despreciable.

### Decision: anadir 11 conceptos y no rellenar rutas por contador

- Decision seleccionada: solo incorporar conceptos con hueco practico verificable.
- Justificacion: `explotar-cve` y su guia ya cubren el flujo completo; crear `cve-applicability`/`poc-review` duplicaria prosa. Pivoting, shells, credenciales, APIs y bases de datos si tienen huecos concretos.
- Alternativas consideradas: forzar un minimo de 3 conceptos en todas las rutas.
- Razones para descartarlas: una regla numerica no justifica duplicar conocimiento.
- Impacto en compatibilidad: aditivo.
- Impacto en seguridad: los ejemplos deben ser inocuos, dirigidos a laboratorios y conservar advertencias de ruido/riesgo.
- Impacto en rendimiento: 11 entradas nuevas en un JSON pequeno.

### Decision: permitir 8 conceptos en Enumeracion de servicios

- Decision seleccionada: anadir `database-enumeration` a `enumeracion-servicios-ruta`, resultando en 8 conceptos.
- Justificacion: bases de datos son otra familia de servicio y la ruta sigue siendo coherente; crear otra ruta para una sola entrada empeoraria el indice.
- Alternativas consideradas: mover bases de datos a `recon-red-ruta` o crear `servicios-avanzados-ruta`.
- Razones para descartarlas: la primera mezcla capas; la segunda fragmenta sin suficiente contenido.
- Impacto en compatibilidad: solo aumenta una lista existente.
- Impacto en seguridad: ninguno.
- Impacto en rendimiento: despreciable.

### Decision: incorporar la guia de APIs sin fusionar comandos en SECTIONS

- Decision seleccionada: la guia vive en `GUIDES`, enlazada a `web-apis-y-autorizacion`; reutiliza comandos ya existentes cuando sea posible.
- Justificacion: las guias son contenido pedagogico, no deben inflar `section.commands` ni cambiar las 441 referencias practicas.
- Alternativas consideradas: agregar otra seccion o duplicar todos los comandos de la guia en `SECTIONS`.
- Razones para descartarlas: aumentan densidad y duplicados.
- Impacto en compatibilidad: aditivo; `guide.section` ya se valida.
- Impacto en seguridad: ejemplos de lectura/confirmacion, no acciones destructivas.
- Impacto en rendimiento: despreciable.

### Decision: validar antes de desplegar Pages

- Decision seleccionada: modificar la workflow existente con job `validate`; `deploy` depende de el y solo corre fuera de pull requests.
- Justificacion: hoy Pages publica aunque tests fallen o `content.json` este obsoleto.
- Alternativas consideradas: workflow separada sin dependencia o confiar en validacion local.
- Razones para descartarlas: una workflow independiente no bloquea el deploy; validacion local no protege pushes futuros.
- Impacto en compatibilidad: mantiene push a `main`/`master` y `workflow_dispatch`; agrega `pull_request` para validar.
- Impacto en seguridad: permisos globales solo `contents: read`; `pages: write` e `id-token: write` se limitan al job `deploy`.
- Impacto en rendimiento: suma menos de un minuto estimado por no instalar dependencias del proyecto.

### Decision: corregir espanol sin modificar contratos

- Decision seleccionada: corregir todo texto visible y prosa, pero excluir IDs, slugs, claves, comandos, placeholders, hashes y expresiones regulares.
- Justificacion: mejora lectura sin arriesgar ejecucion o enlaces.
- Alternativas consideradas: mantener ASCII o ejecutar un reemplazo global mecanico.
- Razones para descartarlas: ASCII reduce calidad; reemplazo global puede romper comandos y patrones.
- Impacto en compatibilidad: `slugify` elimina acentos, pero se anaden tests de estabilidad para los titulos tocados.
- Impacto en seguridad: ninguno.
- Impacto en rendimiento: ninguno.

### Decision: realizar un unico bump PWA al final

- Decision seleccionada: mantener la version actual durante fases intermedias y cambiarla una vez cuando contenido, copy y tests esten cerrados.
- Justificacion: evita varias familias de cache durante una misma implementacion.
- Alternativas consideradas: bump por commit.
- Razones para descartarlas: ruido y riesgo de desalineacion.
- Impacto en compatibilidad: el flujo `registration.update()` / `SKIP_WAITING` / `controllerchange` se conserva.
- Impacto en seguridad: ninguno.
- Impacto en rendimiento: una recarga controlada tras actualizar el service worker.

## 7. Invariantes y compatibilidad

- Comportamiento que debe conservarse: Practica y Aprender; busqueda normalizada; aliases; comandos copiables/editables; variables de room; reverse-shell generator; favoritos; recientes; progreso; notas; rutas anterior/siguiente; enlaces teoria-practica; funcionamiento offline.
- Interfaces que no deben romperse: forma de `sections`, `concepts`, `guides` y `paths` en `content.json`; helpers exportados que usa `web/app.test.mjs`; `SLUG_REDIRECTS`; query/hash `#practica/<slug>` y `#aprender/<mode>/<id>`.
- Datos que no deben perderse: claves locales `thm-profile`, `thm-favs`, `thm-recent`, IP heredada y cualquier progreso/notas guardado por slug/indice.
- Compatibilidad anterior: conservar todos los IDs de los 55 conceptos y 9 guias actuales; no renombrar las 24 secciones; mantener redirecciones `web-y-apis -> web-discovery` y `credenciales-y-loot -> loot-y-secretos`.
- Enlaces, formatos, APIs o configuraciones existentes: todos los `[[concept-id]]` deben resolver; `guide.section` debe existir; todos los conceptos deben pertenecer a una ruta; el origen publicado sigue siendo GitHub Pages y la carpeta desplegada sigue siendo `web`.
- La cifra de 441 comandos pertenece a `sections`; los comandos pedagogicos de conceptos/guias no deben incrementar esa estadistica salvo que se anada deliberadamente una referencia practica a `SECTIONS`, lo cual esta fuera de alcance.
- `content.json` es artefacto generado: no editarlo a mano.
- No corregir tildes dentro de comandos, argumentos, nombres de ficheros, dominios, variables, wordlists, patrones de busqueda tecnica ni placeholders.

## 8. Dependencias entre cambios

- Dependencias entre fases: la CI puede implementarse primero; los nuevos conceptos deben existir antes de referenciarlos en `PATHS`; la guia de APIs debe anadirse despues o junto con los conceptos API; aliases requieren IDs/secciones definitivos; el pulido editorial se hace despues de cerrar contenido; documentacion y version PWA se cierran al final; la exportacion final depende de todas las fuentes Python.
- Partes que pueden ejecutarse en paralelo: solo la preparacion conceptual de textos puede redactarse en paralelo fuera del repositorio. Dentro del repositorio no se recomienda paralelizar porque `tools/concepts.py`, `web/app.test.mjs` y `web/data/content.json` concentran la integracion.
- Archivos que no deben editarse en paralelo: `tools/concepts.py`, `tools/guides.py`, `web/app.mjs`, `web/app.test.mjs`, `web/data/content.json`, `PLAN_IMPLEMENTACION_CONTENIDOS.md` y `.github/workflows/pages.yml`.
- Migraciones o regeneraciones necesarias: no hay migracion de almacenamiento. Ejecutar `python tools/export_web_content.py` tras cada fase que cambie Python; incluir el JSON regenerado en el mismo commit. Actualizar la version PWA una sola vez en la fase de cierre.
- La fase editorial no debe comenzar mientras haya cambios semanticos pendientes, porque mezcla diffs de contenido con correcciones ortograficas.
- La verificacion manual final requiere que todas las fases anteriores y los tests esten verdes.

## 9. Fases de implementacion

### Fase 1 — Gate de calidad antes de GitHub Pages

#### Objetivo

Impedir que Pages publique una exportacion obsoleta o una app con pruebas fallidas.

#### Dependencias

Ninguna; debe completarse antes de los cambios de contenido.

#### Archivos y simbolos afectados

- `.github/workflows/pages.yml` — triggers, permisos y jobs.

#### Cambios exactos

1. Agregar trigger `pull_request` para `main` y `master`, manteniendo `push` y `workflow_dispatch`.
2. Cambiar permisos globales a `contents: read`.
3. Crear job `validate` en `ubuntu-latest` con:
   - `actions/checkout@v4`.
   - `actions/setup-python@v5`, Python `3.13`.
   - `actions/setup-node@v4`, Node `24`.
   - `python -m unittest discover -s tests -v`.
   - `node --test web/app.test.mjs`.
   - `python tools/export_web_content.py --output /tmp/content.json`.
   - `diff -u web/data/content.json /tmp/content.json`.
4. Hacer que `deploy` dependa de `validate` mediante `needs: validate`.
5. Limitar `deploy` a eventos distintos de `pull_request`.
6. Mover `pages: write` e `id-token: write` a permisos del job `deploy`.
7. Conservar environment, concurrency, configure-pages, upload y deploy actuales.

#### Pruebas que deben anadirse o modificarse

- No se anaden tests de aplicacion en esta fase; la propia workflow ejecuta la suite existente y comprueba reproducibilidad.

#### Comandos de validacion

```text
python -m unittest discover -s tests -v
node --test web/app.test.mjs
$tmp = Join-Path $env:TEMP "thm-content-ci.json"
python tools/export_web_content.py --output $tmp
git diff --no-index -- web/data/content.json $tmp
Remove-Item -LiteralPath $tmp
git diff --check
```

#### Criterios de aceptacion

- `validate` corre en pull request, push y dispatch.
- `deploy` no corre en pull request y exige `validate` verde.
- El job de validacion no tiene permisos de escritura en Pages ni OIDC.
- El workflow conserva la publicacion de `web/`.

#### Riesgos y posibles regresiones

- Sintaxis YAML invalida o expresion `if` incorrecta puede bloquear Pages.
- Diferencias de salto de linea no deben falsear la comparacion; el exportador produce JSON determinista y la referencia actual coincide por SHA-256.

#### Condicion de parada

Detenerse si la workflow no puede expresar permisos por job o si la exportacion deja de ser determinista; no relajar el gate para permitir el deploy.

#### Commit sugerido

`ci: validate content before Pages deploy`

### Fase 2 — Teoria coherente de APIs, sesiones y autorizacion

#### Objetivo

Completar el mayor hueco teorico restante de Web APIs y separar autorizacion de las inyecciones.

#### Dependencias

Fase 1 recomendada, aunque el cambio de contenido no depende funcionalmente de CI.

#### Archivos y simbolos afectados

- `tools/concepts.py` — `CONCEPTS`, `PATHS`.
- `web/app.mjs` — `ALIASES`.
- `tests/test_export_web_content.py` — expectativas de exportacion.
- `web/app.test.mjs` — integridad, rutas y aliases.
- `web/data/content.json` — regeneracion.

#### Cambios exactos

1. Anadir `api-testing-model` en `web-apis-y-autorizacion`: modelo endpoint + metodo + entrada + identidad + objeto + respuesta; confirmacion mediante baseline de una peticion conocida y variacion de un solo eje.
2. Anadir `auth-session-security` en `web-apis-y-autorizacion`: autenticacion frente a autorizacion, cookies/tokens, login/logout, rotacion, expiracion, fijacion y reutilizacion; confirmar comparando sesiones propias.
3. Anadir `jwt-security` en `web-apis-y-autorizacion`: estructura header/payload/signature, `alg`, `kid`, `jku`, claims y expiracion; primero inspeccion sin firma y despues pruebas controladas solo si el laboratorio lo indica.
4. Anadir `graphql-security` en `web-apis-y-autorizacion`: endpoint, introspeccion, tipos, queries/mutations, IDs y autorizacion por objeto; confirmar con una query minima.
5. Cada concepto debe usar todos los campos actuales y 1-3 comandos ya presentes en la seccion cuando sea posible.
6. Reemplazar `web-inyecciones-y-autorizacion-ruta` por:
   - `web-inyecciones-ruta`: `ssti`, `ssrf`, `xxe`, `xss`, `file-upload`, `command-injection`.
   - `web-autorizacion-apis-ruta`: `api-testing-model`, `auth-session-security`, `idor-bola`, `jwt-security`, `graphql-security`.
7. Mantener `web-a-shell` sin cambios.
8. Agregar aliases `api`, `sesion`, `session`, `cookie`, `token`, `graphql` y ampliar `jwt` con terminos que existan realmente en los nuevos textos.
9. Regenerar `web/data/content.json`.

#### Pruebas que deben anadirse o modificarse

- Assert de existencia de los cuatro IDs nuevos.
- Assert de composicion y orden exactos de las dos rutas nuevas.
- Assert de desaparicion del ID de ruta mixta.
- Casos de busqueda para `cookie`, `jwt` y `graphql` que incluyan `web-apis-y-autorizacion`.
- Mantener validaciones genericas de campos, enlaces, secciones y conceptos en rutas.

#### Comandos de validacion

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
git diff --check
```

#### Criterios de aceptacion

- El total exportado es 59 conceptos y 14 rutas al terminar esta fase.
- IDOR ya no aparece agrupado bajo una ruta titulada “inyecciones”.
- La ruta API tiene 5 conceptos y la de inyecciones 6.
- Los cuatro conceptos enlazan a `web-apis-y-autorizacion` y contienen confirmaciones inocuas.
- Las busquedas nuevas devuelven la seccion esperada.

#### Riesgos y posibles regresiones

- Referencias `[[...]]` rotas, conceptos duplicados en rutas o aliases demasiado amplios.
- El cambio del ID de ruta no rompe hashes, pero puede alterar el orden visual; revisar el indice de Aprender.

#### Condicion de parada

Detenerse si un concepto nuevo requiere ampliar el esquema o crear una nueva seccion; reescribir el contenido para usar el modelo existente.

#### Commit sugerido

`feat(content): add API authorization learning path`

### Fase 3 — Guia paso a paso para auditar APIs

#### Objetivo

Convertir la teoria API en un flujo operativo util durante una room.

#### Dependencias

Fase 2 completada; la guia debe enlazar los nuevos conceptos.

#### Archivos y simbolos afectados

- `tools/guides.py` — `GUIDES`.
- `tests/test_export_web_content.py` — contrato de guia.
- `web/app.test.mjs` — datos reales de guia.
- `web/data/content.json` — regeneracion.

#### Cambios exactos

1. Anadir guia `api-paso-a-paso`, titulo “Auditar una API paso a paso”, fase `enumeration`, seccion `web-apis-y-autorizacion`.
2. Paso 1 “Mapea superficie y baseline”: endpoint, documentacion, metodos y respuesta normal.
3. Paso 2 “Entiende identidad y sesion”: login, cookie/token, expiracion y logout.
4. Paso 3 “Comprueba autorizacion por objeto”: dos identidades/recursos, IDOR/BOLA, lectura y escritura.
5. Paso 4 “Revisa JWT y GraphQL”: inspeccion de claims, introspeccion, queries/mutations y autorizacion.
6. Paso 5 “Registra evidencia y decide”: resultado, impacto, falso positivo, siguiente vector o descarte.
7. Maximo 3 comandos por paso; reutilizar `curl`, `OPTIONS`, token y GraphQL existentes; no duplicarlos en `SECTIONS`.

#### Pruebas que deben anadirse o modificarse

- Assert de guia `api-paso-a-paso` existente, asociada a `web-apis-y-autorizacion` y con exactamente 5 pasos.
- Assert de maximo 3 comandos por paso.
- Mantener `test_every_guide_section_exists`.

#### Comandos de validacion

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
git diff --check
```

#### Criterios de aceptacion

- El total exportado es 10 guias.
- La guia aparece en Aprender, se busca por API/JWT/GraphQL y abre la seccion practica correcta.
- Cada paso termina en una decision observable.
- `totalCommands` de secciones sigue siendo 441.

#### Riesgos y posibles regresiones

- Duplicar demasiada teoria dentro de la guia o introducir comandos que no existan en la practica.

#### Condicion de parada

Detenerse si la guia supera 5 pasos, 3 comandos por paso o exige una nueva vista.

#### Commit sugerido

`feat(content): add API testing guide`

### Fase 4 — Completar flujos practicos cortos

#### Objetivo

Anadir siete conceptos que cubren huecos operativos concretos sin rellenar rutas por contador.

#### Dependencias

Fase 2 para trabajar sobre el orden final de `PATHS`; Fase 3 no es bloqueante.

#### Archivos y simbolos afectados

- `tools/concepts.py` — `CONCEPTS`, `PATHS`.
- `web/app.mjs` — `ALIASES`.
- `tests/test_export_web_content.py`.
- `web/app.test.mjs`.
- `web/data/content.json`.

#### Cambios exactos

1. `tcp-vs-udp` en `recon-y-servicios`: diferencias de transporte, visibilidad, tiempos, `-sT`/`-sU`, VPN/proxy y cuando no repetir escaneos.
2. `database-enumeration` en `recon-y-servicios`: MySQL 3306, MSSQL 1433, PostgreSQL 5432 y Redis 6379; autenticacion, metadatos y consultas de reconocimiento no destructivas.
3. `file-transfer` en `acceso-inicial`: HTTP, `curl`/`wget`, `certutil`/PowerShell, direccion de transferencia e integridad mediante hash.
4. `shell-troubleshooting` en `acceso-inicial`: listener, LHOST/tun0, egress, puerto ocupado, quoting, interprete y conectividad.
5. `secrets-and-loot` en `loot-y-secretos`: configs, historiales, claves, vaults, navegadores y registro de fuente.
6. `credential-reuse` en `credenciales-y-acceso`: matriz servicio/identidad, formatos local/dominio, validacion manual, lockout y reenumeracion.
7. `pivot-troubleshooting` en `pivoting`: rutas, SOCKS, DNS, `proxy_dns`, escaneo `-sT`, interfaz Ligolo y validacion por capas.
8. Actualizar rutas en este orden:
   - `recon-red-ruta`: `recon-metodologia`, `tcp-vs-udp`.
   - `enumeracion-servicios-ruta`: mantener sus 7 y anadir `database-enumeration` al final.
   - `shells-y-acceso`: `reverse-vs-bind`, `tty-stabilization`, `file-transfer`, `shell-troubleshooting`.
   - `credenciales-ruta`: `secrets-and-loot`, `cracking`, `fuerza-bruta-online`, `credential-reuse`.
   - `pivoting-ruta`: `pivoting-tunel`, `pivot-troubleshooting`.
9. Mantener `cve-ruta` sin cambios y documentar la decision en comentario breve junto a `PATHS` si ya existen comentarios de autoria.
10. Anadir aliases de bases de datos (`3306`, `1433`, `5432`, `6379`, `mysql`, `mssql`, `postgres`, `redis`), transferencia, shell que no conecta, loot y reutilizacion.
11. Regenerar `web/data/content.json`.

#### Pruebas que deben anadirse o modificarse

- Assert de existencia de los siete IDs.
- Assert de orden exacto en las cinco rutas modificadas.
- Assert de 8 conceptos en `enumeracion-servicios-ruta` como excepcion deliberada.
- Casos de aliases para los cuatro puertos de BD, `transferir archivo`, `shell no conecta` y `reutilizar credencial`.
- Assert final de 66 conceptos y 14 rutas.

#### Comandos de validacion

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
git diff --check
```

#### Criterios de aceptacion

- El total exportado es 66 conceptos, 10 guias y 14 rutas.
- Todos los conceptos nuevos pertenecen a una ruta y enlazan a una seccion existente.
- Las rutas cortas reflejan un flujo real sin duplicar los conceptos actuales.
- Las busquedas situacionales y por puerto llegan a contenido pertinente.
- Las confirmaciones son inocuas y orientadas a laboratorio autorizado.

#### Riesgos y posibles regresiones

- Inflar la ruta de servicios, redundancia entre `secrets-and-loot` y la guia de credenciales, o mezclar estabilizacion con troubleshooting.

#### Condicion de parada

Detenerse si algun concepto repite sustancialmente un concepto/guia actual; integrar solo el hueco diferencial o cancelar esa entrada.

#### Commit sugerido

`feat(content): complete practical learning flows`

### Fase 5 — Pulido editorial del contenido visible

#### Objetivo

Corregir tildes, puntuacion y consistencia terminologica sin alterar contratos tecnicos.

#### Dependencias

Fases 2-4 cerradas para evitar conflictos con la autoria de contenido.

#### Archivos y simbolos afectados

- `web/index.html` — copy visible.
- `web/app.mjs` — etiquetas generadas y mensajes.
- `tools/generate_structured_playbook.py` — titulos, resumenes, parrafos, tablas y bullets.
- `tools/generate_thm_playbook.py` — prosa visible, excluyendo comandos.
- `tools/concepts.py` — titulos, rutas y prosa de 66 conceptos.
- `tools/guides.py` — titulos y prosa de 10 guias.
- `web/app.test.mjs` — contratos de copy y mojibake.
- `tests/test_export_web_content.py` — estabilidad de slugs con acentos.
- `web/data/content.json` — regeneracion.

#### Cambios exactos

1. Corregir etiquetas de shell: “Práctica”, “Guías”, “Accesos rápidos”, “Enumeración”, “Confirmación mínima”, “Resultado esperado”, “Qué es”, “Por qué ocurre”, “Cuándo aplica”, “Cuándo NO aplica”, “Señales”, “Ningún”, “Más comandos”.
2. Corregir titulos/resumenes de secciones, rutas, conceptos y guias.
3. Revisar prosa explicativa completa, preservando terminologia tecnica habitual: shell, loot, cracking, privesc, pivoting, Pass-the-Hash, IDOR/BOLA, JWT y GraphQL.
4. No modificar strings dentro de `commands`, IDs, slugs, claves de storage, variables, placeholders, rutas de fichero, URLs, wordlists ni expresiones regulares.
5. Mantener aliases sin tildes cuando sean necesarios para busqueda; la normalizacion ya hace equivalentes ambas formas.
6. Regenerar `content.json` y revisar el diff por archivo para confirmar que los cambios son solo copy/exportacion.

#### Pruebas que deben anadirse o modificarse

- Extender test de copy para etiquetas principales con tildes.
- Mantener test de mojibake sobre HTML/JS/SW/JSON.
- Agregar casos `slugify("Enumeración de servicios")` y `slugify("Guías paso a paso")` para demostrar estabilidad.
- Mantener equivalencia `version`/`versión` y agregar una consulta relevante con tilde/sin tilde.

#### Comandos de validacion

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
git diff --word-diff -- web/index.html web/app.mjs tools/generate_structured_playbook.py tools/generate_thm_playbook.py tools/concepts.py tools/guides.py
git diff --check
```

#### Criterios de aceptacion

- La interfaz y la teoria usan espanol correcto.
- No cambian IDs, slugs, comandos ni claves persistidas.
- No aparece mojibake.
- La busqueda sigue siendo insensible a tildes.

#### Riesgos y posibles regresiones

- Reemplazos globales pueden corromper comandos o claves; el cambio debe hacerse por campos/prosa, no por sustitucion ciega.
- Diff grande puede ocultar cambios semanticos involuntarios.

#### Condicion de parada

Detenerse ante cualquier cambio en un literal de comando, ID, slug, variable o clave; revertir solo ese hunk y continuar manualmente.

#### Commit sugerido

`docs(content): polish Spanish copy`

### Fase 6 — Documentacion de estado y contratos finales

#### Objetivo

Alinear la documentacion anterior con lo realmente implementado y dejar cifras verificables para futuras iteraciones.

#### Dependencias

Fases 2-5 completadas para conocer cifras finales.

#### Archivos y simbolos afectados

- `PLAN_IMPLEMENTACION_CONTENIDOS.md` — linea base, objetivo y estado.
- `tests/test_export_web_content.py` — cifras finales esenciales.
- `web/app.test.mjs` — cifras/IDs/rutas/guia finales.

#### Cambios exactos

1. Marcar el alcance original de 24 secciones/55 conceptos/9 guias/13 rutas como ejecutado.
2. Corregir cualquier referencia antigua a 11 rutas.
3. Anadir una seccion breve “Iteracion posterior” con el resultado de este plan: 24 secciones, 441 comandos, 66 conceptos, 10 guias y 14 rutas.
4. Documentar explicitamente que `enumeracion-servicios-ruta` tiene 8 conceptos por decision consciente.
5. Documentar que `cve-ruta` permanece con uno por no duplicar `explotar-cve` y `cve-metodologia`.
6. Mantener `IMPLEMENTATION_PLAN.md` como plan de ejecucion, no convertirlo en changelog durante la implementacion.

#### Pruebas que deben anadirse o modificarse

- Asserts de cifras finales en el test de datos reales.
- Asserts de IDs de rutas web y guia API.

#### Comandos de validacion

```text
python -m unittest discover -s tests -v
node --test web/app.test.mjs
rg -n "11 rutas|55 conceptos|9 guias" PLAN_IMPLEMENTACION_CONTENIDOS.md
git diff --check
```

#### Criterios de aceptacion

- La documentacion no contradice `content.json`.
- Las excepciones de rutas quedan explicadas.
- Los tests fijan el nuevo baseline.

#### Riesgos y posibles regresiones

- Convertir el documento historico en un segundo plan activo y generar confusion.

#### Condicion de parada

Detenerse si las cifras exportadas no son exactamente las previstas; corregir fuentes/tests antes de documentar.

#### Commit sugerido

`docs: update Fieldbook content baseline`

### Fase 7 — Exportacion final y version PWA

#### Objetivo

Cerrar la iteracion con artefactos reproducibles y una version que actualice correctamente la PWA instalada.

#### Dependencias

Fases 1-6 completadas y verdes.

#### Archivos y simbolos afectados

- `web/data/content.json` — artefacto final.
- `web/app.mjs` — `APP_VERSION`.
- `web/sw.js` — `VERSION`.
- `web/index.html` — query strings de CSS/JS.
- `web/app.test.mjs` — marcador esperado.

#### Cambios exactos

1. Generar `content.json` desde las fuentes.
2. Elegir una version unica con formato `YYYYMMDD-content-depth`, usando la fecha real de implementacion.
3. Sustituir `20260710-alias-densidad` por ese valor en los cuatro contratos.
4. Conservar `registration.update()`, `SKIP_WAITING`, `controllerchange` y fetch de JSON/revshells con `APP_VERSION`.
5. Regenerar a temporal y comparar SHA-256 con el JSON commiteado.

#### Pruebas que deben anadirse o modificarse

- Actualizar el marcador de version en `web/app.test.mjs`.
- Mantener la comprobacion de una sola familia de version en HTML/JS/SW.
- Mantener comprobaciones del flujo de actualizacion.

#### Comandos de validacion

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
$tmp = Join-Path $env:TEMP "thm-content-final.json"
python tools/export_web_content.py --output $tmp
(Get-FileHash -Algorithm SHA256 web/data/content.json).Hash
(Get-FileHash -Algorithm SHA256 $tmp).Hash
Remove-Item -LiteralPath $tmp
git diff --check
```

#### Criterios de aceptacion

- Hashes del JSON coinciden.
- Los cuatro marcadores usan exactamente la misma version.
- Tests verdes.
- No quedan cambios generados sin incluir.

#### Riesgos y posibles regresiones

- Version desalineada deja una app instalada sirviendo mezcla de activos.
- Olvidar el JSON generado hace que CI bloquee Pages.

#### Condicion de parada

Detenerse si los hashes difieren, los marcadores no coinciden o cualquier test de PWA falla.

#### Commit sugerido

`chore: release updated Fieldbook content`

### Fase 8 — QA manual, responsive y despliegue

#### Objetivo

Validar el uso real antes de considerar terminada la iteracion.

#### Dependencias

Fase 7 completada; workspace limpio salvo commits de esta implementacion.

#### Archivos y simbolos afectados

- No requiere cambios salvo que se detecte una regresion; cualquier correccion vuelve a su fase de origen y repite validacion.

#### Cambios exactos

1. Servir `web/` localmente en `127.0.0.1:5177` desde una terminal independiente.
2. Escritorio 1440x900: Practica inicial, Web APIs, busqueda y Aprender/Conceptos.
3. Movil 390x844: topbar, tabs, indice, detalle, tablas, bloques de comandos y room panel sin desbordamiento inutilizable.
4. Teclado: `/` enfoca busqueda; Tab recorre controles; Enter activa; foco visible; Escape cierra modal de explicacion.
5. Hashes: abrir `#practica/web-y-apis`, `#practica/credenciales-y-loot` y un `#aprender/concepts/<id-nuevo>`.
6. Persistencia: favorito, reciente, IP, nota y progreso sobreviven a recarga.
7. Busquedas: ejecutar todas las consultas nuevas y las existentes del test.
8. Offline/update: recargar, comprobar nueva version y verificar que la app instalada no conserva la familia anterior.
9. Tras publicar, comprobar workflow y Pages con GitHub CLI.

#### Pruebas que deben anadirse o modificarse

- Si QA descubre una regresion reproducible, anadir test en la capa correspondiente antes de corregirla.

#### Comandos de validacion

```text
python -m http.server 5177 --bind 127.0.0.1 --directory web
gh run list --workflow pages.yml --limit 1
gh run view <RUN_ID> --log-failed
git status --short --branch
git diff --check
```

#### Criterios de aceptacion

- Todos los recorridos manuales pasan en escritorio y movil.
- No hay consola con errores, contenido en blanco ni hashes rotos.
- La workflow `validate` y el deploy terminan verdes.
- Pages sirve la version nueva y el JSON con las cifras finales.

#### Riesgos y posibles regresiones

- La validacion visual depende de navegador disponible y el chequeo remoto depende de autenticacion `gh` y de que el commit haya sido publicado.

#### Condicion de parada

No declarar terminado si no se puede validar visualmente o si Pages no sirve el commit/version esperados; documentar la limitacion y dejar la fase abierta.

#### Commit sugerido

`fix: address final Fieldbook QA findings` solo si QA produce cambios; si no, no crear commit vacio.

## 10. Validacion integrada

- Formato: no hay formatter configurado; usar `git diff --check` y revision manual de Markdown/Python/JS/YAML.
- Lint: no hay linter configurado; no introducir uno en este alcance.
- Analisis estatico: importacion/ejecucion del exportador a traves de `python -m unittest discover -s tests -v`; revisar `rg -n "\[\[|APP_VERSION|VERSION|SLUG_REDIRECTS" tools web` cuando aplique.
- Type checking: no hay type checker configurado; no introducir uno.
- Tests unitarios: `python -m unittest discover -s tests -v`.
- Tests de integracion: `node --test web/app.test.mjs` sobre `web/data/content.json` real.
- Tests end-to-end: recorridos manuales mediante servidor local; no hay runner E2E instalado y no se anade dependencia.
- Build: no existe build; el equivalente es `python tools/export_web_content.py`.
- Comprobaciones de seguridad: revisar permisos de workflow; confirmar que ejemplos nuevos son para laboratorio, no destructivos y no contienen secretos; revisar `git diff` antes de commit.
- Comprobaciones de migracion: tests de `SLUG_REDIRECTS`, hashes antiguos, conceptos en rutas, secciones de guias y persistencia local manual.
- Pruebas manuales: Practica, Aprender/Conceptos, Aprender/Guias, busqueda por alias, room panel, comandos, modal de explicacion, escritorio/movil/teclado/offline.
- `git diff --check`: `git diff --check`.
- Secuencia completa recomendada:

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs
git diff --check
git status --short --branch
```

## 11. Riesgos, regresiones y rollback

| Riesgo | Probabilidad | Impacto | Prevencion | Deteccion | Recuperacion o rollback |
|---|---|---|---|---|---|
| `content.json` queda obsoleto | Media | Alta | Regenerar en cada fase y gate CI | `diff`/SHA-256 falla | Regenerar desde fuentes y recommitear; no editar JSON a mano |
| Workflow bloquea Pages por YAML invalido | Baja | Alta | Cambio aislado, sintaxis simple, permisos por job | Action no inicia o falla al parsear | Revertir el commit CI con `git revert <commit>` y corregir en rama |
| Deploy ocurre en PR | Baja | Alta | `if` explicito y permisos solo en deploy | Historial de Actions | Corregir condicion; cancelar run si procede |
| Rutas web mezcladas o conceptos huerfanos | Media | Media | Orden exacto fijado en plan y tests | Tests de IDs/rutas | Revertir commit de contenido o corregir `PATHS` |
| Alias generico degrada resultados | Media | Media | Aliases concretos y tests por seccion esperada | Busqueda manual/tests | Reducir expansion o eliminar alias problematico |
| Conceptos nuevos duplican guias existentes | Media | Media | Condicion de parada y revision diferencial | Revision de contenido | Integrar solo el hueco y eliminar duplicacion antes de commit |
| Correccion de tildes rompe comandos/slugs | Media | Alta | No usar reemplazo global; tests slug/hash | Diff, tests, busqueda manual | Revertir hunks editoriales afectados |
| Diff editorial oculta cambio semantico | Media | Media | Commit separado y `--word-diff` | Revision del commit | Revertir commit editorial completo y rehacer por archivos |
| Version PWA desalineada | Baja | Alta | Un unico bump y test hardcoded | Test Node/PWA instalada obsoleta | Corregir los cuatro marcadores y publicar nuevo commit |
| Persistencia local pierde referencias | Baja | Alta | No cambiar claves/slugs; conservar redirects | Prueba manual de favoritos/notas/hashes | Revertir cambio de contrato o anadir migracion puntual |
| QA visual no disponible | Media | Media | Reservar fase explicita y navegador real | Fase 8 sin evidencia | No cerrar la tarea; documentar bloqueo y reanudar cuando haya navegador |
| `enumeracion-servicios-ruta` llega a 8 | Alta | Baja | Decision documentada; revisar indice | Captura/QA visual | Solo dividir si uso real demuestra densidad; no hacerlo preventivamente |

## 12. Preguntas abiertas

- Bloqueante: no hay preguntas bloqueantes.
- No bloqueante: la version exacta PWA se decide en la fecha de implementacion con formato `YYYYMMDD-content-depth`.
- Decision ya resuelta: no se crean nuevas secciones, filtros, metadatos ni conceptos artificiales para inflar rutas.
- Decision ya resuelta: `cve-ruta` permanece con un concepto y `enumeracion-servicios-ruta` puede contener ocho.

## 13. Checklist final

- [ ] La workflow valida tests y exportacion antes de Pages.
- [ ] La workflow valida PRs sin desplegarlos y limita permisos de escritura al job deploy.
- [ ] Se anadieron exactamente los 11 conceptos definidos.
- [ ] Se crearon `web-inyecciones-ruta` y `web-autorizacion-apis-ruta` con el orden especificado.
- [ ] Se anadio `api-paso-a-paso` con 5 pasos y maximo 3 comandos por paso.
- [ ] Las rutas cortas quedaron completadas segun el plan sin duplicar CVE.
- [ ] Los aliases nuevos devuelven secciones pertinentes.
- [ ] Se corrigio el espanol visible sin cambiar contratos tecnicos.
- [ ] `PLAN_IMPLEMENTACION_CONTENIDOS.md` refleja las cifras reales.
- [ ] El export final contiene 24 secciones, 441 comandos, 66 conceptos, 10 guias y 14 rutas.
- [ ] `web/data/content.json` coincide con una regeneracion temporal.
- [ ] Los cuatro marcadores PWA comparten una version nueva.
- [ ] Se conservaron hashes, redirects, favoritos, recientes, variables, notas y progreso.
- [ ] Se validaron escritorio, movil, teclado, busqueda, offline y actualizacion.
- [ ] Se conservaron los cambios existentes del usuario.
- [ ] Se ejecutaron las validaciones indicadas.
- [ ] Se reviso `git diff --check`.

## 14. Handoff para el modelo ejecutor

- Estado de Git analizado: `main` limpio y alineado con `origin/main`.
- Commit de referencia: `908a4479d5539c1b6a06b301ecfbd9c78275d6e6`.
- Archivos prioritarios: `.github/workflows/pages.yml`, `tools/concepts.py`, `tools/guides.py`, `web/app.mjs`, `tests/test_export_web_content.py`, `web/app.test.mjs`, `web/data/content.json`, `PLAN_IMPLEMENTACION_CONTENIDOS.md`, `web/index.html`, `web/sw.js`.
- Decisiones ya cerradas: 11 conceptos; una guia API; separar rutas web sin nuevas secciones; permitir 8 servicios; no dividir CVE; sin filtros/metadatos/dependencias; correccion editorial protegida; un bump PWA final; CI bloquea Pages.
- Orden obligatorio de fases: 1 CI -> 2 conceptos/rutas API -> 3 guia API -> 4 flujos practicos -> 5 editorial -> 6 documentacion -> 7 export/version -> 8 QA.
- Comandos de referencia: `python tools/export_web_content.py`; `python -m unittest discover -s tests -v`; `node --test web/app.test.mjs`; `git diff --check`; `python -m http.server 5177 --bind 127.0.0.1 --directory web`.
- Verificaciones minimas iniciales: confirmar rama/commit/estado limpio; ejecutar las 13 pruebas Python y la suite Node; verificar que una exportacion temporal coincide con `web/data/content.json`.
- Cambios existentes que deben conservarse: toda la implementacion hasta `908a447`, incluidos split de secciones, 55 conceptos, guia Windows, aliases, redirects, colapsado progresivo, version `20260710-alias-densidad` y plan anterior.
- Circunstancias que obligan a detenerse: tests rojos; exportacion no determinista; necesidad de cambiar schema/vistas/secciones; cambio en comandos/IDs/slugs durante editorial; incompatibilidad de persistencia; version PWA desalineada; falta de evidencia visual final.
- Elementos que no deben reanalizarse salvo contradiccion real: `web-discovery` ya abre 7 comandos; las 24 secciones actuales son suficientes; `cve-ruta` no necesita conceptos duplicados; el esquema teorico actual es suficiente; no hacen falta nuevas dependencias.

### Prompt para el modelo ejecutor

Implementa `IMPLEMENTATION_PLAN.md` por fases, respetando sus decisiones,
dependencias, invariantes y criterios de aceptacion. Conserva cambios existentes,
ejecuta las validaciones indicadas y detente ante cualquier condicion de parada.
