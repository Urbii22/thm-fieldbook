# Plan de implementación de contenidos y usabilidad — alcance recortado

## Objetivo

Mejorar THM Fieldbook como herramienta personal de apoyo durante prácticas, rooms y laboratorios de pentesting. El objetivo no es convertirla en una plataforma de certificaciones ni en una wiki exhaustiva, sino conseguir que el usuario encuentre rápidamente qué significa un hallazgo, qué necesita para probarlo, qué resultado debe esperar y cuál es el siguiente paso.

Este plan aplica un recorte deliberado: prioriza las carencias con mayor impacto y aplaza todo lo que implique un coste de autoría o mantenimiento desproporcionado.

## Alcance

### Incluido

- Dividir las dos secciones realmente densas: `web-y-apis` y `credenciales-y-loot`.
- Dividir las rutas de Linux y Windows privesc en esencial y avanzada, sin eliminar profundidad.
- Añadir 13 conceptos prioritarios: 7 de web y 6 de enumeración de servicios.
- Añadir una guía paso a paso de Windows privesc.
- Completar `necesitas` en los 42 conceptos existentes.
- Añadir únicamente tres campos teóricos nuevos: cuándo no aplica, confirmación mínima y resultado esperado.
- Añadir alias de búsqueda por puerto, síntoma y situación.
- Reducir la densidad visual utilizando los patrones existentes de bloques e índices.
- Añadir las pruebas necesarias para proteger slugs, enlaces, rutas y guías.

### Aplazado

- Plantilla de 20 apartados por concepto.
- Fuentes, fechas de revisión, estados editoriales y cadencias de mantenimiento.
- Once facetas de filtrado y metadatos exhaustivos.
- Contenido web avanzado: OAuth, deserialización, race conditions, request smuggling, cache poisoning, prototype pollution y WebSockets.
- Nuevas áreas: cloud, SOC/SIEM, forense, malware, reversing, wireless y móvil.
- Más guías aparte de Windows privesc.
- División completa de la aplicación en 27 secciones.
- División de Active Directory mientras su ruta siga teniendo 5 conceptos.

## Línea base y objetivo final

| Elemento | Estado actual | Objetivo de esta iteración |
|---|---:|---:|
| Secciones | 19 | 24 |
| Conceptos | 42 | 55 |
| Guías | 8 | 9 |
| Rutas | 9 | 11 |
| Conceptos nuevos | — | 13 |
| Campos teóricos obligatorios nuevos | — | 3 |
| Conceptos con `necesitas` | 8/42 | 55/55 |

El aumento de secciones procede únicamente de sustituir:

- Una sección Web por cuatro secciones: incremento neto de 3.
- Una sección Credenciales por tres secciones: incremento neto de 2.

## Principios de implementación

1. No eliminar profundidad existente.
2. No añadir contenido avanzado hasta completar el núcleo.
3. No mostrar más de 12 comandos inicialmente dentro de un bloque.
4. Separar siempre explicación, prueba, resultado y decisión.
5. Mantener los cambios pequeños, verificables y commiteables por fases.
6. Añadir guardas antes de cambiar slugs.
7. Conservar compatibilidad con enlaces y favoritos antiguos.

---

## Action items

[ ] **1. Añadir guardas antes de cambiar la estructura**

### Archivos

- `web/app.test.mjs`
- `tests/test_export_web_content.py`

### Protecciones que ya existen

- IDs de concepto únicos.
- Campos básicos de conceptos.
- Fases válidas.
- `concept.section` apuntando a una sección existente.
- Enlaces `[[concepto]]` resolubles.
- IDs de ruta únicos.
- Conceptos de las rutas existentes.
- Forma válida de comandos en conceptos y guías.

### Guardas nuevas necesarias

1. **Conceptos sin ruta**
   - Construir el conjunto de conceptos utilizados por todas las rutas.
   - Fallar si un concepto no pertenece a ninguna ruta.

2. **Sección de las guías**
   - Verificar que todo `guide.section` exista en las secciones exportadas.

3. **Slugs antiguos**
   - Mantener una tabla de redirección de slugs retirados.
   - Verificar que todo slug retirado apunte a una sección nueva válida.

4. **Alias de búsqueda**
   - Verificar las consultas prioritarias definidas en este plan.

5. **Campos nuevos**
   - Exigir `necesitas`, `no_aplica`, `confirmacion` y `resultado` en todos los conceptos cuando termine la migración.

### Compatibilidad mínima de slugs

| Slug antiguo | Destino predeterminado |
|---|---|
| `web-y-apis` | `web-discovery` |
| `credenciales-y-loot` | `loot-y-secretos` |

Los favoritos, recientes, hashes y enlaces internos que contengan los slugs antiguos deben resolverse al destino nuevo sin producir una pantalla vacía.

### Criterios de aceptación

- Las pruebas actuales siguen pasando.
- Los tres huecos de integridad quedan cubiertos.
- Los slugs antiguos tienen destino explícito antes de ser retirados.
- Este paso no cambia todavía el contenido visible.

[ ] **2. Simplificar la plantilla teórica sin sobrecargarla**

### Archivo principal

- `tools/concepts.py`

### Mantener los campos actuales

- `id`
- `title`
- `phase`
- `section`
- `summary`
- `que`
- `porque`
- `cuando`
- `necesitas`
- `senales`
- `pasos`
- `commands`

### Añadir solo estos tres campos

#### `no_aplica`

Debe responder a: “¿Qué condición me permite descartar esta técnica?”.

Ejemplos de contenido esperado:

- No existe un parámetro controlable.
- El servicio no acepta el método necesario.
- La cuenta no posee el privilegio requerido.
- La versión o configuración no coincide.

#### `confirmacion`

Debe describir una prueba mínima, concreta y preferiblemente inocua.

Ejemplos de contenido esperado:

- Una operación matemática para SSTI.
- Lectura de un fichero conocido para LFI.
- Cambio de un identificador propio por otro para IDOR.
- Un comando como `id`, `whoami` o `hostname` para command injection.

#### `resultado`

Debe describir el patrón observable que confirma o descarta la hipótesis.

Ejemplos de contenido esperado:

- Código 200 con datos de otro usuario.
- Resultado `49` al evaluar una expresión.
- Respuesta que contiene `root:x:0:0`.
- Salida con `uid=` o nombre del usuario de servicio.

### Migración de `necesitas`

Completar primero los 34 conceptos actuales que no tienen el campo.

Cada lista `necesitas` debe contener entre uno y cuatro requisitos concretos:

- Acceso o contexto requerido.
- Entrada controlable.
- Herramienta o información necesaria.
- Restricción relevante.

### Presentación

Mostrar inicialmente:

1. Resumen.
2. Necesitas.
3. Confirmación mínima.
4. Resultado esperado.

Mostrar después:

5. Qué es.
6. Por qué ocurre.
7. Cuándo aplica.
8. Cuándo no aplica.
9. Señales.
10. Pasos y comandos.

### Criterios de aceptación

- Los 55 conceptos finales contienen los cuatro campos prioritarios.
- Ningún concepto añade apartados editoriales adicionales.
- La parte rápida aparece antes de la explicación extensa.
- Los textos son breves y accionables.

[ ] **3. Dividir `web-y-apis` en cuatro secciones**

### Archivos afectados

- `tools/generate_structured_playbook.py`
- `tools/generate_thm_playbook.py`, si los comandos maestros siguen siendo necesarios.
- `tools/export_web_content.py`
- `tools/concepts.py`
- `tools/guides.py`
- `web/app.mjs`
- `web/data/content.json`, regenerado.
- Tests de exportación y aplicación.

### Secciones nuevas

#### A. `web-discovery`

Contenido actual que debe recibir:

- Bloque “Fingerprinting y discovery”.
- `curl`, `whatweb`, `ffuf`, `gobuster`, `feroxbuster`, `wfuzz`, `katana` y `arjun` utilizados para discovery.
- Descubrimiento de directorios, ficheros, vhosts, parámetros y JavaScript.

Reglas:

- Un comando recomendado por tarea.
- Alternativas colapsadas.
- Eliminar duplicados de wordlists o variantes que no cambien la decisión.

#### B. `web-apis-y-autorizacion`

Contenido actual que debe recibir:

- Bloque “APIs REST y métodos HTTP”.
- Enumeración de endpoints.
- Métodos HTTP.
- JSON.
- IDOR/BOLA.
- JWT.
- GraphQL.

Concepto nuevo principal:

- `idor-bola`

#### C. `web-inyecciones`

Contenido actual que debe recibir:

- SSTI.
- SSRF.
- XXE.
- Command injection.
- Payloads de confirmación asociados.

Conceptos nuevos:

- `ssti`
- `ssrf`
- `xxe`
- `command-injection`

SQLi permanece en su sección específica.

#### D. `web-ficheros-y-ejecucion`

Contenido actual que debe recibir:

- LFI.
- LFI a RCE.
- File upload.
- Web shells.
- Lectura de código fuente.
- `.git` expuesto.

Conceptos existentes:

- `lfi`
- `lfi-a-rce`

Concepto nuevo:

- `file-upload`

### Concepto transversal pendiente en Web

- `xss`

Ubicarlo inicialmente en `web-inyecciones` para evitar crear una quinta sección. Si el contenido web de cliente crece en el futuro, podrá independizarse.

### Redistribución de contenido

| Bloque actual | Destino |
|---|---|
| Fingerprinting y discovery | `web-discovery` |
| APIs REST y métodos HTTP | `web-apis-y-autorizacion` |
| LFI/SSTI/upload | Separar entre `web-inyecciones` y `web-ficheros-y-ejecucion` |
| LFI a RCE | `web-ficheros-y-ejecucion` |
| Triage de bugs | Convertir en resumen y enlaces a las tres secciones técnicas |
| Más comandos | Clasificar, deduplicar y asignar por técnica |

### Comandos maestros

`MASTER_SECTION_SLUGS` actualmente fusiona `web-moderna-y-apis` dentro de `web-y-apis`. Antes de retirar el slug:

- Sustituir el destino único por una redistribución explícita.
- Evitar que todos los comandos maestros terminen en `web-discovery`.
- Mantener la deduplicación por comando.
- Añadir una prueba que verifique al menos un comando representativo en cada sección nueva.

### Compatibilidad

- `web-y-apis` debe redirigir a `web-discovery`.
- Los conceptos LFI deben apuntar a `web-ficheros-y-ejecucion`.
- La guía “De la web a una shell” debe apuntar al punto de entrada más adecuado, previsiblemente `web-discovery`.
- Los theory chips deben apuntar a la nueva sección correcta de cada concepto.

### Criterios de aceptación

- No existe un bloque monolítico de 83 comandos.
- Cada comando web pertenece a una sola sección, salvo duplicación deliberada y justificada.
- Los siete conceptos web están enlazados desde su sección correspondiente.
- Buscar LFI, JWT, IDOR, SSTI, SSRF, XXE, XSS, upload o command injection abre contenido relevante.
- Los hashes y favoritos antiguos continúan funcionando.

[ ] **4. Dividir `credenciales-y-loot` en tres secciones**

### Archivos afectados

- `tools/generate_structured_playbook.py`
- `tools/generate_thm_playbook.py`, si aplica.
- `tools/export_web_content.py`
- `tools/concepts.py`
- `tools/guides.py`
- `web/app.mjs`
- `web/data/content.json`, regenerado.
- Tests.

### Secciones nuevas

#### A. `loot-y-secretos`

Contenido:

- Buscar credenciales en disco.
- Ficheros de configuración.
- Historiales.
- Claves SSH.
- Navegadores y aplicaciones.
- Backups.
- Vaults.
- Stego y ficheros, solo como referencia secundaria.

#### B. `hashes-y-cracking`

Contenido:

- Conversiones frecuentes.
- Identificación de hash.
- Hashcat.
- John.
- Reglas y wordlists.
- Archivos protegidos.

Concepto existente principal:

- `cracking`

#### C. `credenciales-y-acceso`

Contenido:

- Reutilización de credenciales.
- Fuerza bruta online.
- Password spraying.
- Validación por servicio.
- Responder y relay de hashes de red.

Concepto existente principal:

- `fuerza-bruta-online`

### Redistribución de bloques actuales

| Bloque actual | Destino |
|---|---|
| Conversiones frecuentes | `hashes-y-cracking` |
| Buscar en disco y reutilizar | Dividir entre `loot-y-secretos` y `credenciales-y-acceso` |
| Fuerza bruta online | `credenciales-y-acceso` |
| Responder/relay | `credenciales-y-acceso` |
| Loot de navegadores y apps | `loot-y-secretos` |
| Stego y forense de ficheros | `loot-y-secretos`, colapsado como referencia |

### Comandos maestros

`MASTER_SECTION_SLUGS` actualmente fusiona `credenciales-cracking-y-loot` dentro de `credenciales-y-loot`.

Actualizar la fusión para:

- Clasificar conversiones y cracking en `hashes-y-cracking`.
- Clasificar búsquedas y loot en `loot-y-secretos`.
- Clasificar pruebas online y reutilización en `credenciales-y-acceso`.
- Evitar una sección nueva que vuelva a concentrar los 62 comandos.

### Compatibilidad

- `credenciales-y-loot` debe redirigir a `loot-y-secretos`.
- La guía “Tengo credenciales, y ahora qué” puede mantener `loot-y-secretos` como entrada y enlazar los pasos de cracking y reutilización.
- Los favoritos y recientes antiguos deben migrar o resolverse.

### Criterios de aceptación

- Ninguna de las tres secciones hereda los 62 comandos completos.
- Buscar hash prioriza `hashes-y-cracking`.
- Buscar contraseña encontrada o credencial válida prioriza `credenciales-y-acceso`.
- Buscar config, history, key o vault prioriza `loot-y-secretos`.
- El contenido de stego no domina la ruta principal de credenciales.

[ ] **5. Dividir las rutas de privesc sin eliminar conceptos**

### Archivo principal

- `tools/concepts.py`, bloque `PATHS`.

### Linux privesc esencial — 7 conceptos

1. `privesc-modelo`
2. `enum-privesc-linux`
3. `sudo-abuse`
4. `suid`
5. `capabilities`
6. `cron-abuse`
7. `writable-sensitive-files`

### Linux privesc avanzada — 7 conceptos

1. `path-hijacking`
2. `python-library-hijacking`
3. `wildcard-injection`
4. `sudo-ld-preload`
5. `group-abuse-linux`
6. `nfs-no-root-squash`
7. `kernel-exploits-linux`

### Windows privesc esencial — 6 conceptos

1. `winprivesc-modelo`
2. `enum-privesc-windows`
3. `token-impersonation`
4. `service-misconfig-windows`
5. `stored-credentials-windows`
6. `always-install-elevated`

### Windows privesc avanzada — 5 conceptos

1. `registry-autoruns`
2. `dll-hijacking`
3. `sebackup-serestore`
4. `uac-bypass`
5. `kernel-exploits-windows`

### Active Directory

Mantener la ruta actual con sus 5 conceptos:

- `ad-modelo`
- `kerberos`
- `asrep-kerberoast`
- `ntlm-pth`
- `bloodhound`

No dividir AD hasta que supere 7 conceptos o exista una segunda capa teórica claramente útil.

### Criterios de aceptación

- Se conservan los 25 conceptos privesc actuales.
- Ninguna ruta supera 7 conceptos.
- La ruta esencial aparece antes que la avanzada.
- La navegación anterior/siguiente no salta entre Linux y Windows.
- Las rutas avanzadas no se presentan como prerrequisito para empezar.

[ ] **6. Añadir los 13 conceptos prioritarios**

### Requisitos comunes

Cada concepto nuevo debe incluir:

- `necesitas`
- `no_aplica`
- `confirmacion`
- `resultado`
- Qué es.
- Por qué ocurre.
- Cuándo aplica.
- Señales.
- Pasos.
- Entre uno y tres comandos esenciales.

### Web — 7 conceptos

#### `ssti`

- Diferenciar reflexión de evaluación.
- Confirmar con operación matemática.
- Identificar el motor antes de usar payloads específicos.
- Resultado: expresión evaluada por el servidor.

#### `ssrf`

- Parámetros típicos: URL, webhook, avatar, import.
- Confirmación contra listener controlado.
- Diferenciar SSRF ciega y visible.
- Resultado: petición recibida o contenido interno devuelto.

#### `xxe`

- Entradas XML, SVG, SOAP, SAML y documentos.
- Confirmación con entidad local inocua en laboratorio.
- Diferenciar parser no vulnerable de salida no reflejada.
- Resultado: contenido de fichero o callback externo.

#### `idor-bola`

- Objetos identificados por ID.
- Necesidad de dos identidades o recursos comparables.
- Confirmación cambiando un identificador.
- Resultado: acceso a datos o acciones de otro usuario.

#### `xss`

- Diferenciar reflejado, almacenado y DOM.
- Confirmación con ejecución controlada.
- Separar reflexión HTML de ejecución JavaScript.
- Resultado: JavaScript ejecutado en el contexto esperado.

#### `file-upload`

- Validaciones de extensión, MIME, magic bytes y nombre.
- Localización del archivo subido.
- Diferenciar almacenamiento de ejecución.
- Resultado: archivo accesible y, si aplica, ejecutable.

#### `command-injection`

- Entradas típicas: host, IP, dominio, filename.
- Confirmación con `id`, `whoami`, `hostname` o delay.
- Diferenciar error del programa de ejecución real.
- Resultado: salida o efecto temporal controlado.

### Enumeración de servicios — 6 conceptos

#### `dns-enum`

- Resolución de nombres.
- Transferencia de zona.
- Registros relevantes.
- Relación con vhosts y dominios internos.

#### `ftp-enum`

- Acceso anonymous.
- Listado y descarga.
- Permisos de escritura.
- Reutilización de credenciales.

#### `snmp-enum`

- Comunidades por defecto.
- Usuarios, procesos, interfaces y software.
- Diferencia entre UDP filtrado y comunidad incorrecta.

#### `nfs-enum`

- Exports.
- Montaje.
- Permisos y UID/GID.
- Relación con `no_root_squash`.

#### `ldap-enum`

- Naming contexts.
- Base DN.
- Bind anónimo frente a autenticado.
- Usuarios, grupos y dominio.

#### `smtp-enum`

- Banner.
- VRFY/EXPN cuando existan.
- Usuarios.
- Relay y envío de prueba dentro del laboratorio.

### Ubicación en rutas

- Los conceptos web deben integrarse en rutas existentes o en una única ruta web adicional, sin crear una ruta por vulnerabilidad.
- Los seis conceptos de servicios deben añadirse a una ruta “Enumeración de servicios”.
- La ruta no debe superar 7 conceptos; puede incluir los seis nuevos más `smb-enum`.

### Criterios de aceptación

- El total final es 55 conceptos.
- Todos pertenecen a una sección y ruta válidas.
- Todos se localizan mediante su nombre, acrónimo y señal típica.
- Ninguno requiere contenido avanzado adicional para ser útil.

[ ] **7. Añadir una guía de Windows privesc**

### Archivo

- `tools/guides.py`

### ID y destino

- ID sugerido: `privesc-windows`
- Título: “Escalar privilegios en Windows”
- Sección: `windows-privesc`
- Fase: `privesc`

### Paso 1. Contexto y privilegios

- Usuario y host.
- Grupos.
- Privilegios de token.
- Versión y arquitectura.
- Decisión: priorizar tokens, servicios, tareas o credenciales.

### Paso 2. Enumeración rápida

- Servicios.
- Tareas programadas.
- Configuraciones.
- Historiales y credenciales.
- Herramienta automatizada como apoyo, no sustituto del análisis.

### Paso 3. Vectores prioritarios

- SeImpersonate y familia Potato.
- Servicios modificables.
- Unquoted service paths.
- AlwaysInstallElevated.
- Ficheros o scripts escribibles.

### Paso 4. Credenciales y privilegios especiales

- `cmdkey`.
- PowerShell history.
- Unattend y configuraciones.
- SeBackup/SeRestore.
- Reutilización controlada.

### Paso 5. Confirmación y cierre

- Confirmar usuario administrador o SYSTEM.
- Registrar vector exacto.
- Guardar evidencia mínima.
- Dejar kernel y UAC como alternativas avanzadas.

### Reglas de la guía

- Máximo cinco pasos.
- Máximo tres comandos esenciales por paso.
- Cada comando incluye por qué y resultado esperado.
- Cada paso termina con una decisión.
- No duplicar el texto completo de los conceptos.

### Criterios de aceptación

- Total final de 9 guías.
- La guía enlaza teoría esencial y avanzada.
- El flujo funciona tanto con shell CMD como PowerShell.
- Los vectores más arriesgados aparecen al final.

[ ] **8. Añadir alias de búsqueda por puerto y síntoma**

### Enfoque

Crear un catálogo pequeño de alias que expanda consultas hacia términos ya indexados. No añadir filtros nuevos ni metadatar todos los comandos.

### Alias mínimos

| Consulta | Expandir hacia |
|---|---|
| `21` | FTP, anonymous, ftp-enum |
| `25` | SMTP, smtp-enum, VRFY |
| `53` | DNS, AXFR, dns-enum |
| `88` | Kerberos, Active Directory, AS-REP |
| `161` | SNMP, snmpwalk, snmp-enum |
| `389` | LDAP, dominio, ldap-enum |
| `445` | SMB, shares, nxc, smbclient |
| `2049` | NFS, showmount, nfs-enum |
| `tengo hash` | cracking, hashcat, John, Pass-the-Hash |
| `tengo credenciales` | reutilización, spraying, servicios |
| `shell muere` | TTY, estabilizar, shell troubleshooting |
| `todo devuelve 200` | wildcard, ffuf, filtros de tamaño |
| `access denied` | permisos, formato de usuario, credenciales |
| `reloj` | Kerberos, clock skew, sincronización |
| `servicio interno` | pivoting, forwarding, SOCKS |
| `version` / `versión` | CVE, searchsploit, PoC |

### Orden esperado de resultados

1. Guía relevante.
2. Concepto.
3. Sección.
4. Comando.

### Criterios de aceptación

- Todos los alias de la tabla tienen una prueba.
- Buscar un puerto no devuelve únicamente el comando que contiene ese número.
- Las consultas con y sin tildes son equivalentes.
- No se añaden nuevas facetas de filtrado.

[ ] **9. Reducir densidad utilizando patrones existentes**

### Secciones nuevas

Mostrar inicialmente:

1. Resumen de la sección.
2. Entre tres y cinco bloques de decisión.
3. Primer bloque abierto.
4. Máximo 12 comandos visibles.

Mantener colapsados:

- Alternativas de herramientas.
- Variantes del mismo comando.
- Payloads avanzados.
- Comandos de referencia.

### Conceptos

Orden rápido:

1. Necesitas.
2. Confirmación mínima.
3. Resultado esperado.
4. Cuándo no aplica.

Orden profundo:

5. Qué es.
6. Por qué ocurre.
7. Cuándo aplica.
8. Señales.
9. Pasos.
10. Comandos.

### Restricciones

- No crear un nuevo sistema de componentes si los bloques actuales ya permiten la separación.
- No añadir una vista nueva.
- No añadir progreso, quizzes ni gamificación.
- No introducir más filtros.

### Criterios de aceptación

- Web y Credenciales dejan de parecer bloques-muro.
- El primer paso útil aparece sin recorrer decenas de comandos.
- El contenido avanzado continúa disponible.
- La navegación por teclado y el foco siguen funcionando.

[ ] **10. Ejecutar la migración por fases verificadas y commits pequeños**

### Orden recomendado

#### Commit 1. Guardas estructurales

- Conceptos en rutas.
- `guide.section` válido.
- Slugs antiguos resolubles.
- Pruebas de alias preparadas.

#### Commit 2. Plantilla teórica mínima

- Añadir los tres campos.
- Completar `necesitas` en los conceptos actuales.
- Adaptar renderizado y pruebas.

#### Commit 3. División de Web

- Crear cuatro secciones.
- Redistribuir comandos.
- Actualizar slugs, conceptos y guía.
- Mantener compatibilidad antigua.

#### Commit 4. División de Credenciales

- Crear tres secciones.
- Redistribuir comandos.
- Actualizar conceptos y guía.
- Mantener compatibilidad antigua.

#### Commit 5. Rutas privesc

- Dividir Linux en 7+7.
- Dividir Windows en 6+5.
- Mantener AD sin cambios.

#### Commit 6. Conceptos web

- Añadir los siete conceptos.
- Enlazar secciones y rutas.
- Añadir alias y relaciones.

#### Commit 7. Conceptos de servicios

- Añadir los seis conceptos.
- Crear o completar la ruta de enumeración.

#### Commit 8. Guía Windows privesc

- Añadir guía.
- Enlazar conceptos esenciales y avanzados.

#### Commit 9. Alias y reducción de densidad

- Añadir alias.
- Ajustar bloques visibles y colapsados.
- Probar consultas prioritarias.

#### Commit 10. Exportación y verificación final

- Regenerar `web/data/content.json`.
- Ejecutar pruebas Python y Node.
- Verificar manualmente rutas, favoritos, hashes y búsqueda.

### Verificación después de cada commit

- `python -m unittest discover -s tests -v`
- `node --test web/app.test.mjs`
- Revisar `git diff --check`.
- Confirmar que `content.json` coincide con las fuentes.
- Abrir al menos una sección y un concepto afectados.

### Escenarios manuales finales

1. Buscar `445` y llegar a SMB.
2. Buscar `shell muere` y llegar a TTY.
3. Buscar `tengo hash` y llegar a cracking/reutilización.
4. Abrir un hash antiguo de `web-y-apis` y verificar redirección.
5. Abrir un favorito antiguo de `credenciales-y-loot`.
6. Navegar las dos rutas Linux.
7. Navegar las dos rutas Windows.
8. Recorrer la guía Windows privesc.
9. Buscar cada uno de los 13 conceptos nuevos.
10. Verificar que ninguna sección nueva concentra otra vez todos los comandos.

### Criterios de aceptación globales

- 24 secciones exportadas.
- 55 conceptos exportados.
- 9 guías exportadas.
- 11 rutas exportadas.
- Ninguna ruta supera 7 conceptos.
- Los 55 conceptos contienen los cuatro campos prioritarios.
- Los slugs antiguos continúan resolviéndose.
- Las búsquedas prioritarias funcionan.
- Las pruebas Python y Node pasan.
- No hay conceptos huérfanos ni referencias rotas.
- No se ha implementado ninguna de las áreas aplazadas.

## Open questions

- Ninguna pregunta bloqueante. El alcance queda cerrado con las cifras y prioridades indicadas en este documento.

