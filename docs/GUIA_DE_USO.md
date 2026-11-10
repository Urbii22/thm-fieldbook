# Guia de uso - THM Fieldbook

THM Fieldbook sirve para transformar un hallazgo de una room en una siguiente comprobacion concreta. No ejecuta comandos: los adapta, explica y copia para que los revises antes de usarlos.

## Flujo recomendado

1. Pulsa `room` y crea una room. Guarda IP objetivo, puertos, dominio y usuario.
2. Busca una evidencia real: un puerto, servicio, error, tecnologia, permiso o credencial.
3. Abre el resultado principal y ejecuta solo las comprobaciones prioritarias que apliquen al alcance.
4. Completa las variables de los comandos (`$IP`, `$USER`, `$PASS`, etc.).
5. Registra evidencia y siguiente paso en Notas. Marca progreso solamente al confirmarlo.
6. Exporta la room y el writeup Markdown al finalizar.

## Ejemplos de busqueda

| Escribe | Resultado esperado |
| --- | --- |
| `445` o `tengo smb 445` | Playbook SMB y acciones iniciales para enumerar usuarios y shares. |
| `tengo credenciales` | Rutas para validar y reutilizar credenciales. |
| `web 403` | Opciones de discovery, vhosts, autenticacion y autorizacion. |
| `jwt` o `graphql` | Contenido de APIs y autenticacion moderna. |
| `sudo NOPASSWD vim` | Ruta Linux de escalada por sudo y GTFOBins. |
| `shell linux www-data` | Estabilizacion de shell y enumeracion local. |
| `shell muere` | Diagnostico de listener, TTY y red. |

## Como interpretar el resultado

- Un puerto conocido muestra primero el servicio y las acciones prioritarias.
- Las secciones relacionadas amplian contexto; no son una lista obligatoria de comandos.
- El icono `i` explica objetivo, requisitos, salida esperada, riesgos y errores comunes cuando existe metadata.
- Los avisos de ruido o riesgo no bloquean nada: son una invitacion a verificar alcance y efecto antes de ejecutar.

## Privacidad y respaldo

Las credenciales, hashes y claves viven solo durante la sesion de forma predeterminada. La opcion de persistirlas es local y explicita. La exportacion de room excluye secretos; usala para respaldar o compartir contexto sin exponerlos.
