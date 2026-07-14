---
titulo: Mapa de fuentes educativas
categoria: Meta
dificultad: Inicial
prerrequisitos:
  - auditoria_repositorio.md
fuentes_internas:
  - tools/concepts.py
  - tools/guides.py
  - tools/generate_structured_playbook.py
  - tools/generate_thm_playbook.py
  - tools/command_metadata.py
fuentes_externas: []
revision: 2026-07-14
estado: revisado
---

# Mapa de fuentes

## Convenciones

- **Completo**: hay concepto y soporte operativo suficiente para un módulo.
- **Parcial**: existe material útil, pero faltan fundamentos, variantes o casos.
- **Operativo**: hay comandos o tabla, no explicación autónoma.
- **Carencia**: no hay soporte interno suficiente; no se creará módulo temático sin investigación y trazabilidad explícitas.

`web/data/content.json` no se repite en cada fila porque es el artefacto generado común a todas las fuentes.

## Fundamentos y metodología

| Tema | Fuente en la aplicación | Tipo | Estado |
|---|---|---|---|
| Alcance y ROE | `concepts.py:rules-of-engagement-scope`; sección `mentalidad-y-preparacion` | Concepto y checklist | Completo |
| Metodología de room | `guides.py:metodologia`; `concepts.py:recon-metodologia` | Guía y concepto | Completo |
| Enumeración basada en evidencias | secciones `mapa-de-decisiones`, `recon-y-servicios`, `errores-tipicos` | Tablas y comandos | Completo |
| Hipótesis y atasco | secciones `checklist-de-atasco`, `errores-tipicos` | Decisiones y diagnóstico | Completo |
| Reporting | `guides.py:pt1-engagement`; `concepts.py:pentest-reporting`; `PLANTILLA_INFORME_PT1.md` | Guía, concepto y plantilla | Completo |
| HTTP, formularios, cookies y sesiones | `concepts.py:auth-session-security`, `burp-manual-testing`, `api-testing-model` | Conceptos parciales | Parcial |
| DNS y redes IP | `dns-enum`, `tcp-vs-udp`, `network-segmentation-firewalls` | Conceptos operativos | Parcial |
| Encoding y normalización | `filtros-incompletos`, LFI, SQLi y XSS | Explicación distribuida | Parcial |
| Shell, procesos, permisos y Bash | conceptos Linux, shells y privesc | Explicación distribuida | Parcial |
| Bases de datos y consultas | `database-enumeration`, `sqli` | Conceptos y comandos | Parcial |
| Source-transformación-sink | conceptos de inyección y autorización | Implícito | Parcial |

## Seguridad web

| Tema | Fuente en la aplicación | Tipo | Estado |
|---|---|---|---|
| Enumeración web | sección `web-discovery`; `enum-wildcard-responses`; `burp-manual-testing` | Comandos y conceptos | Completo |
| Vhosts y subdominios | sección `web-discovery`; `dns-enum` | Comandos | Operativo |
| Backups y código expuesto | sección `web-discovery`; `secrets-and-loot` | Tabla y comandos | Parcial |
| Autenticación, cookies y sesiones | `auth-session-security`; `fuerza-bruta-online` | Conceptos | Parcial |
| MFA/OTP bypass | `mfa-otp-bypass` | Concepto y prueba | Completo |
| Parameter tampering | `client-side-controls`; `mfa-otp-bypass` | Conceptos | Parcial |
| IDOR/BOLA y access control | `idor-bola`; sección `web-apis-y-autorizacion` | Concepto y comandos | Completo |
| SQL injection | `sqli`; sección `sqli`; metadatos asociados | Concepto extenso y payloads | Completo |
| Path traversal y LFI | `lfi`; sección `web-ficheros-y-ejecucion` | Concepto y comandos | Completo |
| LFI a RCE | `lfi-a-rce` | Concepto y prueba | Completo |
| RFI | Sin fuente dedicada | - | Carencia |
| File upload | `file-upload`; sección `web-ficheros-y-ejecucion` | Concepto y prueba | Completo |
| SSRF | `ssrf`; sección `web-inyecciones` | Concepto y pruebas | Completo |
| Command injection | `command-injection`; sección `web-inyecciones` | Concepto y prueba | Completo |
| Argument/option injection | `argument-injection`; sección `web-inyecciones` | Concepto y prueba | Parcial |
| XSS | `xss`; sección `web-inyecciones` | Concepto y prueba | Parcial |
| CSRF | Sin fuente dedicada | - | Carencia |
| SSTI | `ssti`; sección `web-inyecciones` | Concepto y pruebas | Completo |
| XXE | `xxe`; sección `web-inyecciones` | Concepto y pruebas | Completo |
| Deserialización insegura | Sin fuente dedicada | - | Carencia |
| Request smuggling/desync | Sin fuente dedicada | - | Carencia |
| WebSocket smuggling | Sin fuente dedicada | - | Carencia |
| JWT | `jwt-security`; sección `web-apis-y-autorizacion` | Concepto y pruebas | Completo |
| Race conditions | Sin fuente dedicada | - | Carencia |
| Prototype pollution | Sin fuente dedicada | - | Carencia |
| NoSQL injection | Mención heredada sin concepto autónomo | Fragmentos históricos | Carencia |
| APIs y GraphQL | `api-testing-model`, `graphql-security`, guía `api-paso-a-paso` | Conceptos y guía | Completo |
| OAuth/OIDC/CORS | `oauth-oidc-cors` | Concepto y pruebas | Completo |
| WordPress | `wordpress`; sección `wordpress` | Concepto y comandos | Completo |

## Linux

| Tema | Fuente en la aplicación | Tipo | Estado |
|---|---|---|---|
| Enumeración local | `enum-privesc-linux`; guía `privesc-linux`; sección `linux-privesc` | Concepto, guía y comandos | Completo |
| Credenciales/configuraciones | `secrets-and-loot`; sección `loot-y-secretos` | Concepto y comandos | Completo |
| sudo/sudoers | `sudo-abuse`, `sudo-ld-preload` | Conceptos y comandos | Completo |
| SUID/SGID | `suid`; sección `linux-privesc` | Concepto y comandos | Completo |
| Capabilities | `capabilities` | Concepto y comandos | Completo |
| Cron | `cron-abuse` | Concepto y comandos | Completo |
| PATH hijacking | `path-hijacking` | Concepto y comandos | Completo |
| Wildcard injection | `wildcard-injection` | Concepto y comandos | Completo |
| Variables de entorno | `sudo-ld-preload`; `path-hijacking` | Casos concretos | Parcial |
| Librerías compartidas | `sudo-ld-preload`, `python-library-hijacking` | Conceptos | Parcial |
| Servicios y procesos | sección `linux-privesc`; `enum-privesc-linux` | Comandos | Parcial |
| NFS | `nfs-enum`, `nfs-no-root-squash` | Conceptos y comandos | Completo |
| Docker/contenedores | `docker-container-escape`, `group-abuse-linux` | Conceptos y comandos | Completo |
| Kernel exploits | `kernel-exploits-linux` | Concepto y metodología | Completo |
| Systemd | Solo comprobaciones generales, sin concepto | Comandos dispersos | Carencia |
| Scripts/binarios modificables | `writable-sensitive-files`; sección `linux-privesc` | Concepto y comandos | Parcial |
| GTFOBins | `sudo-abuse`, `suid`; sección `linux-privesc` | Referencia operativa | Parcial |

## Windows

| Tema | Fuente en la aplicación | Tipo | Estado |
|---|---|---|---|
| Enumeración local | `enum-privesc-windows`; guía `privesc-windows` | Concepto y guía | Completo |
| Servicios y permisos débiles | `service-misconfig-windows` | Concepto y comandos | Completo |
| Scheduled Tasks | sección `windows-privesc` | Comandos y tabla | Parcial |
| Unquoted service paths | `service-misconfig-windows` | Caso de servicio | Completo |
| AlwaysInstallElevated | `always-install-elevated` | Concepto y comandos | Completo |
| Credenciales | `stored-credentials-windows` | Concepto y comandos | Completo |
| Registry/autoruns | `registry-autoruns` | Concepto y comandos | Completo |
| Tokens y privilegios | `token-impersonation`, `sebackup-serestore` | Conceptos | Completo |
| DLL hijacking | `dll-hijacking` | Concepto y comandos | Completo |
| PowerShell, WinRM y SMB | secciones `windows-privesc`, `credenciales-y-acceso`, `recon-y-servicios` | Comandos | Parcial |
| Impersonation | `token-impersonation` | Concepto y prueba | Completo |
| UAC | `uac-bypass` | Concepto y prueba | Completo |
| Kernel exploits | `kernel-exploits-windows` | Concepto y metodología | Completo |

## Active Directory, redes y acceso

| Tema | Fuente en la aplicación | Tipo | Estado |
|---|---|---|---|
| Fundamentos de dominio | `ad-modelo`; guía `active-directory` | Concepto y guía | Completo |
| LDAP | `ldap-enum` | Concepto y comandos | Completo |
| Kerberos | `kerberos`; `asrep-kerberoast` | Conceptos | Completo |
| NTLM/SMB | `ntlm-pth`, `smb-enum` | Conceptos y comandos | Completo |
| BloodHound | `bloodhound` | Concepto y comando | Completo |
| Password spraying | sección `active-directory`; `fuerza-bruta-online` | Comandos y precauciones | Parcial |
| AS-REP/Kerberoasting | `asrep-kerberoast` | Concepto y comandos | Completo |
| Pass-the-Hash | `ntlm-pth` | Concepto y comandos | Completo |
| Pass-the-Ticket | `ad-tickets-trusts` | Concepto y comandos | Completo |
| Delegaciones | guía `active-directory`; sección `active-directory` | Tabla y comandos | Parcial |
| ACL, grupos y trusts | `bloodhound`, `ad-tickets-trusts` | Conceptos | Parcial |
| Movimiento lateral | `mssql-lateral`, `ntlm-pth`, credenciales | Conceptos y comandos | Parcial |
| AD CS | `ad-cs` | Concepto y comandos | Completo |
| DCSync | Menciones en rutas AD, sin concepto dedicado | Operativo | Parcial |
| Golden/Silver Tickets | Sin concepto dedicado | - | Carencia |
| Pivoting y túneles | `pivoting-tunel`; guía y sección `pivoting` | Concepto, guía y comandos | Completo |
| Diagnóstico de pivoting | `pivot-troubleshooting` | Concepto y comandos | Completo |
| Captura/relay | `packet-analysis`, `network-traffic-mitm` | Conceptos y comandos | Completo |
| Reverse/bind shells | `reverse-vs-bind`; `revshells.json` | Concepto y plantillas | Completo |
| Estabilización | `tty-stabilization`, `shell-troubleshooting`; `revshells.json` | Conceptos y pasos | Completo |

## Regla de desarrollo

Se crearán primero módulos marcados **Completo** o **Parcial**. Las carencias quedarán visibles en el programa y solo se desarrollarán si pueden apoyarse en fuentes externas primarias y se distinguen claramente de la cobertura original.

