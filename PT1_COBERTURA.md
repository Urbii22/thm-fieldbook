# Cobertura PT1

Objetivo principal: preparar la certificacion Penetration Tester Level 1 (PT1) de TryHackMe y reforzar habilidades demostrables para un puesto junior de pentesting.

Fuente de referencia: [PT1 Training Content](https://help.tryhackme.com/en/articles/11172303-pt1-training-content), consultada el 2026-07-13.

## Principios

- Fieldbook apoya decisiones, interpretacion y aprendizaje; no ejecuta acciones por el usuario.
- Practica sigue siendo directa. Las preguntas solo aparecen en Estudiar.
- Se prioriza metodologia reproducible, evidencia e informe sobre acumular payloads.
- Las tecnicas activas se presentan para laboratorios y alcances autorizados.

## Mapa de cobertura

| Dominio oficial PT1 | Cobertura actual | Refuerzo prioritario |
| --- | --- | --- |
| Reconnaissance & Enumeration | Fuerte: Nmap, DNS, subdominios, fingerprinting y servicios | Mantener actualizado y practicar interpretacion de outputs |
| Web Application Testing | Fuerte en OWASP, APIs, auth, sesiones, uploads e inyecciones | Burp y comparacion manual incorporados; falta ampliar controles client-side |
| Network Penetration Testing | Fuerte en SMB, RDP, FTP, SSH, SNMP, credenciales y pivoting | Trafico, poisoning, relay y segmentacion incorporados; falta captura pasiva mas profunda |
| Active Directory Exploitation | Fuerte en enumeracion, roasting, PTH, BloodHound y AD CS | Pass-the-Ticket, ACL y trusts incorporados; ampliar abuso de permisos/trusts con casos guiados |
| Exploitation & Post-Exploitation | Fuerte en CVE, shells, transferencia y privesc Linux/Windows | Revisar Metasploit, persistencia basica, limpieza y OPSEC dentro del alcance |
| Reporting & Time Management | Antes parcial | Guia PT1 de 48 horas e informe profesional incorporada como prioridad maxima |

## Contenido PT1 incorporado

- Concepto `burp-manual-testing`.
- Concepto `network-traffic-mitm`.
- Concepto `ad-tickets-trusts`.
- Concepto `pentest-reporting`.
- Guia `pt1-engagement` con cinco fases desde alcance hasta QA del informe.

## Siguiente orden editorial

1. Controles client-side y flujo completo de Burp con dos cuentas.
2. Captura e interpretacion de trafico con filtros reproducibles.
3. ACL y trusts de AD mediante casos de decision, no recetas aisladas.
4. Metasploit frente a explotacion manual y criterios para elegir.
5. Persistencia, limpieza y OPSEC limitadas al alcance del laboratorio.
6. Plantilla de informe PT1 y simulacro de gestion de las 48 horas.

## Criterio de preparacion

La cobertura teorica no implica estar listo para el examen. Cada dominio debe poder demostrarse en una room sin seguir una receta ciega, explicando:

- que evidencia inicio la hipotesis;
- por que se eligio la prueba;
- que resultado la confirmo o descarto;
- que impacto tuvo;
- como se corregiria;
- como se registraria en un informe profesional.
