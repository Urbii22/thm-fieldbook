---
titulo: "Estabilizacion De Shells"
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

# Estabilizacion De Shells

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- El prompt no muestra usuario@host, o es un simple $ sin mas.
- Las flechas imprimen ^[[A en vez de moverse por el historial.
- connection refused
- timeout

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `python3 -c 'import pty; pty.spawn("/bin/bash")'` | Crea la pseudo-TTY con la que ya funcionan su/sudo/passwd. Es el primer paso y el mas portable si la victima tiene python3. | El prompt suele cambiar a usuario@host. Si no hay python3, prueba python o 'script -qc /bin/bash /dev/null'. |
| `stty raw -echo; fg` | Se ejecuta EN TU KALI tras poner la shell en background (Ctrl+Z). Pasa tu terminal a modo raw para tener Ctrl+C, flechas y autocompletado dentro de la shell remota. | Al volver (fg) la shell ya se comporta como una terminal normal. Si ves letras dobladas o rota, ajusta filas/columnas con stty rows/cols. |
| `ss -ltnp \| grep 4444` | Confirma que el listener esta abierto en el puerto esperado. | Proceso escuchando en 0.0.0.0:4444 o interfaz correcta. |
| `python3 -c 'import pty; pty.spawn("/bin/bash")'` | Crea una pseudo-TTY cuando la shell Linux es interactiva pero limitada. | Prompt utilizable para completar la estabilizacion. |

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
