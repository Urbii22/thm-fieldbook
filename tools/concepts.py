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
            "Convierte la ejecucion de un comando en una shell interactiva: lanza una reverse shell hacia tu maquina y estabilizala.",
            "Con shell ya dentro, cambia de fase: orientate y busca escalada. Los comandos concretos estan en la seccion de practica (ver comandos).",
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
]


PATHS = [
    {
        "id": "web-a-shell",
        "title": "De una web a una shell",
        "summary": "El camino conceptual del pentesting web: entender la inclusion de ficheros, convertirla en ejecucion y, en paralelo, la inyeccion SQL.",
        "concepts": ["lfi", "lfi-a-rce", "sqli"],
    },
]
