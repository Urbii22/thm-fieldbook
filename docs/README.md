---
titulo: Curso de pentesting práctico
categoria: Índice
dificultad: Progresiva
prerrequisitos: []
fuentes_internas:
  - 00_programa_del_curso.md
fuentes_externas: []
revision: 2026-07-14
estado: borrador
---

# Curso de pentesting práctico

Material teórico y práctico derivado de THM Fieldbook. Úsalo únicamente en sistemas propios o expresamente autorizados. La aplicación sigue siendo el playbook rápido; estos documentos explican mecanismos, razonamiento y adaptación.

## Orden recomendado

1. [Programa](00_programa_del_curso.md)
2. [Fundamentos HTTP](01_fundamentos/http_y_sesiones.md)
3. [Redes, DNS y URL](01_fundamentos/redes_dns_y_urls.md)
4. [Encoding y parsers](01_fundamentos/encoding_normalizacion_y_parsers.md)
5. [Linux y shell](01_fundamentos/linux_procesos_permisos_y_shell.md)
6. [Bases de datos y flujo de datos](01_fundamentos/bases_de_datos_y_flujo_de_datos.md)
7. [Metodología general](02_metodologia/metodologia_de_laboratorio.md)
8. [Construcción de payloads](02_metodologia/construccion_y_adaptacion_de_payloads.md)

Los bloques de técnicas, ejercicios, exámenes, soluciones y chuletas se incorporan por lotes. El estado verificable está en [progreso](_meta/progreso.md) y la cobertura real en [mapa de fuentes](_meta/mapa_fuentes.md).

## Navegación

| Bloque | Finalidad |
|---|---|
| `01_fundamentos` | Entender protocolos, intérpretes, datos y permisos |
| `02_metodologia` | Investigar con evidencia y construir pruebas mínimas |
| `03_seguridad_web` | Vulnerabilidades web cubiertas por Fieldbook |
| `04_linux` | Enumeración y escalada local |
| `05_windows` | Enumeración y escalada local |
| `06_active_directory` | Identidades, relaciones y rutas de dominio |
| `07_redes_y_pivoting` | Rutas, túneles, relay y diagnóstico |
| `08_ejercicios` | Problemas sin soluciones visibles |
| `09_examenes` | Evaluaciones y rúbricas |
| `10_solucionarios` | Respuestas razonadas |
| `11_chuletas` | Consulta operativa concisa |

## Índice completo

### 01_fundamentos

- [Bases de datos y flujo de datos](01_fundamentos/bases_de_datos_y_flujo_de_datos.md)
- [Encoding, normalización y parsers](01_fundamentos/encoding_normalizacion_y_parsers.md)
- [HTTP, formularios, cookies y sesiones](01_fundamentos/http_y_sesiones.md)
- [Linux, procesos, permisos y shell](01_fundamentos/linux_procesos_permisos_y_shell.md)
- [Redes, DNS, puertos y URLs](01_fundamentos/redes_dns_y_urls.md)

### 02_metodologia

- [Construcción y adaptación de payloads](02_metodologia/construccion_y_adaptacion_de_payloads.md)
- [Metodología de laboratorio y room](02_metodologia/metodologia_de_laboratorio.md)

### 03_seguridad_web

- [Modelo de pruebas de API](03_seguridad_web/api_testing_model.md)
- [Inyeccion de argumentos (no es command injection)](03_seguridad_web/argument_injection.md)
- [Autenticacion y sesiones en APIs](03_seguridad_web/auth_session_security.md)
- [Controles client-side y validacion del servidor](03_seguridad_web/client_side_controls.md)
- [Command Injection (inyeccion de comandos de SO)](03_seguridad_web/command_injection.md)
- [Enumeracion web con respuestas comodin (wildcard)](03_seguridad_web/enum_wildcard_responses.md)
- [Subida de ficheros a shell](03_seguridad_web/file_upload.md)
- [Seguridad de GraphQL](03_seguridad_web/graphql_security.md)
- [IDOR / Broken Object Level Authorization (BOLA)](03_seguridad_web/idor_bola.md)
- [Seguridad de JWT](03_seguridad_web/jwt_security.md)
- [Local File Inclusion (LFI)](03_seguridad_web/lfi.md)
- [De LFI a ejecucion (RCE)](03_seguridad_web/lfi_a_rce.md)
- [Bypass de OTP/MFA por manipulacion de parametros](03_seguridad_web/mfa_otp_bypass.md)
- [OAuth, OIDC y CORS](03_seguridad_web/oauth_oidc_cors.md)
- [Inyeccion SQL (SQLi)](03_seguridad_web/sqli.md)
- [Server-Side Request Forgery (SSRF)](03_seguridad_web/ssrf.md)
- [Server-Side Template Injection (SSTI)](03_seguridad_web/ssti.md)
- [Atacar WordPress](03_seguridad_web/wordpress.md)
- [Cross-Site Scripting (XSS)](03_seguridad_web/xss.md)
- [XML External Entity (XXE)](03_seguridad_web/xxe.md)

### 04_linux

- [Linux capabilities](04_linux/capabilities.md)
- [Tareas cron escribibles](04_linux/cron_abuse.md)
- [Docker y escapes de contenedor](04_linux/docker_container_escape.md)
- [Enumeracion para privesc en Linux](04_linux/enum_privesc_linux.md)
- [Grupos peligrosos (docker, lxd, disk)](04_linux/group_abuse_linux.md)
- [Exploits de kernel (ultimo recurso)](04_linux/kernel_exploits_linux.md)
- [NFS con no_root_squash](04_linux/nfs_no_root_squash.md)
- [Secuestro de PATH](04_linux/path_hijacking.md)
- [Python library hijacking](04_linux/python_library_hijacking.md)
- [Abuso de sudo](04_linux/sudo_abuse.md)
- [Sudo con env_keep (LD_PRELOAD)](04_linux/sudo_ld_preload.md)
- [Binarios SUID](04_linux/suid.md)
- [Inyeccion por comodin (wildcard)](04_linux/wildcard_injection.md)
- [Ficheros sensibles escribibles](04_linux/writable_sensitive_files.md)

### 05_windows

- [AlwaysInstallElevated](05_windows/always_install_elevated.md)
- [Secuestro de DLL](05_windows/dll_hijacking.md)
- [Enumeracion para privesc en Windows](05_windows/enum_privesc_windows.md)
- [Exploits de kernel en Windows (ultimo recurso)](05_windows/kernel_exploits_windows.md)
- [Autoruns y binarios de arranque](05_windows/registry_autoruns.md)
- [Privilegios SeBackup / SeRestore](05_windows/sebackup_serestore.md)
- [Servicios mal configurados](05_windows/service_misconfig_windows.md)
- [Credenciales guardadas en Windows](05_windows/stored_credentials_windows.md)
- [Impersonation de token (familia Potato)](05_windows/token_impersonation.md)
- [Bypass de UAC](05_windows/uac_bypass.md)

### 06_active_directory

- [AD CS y certificados abusables](06_active_directory/ad_cs.md)
- [Como se ataca Active Directory](06_active_directory/ad_modelo.md)
- [Pass-the-Ticket, ACL y trusts en Active Directory](06_active_directory/ad_tickets_trusts.md)
- [AS-REP roasting y Kerberoasting](06_active_directory/asrep_kerberoast.md)
- [BloodHound: el grafo de permisos](06_active_directory/bloodhound.md)
- [Kerberos en dos minutos](06_active_directory/kerberos.md)
- [Enumeracion de LDAP](06_active_directory/ldap_enum.md)
- [Hashes NTLM y Pass-the-Hash](06_active_directory/ntlm_pth.md)

### 07_redes_y_pivoting

- [Enumeracion de DNS](07_redes_y_pivoting/dns_enum.md)
- [Fingerprinting antes que el nombre del puerto](07_redes_y_pivoting/fingerprinting_servicios.md)
- [Enumeracion de FTP](07_redes_y_pivoting/ftp_enum.md)
- [Segmentacion, rutas y firewalls](07_redes_y_pivoting/network_segmentation_firewalls.md)
- [Trafico de red, poisoning y relay](07_redes_y_pivoting/network_traffic_mitm.md)
- [Enumeracion de NFS](07_redes_y_pivoting/nfs_enum.md)
- [Captura y analisis de paquetes](07_redes_y_pivoting/packet_analysis.md)
- [Diagnóstico de pivoting](07_redes_y_pivoting/pivot_troubleshooting.md)
- [Pivoting: tuneles a la red interna](07_redes_y_pivoting/pivoting_tunel.md)
- [Metodologia de reconocimiento](07_redes_y_pivoting/recon_metodologia.md)
- [Enumeracion de SMB](07_redes_y_pivoting/smb_enum.md)
- [Enumeracion de SMTP](07_redes_y_pivoting/smtp_enum.md)
- [Enumeracion de SNMP](07_redes_y_pivoting/snmp_enum.md)
- [TCP frente a UDP](07_redes_y_pivoting/tcp_vs_udp.md)

### 08_ejercicios

- [Cuaderno de ejercicios](08_ejercicios/cuaderno_de_ejercicios.md)

### 09_examenes

- [Examen de Active Directory](09_examenes/examen_active_directory.md)
- [Examen final integrador](09_examenes/examen_final_integrador.md)
- [Examen de fundamentos](09_examenes/examen_fundamentos.md)
- [Examen de Linux](09_examenes/examen_linux.md)
- [Examen de seguridad web](09_examenes/examen_seguridad_web.md)
- [Examen de Windows](09_examenes/examen_windows.md)

### 10_solucionarios

- [Soluciones razonadas del cuaderno](10_solucionarios/soluciones_cuaderno.md)

### 11_chuletas

- [Active Directory](11_chuletas/active_directory.md)
- [Command Y Argument Injection](11_chuletas/command_y_argument_injection.md)
- [Enumeracion Inicial](11_chuletas/enumeracion_inicial.md)
- [Escalada Linux](11_chuletas/escalada_linux.md)
- [Estabilizacion De Shells](11_chuletas/estabilizacion_de_shells.md)
- [File Upload](11_chuletas/file_upload.md)
- [Http Y Burp](11_chuletas/http_y_burp.md)
- [Interpretacion De Puertos](11_chuletas/interpretacion_de_puertos.md)
- [Lfi Y Path Traversal](11_chuletas/lfi_y_path_traversal.md)
- [Redes Y Pivoting](11_chuletas/redes_y_pivoting.md)
- [Reverse Shells](11_chuletas/reverse_shells.md)
- [Sql Injection](11_chuletas/sql_injection.md)
- [Ssrf](11_chuletas/ssrf.md)
- [Windows](11_chuletas/windows.md)

### Trazabilidad y compilación

- [Matriz de trazabilidad](_meta/matriz_de_trazabilidad.md)
- [Compilar PDF](BUILD.md)
- [Informe de progreso](_meta/progreso.md)
