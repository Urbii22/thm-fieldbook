---
titulo: Redes, DNS, puertos y URLs
categoria: Fundamentos
dificultad: Inicial
prerrequisitos:
  - http_y_sesiones.md
fuentes_internas:
  - ../../tools/concepts.py#tcp-vs-udp
  - ../../tools/concepts.py#dns-enum
  - ../../tools/concepts.py#network-segmentation-firewalls
fuentes_externas:
  - https://www.rfc-editor.org/rfc/rfc3986.html
  - https://www.rfc-editor.org/rfc/rfc1034.html
revision: 2026-07-14
estado: revisado
---

# Redes, DNS, puertos y URLs

## Objetivos

Descomponer una URL, explicar resolución y conexión, reconocer loopback/red privada y evitar confundir puerto con servicio.

## URL y autoridad

```text
https://usuario@api.laboratorio.local:8443/v1/items?id=7#detalle
\___/   \_____/ \___________________/ \_______/ \___/ \_____/
scheme  userinfo        host:port        path    query fragment
```

El fragmento normalmente no se envía al servidor HTTP. `userinfo` puede confundir validaciones caseras. El origen web es la terna esquema, host y puerto normalizados. El path y la query se interpretan después de seleccionar destino y aplicación.

## DNS y conexión

1. El cliente obtiene una dirección para un nombre mediante cachés, archivo hosts o DNS.
2. Selecciona IPv4 o IPv6.
3. Abre transporte al puerto indicado o predeterminado.
4. Para HTTPS negocia TLS y valida identidad.
5. Envía HTTP, cuyo `Host` puede seleccionar un virtual host.

El nombre usado para resolver, el SNI de TLS y `Host` suelen coincidir, pero son datos distintos. Esta diferencia explica muchas pruebas de vhosts y algunos fallos de validación.

## Direcciones relevantes

- IPv4 loopback: `127.0.0.0/8`; `127.0.0.1` es el ejemplo habitual.
- IPv6 loopback: `::1`.
- Redes privadas IPv4: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.
- `0.0.0.0` como dirección de escucha no significa que el cliente deba usarla como destino.

Una cadena diferente puede representar el mismo destino después de resolución o normalización. Las defensas deben validar el destino efectivo, no solo la escritura original.

## Puerto no equivale a servicio

Un puerto es un número de extremo de transporte. Un servicio puede escuchar en cualquier puerto. El número sugiere una hipótesis; banner, protocolo y comportamiento aportan evidencia.

| Observación | Hipótesis | Confirmación mínima |
|---|---|---|
| TCP/8080 abierto | Posible HTTP alternativo | enviar petición HTTP válida |
| UDP/53 responde | Posible DNS | consulta DNS bien formada |
| 445 abierto | Posible SMB | negociación SMB, no solo nombre de puerto |

## Parsing diferencial

Una validación puede extraer `host` con una expresión regular y el cliente HTTP con una biblioteca de URL. Si discrepan sobre `@`, barras, codificación, IPv6 o redirecciones, la validación no protege el destino real. El diagnóstico compara el valor original, el valor normalizado y la conexión observada.

## Resumen

Una URL es una estructura, DNS es resolución y el puerto es un extremo. Separar estas capas permite comprender vhosts, SSRF y pivoting.

## Referencias

- [RFC 3986: URI Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986.html)
- [RFC 1034: Domain Names](https://www.rfc-editor.org/rfc/rfc1034.html)

Anterior: [HTTP](http_y_sesiones.md). Siguiente: [Encoding y parsers](encoding_normalizacion_y_parsers.md).
