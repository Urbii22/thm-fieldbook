# Revision teorica PT1

Fecha: 2026-07-13.

## Objetivo

Comprobar que la teoria de Fieldbook cubre el temario oficial PT1 sin conceptos aislados, enlaces rotos, duplicacion innecesaria ni rutas excesivamente densas. Esta revision evalua la base editorial; la soltura practica debe validarse resolviendo rooms.

## Fuentes primarias

- [PT1 Training Content](https://help.tryhackme.com/en/articles/11172303-pt1-training-content).
- [PT1 Certification](https://tryhackme.com/certification/junior-penetration-tester).
- [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final).
- [CVSS v4.0 Specification](https://www.first.org/cvss/v4-0/specification-document).
- [Burp Suite documentation](https://portswigger.net/burp/documentation/contents).
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/).
- [Metasploit documentation](https://docs.rapid7.com/metasploit/).

## Resultado de la auditoria

- Los seis dominios oficiales PT1 tienen conceptos o guias asociados.
- Los 84 conceptos contienen requisitos, descarte, confirmacion, resultado, senales y pasos.
- Todos los conceptos pertenecen a una ruta.
- Las 11 guias apuntan a secciones existentes.
- Los enlaces internos entre conceptos se validan automaticamente.
- No hay IDs ni resumenes duplicados.
- El contenido activo sigue limitado a laboratorios y alcances autorizados.
- CVSS se usa como medida de severidad, no como sustituto del riesgo contextual.

## Matriz de cobertura revisada

| Dominio PT1 | Contenido principal | Estado |
| --- | --- | --- |
| Reconnaissance & Enumeration | `recon-metodologia`, `fingerprinting-servicios`, `tcp-vs-udp`, `packet-analysis` y enumeracion por servicio | Cubierto |
| Web Application Testing | Burp/manual, client-side, sesiones, IDOR/BOLA, JWT, GraphQL, OAuth/CORS, inyecciones, uploads y traversal | Cubierto |
| Network Penetration Testing | SMB/RDP/FTP/SSH/SNMP, password attacks, sniffing, MITM/relay, segmentacion y pivoting | Cubierto |
| Active Directory Exploitation | LDAP, Kerberos, roasting, PTH/PTT, ACL/trusts, BloodHound y AD CS | Cubierto |
| Exploitation & Post-Exploitation | CVE/manual, Metasploit, shells, transferencia, privesc, persistencia y limpieza | Cubierto |
| Reporting & Time Management | Alcance/ROE, notas, cadena de ataque, riesgo, mitigacion, informe y ventana de 48 horas | Cubierto |

La etiqueta `Cubierto` significa que existe una base explicable y accionable; no demuestra dominio practico ni sustituye completar rooms sin receta.

## Correcciones realizadas

1. Se separaron Burp y controles client-side de la ruta de APIs para no mezclar herramienta, validacion cliente y modelos de autorizacion.
2. Se separo la enumeracion de bases de datos de los servicios de red generales.
3. Los exploits de kernel Linux y Windows quedaron en una ruta comun marcada como ultimo recurso.
4. Docker/container escape paso a la ruta Linux avanzada, no a los vectores esenciales.
5. Todas las rutas quedaron limitadas a siete conceptos como maximo.
6. La nota rapida de hallazgo ahora exige causa, evidencia, reproduccion, impacto y mitigacion.
7. El export Markdown se transformo en un informe PT1 con resumen ejecutivo, alcance/ROE, metodologia, cadena de ataque, hallazgos, limpieza y recomendaciones.
8. El export aplica redaccion basica a campos de credenciales y recuerda revisar secretos antes de compartir; ninguna redaccion automatica sustituye la revision manual.

## Decisiones editoriales

- No se amplia contenido solo para aumentar cifras.
- Los conceptos breves se mantienen cuando ya permiten decidir, confirmar y descartar una hipotesis.
- Persistencia y limpieza se explican como cambios controlados. No se incluyen instrucciones para borrar logs defensivos.
- Los simulacros no forman parte del flujo normal y permanecen pendientes hasta acumular evidencia de rooms reales.

## Puerta de salida

La teoria queda lista para pasar a practica guiada cuando el usuario puede explicar, para cada hallazgo:

1. que evidencia genero la hipotesis;
2. que precondiciones exige;
3. que prueba minima la confirma o descarta;
4. que impacto produce;
5. que mitigacion rompe la cadena;
6. como se registra y reproduce en el informe.
