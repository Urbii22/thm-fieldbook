# Cobertura PT1

Objetivo principal: preparar la certificacion Penetration Tester Level 1 (PT1) de TryHackMe y reforzar habilidades demostrables para un puesto junior de pentesting.

Fuente de referencia: [PT1 Training Content](https://help.tryhackme.com/en/articles/11172303-pt1-training-content), consultada el 2026-07-13.

Fuentes tecnicas primarias: [Burp Suite documentation](https://portswigger.net/burp/documentation/contents), [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/), [Metasploit documentation](https://docs.rapid7.com/metasploit/) y [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final).

## Principios

- Fieldbook apoya decisiones, interpretacion y aprendizaje; no ejecuta acciones por el usuario.
- Practica sigue siendo directa. Las preguntas solo aparecen en Estudiar.
- Se prioriza metodologia reproducible, evidencia e informe sobre acumular payloads.
- Las tecnicas activas se presentan para laboratorios y alcances autorizados.

## Mapa de cobertura

| Dominio oficial PT1 | Cobertura actual | Refuerzo prioritario |
| --- | --- | --- |
| Reconnaissance & Enumeration | Fuerte: Nmap, DNS, subdominios, fingerprinting y servicios | Mantener actualizado y practicar interpretacion de outputs |
| Web Application Testing | Fuerte en OWASP, APIs, auth, sesiones, uploads e inyecciones | Burp, comparacion manual y controles client-side incorporados |
| Network Penetration Testing | Fuerte en SMB, RDP, FTP, SSH, SNMP, credenciales y pivoting | Captura pasiva, poisoning, relay, segmentacion y firewalls incorporados |
| Active Directory Exploitation | Fuerte en enumeracion, roasting, PTH, BloodHound y AD CS | Pass-the-Ticket, ACL y trusts incorporados; ampliar abuso de permisos/trusts con casos guiados |
| Exploitation & Post-Exploitation | Fuerte en CVE, shells, transferencia y privesc Linux/Windows | Flujo de Metasploit y cierre seguro incorporados; ampliar solo con casos reales de rooms |
| Reporting & Time Management | Completa como base teorica | Alcance/ROE, guia PT1 de 48 horas e informe profesional incorporados |

## Contenido PT1 incorporado

- Concepto `burp-manual-testing`.
- Concepto `network-traffic-mitm`.
- Concepto `ad-tickets-trusts`.
- Concepto `pentest-reporting`.
- Concepto `rules-of-engagement-scope`.
- Concepto `client-side-controls`.
- Concepto `packet-analysis`.
- Concepto `network-segmentation-firewalls`.
- Concepto `metasploit-workflow`.
- Concepto `persistence-cleanup-opsec`.
- Guia `pt1-engagement` con cinco fases desde alcance hasta QA del informe.

## Puerta de teoria antes de simulacros

La base teorica se considera completa cuando estan cubiertos los seis dominios oficiales y cada tema explica que es, cuando aplica, que evidencia lo confirma y cuando detenerse. Esta puerta queda cubierta en el contenido actual.

Antes de crear simulacros, el siguiente trabajo editorial sera:

1. Revisar consistencia, enlaces y solapamientos de toda la teoria PT1.
2. Ampliar solo conceptos que una room real revele como insuficientes.
3. Preparar una plantilla reutilizable de hallazgo e informe.
4. Despues, crear simulacros de decision y gestion de las 48 horas como modo opcional.

## Criterio de preparacion

La cobertura teorica no implica estar listo para el examen. Cada dominio debe poder demostrarse en una room sin seguir una receta ciega, explicando:

- que evidencia inicio la hipotesis;
- por que se eligio la prueba;
- que resultado la confirmo o descarto;
- que impacto tuvo;
- como se corregiria;
- como se registraria en un informe profesional.
