---
titulo: "Redes Y Pivoting"
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

# Redes Y Pivoting

Solo para laboratorios autorizados. Sustituye variables, confirma versión y guarda salida.

## Decisión rápida

1. Confirma alcance, identidad y conectividad.
2. Parte de una señal; no ejecutes toda la tabla.
3. Predice salida y prepara un control negativo.
4. Ejecuta la prueba menos intrusiva.
5. Registra evidencia y vuelve al módulo si falla.

## Señales

- ip route
- Dos interfaces
- El pivot tiene una IP en un rango distinto al que tu atacas (ej. 10.10.20.x).
- ip route o arp -a revelan hosts internos que no salian en tu escaneo inicial.
- timeout
- proxy error

## Comandos y pruebas

| Prueba | Objetivo/contexto | Evidencia esperada |
|---|---|---|
| `ip route` | Muestra que redes conoce el host actual y por que interfaz o gateway intentara alcanzarlas. | Prefijos, gateways e interfaces que revelan redes internas y posibles pivots. |
| `ssh -D 1080 -N user@$IP` | Si tienes SSH al pivot, -D monta un proxy SOCKS local sin instalar nada. Es la via mas rapida y limpia con credenciales SSH validas. | No imprime nada (-N): el exito es el puerto 1080 escuchando en tu Kali (compruebalo con ss -tlnp). A partir de ahi, todo va con proxychains. |
| `proxychains nmap -sT -Pn -n -p80,445 10.10.20.5` | proxychains rutea nmap por el SOCKS hacia la red interna. -sT (connect) es obligatorio: por un SOCKS no pasa el SYN scan y darias todo por cerrado. | Puertos abiertos del host interno. Ve a pocos puertos (es lento por el tunel). Servicios abiertos = una mini-room nueva dentro de la red. |
| `ip addr; ip route` | Revela interfaces y redes que realmente ve el pivote. | Subred interna, gateway y rutas disponibles. |
| `ss -ltnp` | Confirma que el servicio de tunel o proxy escucha donde esperas. | Puerto, interfaz y proceso propietario. |

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
