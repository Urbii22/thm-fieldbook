# Concept wiki for the "Aprender" mode of the web app.
#
# A "concepto" is an atomic, prose-first explanation of ONE idea: que es,
# por que ocurre, cuando aplica, que senales lo delatan y los pasos para
# aprovecharlo. Concepts are interlinked with [[otro-id]] inside the prose,
# and each links out to its practice section (slug) via "section" so el
# lector salta a los comandos concretos con "ver comandos".
#
# A "ruta" (learning path) is an ordered list of concept ids: el orden en que
# conviene leerlos para dominar un area.
#
# Exported into web/data/content.json under "concepts" and "paths" by
# export_web_content.py. Prose sin acentos, igual que guides.py.

CONCEPTS = [
    {
        "id": "lfi",
        "title": "Local File Inclusion (LFI)",
        "phase": "enumeration",
        "section": "web-y-apis",
        "summary": "La web incluye un fichero cuyo nombre controlas tu; si no lo valida, lees ficheros del servidor.",
        "que": "Una LFI ocurre cuando una pagina construye la ruta de un fichero a incluir usando un valor que viene del usuario (tipicamente un parametro como ?page=), sin comprobar que ese valor sea uno de los permitidos. El servidor entonces lee y a veces ejecuta el fichero que tu le pidas, no el que el programador esperaba.",
        "porque": "El codigo hace algo como include($_GET['page'].'.php'). El programador asume que page siempre sera 'home' o 'about', pero nada lo obliga. Si metes ../../../../etc/passwd, la funcion de inclusion resuelve esa ruta relativa y sirve el fichero. La causa raiz es confiar en la entrada del usuario para decidir que fichero abrir.",
        "cuando": "Sospecha LFI en cualquier parametro que parezca nombrar una vista, una plantilla, un idioma o un documento: page, file, view, template, lang, doc, include. Sobre todo si el valor aparece reflejado en la URL y el contenido de la pagina cambia segun ese valor.",
        "senales": [
            "Un parametro cuyo valor parece un nombre de fichero o de pagina (?page=home, ?file=report).",
            "La respuesta cambia de forma coherente al pedir rutas: ../ te acerca a la raiz, un fichero inexistente da un error de include con la ruta.",
            "Mensajes de error de PHP que filtran rutas absolutas del servidor (failed to open stream).",
            "Puedes leer /etc/passwd (Linux) o C:\\Windows\\win.ini (Windows) via el parametro.",
        ],
        "pasos": [
            "Confirma la lectura con un fichero que siempre existe: pide /etc/passwd con suficientes ../ para llegar a la raiz.",
            "Si el codigo anade una extension (.php), usa un PHP wrapper para leer el fuente en base64 sin que se ejecute, o busca truncar la extension.",
            "Mapea que mas puedes leer: config con credenciales, claves SSH, logs. Cada fichero legible es una pista para la siguiente fase.",
            "Si controlas el contenido de algun fichero que el servidor luego incluye (un log, una sesion, un upload), la LFI se convierte en ejecucion: mira [[lfi-a-rce]].",
        ],
        "commands": [
            {
                "cmd": "curl -s '$URL/?page=../../../../etc/passwd'",
                "why": "Prueba de lectura con un fichero que siempre existe. Los ../ de sobra suben hasta la raiz aunque no sepas la profundidad real del script.",
                "out": "Lineas root:x:0:0. Si aparecen, hay LFI confirmada. Un error de include con una ruta absoluta tambien es util: te dice donde estas en el disco.",
            },
            {
                "cmd": "curl -s '$URL/?page=php://filter/convert.base64-encode/resource=config'",
                "why": "Si el codigo anade .php y ejecuta el fichero, el wrapper php://filter te deja leer el FUENTE en base64 sin que se ejecute. Asi lees configs con credenciales.",
                "out": "Un blob en base64: decodificalo (base64 -d) para ver el codigo PHP. Busca ahi credenciales de BD, claves de API y rutas a otros ficheros jugosos.",
            },
        ],
    },
    {
        "id": "lfi-a-rce",
        "title": "De LFI a ejecucion (RCE)",
        "phase": "access",
        "section": "web-y-apis",
        "summary": "Leer ficheros no es el final: si logras que el servidor incluya contenido que tu controlas, ejecutas codigo.",
        "que": "Es el salto de 'puedo leer' a 'puedo ejecutar'. Una [[lfi]] por si sola solo lee, pero si consigues que el fichero incluido contenga codigo PHP que tu has metido antes, ese codigo se ejecuta con los permisos del servidor web y obtienes ejecucion remota de comandos.",
        "porque": "include no solo lee: interpreta PHP. Si logras escribir <?php system($_GET['c']); ?> en algun sitio del servidor y luego apuntas la LFI a ese sitio, el include ejecuta tu payload. Los sitios clasicos donde puedes 'inyectar' ese contenido son ficheros que el servidor escribe con datos tuyos: logs de acceso, ficheros de sesion, cabeceras guardadas o subidas de fichero mal filtradas.",
        "cuando": "Cuando ya confirmaste lectura con LFI y ademas existe algun fichero cuyo contenido puedas influir: el User-Agent acaba en un access.log legible, hay ficheros de sesion en /var/lib/php, o hay un formulario de subida. Sin un punto de inyeccion controlable, la LFI se queda en lectura.",
        "senales": [
            "Puedes leer un log (access.log, auth.log) via la LFI: el log refleja datos que tu envias, como el User-Agent.",
            "Existe una subida de ficheros que no valida bien la extension o el contenido.",
            "Puedes fijar el valor de una cookie de sesion y localizar su fichero en disco.",
        ],
        "pasos": [
            "Elige el vector de inyeccion: log poisoning (mandas PHP en el User-Agent y lo ejecutas incluyendo el log), sesion, o subida.",
            "Inyecta un payload minimo que ejecute un comando parametrizado, y confirma con id o whoami que se ejecuta.",
            "Convierte la ejecucion de un comando en una shell interactiva: lanza una reverse shell ([[reverse-vs-bind]]) y estabilizala ([[tty-stabilization]]).",
            "Con shell ya dentro, cambia de fase: orientate y busca escalada ([[privesc-modelo]]). Los comandos concretos estan en la seccion de practica (ver comandos).",
        ],
        "commands": [
            {
                "cmd": "curl -s '$URL/?page=../../../../var/log/apache2/access.log&c=id'",
                "why": "Log poisoning: antes mandas PHP en tu User-Agent (queda escrito en el access.log) y ahora incluyes ese log via la LFI. El servidor interpreta tu PHP y ejecuta el comando de ?c=.",
                "out": "La salida de id incrustada entre las lineas del log confirma ejecucion. Fijate en el usuario (www-data): es con quien tendras la shell al escalar a reverse shell.",
            },
        ],
    },
    {
        "id": "sqli",
        "title": "Inyeccion SQL (SQLi)",
        "phase": "enumeration",
        "section": "sqli",
        "summary": "Tu entrada acaba dentro de una consulta SQL sin separar datos de codigo; puedes reescribir la consulta.",
        "que": "Una SQLi ocurre cuando la aplicacion construye una consulta SQL concatenando texto que viene del usuario. Como el motor no distingue tu 'dato' del 'codigo' de la consulta, puedes cerrar la cadena original e inyectar tu propia logica: saltarte un login, volcar tablas o, segun el motor, ejecutar comandos.",
        "porque": "El codigo hace query = \"SELECT * FROM users WHERE name='\" + input + \"'\". Si tu input es ' OR '1'='1, la consulta final siempre es verdadera. La causa raiz es la misma que en [[lfi]]: mezclar datos no confiables con la instruccion, en vez de usar consultas parametrizadas que separan ambos.",
        "cuando": "En cualquier campo que alimente una busqueda, un login, un filtro o un id: formularios, parametros de URL, cabeceras. Sospecha si al meter una comilla la aplicacion se rompe o cambia de comportamiento.",
        "senales": [
            "Una comilla simple ' provoca un error de SQL o una pagina en blanco/500.",
            "Payloads logicos cambian el resultado: ' OR '1'='1 devuelve mas filas o entra sin password.",
            "La respuesta tarda distinto con un payload de tiempo (blind basada en tiempo).",
            "Diferencias sutiles entre una condicion verdadera y una falsa (blind booleana).",
        ],
        "pasos": [
            "Detecta el punto: mete una comilla y observa el error o el cambio. Deduce si es numerica o entre comillas.",
            "Averigua el numero de columnas (ORDER BY / UNION SELECT) para poder extraer datos por UNION.",
            "Extrae metadatos primero (version, bases de datos, tablas, columnas) y luego los datos que te interesan (usuarios, hashes).",
            "Si es a ciegas, automatiza con una herramienta; los hashes que saques van a la fase de credenciales para crackear y reutilizar.",
        ],
        "commands": [
            {
                "cmd": "sqlmap -u '$URL/item?id=1' --batch --dbs",
                "why": "Cuando ya sospechas SQLi (una comilla rompio la pagina), sqlmap automatiza la deteccion y explotacion. --batch acepta los defaults; --dbs lista las bases de datos como primera prueba de que funciona.",
                "out": "El tipo de inyeccion detectada (boolean, time-based, UNION) y la lista de bases de datos. Con eso, sigue con --tables y -D <db> --dump para extraer usuarios y hashes.",
            },
        ],
    },
    {
        "id": "reverse-vs-bind",
        "title": "Reverse shell vs bind shell",
        "phase": "access",
        "section": "acceso-inicial",
        "summary": "Dos formas de conseguir una shell remota; la direccion de la conexion decide cual funciona detras de un firewall.",
        "que": "Una bind shell abre un puerto EN LA VICTIMA y tu te conectas a el. Una reverse shell hace lo contrario: la victima se conecta HACIA TI, a un listener que tienes abierto. En ambos casos acabas con una shell del objetivo, pero la direccion de la conexion cambia cual es viable.",
        "porque": "Los firewalls casi siempre bloquean conexiones entrantes a la victima pero permiten las salientes. Por eso la reverse shell (victima -> atacante) funciona donde la bind shell (atacante -> victima) falla: la conexion de salida rara vez esta filtrada. Por defecto, piensa siempre en reverse.",
        "cuando": "Reverse: el caso normal, sobre todo si la victima esta tras NAT o firewall. Bind: solo cuando TU no puedes recibir conexiones (estas tras NAT sin port-forward) pero la victima si acepta entrantes. Tras conseguirla, casi siempre toca [[tty-stabilization]].",
        "senales": [
            "Tienes ejecucion de comandos (RCE, [[lfi-a-rce]], una inyeccion) pero aun no una shell interactiva.",
            "Tu listener no recibe nada: revisa que LHOST sea TU IP de atacante (VPN, no la local) y que el puerto no este ocupado ni filtrado.",
            "La shell entra pero es 'tonta': sin Ctrl+C, sin flechas, sin autocompletado -> necesita estabilizarse.",
        ],
        "pasos": [
            "Abre SIEMPRE el listener antes de disparar el payload; si no, la conexion llega a la nada y la pierdes.",
            "Genera el payload con TU IP de atacante como LHOST y un puerto que estes escuchando (usa el generador de la app).",
            "Dispara el payload por tu vector de ejecucion y espera el 'connect received' en el listener.",
            "Nada mas entrar, estabiliza la shell: mira [[tty-stabilization]].",
        ],
        "commands": [
            {
                "cmd": "nc -lvnp 4444",
                "why": "Pone tu maquina a escuchar para recibir una reverse shell. -l escucha, -v verboso, -n sin DNS, -p el puerto. Debe estar abierto ANTES de lanzar el payload.",
                "out": "'listening on [any] 4444' y luego 'connect to ... from ...' cuando entre. Si no entra nada, el LHOST/puerto del payload no coincide o hay un firewall de salida.",
            },
        ],
    },
    {
        "id": "tty-stabilization",
        "title": "Estabilizar la shell (TTY)",
        "phase": "access",
        "section": "acceso-inicial",
        "summary": "Convertir una shell tonta en una TTY completa: sin esto, Ctrl+C te mata la sesion y muchos comandos fallan.",
        "que": "Una reverse shell recien llegada no es una terminal de verdad: no tiene TTY. Eso significa sin autocompletado, sin historial, sin flechas, y Ctrl+C mata TODA la shell en vez de el comando actual. Estabilizar es darle una pseudo-TTY para trabajar como en una terminal normal.",
        "porque": "Programas como su, ssh, sudo, passwd o los editores exigen un TTY y fallan ('must be run from a terminal') en una shell tonta. Ademas, sin estabilizar, un Ctrl+C accidental te deja fuera y hay que repetir todo el acceso. Estabilizar temprano ahorra sustos.",
        "cuando": "Justo despues de recibir una [[reverse-vs-bind]] shell en Linux, antes de ponerte a enumerar privesc. En Windows el concepto no aplica igual (se suele saltar a evil-winrm o a una shell de Meterpreter).",
        "senales": [
            "El prompt no muestra usuario@host, o es un simple $ sin mas.",
            "Las flechas imprimen ^[[A en vez de moverse por el historial.",
            "su o sudo responden 'must be run from a terminal'.",
        ],
        "pasos": [
            "Lanza una pseudo-TTY con python3/pty (o script /dev/null si no hay python).",
            "Exporta un TERM valido (export TERM=xterm) para que funcionen editores y clear.",
            "Pon la shell en background (Ctrl+Z), ajusta tu terminal con stty raw -echo y vuelve con fg.",
            "Ya con TTY estable, arranca la enumeracion (whoami/id, sudo -l) sin miedo a Ctrl+C.",
        ],
        "commands": [
            {
                "cmd": "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
                "why": "Crea la pseudo-TTY con la que ya funcionan su/sudo/passwd. Es el primer paso y el mas portable si la victima tiene python3.",
                "out": "El prompt suele cambiar a usuario@host. Si no hay python3, prueba python o 'script -qc /bin/bash /dev/null'.",
            },
            {
                "cmd": "stty raw -echo; fg",
                "why": "Se ejecuta EN TU KALI tras poner la shell en background (Ctrl+Z). Pasa tu terminal a modo raw para tener Ctrl+C, flechas y autocompletado dentro de la shell remota.",
                "out": "Al volver (fg) la shell ya se comporta como una terminal normal. Si ves letras dobladas o rota, ajusta filas/columnas con stty rows/cols.",
            },
        ],
    },
    {
        "id": "privesc-modelo",
        "title": "El modelo de la escalada de privilegios",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "Toda privesc es lo mismo: algo mas privilegiado ejecuta, lee o confia en algo que tu puedes controlar.",
        "que": "Escalar privilegios es encontrar un punto donde un proceso o usuario mas poderoso (normalmente root) depende de algo que tu puedes modificar o influir: un binario, un script, una ruta, un fichero de config, una variable de entorno. No es magia ni un exploit unico: es esa relacion de confianza rota.",
        "porque": "Los sistemas ejecutan tareas privilegiadas continuamente (cron, servicios, binarios SUID). Si cualquiera de esas tareas toca algo escribible o controlable por tu usuario, heredas su privilegio. La causa raiz siempre es una frontera de confianza mal puesta.",
        "cuando": "Siempre que tengas una shell de usuario normal y quieras root. Antes de explotar toca enumerar de forma sistematica: [[suid]], [[sudo-abuse]] y [[cron-abuse]] son los tres vectores mas comunes; empieza por los rapidos.",
        "senales": [
            "Perteneces a un grupo potente (docker, lxd, disk, adm): a menudo es root casi directo.",
            "Existe un binario, script o tarea que corre como root y que tu puedes leer o escribir.",
            "Hay credenciales reutilizables en disco que pertenecen a otro usuario.",
        ],
        "pasos": [
            "Orientate: whoami/id/groups. Un grupo peligroso puede acortar todo el camino.",
            "Enumera en orden por rentabilidad: primero sudo ([[sudo-abuse]]) y SUID ([[suid]]), luego cron ([[cron-abuse]]) y configs.",
            "Para cada binario o vector que salga, busca la receta exacta (GTFOBins) antes de improvisar.",
            "Explota, confirma con id que eres uid=0, y documenta el root cause para el writeup.",
        ],
        "commands": [
            {
                "cmd": "id; groups",
                "why": "El punto de partida. Los grupos deciden atajos: docker/lxd permiten escapar a root montando el disco del host; sin grupos jugosos, toca la enumeracion sistematica.",
                "out": "Tu uid/gid y grupos. docker/lxd -> escape casi directo. adm -> lectura de logs. disk -> lectura cruda del disco (incluido /etc/shadow).",
            },
        ],
    },
    {
        "id": "suid",
        "title": "Binarios SUID",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "Un binario SUID se ejecuta con los privilegios de su dueno (a menudo root), no con los tuyos.",
        "que": "El bit SUID hace que un ejecutable corra siempre como su propietario, sin importar quien lo lance. Si el dueno es root y el binario permite ejecutar comandos, leer/escribir ficheros o lanzar otra shell, puedes abusar de el para actuar como root. Es una aplicacion directa del [[privesc-modelo]].",
        "porque": "SUID existe para casos legitimos (passwd necesita tocar /etc/shadow). El problema es cuando un binario con SUID tiene una funcion que permite salir a una shell o leer ficheros arbitrarios: entonces esa capacidad se ejecuta como root. GTFOBins cataloga exactamente que binarios son abusables y como.",
        "cuando": "En la fase de privesc Linux, justo despues de mirar [[sudo-abuse]]. Busca binarios SUID que NO sean del sistema base o cuya version sea conocida por ser abusable.",
        "senales": [
            "find de SUID devuelve binarios raros (nmap, find, cp, python, vim, tar) fuera de los tipicos.",
            "Un binario a medida del reto con el bit SUID puesto.",
            "El binario aparece en GTFOBins con la etiqueta SUID.",
        ],
        "pasos": [
            "Lista los binarios SUID del sistema.",
            "Descarta los normales (passwd, sudo, mount, ping) y quedate con lo inusual.",
            "Busca cada candidato en GTFOBins filtrando por 'SUID': te da la linea exacta.",
            "Ejecuta el abuso y confirma con id que tienes euid=0.",
        ],
        "commands": [
            {
                "cmd": "find / -perm -4000 -type f 2>/dev/null",
                "why": "Lista todos los binarios con bit SUID. -perm -4000 filtra justo ese bit; 2>/dev/null oculta el ruido de permiso denegado.",
                "out": "Rutas de binarios SUID. Ignora los tipicos del sistema; cualquier cosa rara o a medida -> GTFOBins. Anota tambien la version si es un binario conocido.",
            },
        ],
    },
    {
        "id": "sudo-abuse",
        "title": "Abuso de sudo",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "sudo -l te dice que puedes ejecutar como root; muchos binarios permiten saltar de ahi a una shell root.",
        "que": "sudo permite a un usuario ejecutar comandos concretos como otro (normalmente root). Si tu usuario tiene permitido ejecutar un binario que ademas puede lanzar una shell, leer/escribir ficheros o ejecutar codigo, ese permiso puntual se convierte en root total. Otra cara del [[privesc-modelo]].",
        "porque": "El admin concede sudo sobre un binario pensando que solo hace su funcion, pero muchos binarios tienen funciones secundarias (un editor puede abrir una shell, less puede ejecutar comandos). GTFOBins lista para cada uno como escapar. Ademas fallos como env_keep o rutas relativas amplian el abuso.",
        "cuando": "Es lo PRIMERO que se mira en privesc Linux por su alta rentabilidad. En cuanto tengas una shell estable ([[tty-stabilization]]), lanza sudo -l.",
        "senales": [
            "sudo -l muestra entradas '(root) NOPASSWD: /ruta/bin' (ni siquiera piden password).",
            "El binario permitido aparece en GTFOBins bajo 'sudo'.",
            "Ves env_keep+=LD_PRELOAD o rutas relativas: vectores extra de abuso.",
        ],
        "pasos": [
            "Ejecuta sudo -l para ver que tienes permitido y si es sin password.",
            "Busca el binario permitido en GTFOBins, seccion 'sudo'.",
            "Aplica la linea de escape (suele forzar una shell o ejecutar un comando como root).",
            "Confirma con id; si eres root, recoge la flag y anota el vector.",
        ],
        "commands": [
            {
                "cmd": "sudo -l",
                "why": "Enumera exactamente que comandos puedes correr como otro usuario. Es el vector mas rapido y comun; muchas rooms se resuelven aqui sin buscar mas.",
                "out": "Entradas '(root) NOPASSWD: ...'. Cada binario permitido -> GTFOBins. Si pide password y no la tienes, este vector queda en pausa.",
            },
            {
                "cmd": "sudo /usr/bin/find . -exec /bin/sh \\; -quit",
                "why": "Ejemplo tipico de GTFOBins: si puedes sudo find, su flag -exec lanza una shell heredando el privilegio root de sudo.",
                "out": "Prompt # y id con uid=0. Cambia find por el binario concreto que te permita tu sudo -l; la idea (forzar una shell) es la misma.",
            },
        ],
    },
    {
        "id": "cron-abuse",
        "title": "Tareas cron escribibles",
        "phase": "privesc",
        "section": "linux-privesc",
        "summary": "Si root ejecuta periodicamente un script o binario que tu puedes modificar, tu codigo correra como root.",
        "que": "cron ejecuta tareas programadas, a menudo como root. Si una de esas tareas llama a un script, binario o ruta que tu usuario puede escribir (o si usa comodines o rutas relativas manipulables), puedes inyectar tu propio comando y esperar a que cron lo ejecute con privilegios. Es el [[privesc-modelo]] aplicado al tiempo.",
        "porque": "Los admins programan mantenimiento (backups, limpiezas) como root y a veces dejan el script en una ruta escribible por otros, o usan comodines (tar *) que un atacante puede secuestrar creando ficheros con nombres especiales. cron lo ejecuta tal cual, sin validar quien toco el script.",
        "cuando": "Cuando sudo ([[sudo-abuse]]) y SUID ([[suid]]) no dieron nada. cron es mas lento porque hay que esperar a que la tarea corra, pero es un vector muy comun en rooms.",
        "senales": [
            "Un script referenciado en cron es escribible por tu usuario o su grupo.",
            "La tarea usa una ruta relativa o un comodin (*) en un directorio donde puedes crear ficheros.",
            "Aparecen procesos que arrancan cada pocos minutos (pspy lo revela) corriendo como root.",
        ],
        "pasos": [
            "Lee las tareas programadas del sistema y de otros usuarios.",
            "Comprueba permisos de los scripts/binarios que invocan (ls -l): busca los escribibles.",
            "Inyecta tu payload (una reverse shell o el bit SUID a bash) en el punto controlable.",
            "Espera a que cron ejecute y recoge tu shell/binario root.",
        ],
        "commands": [
            {
                "cmd": "cat /etc/crontab; ls -la /etc/cron.*",
                "why": "Muestra las tareas programadas del sistema y con que frecuencia corren. Es el primer sitio donde mirar que ejecuta root de forma automatica.",
                "out": "Lineas con horario, usuario (root) y el comando/script. Anota los scripts que corren como root: el siguiente paso es ver si puedes escribirlos.",
            },
            {
                "cmd": "ls -l /ruta/al/script_de_cron.sh",
                "why": "Comprueba si el script que ejecuta root es escribible por ti. Ese permiso de escritura es justo la frontera de confianza rota que necesitas.",
                "out": "Los permisos y el dueno. Si tu usuario o un grupo tuyo tiene w, puedes inyectar comandos. Si no, busca comodines o rutas relativas manipulables.",
            },
        ],
    },
    {
        "id": "smb-enum",
        "title": "Enumeracion de SMB",
        "phase": "enumeration",
        "section": "recon-y-servicios",
        "summary": "El puerto 445 suele regalar shares legibles, nombres de usuario y el dominio; comprueba siempre el acceso anonimo primero.",
        "que": "SMB (445, y 139) es el protocolo de comparticion de ficheros de Windows. Enumerarlo consiste en listar sus shares (carpetas compartidas), ver a cuales puedes acceder sin o con credenciales, y sacar informacion del sistema y del dominio. Es una de las superficies mas rentables en rooms Windows/AD.",
        "porque": "Muchas configuraciones permiten sesion nula o de invitado, dejando shares legibles con backups, configs o credenciales. Y aunque no haya acceso anonimo, SMB filtra el nombre del equipo, el dominio y a veces la lista de usuarios, que alimentan el resto del ataque (spraying, [[kerberos]]).",
        "cuando": "Siempre que el recon muestre 445 abierto. Es de las primeras cosas a enumerar; en un DC ademas se combina con LDAP y Kerberos ([[ad-modelo]]).",
        "senales": [
            "nmap marca 445/tcp open microsoft-ds o el script smb saca el dominio.",
            "Un share con permiso READ que no sea IPC$ (a menudo backups, transfer, dev).",
            "Sesion nula/guest aceptada: puedes listar sin credenciales.",
        ],
        "pasos": [
            "Comprueba acceso anonimo listando shares con usuario vacio o guest.",
            "Entra a cada share legible y saquea configs, backups y ficheros de usuario.",
            "Si tienes credenciales, repite: suele abrir mas shares y, si eres admin local, ejecucion.",
            "Extrae usuarios (rid-brute) para alimentar spraying y roasting en AD.",
        ],
        "commands": [
            {
                "cmd": "nxc smb $IP -u '' -p '' --shares",
                "why": "Comprueba sesion nula y lista los shares de golpe. Es la prueba mas rentable en SMB: un share legible te ahorra toda la fase de explotacion.",
                "out": "Columna READ/WRITE por share. Un READ fuera de IPC$ es saqueo directo. El encabezado tambien confirma nombre de equipo y dominio.",
            },
            {
                "cmd": "nxc smb $IP -u 'guest' -p '' --rid-brute",
                "why": "Si hay acceso guest/nulo, itera los RID para sacar la lista de usuarios del dominio sin credenciales. Necesitas usuarios validos antes de rociar passwords.",
                "out": "Lineas SidTypeUser = usuarios reales. Extrae los nombres (sin las cuentas de maquina terminadas en $) a users.txt para spraying y roasting.",
            },
        ],
    },
    {
        "id": "ad-modelo",
        "title": "Como se ataca Active Directory",
        "phase": "access",
        "section": "active-directory",
        "summary": "En AD no explotas una maquina: transformas una identidad en mas permisos, en cadena, hasta Domain Admin.",
        "que": "Active Directory es el directorio que gestiona usuarios, equipos y permisos de una red Windows. Atacarlo no va de un exploit puntual, sino de conseguir una identidad (un usuario) y usar sus permisos para conseguir otra mas fuerte, repitiendo hasta llegar a Domain Admin o al hash de krbtgt.",
        "porque": "AD esta hecho de relaciones de confianza (grupos, delegaciones, ACLs, sesiones). Cada credencial abre nuevas relaciones que explotar. Por eso la mentalidad es distinta: importa mas el grafo de permisos ([[bloodhound]] lo mapea) que la version de un servicio.",
        "cuando": "En cuanto el recon confirme un DC (puertos 88 Kerberos + 389 LDAP + 445). El trabajo previo imprescindible es resolver nombres y hora, o Kerberos falla con errores confusos.",
        "senales": [
            "Puertos 88, 389, 445, 636, 3268 abiertos en el mismo host.",
            "nmap/enum filtra un nombre de dominio (algo.local) y el hostname del DC.",
            "Errores de 'clock skew' al usar herramientas: tu reloj no cuadra con el DC.",
        ],
        "pasos": [
            "Prepara nombres (/etc/hosts) y sincroniza la hora con el DC.",
            "Consigue el primer usuario: enum de SMB ([[smb-enum]]), rid-brute y password spraying controlado.",
            "Saca hashes crackeables por Kerberos ([[asrep-kerberoast]]) y mapea permisos con [[bloodhound]].",
            "Extrae hashes del objetivo y autentica con [[ntlm-pth]] hasta Domain Admin.",
        ],
        "commands": [
            {
                "cmd": "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,636,3268,5985 $IP",
                "why": "Escanea los puertos tipicos de un DC de una vez. La combinacion 88+389+445 confirma que estas ante un dominio y no una maquina suelta.",
                "out": "Puerto 88 abierto = DC. Los scripts LDAP/SMB filtran el nombre del dominio y del DC: anotalos para /etc/hosts antes de seguir.",
            },
        ],
    },
    {
        "id": "kerberos",
        "title": "Kerberos en dos minutos",
        "phase": "access",
        "section": "active-directory",
        "summary": "El sistema de tickets de AD; entender TGT y TGS explica por que existen AS-REP roast y Kerberoasting.",
        "que": "Kerberos es como AD autentica sin mandar la password por la red. Al iniciar sesion, el usuario obtiene un TGT (ticket para pedir tickets) del DC. Luego, para usar un servicio, cambia el TGT por un TGS (ticket de servicio). Todo gira en torno a tickets cifrados con claves derivadas de passwords.",
        "porque": "Porque esos tickets van cifrados con la clave del usuario o del servicio, y se pueden pedir en situaciones que permiten crackearlos offline: eso es lo que explotan [[asrep-kerberoast]]. Ademas, si robas o falsificas tickets, te haces pasar por otro sin su password.",
        "cuando": "Es teoria de apoyo para la fase AD ([[ad-modelo]]). No hace falta dominarla para atacar, pero entender TGT/TGS te dice por que funcionan los ataques de roasting y de tickets.",
        "senales": [
            "Puerto 88 abierto: hay Kerberos y por tanto un DC.",
            "Errores 'KRB_AP_ERR_SKEW' = tu reloj esta desincronizado con el DC.",
            "Hashes que empiezan por $krb5asrep$ o $krb5tgs$ al hacer roasting.",
        ],
        "pasos": [
            "Asegura nombres y hora: Kerberos es muy sensible al reloj (max ~5 min de desfase).",
            "Con o sin credencial, intenta roasting para sacar tickets crackeables ([[asrep-kerberoast]]).",
            "Crackea los tickets offline para obtener nuevas credenciales.",
            "Con credenciales de mas nivel, sigue el grafo de permisos hacia Domain Admin.",
        ],
        "commands": [
            {
                "cmd": "sudo ntpdate $DC_HOST",
                "why": "Sincroniza tu reloj con el DC. Kerberos rechaza tickets si el desfase supera unos minutos; este es el arreglo del clasico error de clock skew.",
                "out": "Imprime el ajuste de tiempo aplicado. Tras esto, las herramientas de Kerberos (impacket) dejan de fallar por skew. Alternativa: faketime.",
            },
        ],
    },
    {
        "id": "asrep-kerberoast",
        "title": "AS-REP roasting y Kerberoasting",
        "phase": "access",
        "section": "active-directory",
        "summary": "Dos formas de sacar hashes crackeables de Kerberos: sin credenciales (AS-REP) o con una cualquiera (Kerberoast).",
        "que": "Son dos ataques que piden tickets de [[kerberos]] y se quedan con la parte cifrada para crackearla offline. AS-REP roasting funciona contra usuarios con la preautenticacion desactivada y no necesita credenciales. Kerberoasting pide tickets de cuentas de servicio (con SPN) y requiere una credencial de dominio cualquiera.",
        "porque": "El ticket va cifrado con una clave derivada de la password del usuario o de la cuenta de servicio. Si esa password es debil, la crackeas offline sin tocar el DC (sin riesgo de bloqueo). Las cuentas de servicio suelen tener passwords viejas y privilegios altos: premio doble.",
        "cuando": "AS-REP: en cuanto tengas una lista de usuarios ([[smb-enum]]), aunque no tengas password. Kerberoast: en cuanto consigas UNA credencial valida. Ambos encajan en la fase AD ([[ad-modelo]]).",
        "senales": [
            "GetNPUsers devuelve hashes $krb5asrep$ (hay usuarios sin preauth).",
            "GetUserSPNs lista cuentas de servicio con SPN y devuelve $krb5tgs$.",
            "Los nombres de esas cuentas huelen a privilegio (svc_sql, backup, admin).",
        ],
        "pasos": [
            "AS-REP: pasa la lista de usuarios a GetNPUsers con -no-pass.",
            "Kerberoast: con una credencial, pide los tickets de SPN con GetUserSPNs -request.",
            "Crackea los hashes con hashcat (modo 18200 AS-REP, 13100 Kerberoast) y rockyou.",
            "Cada password crackeada -> nueva identidad: vuelve a enumerar el dominio con ella.",
        ],
        "commands": [
            {
                "cmd": "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP",
                "why": "AS-REP roasting sin credenciales: pide tickets para usuarios con preauth desactivada. Solo necesitas la lista de usuarios y la IP del DC.",
                "out": "Hashes $krb5asrep$ para los usuarios vulnerables. Cada uno es crackeable offline (hashcat -m 18200). Sin salida = nadie tiene preauth desactivada.",
            },
            {
                "cmd": "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request",
                "why": "Kerberoasting: con una credencial de dominio pides los tickets de las cuentas de servicio. Esas cuentas suelen tener passwords debiles y muchos permisos.",
                "out": "Hashes $krb5tgs$ junto al nombre del servicio. Prioriza los que parezcan admin; crackea con hashcat -m 13100.",
            },
        ],
    },
    {
        "id": "ntlm-pth",
        "title": "Hashes NTLM y Pass-the-Hash",
        "phase": "access",
        "section": "active-directory",
        "summary": "En Windows el hash NTLM basta para autenticarte: no siempre hace falta crackear la password.",
        "que": "Windows guarda las passwords como hashes NTLM. Para muchos protocolos de autenticacion, el hash ES la credencial: si lo tienes, puedes autenticarte SIN conocer la password en claro. Eso es Pass-the-Hash (PtH), y convierte un volcado de hashes directamente en acceso.",
        "porque": "El protocolo NTLM usa el hash como secreto compartido, no la password. Por eso volcar hashes (con secretsdump/DCSync tras conseguir privilegios) permite moverte por la red autenticandote con el hash. Solo necesitas crackear si el servicio exige la password en claro o quieres reutilizarla en sitios no-NTLM.",
        "cuando": "Cuando ya has volcado hashes (por admin local, DCSync o del SAM) en la fase AD ([[ad-modelo]]). Es la forma habitual de usar el hash de administrator o de una cuenta de servicio sin perder tiempo crackeando.",
        "senales": [
            "secretsdump te da lineas usuario:rid:lmhash:nthash.",
            "nxc marca (Pwn3d!) al probar el hash: tienes ejecucion.",
            "Tienes el NT hash de administrator o krbtgt.",
        ],
        "pasos": [
            "Vuelca los hashes del objetivo (secretsdump con una cuenta con privilegios).",
            "Prueba el NT hash contra SMB/WinRM con -H en vez de -p.",
            "Si (Pwn3d!), entra con evil-winrm -H para una shell interactiva.",
            "El hash de krbtgt permite Golden Ticket (persistencia total del dominio).",
        ],
        "commands": [
            {
                "cmd": "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP",
                "why": "Con una cuenta con privilegios (admin local o derechos de replicacion/DCSync) vuelca los hashes NTLM, incluidos administrator y krbtgt.",
                "out": "Lineas usuario:rid:lm:nt. El NT hash de administrator sirve para PtH; el de krbtgt para Golden Ticket. Copia los que apunten a cuentas privilegiadas.",
            },
            {
                "cmd": "evil-winrm -i $IP -u administrator -H <NTLM>",
                "why": "Pass-the-Hash por WinRM: te autenticas con el hash NTLM (-H) sin la password. Si el crackeo falla o tarda, esto te da la shell igual.",
                "out": "Un prompt PS de administrator (whoami lo confirma). Desde ahi recoge la flag y documenta la cadena que te llevo hasta el hash.",
            },
        ],
    },
    {
        "id": "bloodhound",
        "title": "BloodHound: el grafo de permisos",
        "phase": "access",
        "section": "active-directory",
        "summary": "Mapea el dominio como un grafo y te muestra la ruta mas corta de tu usuario a Domain Admin.",
        "que": "BloodHound recolecta usuarios, grupos, equipos, sesiones y ACLs del dominio y los representa como un grafo. En lugar de adivinar que permiso abusar, ves la ruta concreta: quien puede resetear la password de quien, que grupo tiene GenericAll sobre otro, donde hay sesiones de admin que robar.",
        "porque": "En un dominio real las relaciones de permisos son miles y a mano es imposible. El grafo revela caminos no obvios (encadenar tres permisos mediocres para llegar a DA) que definen el ataque en AD ([[ad-modelo]]).",
        "cuando": "En cuanto tengas UNA credencial valida. Es lo que haces cuando el roasting ([[asrep-kerberoast]]) no basto o para planificar el salto final a Domain Admin.",
        "senales": [
            "Aristas 'GenericAll', 'WriteDACL', 'ForceChangePassword' hacia grupos privilegiados.",
            "Sesiones de un admin en una maquina donde tu tienes acceso.",
            "Un camino corto marcado hacia el grupo Domain Admins.",
        ],
        "pasos": [
            "Recolecta los datos del dominio con un colector (bloodhound-python o SharpHound).",
            "Importa el zip en la GUI y marca tu usuario como 'owned'.",
            "Usa 'Shortest paths to Domain Admins' y estudia cada arista del camino.",
            "Abusa del permiso concreto (cada tipo de arista tiene su tecnica) y avanza un paso.",
        ],
        "commands": [
            {
                "cmd": "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip",
                "why": "Recolecta todo el grafo del dominio con una sola credencial, sin necesidad de pisar una maquina Windows. -c all junta toda la informacion; --zip lo deja listo para importar.",
                "out": "Un .zip para arrastrar a la GUI de BloodHound. Alli marca tu usuario como owned y lanza la consulta de rutas a Domain Admins.",
            },
        ],
    },
]


PATHS = [
    {
        "id": "web-a-shell",
        "title": "De una web a una shell",
        "summary": "El camino conceptual del pentesting web: entender la inclusion de ficheros, convertirla en ejecucion y, en paralelo, la inyeccion SQL.",
        "concepts": ["lfi", "lfi-a-rce", "sqli"],
    },
    {
        "id": "shells-y-acceso",
        "title": "Shells y acceso inicial",
        "summary": "Ya tienes ejecucion de comandos: como convertirla en una shell usable. Reverse vs bind y por que hay que estabilizar la TTY.",
        "concepts": ["reverse-vs-bind", "tty-stabilization"],
    },
    {
        "id": "privesc-linux-ruta",
        "title": "Escalada de privilegios en Linux",
        "summary": "De usuario normal a root. Primero el modelo mental, luego los tres vectores mas comunes en orden de rentabilidad.",
        "concepts": ["privesc-modelo", "sudo-abuse", "suid", "cron-abuse"],
    },
    {
        "id": "servicios-y-smb",
        "title": "Enumeracion de servicios",
        "summary": "Exprimir un servicio antes de explotarlo. SMB como ejemplo por su altisima rentabilidad en rooms Windows.",
        "concepts": ["smb-enum"],
    },
    {
        "id": "active-directory-ruta",
        "title": "Active Directory",
        "summary": "El cambio de mentalidad: transformar identidad en permisos. Modelo, Kerberos y su roasting, hashes NTLM y el grafo de BloodHound.",
        "concepts": ["ad-modelo", "kerberos", "asrep-kerberoast", "ntlm-pth", "bloodhound"],
    },
]
