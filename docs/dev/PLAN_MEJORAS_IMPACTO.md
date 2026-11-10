# Plan de implementación — THM Fieldbook: utilidad e impacto

## 1. Objetivo

Evolucionar THM Fieldbook de forma incremental, conservando su identidad de chuleta rápida, estática y offline. El objetivo principal es reducir el tiempo entre **«he encontrado esto»** y **«este es el siguiente paso útil»**, conectando búsqueda, rooms, notas, progreso y contenido sin convertir la aplicación en un gestor de proyectos.

La implementación se divide en entregas independientes: primero búsqueda, privacidad y accesibilidad; después rooms, notas y progreso; finalmente metadatos y ampliación editorial.

## 2. Principios obligatorios

1. Mantener despliegue estático en GitHub Pages.
2. Mantener funcionamiento completamente offline.
3. No añadir backend, cuentas, telemetría ni sincronización remota.
4. La aplicación nunca ejecutará comandos; solo mostrará, adaptará y copiará texto.
5. No introducir frameworks, bundlers ni dependencias externas de runtime.
6. Conservar los slugs, hashes, favoritos, recientes, variables, notas y progreso existentes.
7. Mantener los exports públicos usados por `web/app.test.mjs`.
8. `web/data/content.json` seguirá siendo un artefacto generado, nunca editado manualmente.
9. Toda migración de datos será reversible y no eliminará el estado antiguo en su primera versión.
10. Cada entrega deberá funcionar y poder publicarse de manera independiente.

## 3. Alcance

### Incluido

- Búsqueda contextual por hallazgo, síntoma, servicio, herramienta y puerto.
- Ranking, deduplicación y presentación de resultados.
- Rooms ligeras guardables, importables y exportables.
- Protección y tratamiento explícito de credenciales.
- Notas semiestructuradas y export Markdown.
- Progreso asistido, siempre confirmado por el usuario.
- Metadatos verificables para los comandos prioritarios.
- Mejoras de inicio, responsive, teclado y accesibilidad.
- Nuevos contenidos: AD CS, contenedores/DevOps, autenticación moderna, bases de datos, transferencia y post-explotación.
- Migración compatible del estado actual.
- Pruebas, PWA, CI, rollout y rollback.

### Fuera de alcance

- Backend, cuentas, sincronización, nube o telemetría.
- LLM, IA generativa o recomendaciones remotas.
- Ejecución de comandos desde el navegador.
- Cockpit, kanban, inventario avanzado de hosts o gestor de operaciones.
- Reescritura completa de `web/app.mjs`.
- Reversing, pwn, forense, estego y crypto hasta confirmar que forman parte del alcance editorial.

## 4. Arquitectura propuesta

Se conservará `web/app.mjs` como controlador principal. Solo se extraerán funciones puras y aisladas que necesiten pruebas independientes.

```text
web/
  app.mjs                       # estado UI, render y wiring existente
  js/
    search-engine.mjs           # búsqueda normalizada
    search-ranking.mjs          # scoring y deduplicación
    intent-rules.mjs            # reglas «he encontrado X»
    room-store.mjs              # persistencia, migración e import/export
    notes-report.mjs            # plantillas, redacción y Markdown
    progress.mjs                # sugerencias de progreso
    command-metadata.mjs        # lookup de metadata
  *.test.mjs                    # pruebas puras por módulo

tools/
  command_metadata.py           # autoría de metadata de comandos
  intent_rules.py               # reglas exportables si se decide centralizarlas
  concepts.py
  guides.py
  generate_structured_playbook.py
  export_web_content.py
```

`web/app.mjs` reexportará las funciones públicas actuales para mantener compatibilidad.

## 5. Modelo de datos

### 5.1 Room ligera

```text
Room = {
  version,
  id,
  name,
  createdAt,
  updatedAt,
  targetIp,
  attackerIp,
  domain,
  dcHost,
  dcFqdn,
  ports,
  user,
  credentialType,
  notes,
  progress,
  checks,
  reverseShellPreferences
}
```

El secreto no formará parte del objeto persistente por defecto.

### 5.2 Claves de almacenamiento

- `thm-rooms:v1`: rooms persistentes.
- `thm-rooms:active`: id activo.
- `thm-room-secret:<id>`: secreto temporal en `sessionStorage`.
- `thm-rooms:migrated`: marca de migración.
- Las claves antiguas `thm-room`, `thm-favs` y `thm-recent` seguirán siendo legibles.

### 5.3 Metadatos de comandos

`section.commands` continuará siendo un array de strings. Se añadirá una colección independiente `commandMetadata`, enlazada mediante `sectionSlug + comando normalizado`.

Campos previstos:

- objetivo;
- herramienta;
- entorno de ejecución;
- sistema objetivo;
- credenciales requeridas;
- tipo de credencial;
- privilegios necesarios;
- ruido;
- riesgo;
- precondiciones;
- salida esperada;
- señal de éxito;
- errores frecuentes;
- alternativa;
- versión comprobada;
- fecha de revisión;
- referencia opcional.

## 6. Fase 0 — Línea base y contratos

### Objetivo

Congelar el comportamiento que no debe romperse y preparar fixtures reproducibles.

### Tareas

1. Inventariar todos los helpers exportados por `web/app.mjs`.
2. Documentar hashes y deep-links soportados.
3. Crear fixtures de:
   - usuario nuevo;
   - perfil 1.x completo;
   - perfil corrupto;
   - room sin IP;
   - password, hash y key;
   - notas largas;
   - checks y progreso existentes.
4. Definir una matriz de consultas de referencia:
   - `21`, `80`, `445`, `1433`, `6379`;
   - `tengo credenciales`;
   - `shell muere`;
   - `web devuelve 403`;
   - `SeImpersonatePrivilege`;
   - `NOPASSWD vim`;
   - `kdbx`;
   - `jwt`, `graphql`, `docker socket`, `AD CS`;
   - `access denied`, `clock skew`, `todo devuelve 200`.
5. Definir para cada consulta:
   - intención esperada;
   - fase;
   - playbook;
   - tres primeras acciones;
   - resultados que deben penalizarse.
6. Añadir pruebas de caracterización antes de cambiar el comportamiento.

### Criterios de aceptación

- Los contratos antiguos están cubiertos por pruebas.
- Existe una fixture realista de estado 1.x.
- Slugs, hashes, favoritos, notas y progreso actuales tienen tests de regresión.
- Ninguna fase posterior puede cambiar un contrato sin actualizar una prueba explícita.

## 7. Fase 1 — Búsqueda contextual y ranking

### Objetivo

Hacer que la búsqueda responda primero a la intención real del usuario.

### Tareas

1. Extraer la lógica pura a `search-engine.mjs` y `search-ranking.mjs`.
2. Normalizar cada resultado con:
   - tipo;
   - intención;
   - fase;
   - confianza;
   - acción principal;
   - resultados relacionados;
   - motivo del match.
3. Hacer que `PORT_DB` domine cuando la entrada sea un puerto reconocido.
4. Mostrar en el panel central:
   - servicio;
   - interpretación;
   - tres acciones ordenadas;
   - comandos adaptados;
   - señal esperada;
   - enlace al dossier.
5. Mover las coincidencias textuales genéricas a “Relacionadas”.
6. Penalizar:
   - números dentro de listas largas;
   - comandos con IP fija;
   - fases no relacionadas;
   - duplicados exactos o equivalentes;
   - coincidencias únicamente sobre placeholders.
7. Favorecer:
   - servicio o herramienta exactos;
   - aliases explícitos;
   - título/resumen;
   - metadata;
   - sección asociada al puerto.
8. Crear reglas deterministas para:
   - `tengo smb 445`;
   - `encontré user:pass`;
   - `shell linux www-data`;
   - `sudo -l NOPASSWD vim`;
   - `web 403`;
   - `hash ntlm`;
   - `SeImpersonatePrivilege`.
9. Mantener búsqueda por sección, herramienta, comando y concepto.

### Casos límite

- Consultas vacías o de una letra.
- Puertos inválidos.
- Consultas con y sin tildes.
- Consultas que combinan puerto y tecnología.
- Varias intenciones con igual score.
- Comandos duplicados en secciones distintas.
- Consultas extremadamente largas.

### Criterios de aceptación

- `445` muestra SMB y sus acciones como resultado principal.
- Pivoting no supera a SMB únicamente por contener `445`.
- Todas las consultas de referencia obtienen el resultado esperado dentro del top 3.
- No se pierde cobertura de herramientas o comandos actuales.

## 8. Fase 2 — Entrada práctica y navegación

### Objetivo

Reducir la fricción al empezar sin eliminar Aprender ni los atajos existentes.

### Tareas

1. Recordar la última vista utilizada.
2. En primer uso, ofrecer:
   - “Estoy aprendiendo”;
   - “Estoy resolviendo una room”.
3. Para usuarios recurrentes:
   - abrir la última vista;
   - enfocar búsqueda en Práctica;
   - mantener `/` como atajo.
4. Ordenar Práctica:
   - búsqueda;
   - resultado;
   - atajos;
   - filtros;
   - métricas.
5. Mostrar recientes antes del catálogo completo cuando no exista consulta.
6. Compactar los seis atajos cuando haya búsqueda activa.
7. Añadir ejemplos por hallazgo, no solo por herramienta.
8. Preservar hashes y redirecciones existentes.

### Criterios de aceptación

- El usuario recurrente puede escribir inmediatamente.
- La vista elegida persiste tras recargar.
- Aprender sigue accesible en un solo toque.
- Ningún deep-link antiguo termina vacío.

## 9. Fase 3 — Privacidad y variables de credencial

### Objetivo

Evitar exposición accidental y sustituciones incorrectas.

### Tareas

1. Cambiar password a `type=password`.
2. Añadir mostrar/ocultar.
3. Explicar “guardado solo en este navegador”.
4. Ofrecer persistencia:
   - no guardar;
   - guardar durante la sesión;
   - guardar localmente con advertencia.
5. Añadir tipos:
   - password;
   - hash;
   - key.
6. Añadir placeholders:
   - `$PASS`;
   - `$HASH`;
   - `$KEY`;
   - `$USER`.
7. Evitar cruces entre tipos de credencial.
8. Redactar secretos por defecto en downloads y exports.
9. No incluir secretos en errores, logs o nombres de fichero.

### Criterios de aceptación

- La contraseña no es visible por defecto.
- Los secretos no persisten sin consentimiento.
- `$HASH` nunca recibe una contraseña automáticamente.
- Ningún export incluye secretos por defecto.

## 10. Fase 4 — Rooms ligeras

### Objetivo

Permitir cambiar entre rooms sin convertir la app en un workspace complejo.

### Tareas

1. Implementar `room-store.mjs`.
2. Permitir:
   - crear;
   - renombrar;
   - duplicar;
   - activar;
   - borrar;
   - exportar;
   - importar.
3. Integrar un selector compacto en el panel Room.
4. Migrar estado 1.x:
   - copiar, no mover;
   - conservar la clave antigua;
   - marcar la migración;
   - no repetirla.
5. Crear backup previo al reset.
6. Ofrecer deshacer reset.
7. Validar imports:
   - esquema;
   - versión;
   - tamaño;
   - campos permitidos;
   - escaping;
   - ids duplicados.
8. Mostrar preview antes de importar.
9. Gestionar almacenamiento lleno y errores de escritura.

### Casos límite

- Perfil antiguo sin IP.
- JSON corrupto o malicioso.
- Import duplicado.
- Room activa eliminada.
- Varias pestañas abiertas.
- Migración interrumpida.
- localStorage lleno.

### Criterios de aceptación

- Tres rooms pueden alternarse sin mezclar notas o variables.
- El perfil 1.x migra sin perder progreso o checks.
- Si falla la migración, el estado antiguo sigue disponible.
- El reset puede deshacerse.

## 11. Fase 5 — Notas, writeup y progreso asistido

### Objetivo

Mantener la rapidez del textarea y mejorar la reutilización de la información.

### Tareas

1. Mantener notas como Markdown editable.
2. Añadir inserciones rápidas:
   - hallazgo;
   - credencial;
   - hostname/dominio;
   - flag;
   - comando + resultado;
   - hipótesis;
   - siguiente paso;
   - root cause.
3. Permitir timestamp y host/servicio opcionales.
4. Hacer que `+nota` añada:
   - comando adaptado;
   - sección de origen;
   - target;
   - espacio para resultado.
5. Implementar `notes-report.mjs`.
6. Exportar:
   - `.txt` original;
   - `.md` estructurado;
   - copia Markdown;
   - JSON de room.
7. Redactar secretos por defecto.
8. Sugerir progreso cuando se registre:
   - puertos/recon;
   - credencial;
   - shell;
   - flag root.
9. Requerir confirmación antes de modificar progreso.
10. Migrar checks basados en índices hacia identificadores persistentes.

### Criterios de aceptación

- El usuario conserva texto libre.
- Una room puede exportarse como writeup legible.
- Los secretos quedan redactados.
- El progreso nunca cambia silenciosamente.
- Los checks antiguos continúan completados.

## 12. Fase 6 — Metadatos de comandos

### Objetivo

Convertir los comandos prioritarios en conocimiento verificable y mantenible.

### Tareas

1. Crear `tools/command_metadata.py`.
2. Añadir `commandMetadata` al payload generado.
3. Enriquecer inicialmente 100–150 comandos de:
   - quick start;
   - recon;
   - web discovery;
   - credenciales;
   - acceso inicial;
   - Linux/Windows privesc;
   - AD;
   - pivoting;
   - CVE;
   - transferencia.
4. Mostrar metadata en:
   - modal Explicar;
   - resultados de búsqueda;
   - tarjetas de intención;
   - filtros;
   - avisos de riesgo.
5. Mantener heurísticas como fallback.
6. Añadir filtros:
   - Kali/Linux/Windows;
   - con/sin credenciales;
   - silencioso/ruidoso;
   - password/hash/key;
   - herramienta.
7. Validar:
   - referencias huérfanas;
   - claves duplicadas;
   - enums;
   - fechas;
   - versiones;
   - referencias opcionales.

### Criterios de aceptación

- Los comandos prioritarios muestran información específica.
- Modificar un comando con metadata sin actualizar su fuente rompe los tests.
- Los 441 comandos actuales continúan buscables y copiables.

## 13. Fase 7 — Responsive y accesibilidad

### Objetivo

Priorizar resultados en móvil y completar la semántica de interacción.

### Tareas

1. En móvil ordenar:
   - búsqueda;
   - resultado;
   - filtros;
   - atajos;
   - métricas.
2. Convertir fase/tema en “Filtros (n)”.
3. Evitar truncado del target.
4. Mantener copiar, explicar y `+nota` accesibles.
5. Añadir a tabs:
   - `aria-selected`;
   - `aria-controls`;
   - ids de panel;
   - flechas izquierda/derecha.
6. Añadir estados accesibles a filtros y progreso.
7. Anunciar:
   - copia;
   - error;
   - resultado actualizado;
   - filtro;
   - sugerencia de progreso.
8. Gestionar foco en modales, dossier, room y notas.
9. Devolver foco al disparador al cerrar.
10. Mantener Escape y bloquear scroll de fondo.
11. Aumentar objetivos táctiles.
12. No depender exclusivamente del color.
13. Mantener reduced motion.

### Viewports de validación

- 1440×900.
- 1024×768.
- 768×1024.
- 390×844.
- Zoom 200 %.
- Navegación completa sin ratón.

### Criterios de aceptación

- Búsqueda y primer resultado aparecen en la primera pantalla móvil.
- Tabs anuncian correctamente selección y panel.
- Todas las funciones principales son accesibles por teclado.
- No se pierde contenido al 200 %.

## 14. Fase 8 — Ampliación editorial

### Paquete A — Active Directory moderno

- AD CS.
- Templates vulnerables.
- ESC1–ESC8 a nivel metodológico.
- Delegación.
- Trusts.
- BloodHound CE.

### Paquete B — Contenedores y DevOps

- Docker socket/API.
- Capabilities y mounts.
- Kubernetes básico.
- Service accounts.
- Registries.
- Git y secretos.
- CI/CD.

### Paquete C — Autenticación web moderna

- OAuth/OIDC.
- CORS.
- Reset de contraseña.
- MFA.
- Session fixation.
- WebSockets.
- Deserialización.
- Autorización por objeto y función.

### Paquete D — Bases de datos

- MSSQL y linked servers.
- PostgreSQL.
- MySQL/MariaDB.
- Redis.
- MongoDB.
- Acceso anónimo.
- Lectura de ficheros.
- Ejecución según privilegios.
- Loot y pivot.

### Paquete E — Transferencia y post-explotación

- Kali→Linux.
- Kali→Windows.
- LOLBins.
- Entornos sin internet.
- Verificación de integridad.
- Limpieza.
- Evidencia mínima.
- Root cause.
- Writeup reproducible.

### Plantilla obligatoria por concepto

- cuándo aplica;
- cuándo no;
- requisitos;
- señales;
- pasos;
- confirmación segura;
- resultado esperado;
- siguiente decisión;
- conceptos relacionados.

### Mantenimiento

- Revisión trimestral de herramientas prioritarias.
- Aviso para contenido sin verificar durante 12 meses.
- Versiones y fechas en comandos críticos.
- Test de búsqueda por cada bloque nuevo.

### Criterios de aceptación

- Todo concepto pertenece a una ruta.
- No existen enlaces `[[...]]` rotos.
- El contenido nuevo es localizable por situación y término técnico.
- El JSON regenerado coincide exactamente con el comprometido.

## 15. Estrategia de pruebas

### Node

- Intención y ranking.
- Puertos.
- Deduplicación.
- Metadatos.
- `$PASS/$HASH/$KEY`.
- Room store.
- Migración.
- Notas y Markdown.
- Redacción.
- Progreso sugerido.
- Slugs y deep-links.
- Exports heredados.

### Python

- Esquema de metadata.
- Integridad de conceptos.
- Rutas y guías.
- Aliases.
- Fechas/versiones.
- Referencias.
- Export reproducible.

### Browser

- Primer uso.
- Usuario recurrente.
- Búsqueda `445`.
- Búsqueda contextual.
- Rooms.
- Import/export.
- Notas/writeup.
- Teclado.
- Móvil.
- Actualización PWA.
- Carga offline.

### Comandos de validación

```text
node --test web/app.test.mjs web/js/*.test.mjs
python -m unittest discover -s tests -v
python tools/export_web_content.py --output <temporal>
git diff --check
```

## 16. Seguridad y casos de riesgo

1. Escapar nombres de room y contenido importado.
2. Rechazar HTML y propiedades desconocidas en imports.
3. Limitar tamaño de JSON y notas.
4. No ejecutar contenido importado.
5. No incluir secretos en logs o errores.
6. Redactar exports por defecto.
7. Mantener recursos externos fuera de la PWA.
8. Verificar CSP.
9. Recuperar estado si falla localStorage.
10. Probar varias pestañas y actualizaciones concurrentes.
11. Mantener un snapshot antes de reset/migración.
12. No borrar claves antiguas hasta completar el rollout.

## 17. Rollout

### Entrega 1 — Impacto rápido

- Recordar vista.
- Ranking y búsqueda contextual inicial.
- Resultado dominante por puerto.
- Password oculto.
- `$HASH/$KEY`.
- Semántica de tabs.
- Orden móvil.

### Entrega 2 — Utilidad diaria

- Rooms.
- Migración.
- Import/export.
- Notas semiestructuradas.
- Writeup Markdown.
- Progreso sugerido.

### Entrega 3 — Autoridad de contenido

- Metadata de comandos.
- Filtros contextuales.
- Fechas/versiones.
- Paquetes editoriales.

### Requisitos por entrega

1. Tests verdes.
2. Revisión visual desktop/móvil.
3. Único valor de versión en `index.html`, `app.mjs`, `sw.js` y tests.
4. Incremento de `CACHE`.
5. Prueba de actualización desde la versión anterior.
6. Rollback sin pérdida de rooms.
7. Export generado sin diferencias.

## 18. Condiciones que bloquean el despliegue

- Migración fallida.
- Tests rojos.
- Diferencia entre fuentes y `content.json`.
- Metadata huérfana.
- Secretos presentes en exports por defecto.
- Errores de consola en flujos críticos.
- Service worker sirviendo activos incompatibles.
- Deep-links antiguos rotos.
- Pérdida de notas, favoritos o progreso.

## 19. Definición de terminado

- Las consultas de referencia devuelven una acción pertinente dentro del top 3.
- `445` prioriza SMB de extremo a extremo.
- Rooms antiguas migran sin pérdida.
- Los secretos no persisten sin consentimiento.
- Una room se exporta como Markdown reproducible.
- Entre 100 y 150 comandos críticos tienen metadata completa.
- Los contenidos nuevos están integrados en búsqueda, conceptos y rutas.
- Desktop, móvil, teclado, zoom y offline están verificados.
- CI impide publicar contenido generado obsoleto.
- La app conserva su rapidez, su funcionamiento offline y su modelo mental de chuleta.

## 20. Decisiones pendientes

1. Confirmar si reversing, pwn, forense, estego y crypto quedan fuera del producto.
2. Decidir si guardar contraseñas persistentemente estará prohibido o permitido mediante opt-in explícito.
3. Elegir el primer paquete editorial: recomendación inicial, AD CS y bases de datos.
