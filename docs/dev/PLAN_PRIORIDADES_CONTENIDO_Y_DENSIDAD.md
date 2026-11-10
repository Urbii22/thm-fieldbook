# Plan

Reorientar THM Fieldbook hacia contenido fiable, actualizado y facil de consultar en escritorio. El aprendizaje activo sera un modo adicional voluntario; no alterara el flujo rapido por defecto.

## Alcance

### Incluido

- Revision y actualizacion de contenidos.
- Metadata fiable para comandos prioritarios.
- Reduccion de densidad en escritorio.
- Mejora de busqueda y conexiones entre practica y teoria.
- Modo de estudio opcional.
- Accesibilidad basica de escritorio.
- Validacion, exportacion y actualizacion PWA.

### Fuera de alcance

- Mejoras especificas para movil.
- Ejecucion automatica de comandos.
- Recomendaciones autonomas.
- Preguntas obligatorias en el flujo normal.
- Backend, cuentas, telemetria o sincronizacion.
- Gamificacion y nuevos filtros.

## Prioridades

1. Exactitud y actualizacion del contenido.
2. Reduccion de densidad y mejora de la jerarquia.
3. Integracion entre evidencia, teoria y acciones practicas.
4. Modo de estudio activo opcional.
5. Accesibilidad y pulido de escritorio.
6. Publicacion y validacion final.

## Estado de implementacion (2026-07-13)

- [x] Auditar la cobertura real y distinguir fichas curadas de explicaciones generales.
- [x] Corregir los comandos SMB prioritarios y la semantica de flags de NetExec.
- [x] Reducir la densidad inicial de Practica y mantener filtros cerrados.
- [x] Simplificar las acciones y utilidades del panel de room.
- [x] Incorporar Estudiar como modo voluntario, sin progreso automatico.
- [x] Mejorar foco y teclado en dialogos y Notas.
- [x] Regenerar contenido y alinear la version PWA.
- [x] Fijar PT1 de TryHackMe como certificacion objetivo y crear su mapa de cobertura.
- [x] Completar la base teorica PT1: alcance/ROE, client-side, trafico, segmentacion, ACL/trusts, Metasploit, OPSEC e informe.
- [x] Revisar transversalmente estructura, cobertura, enlaces, solapamientos y profundidad de la teoria PT1.
- [x] Preparar una plantilla reutilizable de hallazgo e informe PT1 e integrarla en el export Markdown.
- [ ] Ampliar solo los huecos que aparezcan durante rooms reales.
- [ ] Crear simulacros solo despues de esa revision, dentro del modo Estudiar opcional.

## Plan de trabajo

### 1. Auditar el contenido actual

- Verificar la linea base real: secciones, comandos, conceptos, guias, rutas y fichas de metadata.
- Localizar errores tecnicos, explicaciones ambiguas, duplicados e informacion desactualizada.
- Identificar comandos prioritarios presentes en busquedas, accesos rapidos, guias y conceptos.
- Clasificar los huecos por fase: reconocimiento, enumeracion, acceso, escalada, Active Directory, web, pivoting y cierre.
- Evitar ampliar contenido unicamente para aumentar cifras.

### 2. Corregir y ampliar el conocimiento prioritario

- Sustituir explicaciones heuristicas incorrectas por metadata especifica de cada herramienta.
- Cubrir primero todos los comandos mostrados como acciones prioritarias.
- Documentar para cada comando prioritario:
  - objetivo;
  - requisitos;
  - significado de los flags;
  - resultado esperado;
  - senal de exito;
  - errores frecuentes;
  - riesgo y ruido;
  - alternativa relevante.
- Mostrar una advertencia clara cuando una explicacion no este curada o verificada.
- Anadir pruebas que validen flags y resultados de comandos representativos.

### 3. Actualizar conceptos, guias y rutas

- Revisar conceptos y guias por utilidad real durante una room y para certificaciones.
- Completar primero los flujos con huecos operativos o teoricos.
- Mantener una progresion coherente desde fundamentos hasta tecnicas avanzadas.
- Eliminar repeticiones entre conceptos, guias y secciones practicas.
- Conservar IDs, slugs, hashes y compatibilidad con favoritos y progreso existentes.
- Preparar el contenido para poder mapearlo posteriormente a certificaciones concretas.

### 4. Mejorar busqueda y navegacion contextual

- Ampliar aliases para puertos, servicios, errores, sintomas y situaciones habituales.
- Priorizar el resultado que mejor responde a la evidencia escrita por el usuario.
- Conectar cada resultado practico con sus conceptos y guias relacionados.
- Facilitar el regreso desde la teoria a los comandos de la fase correspondiente.
- Mantener recomendaciones deterministas y transparentes.

### 5. Reducir la densidad de Practica en escritorio

- Dar prioridad a busqueda, resultado principal y contexto actual de la room.
- Ocultar o mover las metricas de inventario a una zona secundaria.
- Compactar los accesos rapidos cuando exista una busqueda activa.
- Mantener filtros cerrados hasta que sean necesarios.
- Mostrar recientes o el ultimo contexto antes que el catalogo completo.
- Evitar que fases, ejemplos, filtros, metricas y atajos compitan simultaneamente.

### 6. Reducir la densidad del contenido

- Mostrar inicialmente un numero limitado de comandos prioritarios.
- Agrupar y colapsar alternativas equivalentes.
- Mantener payloads avanzados y comandos de referencia cerrados por defecto.
- Mostrar primero resumen, requisitos, confirmacion minima y resultado esperado.
- Evitar tarjetas, contenedores o bloques que repitan informacion.
- Mantener todo el contenido accesible mediante divulgacion progresiva.

### 7. Simplificar el panel de room

- Priorizar IP, contexto y variables utilizadas con frecuencia.
- Mover duplicar, importar, exportar y eliminar a un menu secundario.
- Colocar el generador de reverse shell dentro de una seccion de utilidades.
- Mantener secretos protegidos y fuera de exportaciones por defecto.
- No convertir la room en un gestor de proyectos ni automatizar su progreso.

### 8. Incorporar un modo de estudio opcional

- Anadir `Estudiar` como modo secundario dentro de Aprender.
- Mantenerlo desactivado por defecto.
- No introducir preguntas ni interrupciones en Practica o en la lectura normal.
- Incluir de forma voluntaria:
  - preguntas antes de revelar la respuesta;
  - casos de interpretacion de resultados;
  - decisiones sobre el siguiente paso;
  - autoevaluacion manual: `no lo entiendo`, `con ayuda`, `puedo explicarlo`.
- No modificar progreso ni confianza sin confirmacion explicita del usuario.
- No generar soluciones automaticas ni ejecutar acciones.

### 9. Mejorar accesibilidad de escritorio

- Gestionar foco inicial, atrapamiento y retorno en modales y drawers.
- Sustituir elementos con `role="button"` por botones reales cuando corresponda.
- Mejorar el contraste del texto secundario de tamano pequeno.
- Mantener navegacion completa por teclado y foco visible.
- Revisar objetivos interactivos pequenos como explicar, guardar y editar.
- No dedicar esta iteracion a responsive o QA movil.

### 10. Validar y publicar

- Regenerar `web/data/content.json` exclusivamente desde las fuentes Python.
- Ejecutar:

```text
python tools/export_web_content.py
python -m unittest discover -s tests -v
node --test web/app.test.mjs web/js/search-ranking.test.mjs web/js/search-engine.test.mjs web/js/room-store.test.mjs web/js/progress.test.mjs web/js/notes-report.test.mjs web/js/intent-rules.test.mjs
git diff --check
```

- Verificar manualmente en escritorio:
  - entrada en Practica;
  - busquedas por puerto, servicio, error y evidencia;
  - apertura de conceptos y guias;
  - panel de room;
  - notas y exportacion;
  - foco y teclado;
  - persistencia;
  - funcionamiento offline.
- Actualizar una sola vez los marcadores de version PWA al cerrar la iteracion.
- Revisar el diff final antes de crear commits o publicar.

## Criterios de aceptacion

- Ninguna accion prioritaria muestra flags o resultados explicados incorrectamente.
- Los comandos destacados tienen metadata curada o indican claramente que falta verificarla.
- La pantalla inicial de Practica muestra una jerarquia mas clara y menos elementos simultaneos.
- Las secciones no presentan muros de comandos al abrirse.
- El contenido avanzado sigue disponible mediante bloques colapsados.
- Practica y Aprender conservan su funcionamiento directo actual.
- El modo Estudiar es opcional y esta desactivado por defecto.
- El usuario confirma manualmente progreso, resultados y confianza.
- No se introducen automatizacion, ejecucion de comandos ni decisiones opacas.
- Los tests Python y Node pasan.
- `content.json` coincide con las fuentes y la PWA sirve la version nueva.
- No se producen regresiones en hashes, favoritos, rooms, notas o progreso.

## Riesgos

- Un diff editorial grande puede ocultar cambios tecnicos involuntarios.
- Las explicaciones genericas pueden seguir transmitiendo conceptos incorrectos si no se limita su uso.
- Reducir densidad puede esconder acciones importantes si la divulgacion progresiva no es clara.
- Nuevos conceptos pueden duplicar guias o secciones existentes.
- Cambiar IDs o slugs puede romper favoritos, hashes y progreso guardado.
- Una version PWA desalineada puede servir contenido antiguo.

## Orden recomendado de commits

1. `test(content): add knowledge integrity contracts`
2. `fix(content): correct priority command explanations`
3. `feat(content): update concepts guides and aliases`
4. `refactor(ui): reduce desktop information density`
5. `refactor(ui): simplify room utilities`
6. `feat(learn): add optional study mode`
7. `fix(a11y): improve desktop focus and contrast`
8. `chore: export and release updated Fieldbook content`

## Certificacion objetivo

- PT1 de TryHackMe es la referencia editorial principal.
- La prioridad es adquirir capacidad practica y explicable para optar cuanto antes a puestos junior de pentesting.
- El detalle de cobertura y los huecos se mantienen en `PT1_COBERTURA.md`.
