const BLANK_PROFILE = {
  ip: "",
  attacker: "",
  domain: "",
  dcHost: "",
  dcFqdn: "",
  port: "",
  user: "",
  pass: "",
  notes: "",
  revType: "bash",
  revLport: "4444",
  checks: {},
};

const state = {
  query: "",
  tag: "all",
  phase: "all",
  mode: "sections",
  activeSlug: "",
  room: { ip: "", url: "" },
  profile: { ...BLANK_PROFILE, checks: {} },
  data: null,
  visible: [],
  commandIndex: [],
  favs: new Set(),
  recent: [],
  favOnly: false,
  view: "practica",
  guides: [],
  activeGuide: "",
  concepts: [],
  paths: [],
  activeConcept: "",
  learnMode: "guides",
};

const PROFILE_KEY = "thm-room";
const LEGACY_IP_KEY = "thm-room-ip";
const FAVS_KEY = "thm-favs";
const RECENT_KEY = "thm-recent";
const APP_VERSION = "20260708-cmdnotes";
let suppressHash = false;

// Shell-payload templates are loaded from ./data/revshells.json at runtime.
let REV_TEMPLATES = [];
let STABILIZE = [];

// Secondary room variables (IP lives in the topbar). token = human hint of what it fills.
const ROOM_VARS = [
  { key: "attacker", label: "Attacker IP", ph: "10.8.0.5", token: "ATTACKER_IP · LHOST", mono: true },
  { key: "domain", label: "Domain", ph: "corp.local", token: "$DOMAIN", mono: true },
  { key: "dcHost", label: "DC host", ph: "DC01", token: "$DC_HOST", mono: true },
  { key: "dcFqdn", label: "DC FQDN", ph: "dc01.corp.local", token: "$DC_FQDN", mono: true },
  { key: "port", label: "Puerto(s)", ph: "80,443", token: "<PUERTOS> · $PORT", mono: true },
  { key: "user", label: "Usuario", ph: "jdoe", token: "$USER", mono: true },
  { key: "pass", label: "Password", ph: "P@ssw0rd", token: "$PASS", mono: true },
];

// Known placeholders to highlight when still unresolved after adaptCommand.
const UNRESOLVED_RE =
  /(\$(?:IP|URL|DOMAIN|DC_HOST|DC_FQDN|PORT|USER|PASS|LHOST|LPORT|RHOST)\b|&lt;(?:IP|URL|DOMAIN|DC_HOST|DC_FQDN|PORT|PUERTOS|USER|PASS|LHOST|LPORT|RHOST)&gt;|\bATTACKER_IP\b)/g;

const COPY_ICON =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg>';

const shortcutHints = {
  "Estoy atascado": "Reset de 10 minutos",
  "Tengo credenciales": "Cracking, loot y reuse",
  "Tengo shell": "Estabiliza y escala",
  "Veo una web": "Discovery, auth y APIs",
  "Necesito pivotar": "Tuneles y alcance interno",
  "Tengo una version/CVE": "Valida antes de explotar",
};

export function normalizeQuery(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

// Synonyms/aliases: a typed term also credits sections mentioning these expansions.
const ALIASES = {
  smb: ["enum4linux", "smbclient", "smbmap", "nxc", "netexec", "responder", "445"],
  ad: ["active directory", "kerberos", "bloodhound", "ldap", "kerberoast", "secretsdump", "impacket"],
  dc: ["domain controller", "active directory", "kerberos", "ldap"],
  kerberos: ["kerberoast", "asrep", "ticket", "impacket", "getuserspns"],
  rev: ["reverse shell", "revshell", "pty", "estabilizar", "socat"],
  revshell: ["reverse shell", "pty", "estabilizar", "socat"],
  shell: ["reverse shell", "pty", "estabilizar", "tty"],
  web: ["ffuf", "gobuster", "feroxbuster", "sqli", "idor", "api"],
  fuzz: ["ffuf", "gobuster", "feroxbuster", "wfuzz", "directorios"],
  creds: ["credenciales", "hash", "hashcat", "john", "loot", "password"],
  cred: ["credenciales", "hash", "hashcat", "john", "loot", "password"],
  hash: ["hashcat", "john", "crack", "rockyou", "wordlist"],
  crack: ["hashcat", "john", "rockyou", "wordlist"],
  priv: ["privesc", "sudo", "suid", "winpeas", "linpeas", "gtfobins"],
  privesc: ["sudo", "suid", "winpeas", "linpeas", "gtfobins", "escalada"],
  pivot: ["chisel", "ligolo", "proxychains", "tunnel", "tunel", "socks"],
  tunnel: ["chisel", "ligolo", "proxychains", "socks", "tunel"],
  nmap: ["escaneo", "puertos", "recon", "servicios"],
  scan: ["nmap", "escaneo", "puertos"],
  jwt: ["token", "jku", "hs256", "none"],
  upload: ["webshell", "bypass", "magic bytes", "subida"],
  rce: ["exploit", "poc", "cve", "payload", "lfi", "webshell", "command injection"],
  lfi: ["local file inclusion", "php filter", "proc/self", "log poisoning", "wrapper", "rce", "traversal"],
  cve: ["exploit", "poc", "rce", "payload"],
  wordpress: ["wpscan", "wp-login", "wp"],
  sqli: ["sqlmap", "union", "injection", "inyeccion"],
  linux: ["suid", "sudo", "cron", "gtfobins", "linpeas"],
  windows: ["winpeas", "powershell", "servicios", "registry", "winrm"],
};

const COMMAND_QUERY_TERMS = new Set([
  "arjun",
  "certutil",
  "chisel",
  "curl",
  "enum4linux",
  "feroxbuster",
  "ffuf",
  "gobuster",
  "hashcat",
  "john",
  "jwt_tool",
  "katana",
  "ligolo",
  "linpeas",
  "nmap",
  "nxc",
  "proxychains",
  "smbclient",
  "sqlmap",
  "whatweb",
  "wfuzz",
  "winpeas",
  "wpscan",
]);

function boundedEditDistance(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  const prev = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i += 1) {
    const curr = [i];
    let rowMin = i;
    for (let j = 1; j <= b.length; j += 1) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      const val = Math.min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost);
      curr[j] = val;
      if (val < rowMin) rowMin = val;
    }
    if (rowMin > max) return max + 1;
    prev.length = 0;
    prev.push(...curr);
  }
  return prev[b.length];
}

function fuzzyToken(tokens, term) {
  if (term.length < 4) return false;
  return tokens.some((token) => token.length >= 3 && boundedEditDistance(token, term, 1) <= 1);
}

function scoreSection(section, terms) {
  if (terms.length === 0) return 1;
  const title = normalizeQuery(section.title);
  const tags = normalizeQuery(section.tags.join(" "));
  const body = normalizeQuery(section.searchText);
  const titleTokens = title.split(" ");
  const tagTokens = tags.split(" ");
  const bodyTokens = [...new Set(body.split(" "))];
  return terms.reduce((score, term) => {
    let s = 0;
    if (title.includes(term)) s += 8;
    else if (tags.includes(term)) s += 5;
    else if (body.includes(term)) s += 2;
    else if (fuzzyToken(titleTokens, term)) s += 4;
    else if (fuzzyToken(tagTokens, term)) s += 3;
    else if (term.length >= 5 && fuzzyToken(bodyTokens, term)) s += 2;
    if (s === 0) {
      const expansions = ALIASES[term] || [];
      for (const needle of expansions) {
        if (body.includes(needle) || tags.includes(needle)) {
          s += 2;
          break;
        }
      }
    }
    return score + s;
  }, 0);
}

export function filterSections(sections, filters) {
  const query = normalizeQuery(filters.query);
  const terms = query ? query.split(" ") : [];
  return sections
    .filter((section) => filters.tag === "all" || section.tags.includes(filters.tag))
    .filter((section) => filters.phase === "all" || section.phase === filters.phase)
    .map((section) => ({ section, score: scoreSection(section, terms) }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score || a.section.order - b.section.order)
    .map((entry) => entry.section);
}

export function getTopCommands(sections, limit = 8) {
  return sections.flatMap((section) => section.commands).slice(0, limit);
}

export function shouldRenderCodeBlock(lines, section) {
  const commands = new Set((section?.commands || []).map((command) => String(command).trim()));
  const normalized = (lines || []).map((line) => String(line).trim()).filter(Boolean);
  return normalized.some((line) => !commands.has(line));
}

export function buildRoomContext(ipValue) {
  const ip = String(ipValue || "").trim();
  return {
    ip,
    url: ip ? `http://${ip}` : "",
  };
}

export function adaptCommand(command, room) {
  if (!room) return command;
  let out = String(command);
  const sub = (needle, value) => {
    if (value) out = out.replaceAll(needle, value);
  };
  if (room.ip) {
    sub("$IP", room.ip);
    sub("<IP>", room.ip);
    sub("10.10.10.10", room.ip);
  }
  if (room.url) {
    sub("$URL", room.url);
    sub("http://target.local", room.url);
    sub("https://target.local", room.url.replace("http://", "https://"));
  }
  sub("ATTACKER_IP", room.attacker);
  sub("$LHOST", room.attacker);
  sub("<LHOST>", room.attacker);
  sub("$DOMAIN", room.domain);
  sub("<DOMAIN>", room.domain);
  sub("$DC_FQDN", room.dcFqdn);
  sub("<DC_FQDN>", room.dcFqdn);
  sub("$DC_HOST", room.dcHost);
  sub("<DC_HOST>", room.dcHost);
  sub("<PUERTOS>", room.port);
  sub("$PORT", room.port);
  sub("<PORT>", room.port);
  sub("$USER", room.user);
  sub("<USER>", room.user);
  sub("$PASS", room.pass);
  sub("<PASS>", room.pass);
  return out;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function queryTerms() {
  return String(state.query || "")
    .split(/\s+/)
    .map((term) => term.trim())
    .filter((term) => term.length >= 2);
}

export function filterCommandEntries(commandIndex, query, limit = 80) {
  const terms = normalizeQuery(query).split(" ").filter(Boolean);
  const scored = [];
  for (const entry of commandIndex) {
    const hay = normalizeQuery(entry.command);
    const words = hay.split(/[^a-z0-9_.-]+/).filter(Boolean);
    let score = terms.length ? 0 : 1;
    let ok = true;
    for (const term of terms) {
      if (hay.startsWith(term)) score += 8;
      else if (words.includes(term)) score += 5;
      else if (hay.includes(term)) score += 2;
      else {
        ok = false;
        break;
      }
    }
    if (ok && score > 0) scored.push({ entry, score });
  }
  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((item) => item.entry);
}

function highlight(escaped, terms) {
  if (!terms.length) return escaped;
  const pattern = terms
    .map((term) => term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .filter(Boolean)
    .join("|");
  if (!pattern) return escaped;
  return escaped.replace(new RegExp(`(${pattern})`, "gi"), '<mark class="hit">$1</mark>');
}

function phaseLabel(phase) {
  const labels = {
    access: "Acceso",
    closeout: "Cierre",
    enumeration: "Enumeracion",
    pivot: "Pivot",
    privesc: "Privesc",
    recon: "Recon",
    reference: "Referencia",
  };
  return labels[phase] || phase;
}

const KNOWN_PHASES = new Set(["access", "closeout", "enumeration", "pivot", "privesc", "recon", "reference"]);

function phaseStyle(phase) {
  return KNOWN_PHASES.has(phase) ? `--phase:var(--phase-${phase})` : "";
}

function markPlaceholders(escaped) {
  return escaped.replace(UNRESOLVED_RE, (match) => `<mark class="ph">${match}</mark>`);
}

// token -> short ES explanation, shown on hover of the "i" marker.
const FLAG_HELP = {
  nmap: "escaneo de puertos y servicios",
  "-p-": "todos los 65535 puertos",
  "-sC": "scripts NSE por defecto",
  "-sV": "detecta versiones",
  "-sU": "escaneo UDP",
  "-sS": "escaneo SYN sigiloso",
  "-sT": "escaneo TCP connect",
  "-Pn": "omite el ping de descubrimiento",
  "-n": "sin resolucion DNS",
  "-v": "salida verbosa",
  "-O": "detecta el sistema operativo",
  "-A": "OS + version + scripts + traceroute",
  "--min-rate": "fuerza paquetes/seg (ruidoso)",
  "-T4": "timing agresivo",
  "-T5": "timing insano (muy ruidoso)",
  "-oN": "guarda salida en texto",
  "-oA": "guarda salida en los 3 formatos",
  ffuf: "fuzzing web de rutas/parametros",
  gobuster: "fuerza rutas/DNS/vhosts",
  feroxbuster: "fuerza rutas recursivo",
  "-w": "wordlist (diccionario)",
  "-u": "URL objetivo",
  "-H": "cabecera HTTP",
  hashcat: "crackeo de hashes por GPU",
  "-m": "tipo de hash (modo)",
  "-a": "modo de ataque",
  john: "crackeo de hashes (CPU)",
  "--wordlist": "diccionario",
  curl: "cliente HTTP",
  "-i": "incluye cabeceras en la salida",
  "-x": "usa proxy",
  chisel: "tunel TCP / SOCKS",
  "ligolo-ng": "tunel y pivoting",
  proxychains: "rutea trafico por un proxy",
  "impacket-": "suite de ataques AD/SMB",
  crackmapexec: "enum/exec masivo SMB/WinRM",
  nxc: "netexec: enum/exec masivo",
  netexec: "enum/exec masivo (ex-CME)",
  "evil-winrm": "shell interactiva por WinRM",
  smbclient: "cliente SMB",
  enum4linux: "enumeracion SMB/AD",
  "sudo -l": "lista permisos sudo",
  linpeas: "auditoria de privesc en Linux",
  winpeas: "auditoria de privesc en Windows",
};

const DANGER_PATTERNS = [
  /\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r/,
  /\bmkfs\b/,
  /\bdd\s+if=/,
  /:\s*\(\)\s*\{.*\};\s*:/,
  /\b(shutdown|reboot|halt|poweroff)\b/,
  /chmod\s+-R?\s*777\s+\//,
  /\bdel\s+\/[fsq]/i,
  /format\s+[a-z]:/i,
];

const NOISY_PATTERNS = [
  /--min-rate/,
  /\b-T[45]\b/,
  /\b(hydra|medusa|patator|masscan)\b/,
  /\b(crackmapexec|nxc|netexec)\b/,
  /\b(ffuf|gobuster|feroxbuster|wfuzz)\b/,
  /\bresponder\b/,
  /nmap\b[^|]*-p-/,
];

function detectRisk(raw) {
  const lower = String(raw).toLowerCase();
  if (DANGER_PATTERNS.some((re) => re.test(lower))) {
    return { level: "danger", reason: "Destructivo: revisa a fondo antes de ejecutar." };
  }
  if (NOISY_PATTERNS.some((re) => re.test(lower))) {
    return { level: "noisy", reason: "Ruidoso: puede disparar IDS o llenar logs." };
  }
  return null;
}

// token -> what it represents, shown as a variable to swap in the explain modal.
const VAR_HELP = {
  "$IP": "IP objetivo",
  "<IP>": "IP objetivo",
  "$RHOST": "IP objetivo",
  "$URL": "URL objetivo",
  "<URL>": "URL objetivo",
  "$DOMAIN": "dominio de Active Directory",
  "<DOMAIN>": "dominio de Active Directory",
  "$DC_HOST": "hostname del Domain Controller",
  "<DC_HOST>": "hostname del Domain Controller",
  "$DC_FQDN": "FQDN del Domain Controller",
  "<DC_FQDN>": "FQDN del Domain Controller",
  "$PORT": "puerto(s)",
  "<PORT>": "puerto(s)",
  "<PUERTOS>": "puerto(s)",
  "$USER": "usuario",
  "<USER>": "usuario",
  "$PASS": "contrasena",
  "<PASS>": "contrasena",
  "$LHOST": "tu IP (attacker / listener)",
  "<LHOST>": "tu IP (attacker / listener)",
  "ATTACKER_IP": "tu IP (attacker / listener)",
  "$LPORT": "tu puerto de escucha",
  "<LPORT>": "tu puerto de escucha",
};

// first-token tool -> one-line purpose for the explain modal.
const TOOL_PURPOSE = {
  nmap: "Escanea puertos y detecta servicios y versiones en el objetivo.",
  ffuf: "Fuzzing web: descubre rutas, ficheros o parametros por fuerza bruta.",
  gobuster: "Fuerza bruta de rutas, subdominios o vhosts en un servidor web.",
  feroxbuster: "Fuerza bruta recursiva de rutas web.",
  wfuzz: "Fuzzing web de parametros y rutas.",
  hashcat: "Crackea hashes con GPU usando diccionario o reglas.",
  john: "Crackea hashes con CPU (John the Ripper).",
  curl: "Cliente HTTP para lanzar peticiones y ver la respuesta.",
  wget: "Descarga ficheros por HTTP/HTTPS.",
  chisel: "Crea un tunel TCP/SOCKS para pivotar a redes internas.",
  socat: "Reenvia y conecta sockets; util para shells y tuneles.",
  proxychains: "Rutea la herramienta que le sigue a traves de un proxy SOCKS.",
  crackmapexec: "Enumera y ejecuta en masa sobre SMB/WinRM/LDAP.",
  nxc: "NetExec: enumera y ejecuta en masa (sucesor de CrackMapExec).",
  netexec: "Enumera y ejecuta en masa sobre SMB/WinRM/LDAP.",
  "evil-winrm": "Shell interactiva remota por WinRM.",
  smbclient: "Cliente para listar y acceder a recursos compartidos SMB.",
  smbmap: "Enumera shares SMB y sus permisos.",
  enum4linux: "Enumera usuarios, grupos y shares por SMB/AD.",
  "enum4linux-ng": "Enumeracion SMB/AD (version mejorada).",
  responder: "Envenena LLMNR/NBT-NS para capturar hashes NetNTLM.",
  linpeas: "Audita un sistema Linux buscando vias de escalada.",
  winpeas: "Audita un sistema Windows buscando vias de escalada.",
  wpscan: "Escanea WordPress: usuarios, plugins y vulnerabilidades.",
  sqlmap: "Automatiza la deteccion y explotacion de inyeccion SQL.",
  hydra: "Fuerza bruta de credenciales contra un servicio de red.",
  msfvenom: "Genera payloads (shells, binarios) para explotacion.",
  nc: "Netcat: abre o escucha conexiones TCP/UDP (listener o cliente).",
  ncat: "Netcat de Nmap: conexiones TCP/UDP, listener o cliente.",
  ssh: "Cliente SSH para acceso remoto y tuneles.",
  sudo: "Ejecuta como otro usuario; util para revisar o abusar de permisos.",
  ldapsearch: "Consulta un directorio LDAP.",
  kinit: "Solicita un ticket Kerberos (TGT).",
};

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function baseTool(token) {
  const clean = String(token || "").split("/").pop().toLowerCase();
  return clean;
}

const PORT_FLAGS = new Set(["-p", "--port", "-p-", "-dport", "--dport", "--top-ports"]);

function classifyToken(token, index, prevToken) {
  if (VAR_HELP[token]) return VAR_HELP[token];
  if (/^\$[A-Za-z_]+$/.test(token) || /^<[A-Za-z]/.test(token) || token === "ATTACKER_IP") {
    return "variable: reemplaza por tu valor";
  }
  if (index === 0) return "herramienta principal";
  if (token.startsWith("--")) return FLAG_HELP[token] || "opcion (forma larga)";
  if (token.startsWith("-")) return FLAG_HELP[token] || "flag / opcion";
  if (/^https?:\/\//.test(token)) return "URL objetivo";
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(token)) return "direccion IP";
  if (/[/\\]/.test(token) || /\.(txt|lst|list|conf|xml|json|pcap|php|sh|py|exe|elf)$/i.test(token)) {
    return "ruta / fichero / wordlist";
  }
  if (/^\d+[,-]\d+/.test(token) || PORT_FLAGS.has(prevToken)) return "puerto(s)";
  if (/^\d+$/.test(token)) return "valor numerico";
  if (/^[A-Za-z0-9_.]+=.+/.test(token)) return "parametro clave=valor";
  return "argumento / valor";
}

function describeCommand(raw) {
  const tokens = String(raw).split(/\s+/).filter(Boolean);
  const base = baseTool(tokens[0] || "");
  let purpose = TOOL_PURPOSE[base];
  if (!purpose) purpose = FLAG_HELP[base] ? `${capitalize(FLAG_HELP[base])}.` : "Comando de shell.";
  const parts = tokens.map((token, index) => ({ token, desc: classifyToken(token, index, tokens[index - 1]) }));
  const seen = new Set();
  const vars = [];
  for (const token of tokens) {
    const isVar = VAR_HELP[token] || /^\$[A-Za-z_]+$/.test(token) || /^<[A-Za-z]/.test(token) || token === "ATTACKER_IP";
    if (isVar && !seen.has(token)) {
      seen.add(token);
      vars.push({ token, desc: VAR_HELP[token] || "reemplaza por tu valor" });
    }
  }
  return { purpose, parts, vars };
}

function infoMarkFor(rawCommand) {
  return `<span class="cmd-info" data-explain="${escapeHtml(rawCommand)}" role="button" tabindex="0" title="Explicar comando" aria-label="Explicar comando">i</span>`;
}

function ensureCmdModal() {
  let el = document.querySelector("[data-cmd-modal]");
  if (el) return el;
  el = document.createElement("div");
  el.className = "cmd-modal-backdrop";
  el.setAttribute("data-cmd-modal", "");
  el.hidden = true;
  el.innerHTML = `<div class="cmd-modal-box" role="dialog" aria-modal="true" aria-label="Explicacion del comando"></div>`;
  document.body.appendChild(el);
  el.addEventListener("click", (event) => {
    if (event.target === el) closeCmdModal();
  });
  return el;
}

function closeCmdModal() {
  const el = document.querySelector("[data-cmd-modal]");
  if (el) el.hidden = true;
}

function openCmdModal(raw) {
  if (!raw) return;
  const el = ensureCmdModal();
  const box = el.querySelector(".cmd-modal-box");
  const info = describeCommand(raw);
  const adapted = adaptCommand(raw, state.room);
  const risk = detectRisk(raw);
  const partsHtml = info.parts
    .map((part) => `<li><code>${escapeHtml(part.token)}</code><span>${escapeHtml(part.desc)}</span></li>`)
    .join("");
  const varsHtml = info.vars.length
    ? `<div class="cmd-modal-vars"><h4>Variables a ajustar</h4><ul>${info.vars
        .map((v) => `<li><code>${escapeHtml(v.token)}</code><span>${escapeHtml(v.desc)}</span></li>`)
        .join("")}</ul></div>`
    : "";
  const riskHtml = risk
    ? `<p class="cmd-modal-risk risk-${risk.level}">${risk.level === "danger" ? "⚠" : "📡"} ${escapeHtml(risk.reason)}</p>`
    : "";
  box.innerHTML = `
    <button type="button" class="cmd-modal-close" data-cmd-close aria-label="Cerrar">×</button>
    <code class="cmd-modal-cmd">${escapeHtml(adapted)}</code>
    <p class="cmd-modal-purpose">${escapeHtml(info.purpose)}</p>
    ${riskHtml}
    <h4>Partes del comando</h4>
    <ul class="cmd-modal-parts">${partsHtml}</ul>
    ${varsHtml}
    <button type="button" class="cmd-modal-copy" data-copy="${escapeHtml(adapted)}">copiar comando</button>`;
  box.querySelector("[data-cmd-close]").addEventListener("click", closeCmdModal);
  el.hidden = false;
  bindCopyButtons();
}

function commandCard(rawCommand, opts = {}) {
  const command = adaptCommand(rawCommand, state.room);
  const esc = escapeHtml(command);
  const risk = detectRisk(rawCommand);
  const riskMark = risk
    ? `<span class="risk-badge risk-${risk.level}" title="${escapeHtml(risk.reason)}" aria-label="${escapeHtml(risk.reason)}">${risk.level === "danger" ? "⚠" : "📡"}</span>`
    : "";
  const infoMark = infoMarkFor(rawCommand);
  const editBtn = opts.edit
    ? `<button type="button" class="cmd-edit-btn" data-edit title="Editar antes de copiar" aria-label="Editar">✎</button>`
    : "";
  const tools = riskMark || infoMark || editBtn ? `<div class="cmd-tools">${riskMark}${infoMark}${editBtn}</div>` : "";
  return `<div class="cmd ${risk ? `risk-${risk.level}` : ""}">
    <div class="cmd-view">
      <button type="button" class="cmd-copy" data-copy="${esc}" title="Copiar comando"><code>${highlight(markPlaceholders(esc), opts.terms || [])}</code><span class="copy-btn">${COPY_ICON}<span class="copy-label">copy</span></span></button>
      ${tools}
    </div>
    ${
      opts.edit
        ? `<div class="cmd-edit-wrap" hidden><input type="text" class="cmd-input" spellcheck="false" value="${esc}" /><button type="button" class="cmd-edit-copy">copiar</button></div>`
        : ""
    }
  </div>`;
}

function checkKey(slug, blockIndex, itemIndex) {
  return `${slug}::${blockIndex}::${itemIndex}`;
}

function blockHtml(block, ctx = {}) {
  const [kind, payload] = block;
  if (kind === "p") return `<p>${escapeHtml(payload)}</p>`;
  if (kind === "h2") return `<h3>${escapeHtml(payload)}</h3>`;
  if (kind === "bullets") {
    const items = payload
      .map((item, itemIndex) => {
        const key = checkKey(ctx.slug, ctx.index, itemIndex);
        const done = Boolean(state.profile.checks[key]);
        return `<li class="check-item ${done ? "done" : ""}">
          <label>
            <input type="checkbox" data-check="${escapeHtml(key)}" ${done ? "checked" : ""} />
            <span>${escapeHtml(item)}</span>
          </label>
        </li>`;
      })
      .join("");
    return `<ul class="checklist">${items}</ul>`;
  }
  if (kind === "code") {
    return `<div class="code-stack">${payload
      .map((line) => commandCard(line, { edit: true, terms: queryTerms() }))
      .join("")}</div>`;
  }
  if (kind === "table") {
    const rows = payload
      .map((row, index) => {
        const cells = row.map((cell) => `<${index === 0 ? "th" : "td"}>${escapeHtml(cell)}</${index === 0 ? "th" : "td"}>`).join("");
        return `<tr>${cells}</tr>`;
      })
      .join("");
    return `<div class="table-wrap"><table>${rows}</table></div>`;
  }
  return "";
}

function buildRevshell(id, lhost, lport) {
  const entry = REV_TEMPLATES.find((item) => item.id === id) || REV_TEMPLATES[0];
  if (!entry) return "";
  const tpl = Array.isArray(entry.parts) ? entry.parts.join("") : String(entry.tpl || "");
  return tpl.replaceAll("{LHOST}", lhost).replaceAll("{LPORT}", lport);
}

function b64Utf8(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

function b64Utf16le(str) {
  let bin = "";
  for (const ch of str) {
    const c = ch.charCodeAt(0);
    bin += String.fromCharCode(c & 0xff, (c >> 8) & 0xff);
  }
  return btoa(bin);
}

function encodingVariants(command, type) {
  const url = encodeURIComponent(command);
  const b64 = type === "powershell" ? `powershell -enc ${b64Utf16le(command)}` : `echo '${b64Utf8(command)}' | base64 -d | bash`;
  return { url, b64 };
}

function renderRevshell() {
  const out = document.querySelector("[data-rev-out]");
  const listenerOut = document.querySelector("[data-rev-listener]");
  const lhostReadout = document.querySelector("[data-rev-lhost]");
  const typeSelect = document.querySelector("[data-rev-type]");
  const lportInput = document.querySelector("[data-rev-lport]");
  if (!out) return;
  if (!REV_TEMPLATES.length) {
    out.innerHTML = `<p class="rev-empty">Plantillas no disponibles.</p>`;
    if (listenerOut) listenerOut.innerHTML = "";
    return;
  }
  const lhost = state.profile.attacker.trim() || "ATTACKER_IP";
  const lport = String(state.profile.revLport || "").trim() || "4444";
  if (typeSelect && typeSelect.options.length !== REV_TEMPLATES.length) {
    typeSelect.innerHTML = REV_TEMPLATES.map(
      (item) => `<option value="${escapeHtml(item.id)}">${escapeHtml(item.label)}</option>`,
    ).join("");
  }
  if (typeSelect) typeSelect.value = state.profile.revType || REV_TEMPLATES[0].id;
  if (lportInput && document.activeElement !== lportInput) lportInput.value = lport;
  if (lhostReadout) lhostReadout.textContent = lhost;
  const type = state.profile.revType || REV_TEMPLATES[0].id;
  const command = buildRevshell(type, lhost, lport);
  out.innerHTML = commandCard(command, { edit: true });
  if (listenerOut) listenerOut.innerHTML = commandCard(`nc -lvnp ${lport}`, {});

  const enc = document.querySelector("[data-rev-enc]");
  if (enc) {
    const { url, b64 } = encodingVariants(command, type);
    enc.innerHTML = `<span class="rev-enc-label">variantes</span>
      <button type="button" class="rev-enc-btn" data-copy="${escapeHtml(b64)}" title="Copiar codificado en base64">base64</button>
      <button type="button" class="rev-enc-btn" data-copy="${escapeHtml(url)}" title="Copiar URL-encoded">url</button>`;
  }

  const stab = document.querySelector("[data-rev-stabilize]");
  if (stab) {
    stab.innerHTML = STABILIZE.map((step) => {
      const cmd = (step.parts || []).join("");
      const label = step.label ? `<span class="stab-label">${escapeHtml(step.label)}</span>` : "";
      return `<div class="stab-step">${label}${commandCard(cmd, {})}</div>`;
    }).join("");
  }

  bindCommandToolsIn(document.querySelector(".revshell-block"));
  bindCopyButtons();
}

function renderOptions(container, values, selected, labeler, onSelect) {
  container.innerHTML = [
    `<button type="button" class="${selected === "all" ? "active" : ""}" data-value="all">Todo</button>`,
    ...values.map(
      (value) =>
        `<button type="button" class="${selected === value ? "active" : ""}" data-value="${escapeHtml(value)}">${escapeHtml(labeler(value))}</button>`,
    ),
  ].join("");
  container.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => onSelect(button.dataset.value));
  });
}

function renderShortcuts(data) {
  const container = document.querySelector("[data-shortcuts]");
  container.innerHTML = data.shortcuts
    .map(
      (shortcut) =>
        `<button type="button" data-query="${escapeHtml(shortcut.query)}" data-target="${escapeHtml(shortcut.target)}">
          <strong>${escapeHtml(shortcut.label)}</strong>
          <span>${escapeHtml(shortcutHints[shortcut.label] || "Abrir ruta recomendada")}</span>
        </button>`,
    )
    .join("");
  container.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = "sections";
      state.query = button.dataset.query;
      state.activeSlug = button.dataset.target;
      document.querySelector("[data-search]").value = state.query;
      pushRecent(state.activeSlug);
      writeHash(true);
      render();
    });
  });
}

function renderResults(sections) {
  const container = document.querySelector("[data-results]");
  const commandMatches = state.query ? renderInlineCommandMatches() : "";
  if (!sections.length) {
    container.innerHTML = commandMatches || `<p class="list-empty">Sin coincidencias. Cambia fase, tema o termino.</p>`;
    bindInlineCommandMatches(container);
    return;
  }
  const terms = queryTerms();
  container.innerHTML = commandMatches + sections
    .map((section) => {
      const fav = state.favs.has(section.slug);
      return `<div class="result-wrap">
        <button type="button" role="option" aria-selected="${state.activeSlug === section.slug}" class="result ${state.activeSlug === section.slug ? "active" : ""}" style="${phaseStyle(section.phase)}" data-slug="${escapeHtml(section.slug)}">
          <span class="result-top">
            <span class="result-phase">${escapeHtml(phaseLabel(section.phase))}</span>
            <span class="result-cmdcount">${section.commands.length} cmd</span>
          </span>
          <strong>${highlight(escapeHtml(section.title), terms)}</strong>
          <span class="result-summary">${highlight(escapeHtml(section.summary), terms)}</span>
          <span class="result-tags">${section.tags.slice(0, 4).map((tag) => `<b>${escapeHtml(tag)}</b>`).join("")}</span>
        </button>
        <button type="button" class="fav-star ${fav ? "on" : ""}" data-fav="${escapeHtml(section.slug)}" title="${fav ? "Quitar de favoritos" : "Anadir a favoritos"}" aria-label="Favorito">${fav ? "★" : "☆"}</button>
      </div>`;
    })
    .join("");
  bindInlineCommandMatches(container);
  container.querySelectorAll(".result").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeSlug = button.dataset.slug;
      pushRecent(button.dataset.slug);
      writeHash(true);
      render();
    });
  });
  container.querySelectorAll("[data-fav]").forEach((star) => {
    star.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleFav(star.dataset.fav);
    });
  });
}

function renderInlineCommandMatches() {
  const entries = filterCommandEntries(state.commandIndex, state.query, 6);
  if (!entries.length) return "";
  const terms = queryTerms();
  return `<section class="command-matches" aria-label="Comandos encontrados">
    <div class="command-matches-head">
      <strong>Comandos encontrados</strong>
      <button type="button" data-switch-commands>${entries.length === 6 ? "ver mas" : `${entries.length} resultados`}</button>
    </div>
    ${entries
      .map((entry) => {
        const command = adaptCommand(entry.command, state.room);
        const value = escapeHtml(command);
        return `<button type="button" class="command-match" data-copy="${value}" data-slug="${escapeHtml(entry.section.slug)}" title="Copiar comando">
          <code>${highlight(markPlaceholders(value), terms)}</code>
          <span>${escapeHtml(entry.section.title)}</span>
          ${infoMarkFor(entry.command)}
          <b>copy</b>
        </button>`;
      })
      .join("")}
  </section>`;
}

function bindInlineCommandMatches(container) {
  container.querySelector("[data-switch-commands]")?.addEventListener("click", () => {
    state.mode = "commands";
    render();
  });
  container.querySelectorAll(".command-match").forEach((button) => {
    button.addEventListener("dblclick", () => {
      state.mode = "sections";
      state.activeSlug = button.dataset.slug;
      pushRecent(button.dataset.slug);
      writeHash(true);
      render();
    });
  });
}

function filterCommands(limit = 80) {
  return filterCommandEntries(state.commandIndex, state.query, limit);
}

function isCommandFocusedQuery(entries) {
  if (state.mode === "commands") return entries.length > 0;
  const terms = normalizeQuery(state.query).split(" ").filter(Boolean);
  if (!terms.length || !entries.length) return false;
  if (terms.some((term) => COMMAND_QUERY_TERMS.has(term))) return true;
  return entries.some((entry) => {
    const words = normalizeQuery(entry.command).split(/[^a-z0-9_.-]+/).filter(Boolean);
    return terms.every((term) => words.includes(term));
  });
}

function renderCommandResults() {
  const container = document.querySelector("[data-results]");
  const entries = filterCommands();
  if (!entries.length) {
    container.innerHTML = `<p class="list-empty">Ningun comando coincide. Prueba otro termino.</p>`;
    return;
  }
  const terms = queryTerms();
  container.innerHTML = entries
    .map((entry) => {
      const command = adaptCommand(entry.command, state.room);
      const value = escapeHtml(command);
      const risk = detectRisk(entry.command);
      const riskMark = risk
        ? `<span class="risk-badge risk-${risk.level}" title="${escapeHtml(risk.reason)}">${risk.level === "danger" ? "⚠" : "📡"}</span>`
        : "";
      const infoMark = infoMarkFor(entry.command);
      return `<button type="button" class="cmd-result" style="${phaseStyle(entry.section.phase)}" data-copy="${value}" data-slug="${escapeHtml(entry.section.slug)}" title="Copiar comando">
        <code>${highlight(markPlaceholders(value), terms)}</code>
        <span class="cmd-src"><em>${escapeHtml(phaseLabel(entry.section.phase))}</em>${escapeHtml(entry.section.title)}<span class="cmd-src-tools">${riskMark}${infoMark}</span></span>
        <span class="copy-btn">${COPY_ICON}<span class="copy-label">copy</span></span>
      </button>`;
    })
    .join("");
  container.querySelectorAll(".cmd-result").forEach((button) => {
    button.addEventListener("dblclick", () => {
      state.mode = "sections";
      state.activeSlug = button.dataset.slug;
      pushRecent(button.dataset.slug);
      writeHash(true);
      render();
    });
  });
}

function renderCommandSearchDetail() {
  const container = document.querySelector("[data-detail]");
  const entries = filterCommands(80);
  if (!state.query || !isCommandFocusedQuery(entries)) return false;

  const terms = queryTerms();
  const copyAll = escapeHtml(entries.map((entry) => adaptCommand(entry.command, state.room)).join("\n"));
  const helper = state.room.ip
    ? `Adaptados a <b>${escapeHtml(state.room.ip)}</b>.`
    : "Fija la IP de la room arriba para autocompletar <b>$IP</b> / <b>$URL</b>.";

  container.setAttribute("style", phaseStyle(entries[0].section.phase));
  container.innerHTML = `
    <header class="detail-head command-search-head">
      <div class="detail-meta">
        <span class="detail-phase">Busqueda</span>
        <span class="detail-count">${entries.length} comandos</span>
      </div>
      <h2>Comandos para "${escapeHtml(state.query)}"</h2>
      <p>Resultados copiables del master y de las secciones. Doble click en un resultado de la izquierda abre su seccion.</p>
    </header>
    <section class="detail-body">
      <section class="command-shelf command-focus" aria-label="Comandos encontrados">
        <div class="command-shelf-head">
          <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
          <h3>comandos encontrados</h3>
          <button type="button" class="copy-all" data-copy="${copyAll}" title="Copiar todos">${COPY_ICON}<span class="copy-label">copiar todo</span></button>
        </div>
        <p class="command-hint">${helper}</p>
        <div class="command-grid command-hit-grid">
          ${entries
            .map(
              (entry) => `<article class="command-hit-card" style="${phaseStyle(entry.section.phase)}">
                <div class="command-hit-source">
                  <span>${escapeHtml(phaseLabel(entry.section.phase))}</span>
                  <button type="button" data-open-section="${escapeHtml(entry.section.slug)}">${escapeHtml(entry.section.title)}</button>
                </div>
                ${commandCard(entry.command, { edit: true, terms })}
              </article>`,
            )
            .join("")}
        </div>
      </section>
    </section>
  `;
  container.querySelectorAll("[data-open-section]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeSlug = button.dataset.openSection;
      state.query = "";
      state.mode = "sections";
      document.querySelector("[data-search]").value = "";
      pushRecent(state.activeSlug);
      writeHash(true);
      render();
    });
  });
  bindCommandTools();
  return true;
}

function commandsHtml(section) {
  if (!section.commands.length) return "";
  const helper = state.room.ip
    ? `Adaptados a <b>${escapeHtml(state.room.ip)}</b>.`
    : "Fija la IP de la room arriba para autocompletar <b>$IP</b> / <b>$URL</b>.";
  const allCommands = escapeHtml(section.commands.map((command) => adaptCommand(command, state.room)).join("\n"));
  return `<section class="command-shelf" aria-label="Comandos de esta seccion">
    <div class="command-shelf-head">
      <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
      <h3>comandos · ${section.commands.length}</h3>
      <button type="button" class="copy-all" data-copy="${allCommands}" title="Copiar todos">${COPY_ICON}<span class="copy-label">copiar todo</span></button>
    </div>
    <p class="command-hint">${helper}</p>
  </section>`;
}

// Split a section's blocks into groups at each ("h2", …) boundary. Content before
// the first h2 is an untitled intro group. Keeps each block's original index so
// checklist keys (slug::blockIndex::itemIndex) stay stable.
function buildSectionGroups(section) {
  const groups = [];
  let current = { title: null, blocks: [] };
  (section.blocks || []).forEach((block, index) => {
    if (block[0] === "h2") {
      if (current.title !== null || current.blocks.length) groups.push(current);
      current = { title: block[1], blocks: [] };
    } else {
      current.blocks.push([block, index]);
    }
  });
  if (current.title !== null || current.blocks.length) groups.push(current);
  return groups;
}

function countGroupCommands(group) {
  return group.blocks.reduce((sum, [block]) => (block[0] === "code" ? sum + block[1].length : sum), 0);
}

// Commands that live only in section.commands (e.g. merged from the master guide)
// and are not in any code block, so the detail still surfaces them.
function leftoverCommands(section) {
  const inBlocks = new Set();
  for (const block of section.blocks || []) {
    if (block[0] === "code") {
      for (const line of block[1]) inBlocks.add(String(line).trim());
    }
  }
  return (section.commands || []).filter((command) => !inBlocks.has(String(command).trim()));
}

function sectionBodyHtml(section) {
  const groups = buildSectionGroups(section);
  const toc = [];
  const parts = [];
  let k = 0;

  for (const group of groups) {
    const body = group.blocks
      .map(([block, index]) => blockHtml(block, { slug: section.slug, index, section }))
      .join("");
    if (group.title === null) {
      if (body) parts.push(`<div class="cmd-group cmd-intro">${body}</div>`);
      continue;
    }
    const id = `sec-grp-${k++}`;
    const count = countGroupCommands(group);
    toc.push({ id, title: group.title, count });
    parts.push(
      `<details class="cmd-group" open id="${id}"><summary class="cmd-group-head"><span class="cmd-group-title">${escapeHtml(group.title)}</span>${count ? `<b>${count} cmd</b>` : ""}<span class="cmd-group-chev" aria-hidden="true">▾</span></summary><div class="cmd-group-body">${body}</div></details>`,
    );
  }

  const leftover = leftoverCommands(section);
  if (leftover.length) {
    const id = `sec-grp-${k++}`;
    toc.push({ id, title: "Mas comandos", count: leftover.length });
    const terms = queryTerms();
    const cards = leftover.map((command) => commandCard(command, { edit: true, terms })).join("");
    parts.push(
      `<details class="cmd-group" open id="${id}"><summary class="cmd-group-head"><span class="cmd-group-title">Mas comandos</span><b>${leftover.length} cmd</b><span class="cmd-group-chev" aria-hidden="true">▾</span></summary><div class="cmd-group-body"><div class="code-stack">${cards}</div></div></details>`,
    );
  }

  const tocHtml =
    toc.length >= 2
      ? `<nav class="section-toc" aria-label="Ir a un bloque de la seccion">${toc
          .map((item) => `<button type="button" data-jump="${item.id}"><span>${escapeHtml(item.title)}</span><b>${item.count}</b></button>`)
          .join("")}</nav>`
      : "";
  return tocHtml + parts.join("");
}

// Keep --topbar-h in sync with the real sticky topbar height so the in-section
// TOC pins right below it (topbar stacks taller on narrow viewports / open room).
function trackTopbarHeight() {
  const topbar = document.querySelector(".topbar");
  if (!topbar) return;
  const set = () => document.documentElement.style.setProperty("--topbar-h", `${topbar.offsetHeight}px`);
  set();
  if ("ResizeObserver" in window) new ResizeObserver(set).observe(topbar);
  window.addEventListener("resize", set);
}

function bindSectionNav() {
  const container = document.querySelector("[data-detail]");
  if (!container) return;
  const buttons = [...container.querySelectorAll(".section-toc [data-jump]")];
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = container.querySelector(`#${CSS.escape(button.dataset.jump)}`);
      if (!target) return;
      if (target.tagName === "DETAILS") target.open = true;
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      buttons.forEach((other) => other.classList.toggle("active", other === button));
    });
  });
}

function renderRoomConfig() {
  const input = document.querySelector("[data-room-ip]");
  const status = document.querySelector("[data-room-status]");
  const wrap = input?.closest(".target");
  if (!input || !status) return;
  if (document.activeElement !== input) input.value = state.room.ip;
  status.textContent = state.room.ip ? "activo" : "sin IP";
  if (wrap) wrap.dataset.targetState = state.room.ip ? "active" : "idle";
}

function renderDetail(section) {
  const container = document.querySelector("[data-detail]");
  if (!section) {
    container.style.removeProperty("--phase");
    container.innerHTML = `<div class="empty"><span class="empty-mark">¯\\_(ツ)_/¯</span><strong>Nada por aqui</strong><p>Prueba con otro concepto, fase o etiqueta.</p></div>`;
    return;
  }
  const progress = checklistProgress(section);
  const progressChip = progress.total
    ? `<span class="detail-progress" data-progress><b>${progress.done}</b>/${progress.total} hecho</span>`
    : "";
  container.setAttribute("style", phaseStyle(section.phase));
  container.innerHTML = `
    <header class="detail-head">
      <div class="detail-meta">
        <span class="detail-phase">${escapeHtml(phaseLabel(section.phase))}</span>
        <span class="detail-count">${section.commands.length} comandos</span>
        ${progressChip}
        <button type="button" class="detail-fav ${state.favs.has(section.slug) ? "on" : ""}" data-fav-detail title="Favorito">${state.favs.has(section.slug) ? "★ guardada" : "☆ guardar"}</button>
      </div>
      <h2>${escapeHtml(section.title)}</h2>
      <p>${escapeHtml(section.summary)}</p>
      <div class="tag-row">${section.tags.map((tag) => `<button type="button" data-tag="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`).join("")}</div>
    </header>
    <section class="detail-body">${commandsHtml(section)}${sectionBodyHtml(section)}</section>
  `;
  container.querySelectorAll("[data-tag]").forEach((button) => {
    button.addEventListener("click", () => {
      state.tag = button.dataset.tag;
      render();
    });
  });
  container.querySelector("[data-fav-detail]")?.addEventListener("click", () => {
    toggleFav(section.slug);
  });
  bindChecklist(section);
  bindCommandTools();
  bindSectionNav();
}

function checklistProgress(section) {
  let total = 0;
  let done = 0;
  section.blocks.forEach((block, index) => {
    if (block[0] !== "bullets") return;
    block[1].forEach((_item, itemIndex) => {
      total += 1;
      if (state.profile.checks[checkKey(section.slug, index, itemIndex)]) done += 1;
    });
  });
  return { total, done };
}

function bindChecklist(section) {
  const container = document.querySelector("[data-detail]");
  const chip = container.querySelector("[data-progress]");
  container.querySelectorAll("[data-check]").forEach((box) => {
    box.addEventListener("change", () => {
      const key = box.dataset.check;
      if (box.checked) state.profile.checks[key] = true;
      else delete state.profile.checks[key];
      box.closest(".check-item")?.classList.toggle("done", box.checked);
      saveProfile();
      if (chip) {
        const progress = checklistProgress(section);
        chip.innerHTML = `<b>${progress.done}</b>/${progress.total} hecho`;
      }
    });
  });
}

function bindCommandTools() {
  bindCommandToolsIn(document.querySelector("[data-detail]"));
}

function bindCommandToolsIn(container) {
  if (!container) return;
  container.querySelectorAll(".cmd").forEach((card) => {
    const editBtn = card.querySelector("[data-edit]");
    if (!editBtn || editBtn.dataset.bound) return;
    editBtn.dataset.bound = "1";
    const view = card.querySelector(".cmd-view");
    const wrap = card.querySelector(".cmd-edit-wrap");
    const input = card.querySelector(".cmd-input");
    const copyBtn = card.querySelector(".cmd-edit-copy");
    const open = () => {
      view.hidden = true;
      wrap.hidden = false;
      input.focus();
      input.select();
    };
    const close = () => {
      view.hidden = false;
      wrap.hidden = true;
    };
    editBtn.addEventListener("click", open);
    copyBtn.addEventListener("click", async () => {
      const ok = await copyText(input.value);
      if (!ok) return;
      copyBtn.textContent = "copiado";
      window.setTimeout(() => {
        copyBtn.textContent = "copiar";
        close();
      }, 900);
    });
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        copyBtn.click();
      } else if (event.key === "Escape") {
        event.preventDefault();
        close();
      }
    });
  });
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    area.remove();
    return ok;
  }
}

function bindCopyButtons() {
  document.querySelectorAll("[data-copy]").forEach((button) => {
    if (button.dataset.copyBound) return;
    button.dataset.copyBound = "1";
    button.addEventListener("click", async (event) => {
      event.stopPropagation();
      const ok = await copyText(button.dataset.copy);
      if (!ok) return;
      const label = button.querySelector(".copy-label") || button;
      const original = label.textContent;
      button.classList.add("copied");
      label.textContent = "copiado";
      window.setTimeout(() => {
        button.classList.remove("copied");
        label.textContent = original;
      }, 1100);
    });
  });
}

function writeHash(push) {
  const q = state.query ? `?q=${encodeURIComponent(state.query)}` : "";
  const target = state.activeSlug ? `#${state.activeSlug}${q}` : q ? `#${q}` : "#";
  if (location.hash === target) return;
  suppressHash = true;
  if (push) history.pushState(null, "", target);
  else history.replaceState(null, "", target);
  suppressHash = false;
}

function applyHashToState() {
  const raw = location.hash.replace(/^#/, "");
  if (!raw) return;
  const [slugPart, qs] = raw.split("?");
  const slug = decodeURIComponent(slugPart || "");
  const query = new URLSearchParams(qs || "").get("q") || "";
  state.query = query;
  const search = document.querySelector("[data-search]");
  if (search) search.value = query;
  if (slug) state.activeSlug = slug;
}

function loadFavs() {
  try {
    state.favs = new Set(JSON.parse(localStorage.getItem(FAVS_KEY) || "[]"));
  } catch {
    state.favs = new Set();
  }
  try {
    state.recent = JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
  } catch {
    state.recent = [];
  }
}

function saveFavs() {
  try {
    localStorage.setItem(FAVS_KEY, JSON.stringify([...state.favs]));
    localStorage.setItem(RECENT_KEY, JSON.stringify(state.recent));
  } catch {
    /* ignore */
  }
}

function toggleFav(slug) {
  if (!slug) return;
  if (state.favs.has(slug)) state.favs.delete(slug);
  else state.favs.add(slug);
  saveFavs();
  render();
}

function pushRecent(slug) {
  if (!slug) return;
  state.recent = [slug, ...state.recent.filter((item) => item !== slug)].slice(0, 6);
  saveFavs();
}

function renderRecent() {
  const row = document.querySelector("[data-recent]");
  if (!row) return;
  const show = state.mode === "sections" && !state.query && !state.favOnly && state.recent.length > 1;
  if (!show) {
    row.setAttribute("hidden", "");
    row.innerHTML = "";
    return;
  }
  const bySlug = new Map(state.data.sections.map((section) => [section.slug, section]));
  const chips = state.recent
    .map((slug) => bySlug.get(slug))
    .filter(Boolean)
    .slice(0, 6);
  if (!chips.length) {
    row.setAttribute("hidden", "");
    return;
  }
  row.removeAttribute("hidden");
  row.innerHTML =
    `<span class="recent-label">recientes</span>` +
    chips
      .map(
        (section) =>
          `<button type="button" class="recent-chip" style="${phaseStyle(section.phase)}" data-recent-slug="${escapeHtml(section.slug)}">${escapeHtml(section.title)}</button>`,
      )
      .join("");
  row.querySelectorAll("[data-recent-slug]").forEach((chip) => {
    chip.addEventListener("click", () => {
      state.activeSlug = chip.dataset.recentSlug;
      pushRecent(state.activeSlug);
      writeHash(true);
      render();
    });
  });
}

function loadProfile() {
  let stored = {};
  try {
    stored = JSON.parse(localStorage.getItem(PROFILE_KEY) || "{}") || {};
  } catch {
    stored = {};
  }
  const legacyIp = localStorage.getItem(LEGACY_IP_KEY);
  if (legacyIp && !stored.ip) stored.ip = legacyIp;
  return {
    ...BLANK_PROFILE,
    ...stored,
    checks: { ...(stored.checks || {}) },
  };
}

function saveProfile() {
  try {
    localStorage.setItem(PROFILE_KEY, JSON.stringify(state.profile));
  } catch {
    /* storage full or blocked: keep working in-memory */
  }
}

function applyProfile() {
  const p = state.profile;
  state.room = {
    ...buildRoomContext(p.ip),
    attacker: p.attacker.trim(),
    domain: p.domain.trim(),
    dcHost: p.dcHost.trim(),
    dcFqdn: p.dcFqdn.trim(),
    port: p.port.trim(),
    user: p.user.trim(),
    pass: p.pass.trim(),
  };
}

function setVars() {
  return ROOM_VARS.filter((v) => String(state.profile[v.key] || "").trim()).length;
}

function renderRoomBadge() {
  const badge = document.querySelector("[data-room-count]");
  if (!badge) return;
  const count = setVars();
  badge.textContent = count ? String(count) : "";
  badge.hidden = count === 0;
}

function renderVarsPanel() {
  const container = document.querySelector("[data-vars]");
  if (!container) return;
  container.innerHTML = ROOM_VARS.map(
    (v) => `<label class="var-field">
      <span class="var-label">${escapeHtml(v.label)}<b>${escapeHtml(v.token)}</b></span>
      <input type="text" spellcheck="false" autocomplete="off" data-var="${escapeHtml(v.key)}" placeholder="${escapeHtml(v.ph)}" value="${escapeHtml(state.profile[v.key] || "")}" />
    </label>`,
  ).join("");
  container.querySelectorAll("[data-var]").forEach((input) => {
    input.addEventListener("input", (event) => {
      state.profile[input.dataset.var] = event.target.value;
      saveProfile();
      applyProfile();
      renderRoomBadge();
      render();
    });
  });
}

function renderNotes() {
  const notes = document.querySelector("[data-notes]");
  if (!notes) return;
  if (document.activeElement !== notes) notes.value = state.profile.notes || "";
}

function resetRoom() {
  state.profile = { ...BLANK_PROFILE, checks: {} };
  saveProfile();
  applyProfile();
  const ipInput = document.querySelector("[data-room-ip]");
  if (ipInput) ipInput.value = "";
  const notes = document.querySelector("[data-notes]");
  if (notes) notes.value = "";
  renderVarsPanel();
  renderRoomBadge();
  render();
}

function bindRoomPanel() {
  const toggle = document.querySelector("[data-room-toggle]");
  const panel = document.querySelector("[data-roompanel]");
  if (toggle && panel) {
    toggle.addEventListener("click", () => {
      const open = panel.hasAttribute("hidden");
      if (open) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }
  const notes = document.querySelector("[data-notes]");
  if (notes) {
    notes.addEventListener("input", (event) => {
      state.profile.notes = event.target.value;
      saveProfile();
    });
  }
  const reset = document.querySelector("[data-reset-room]");
  if (reset) reset.addEventListener("click", resetRoom);

  const revType = document.querySelector("[data-rev-type]");
  if (revType) {
    revType.addEventListener("change", (event) => {
      state.profile.revType = event.target.value;
      saveProfile();
      renderRevshell();
    });
  }
  const revLport = document.querySelector("[data-rev-lport]");
  if (revLport) {
    revLport.addEventListener("input", (event) => {
      state.profile.revLport = event.target.value;
      saveProfile();
      renderRevshell();
    });
  }
}

function renderModeToggle() {
  const toggle = document.querySelector("[data-mode]");
  const hint = document.querySelector("[data-list-hint]");
  if (toggle) {
    toggle.querySelectorAll("button").forEach((button) => {
      button.classList.toggle("active", button.dataset.modeVal === state.mode);
    });
  }
  if (hint) {
    hint.textContent = state.mode === "commands" ? `${filterCommands().length} comandos` : "↑↓ navegar";
  }
}

// A learn command is either a plain string or {cmd, why, out}: why = por que /
// cuando usarlo, out = que detalles buscar en su salida.
function commandOf(command) {
  return typeof command === "string" ? command : command.cmd;
}

function commandText(command) {
  return typeof command === "string"
    ? command
    : [command.cmd, command.why, command.out].filter(Boolean).join(" ");
}

function annotatedCommandHtml(command, terms) {
  const card = commandCard(commandOf(command), { edit: true });
  if (typeof command === "string" || (!command.why && !command.out)) return card;
  const hl = (text) => highlight(escapeHtml(text), terms);
  const why = command.why ? `<p class="cmd-why"><b>Por que</b><span>${hl(command.why)}</span></p>` : "";
  const out = command.out ? `<p class="cmd-out"><b>En la salida busca</b><span>${hl(command.out)}</span></p>` : "";
  return `<div class="cmd-with-note">${card}<div class="cmd-annot">${why}${out}</div></div>`;
}

function guideStepHtml(step, index) {
  const terms = queryTerms();
  const hl = (text) => highlight(escapeHtml(text), terms);
  const cmds = (step.commands || []).map((command) => annotatedCommandHtml(command, terms)).join("");
  return `<article class="guide-step">
    <div class="guide-step-num">${index + 1}</div>
    <div class="guide-step-main">
      <h3>${hl(step.title)}</h3>
      <p class="guide-idea">${hl(step.idea)}</p>
      ${cmds ? `<div class="guide-cmds">${cmds}</div>` : ""}
      ${step.look ? `<p class="guide-note guide-look"><b>Que buscar</b><span>${hl(step.look)}</span></p>` : ""}
      ${step.decide ? `<p class="guide-note guide-decide"><b>Segun lo que veas</b><span>${hl(step.decide)}</span></p>` : ""}
    </div>
  </article>`;
}

function guideMatches(guide, terms) {
  if (!terms.length) return true;
  const hay = normalizeQuery(
    [
      guide.title,
      guide.summary,
      ...guide.steps.flatMap((step) => [step.title, step.idea, step.look, step.decide, ...(step.commands || []).map(commandText)]),
    ].join(" "),
  );
  return terms.every((term) => hay.includes(term));
}

function gotoSection(slug) {
  state.query = "";
  state.tag = "all";
  state.phase = "all";
  state.favOnly = false;
  const search = document.querySelector("[data-search]");
  if (search) search.value = "";
  setView("practica");
  state.activeSlug = slug;
  pushRecent(slug);
  writeHash(true);
  render();
  document.querySelector("[data-detail]")?.scrollIntoView({ block: "start" });
}

function renderLearn() {
  document.querySelectorAll("[data-learn-tabs] button").forEach((button) => {
    button.classList.toggle("active", button.dataset.learnVal === state.learnMode);
  });
  if (state.learnMode === "concepts") renderConcepts();
  else renderGuides();
}

function conceptById(id) {
  return state.concepts.find((concept) => concept.id === id);
}

// Turn prose with [[id]] links into HTML: escape + highlight plain runs, and
// resolve each [[id]] to a clickable concept link (falls back to plain text
// when the target does not exist yet).
function conceptProseHtml(text, terms) {
  if (!text) return "";
  const parts = String(text).split(/(\[\[[^\]]+\]\])/g);
  return parts
    .map((part) => {
      const match = /^\[\[([^\]]+)\]\]$/.exec(part);
      if (!match) return highlight(escapeHtml(part), terms);
      const target = conceptById(match[1].trim());
      const label = highlight(escapeHtml(target ? target.title : match[1].trim()), terms);
      if (!target) return label;
      return `<button type="button" class="concept-link" data-concept-link="${escapeHtml(target.id)}">${label}</button>`;
    })
    .join("");
}

function conceptMatches(concept, terms) {
  if (!terms.length) return true;
  const hay = normalizeQuery(
    [
      concept.title,
      concept.summary,
      concept.que,
      concept.porque,
      concept.cuando,
      ...(concept.senales || []),
      ...(concept.pasos || []),
      ...(concept.commands || []).map(commandText),
    ].join(" "),
  );
  return terms.every((term) => hay.includes(term));
}

function conceptPageHtml(concept, terms) {
  const prose = (text) => conceptProseHtml(text, terms);
  const cmds = (concept.commands || []).map((command) => annotatedCommandHtml(command, terms)).join("");
  const gotoBtn = concept.section
    ? `<button type="button" class="guide-goto" data-goto-section="${escapeHtml(concept.section)}">Ver comandos de esta fase &rarr;</button>`
    : "";
  const block = (title, body) => (body ? `<section class="concept-block"><h3>${title}</h3><p>${body}</p></section>` : "");
  const senales = (concept.senales || []).length
    ? `<section class="concept-block"><h3>Que senales lo delatan</h3><ul class="concept-signals">${concept.senales
        .map((item) => `<li>${prose(item)}</li>`)
        .join("")}</ul></section>`
    : "";
  const pasos = (concept.pasos || []).length
    ? `<section class="concept-block"><h3>Pasos</h3><ol class="concept-steps">${concept.pasos
        .map((item) => `<li>${prose(item)}</li>`)
        .join("")}</ol></section>`
    : "";
  const cmdBlock = cmds ? `<section class="concept-block"><h3>Comandos de ejemplo</h3><div class="guide-cmds">${cmds}</div></section>` : "";
  return `<header class="guide-head">
      <span class="detail-phase">${escapeHtml(phaseLabel(concept.phase))}</span>
      <h2>${highlight(escapeHtml(concept.title), terms)}</h2>
      <p>${prose(concept.summary)}</p>
      ${gotoBtn}
    </header>
    ${block("Que es", prose(concept.que))}
    ${block("Por que ocurre", prose(concept.porque))}
    ${block("Cuando aplica", prose(concept.cuando))}
    ${senales}
    ${pasos}
    ${cmdBlock}`;
}

function renderConcepts() {
  const listEl = document.querySelector("[data-guide-list]");
  const detailEl = document.querySelector("[data-guide-detail]");
  if (!listEl || !detailEl) return;
  if (!state.concepts.length) {
    listEl.innerHTML = "";
    detailEl.removeAttribute("style");
    detailEl.innerHTML = `<p class="list-empty">No hay conceptos disponibles.</p>`;
    return;
  }
  const terms = normalizeQuery(state.query).split(" ").filter(Boolean);
  const hlTerms = queryTerms();
  const matchIds = new Set(state.concepts.filter((concept) => conceptMatches(concept, terms)).map((c) => c.id));
  if (!matchIds.size) {
    listEl.innerHTML = `<p class="list-empty">Ningun concepto menciona "${escapeHtml(state.query)}".</p>`;
    detailEl.removeAttribute("style");
    detailEl.innerHTML = `<div class="empty"><span class="empty-mark">?</span><strong>Sin concepto para eso</strong><p>Cambia a <b>Practica</b> y busca ahi: tiene el comando concreto aunque no haya teoria.</p></div>`;
    return;
  }
  if (!matchIds.has(state.activeConcept)) {
    state.activeConcept = state.concepts.find((c) => matchIds.has(c.id)).id;
  }
  // Left index: concepts grouped under their ruta, in ruta order; only matches shown.
  const inPath = new Set();
  const groups = state.paths
    .map((path) => {
      const items = (path.concepts || []).map(conceptById).filter((c) => c && matchIds.has(c.id));
      items.forEach((c) => inPath.add(c.id));
      return { title: path.title, summary: path.summary, items };
    })
    .filter((group) => group.items.length);
  const orphans = state.concepts.filter((c) => matchIds.has(c.id) && !inPath.has(c.id));
  if (orphans.length) groups.push({ title: "Otros conceptos", summary: "", items: orphans });
  const itemBtn = (concept) => `<button type="button" class="concept-item ${state.activeConcept === concept.id ? "active" : ""}" style="${phaseStyle(concept.phase)}" data-concept="${escapeHtml(concept.id)}">
        <span class="guide-item-phase">${escapeHtml(phaseLabel(concept.phase))}</span>
        <strong>${highlight(escapeHtml(concept.title), hlTerms)}</strong>
        <span class="guide-item-sum">${highlight(escapeHtml(concept.summary), hlTerms)}</span>
      </button>`;
  listEl.innerHTML = groups
    .map(
      (group) => `<div class="concept-path">
        <h3 class="concept-path-title">${escapeHtml(group.title)}</h3>
        ${group.summary ? `<p class="concept-path-sum">${escapeHtml(group.summary)}</p>` : ""}
        ${group.items.map(itemBtn).join("")}
      </div>`,
    )
    .join("");
  listEl.querySelectorAll("[data-concept]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeConcept = button.dataset.concept;
      renderConcepts();
      detailEl.scrollIntoView({ block: "nearest" });
    });
  });
  const concept = conceptById(state.activeConcept);
  detailEl.setAttribute("style", phaseStyle(concept.phase));
  detailEl.innerHTML = conceptPageHtml(concept, hlTerms);
  detailEl.querySelector("[data-goto-section]")?.addEventListener("click", (event) => {
    gotoSection(event.currentTarget.dataset.gotoSection);
  });
  detailEl.querySelectorAll("[data-concept-link]").forEach((link) => {
    link.addEventListener("click", () => {
      state.activeConcept = link.dataset.conceptLink;
      renderConcepts();
      detailEl.scrollIntoView({ block: "start" });
    });
  });
  bindCommandToolsIn(detailEl);
  bindCopyButtons();
}

function renderGuides() {
  const listEl = document.querySelector("[data-guide-list]");
  const detailEl = document.querySelector("[data-guide-detail]");
  if (!listEl || !detailEl) return;
  if (!state.guides.length) {
    detailEl.innerHTML = `<p class="list-empty">No hay guias disponibles.</p>`;
    return;
  }
  const terms = normalizeQuery(state.query).split(" ").filter(Boolean);
  const matches = state.guides.filter((guide) => guideMatches(guide, terms));
  if (!matches.length) {
    listEl.innerHTML = `<p class="list-empty">Ninguna guia menciona "${escapeHtml(state.query)}".</p>`;
    detailEl.removeAttribute("style");
    detailEl.innerHTML = `<div class="empty"><span class="empty-mark">?</span><strong>Sin guia para eso</strong><p>Cambia a <b>Practica</b> y busca ahi: tiene el comando concreto aunque no haya guia teorica.</p></div>`;
    return;
  }
  if (!matches.some((guide) => guide.id === state.activeGuide)) {
    state.activeGuide = matches[0].id;
  }
  const hlTerms = queryTerms();
  listEl.innerHTML = matches
    .map(
      (guide) => `<button type="button" class="guide-item ${state.activeGuide === guide.id ? "active" : ""}" style="${phaseStyle(guide.phase)}" data-guide="${escapeHtml(guide.id)}">
        <span class="guide-item-phase">${escapeHtml(phaseLabel(guide.phase))}</span>
        <strong>${highlight(escapeHtml(guide.title), hlTerms)}</strong>
        <span class="guide-item-sum">${highlight(escapeHtml(guide.summary), hlTerms)}</span>
        <span class="guide-item-steps">${guide.steps.length} pasos</span>
      </button>`,
    )
    .join("");
  listEl.querySelectorAll("[data-guide]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeGuide = button.dataset.guide;
      renderLearn();
      detailEl.scrollIntoView({ block: "nearest" });
    });
  });
  const guide = state.guides.find((item) => item.id === state.activeGuide);
  detailEl.setAttribute("style", phaseStyle(guide.phase));
  const gotoBtn = guide.section
    ? `<button type="button" class="guide-goto" data-goto-section="${escapeHtml(guide.section)}">Ver todos los comandos de esta fase →</button>`
    : "";
  detailEl.innerHTML = `<header class="guide-head">
      <span class="detail-phase">${escapeHtml(phaseLabel(guide.phase))}</span>
      <h2>${escapeHtml(guide.title)}</h2>
      <p>${escapeHtml(guide.summary)}</p>
      ${gotoBtn}
    </header>
    <div class="guide-steps">${guide.steps.map((step, index) => guideStepHtml(step, index)).join("")}</div>`;
  detailEl.querySelector("[data-goto-section]")?.addEventListener("click", (event) => {
    gotoSection(event.currentTarget.dataset.gotoSection);
  });
  bindCommandToolsIn(detailEl);
  bindCopyButtons();
}

function setView(view) {
  state.view = view === "aprender" ? "aprender" : "practica";
  const isLearn = state.view === "aprender";
  const learn = document.querySelector("[data-learn]");
  const quickbar = document.querySelector(".quickbar");
  const workbench = document.querySelector(".workbench");
  if (learn) learn.hidden = !isLearn;
  if (quickbar) quickbar.hidden = isLearn;
  if (workbench) workbench.hidden = isLearn;
  document.querySelectorAll("[data-view-tabs] button").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewVal === state.view);
  });
  if (isLearn) renderLearn();
}

function bindViewTabs() {
  document.querySelectorAll("[data-view-tabs] button").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.viewVal));
  });
}

function bindLearnTabs() {
  document.querySelectorAll("[data-learn-tabs] button").forEach((button) => {
    button.addEventListener("click", () => {
      state.learnMode = button.dataset.learnVal === "concepts" ? "concepts" : "guides";
      renderLearn();
    });
  });
}

function render() {
  applyProfile();
  let sections = filterSections(state.data.sections, state);
  if (state.favOnly) sections = sections.filter((section) => state.favs.has(section.slug));
  state.visible = sections;
  if (!sections.some((section) => section.slug === state.activeSlug)) {
    state.activeSlug = sections[0]?.slug || "";
  }
  const active = sections.find((section) => section.slug === state.activeSlug);
  document.querySelector("[data-count]").textContent = String(sections.length);
  renderOptions(document.querySelector("[data-tags]"), state.data.tags, state.tag, (tag) => tag, (value) => {
    state.tag = value;
    render();
  });
  renderOptions(document.querySelector("[data-phases]"), state.data.phases, state.phase, phaseLabel, (value) => {
    state.phase = value;
    render();
  });
  renderModeToggle();
  renderRecent();
  const favBtn = document.querySelector("[data-fav-only]");
  if (favBtn) favBtn.classList.toggle("active", state.favOnly);
  if (state.mode === "commands") renderCommandResults();
  else renderResults(sections);
  if (!renderCommandSearchDetail()) renderDetail(active);
  renderRoomConfig();
  renderNotes();
  renderRoomBadge();
  renderRevshell();
  if (state.view === "aprender") renderLearn();
  bindCopyButtons();
}

function moveActive(delta) {
  if (state.mode !== "sections") return;
  const sections = state.visible;
  if (!sections.length) return;
  const current = sections.findIndex((section) => section.slug === state.activeSlug);
  const next = Math.max(0, Math.min(sections.length - 1, (current < 0 ? 0 : current) + delta));
  state.activeSlug = sections[next].slug;
  writeHash(false);
  render();
  const activeEl = document.querySelector(".result.active");
  if (activeEl) activeEl.scrollIntoView({ block: "nearest" });
}

function isTyping(target) {
  return target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.tagName === "SELECT");
}

function bindExplain() {
  // Capture phase so the "i" marker opens the modal before the copy handler fires.
  document.addEventListener(
    "click",
    (event) => {
      const trigger = event.target.closest?.("[data-explain]");
      if (!trigger) return;
      event.preventDefault();
      event.stopPropagation();
      openCmdModal(trigger.dataset.explain);
    },
    true,
  );
  document.addEventListener("keydown", (event) => {
    if ((event.key === "Enter" || event.key === " ") && event.target?.matches?.("[data-explain]")) {
      event.preventDefault();
      openCmdModal(event.target.dataset.explain);
    }
  });
}

function bindKeyboard() {
  const search = document.querySelector("[data-search]");
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      const modal = document.querySelector("[data-cmd-modal]");
      if (modal && !modal.hidden) {
        event.preventDefault();
        closeCmdModal();
        return;
      }
    }
    if ((event.key === "/" || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k")) && !isTyping(event.target)) {
      event.preventDefault();
      search.focus();
      search.select();
      return;
    }
    if (event.key === "Escape" && event.target === search) {
      if (search.value) {
        search.value = "";
        state.query = "";
        writeHash(false);
        if (state.view === "aprender") renderLearn();
        else render();
      } else {
        search.blur();
      }
      return;
    }
    if ((event.key === "ArrowDown" || event.key === "ArrowUp") && (!isTyping(event.target) || event.target === search)) {
      event.preventDefault();
      moveActive(event.key === "ArrowDown" ? 1 : -1);
    }
  });
}

function bindModeToggle() {
  const toggle = document.querySelector("[data-mode]");
  if (!toggle) return;
  toggle.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.modeVal;
      render();
    });
  });
}

function bindServiceWorkerUpdates() {
  if (!("serviceWorker" in navigator)) return;

  let refreshing = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (refreshing) return;
    refreshing = true;
    window.location.reload();
  });

  const activateWaitingWorker = (registration) => {
    if (!registration?.waiting) return;
    registration.waiting.postMessage({ type: "SKIP_WAITING" });
  };

  const watchRegistration = (registration) => {
    registration.addEventListener("updatefound", () => {
      const worker = registration.installing;
      if (!worker) return;
      worker.addEventListener("statechange", () => {
        if (worker.state === "installed" && navigator.serviceWorker.controller) {
          activateWaitingWorker(registration);
        }
      });
    });
    activateWaitingWorker(registration);
    registration.update().catch(() => {});
  };

  const registerSw = () => navigator.serviceWorker.register("./sw.js").then(watchRegistration).catch(() => {});
  if (document.readyState === "complete") registerSw();
  else window.addEventListener("load", registerSw, { once: true });
}

async function init() {
  const response = await fetch(`./data/content.json?v=${APP_VERSION}`);
  state.data = await response.json();
  try {
    const revResponse = await fetch(`./data/revshells.json?v=${APP_VERSION}`);
    const revData = await revResponse.json();
    REV_TEMPLATES = Array.isArray(revData.templates) ? revData.templates : [];
    STABILIZE = Array.isArray(revData.stabilize) ? revData.stabilize : [];
  } catch {
    REV_TEMPLATES = [];
    STABILIZE = [];
  }
  state.activeSlug = state.data.sections[0]?.slug || "";
  state.guides = Array.isArray(state.data.guides) ? state.data.guides : [];
  state.activeGuide = state.guides[0]?.id || "";
  state.concepts = Array.isArray(state.data.concepts) ? state.data.concepts : [];
  state.paths = Array.isArray(state.data.paths) ? state.data.paths : [];
  state.activeConcept = state.concepts[0]?.id || "";
  state.profile = loadProfile();
  applyProfile();
  loadFavs();
  state.commandIndex = state.data.sections.flatMap((section) =>
    section.commands.map((command) => ({ command, section })),
  );
  applyHashToState();
  pushRecent(state.activeSlug);
  document.querySelector("[data-total]").textContent = String(state.data.stats.totalSections);
  document.querySelector("[data-command-total]").textContent = String(state.data.stats.totalCommands);
  document.querySelector("[data-search]").addEventListener("input", (event) => {
    state.query = event.target.value;
    writeHash(false);
    if (state.view === "aprender") renderLearn();
    else render();
  });
  const ipInput = document.querySelector("[data-room-ip]");
  ipInput.value = state.profile.ip;
  ipInput.addEventListener("input", (event) => {
    state.profile.ip = event.target.value;
    saveProfile();
    applyProfile();
    render();
  });
  renderVarsPanel();
  bindRoomPanel();
  bindModeToggle();
  document.querySelector("[data-fav-only]")?.addEventListener("click", () => {
    state.favOnly = !state.favOnly;
    render();
  });
  renderShortcuts(state.data);
  bindKeyboard();
  bindExplain();
  bindViewTabs();
  bindLearnTabs();
  trackTopbarHeight();
  window.addEventListener("popstate", () => {
    applyHashToState();
    render();
  });
  render();
  bindServiceWorkerUpdates();
}

if (typeof document !== "undefined") {
  init().catch((error) => {
    document.body.innerHTML = `<main class="fatal"><h1>No se pudo cargar la base THM</h1><pre>${escapeHtml(error.message)}</pre></main>`;
  });
}
