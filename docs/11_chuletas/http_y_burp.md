---
titulo: "Http Y Burp"
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

# Http Y Burp

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- Cookie de sesion
- Authorization Bearer
- rutas /api
- respuestas JSON
- Set-Cookie
- Authorization: Bearer

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `curl -i $URL/` | Establece una respuesta HTTP base fuera del navegador para comparar status y cabeceras. | Status, cabeceras y cuerpo de referencia. |
| `curl -sS $URL/swagger.json` | Busca un contrato OpenAPI publicado. | Listado de rutas, metodos y esquemas. |
| `curl -sS -i -X OPTIONS "$URL/api/resource"` | Comprueba metodos aceptados por un recurso. | Cabeceras Allow y respuesta del endpoint. |
| `curl -sS "$URL/api/me" -H "Authorization: Bearer $TOKEN"` | Verifica el contexto de identidad actual. | Perfil o respuesta autenticada. |
| `curl -sS -i "$URL/api/me"` | Compara el endpoint sin credenciales. | 401/403 o respuesta publica. |

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
