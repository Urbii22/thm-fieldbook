# Step-by-step learning guides for the "Aprender" mode of the web app.
# Prose-first: each step explains the idea (why), what to look for, and how to
# decide the next move. Commands are the same ones the practice mode adapts.
# Exported into web/data/content.json under "guides" by export_web_content.py.

GUIDES = [
    {
        "id": "metodologia",
        "title": "Como enfrentar una room",
        "phase": "recon",
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
]
