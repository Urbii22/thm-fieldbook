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
};

const PROFILE_KEY = "thm-room";
const LEGACY_IP_KEY = "thm-room-ip";
const FAVS_KEY = "thm-favs";
const RECENT_KEY = "thm-recent";
let suppressHash = false;

// Shell-payload templates are loaded from ./data/revshells.json at runtime.
let REV_TEMPLATES = [];

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
  rce: ["exploit", "poc", "cve", "payload"],
  cve: ["exploit", "poc", "rce", "payload"],
  wordpress: ["wpscan", "wp-login", "wp"],
  sqli: ["sqlmap", "union", "injection", "inyeccion"],
  linux: ["suid", "sudo", "cron", "gtfobins", "linpeas"],
  windows: ["winpeas", "powershell", "servicios", "registry", "winrm"],
};

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
  "-Pn": "omite el ping de descubrimiento",
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

function explainCommand(raw) {
  const lower = String(raw).toLowerCase();
  const tokens = lower.split(/\s+/);
  const out = [];
  for (const [key, desc] of Object.entries(FLAG_HELP)) {
    let hit = false;
    if (key.includes(" ")) hit = lower.includes(key);
    else if (key.endsWith("-") && key.length > 2) hit = lower.includes(key);
    else if (key.startsWith("-")) hit = tokens.includes(key);
    else hit = tokens.some((token) => token === key || token.startsWith(`${key}`));
    if (hit) out.push({ token: key, desc });
    if (out.length >= 6) break;
  }
  return out;
}

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

function commandCard(rawCommand, opts = {}) {
  const command = adaptCommand(rawCommand, state.room);
  const esc = escapeHtml(command);
  const risk = detectRisk(rawCommand);
  const help = explainCommand(rawCommand);
  const riskMark = risk
    ? `<span class="risk-badge risk-${risk.level}" title="${escapeHtml(risk.reason)}" aria-label="${escapeHtml(risk.reason)}">${risk.level === "danger" ? "⚠" : "📡"}</span>`
    : "";
  const infoMark = help.length
    ? `<span class="cmd-info" tabindex="0" title="${escapeHtml(help.map((h) => `${h.token} — ${h.desc}`).join("\n"))}">i</span>`
    : "";
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
  const command = buildRevshell(state.profile.revType || REV_TEMPLATES[0].id, lhost, lport);
  out.innerHTML = commandCard(command, { edit: true });
  if (listenerOut) listenerOut.innerHTML = commandCard(`nc -lvnp ${lport}`, {});
  bindCommandToolsIn(document.querySelector(".revshell-block"));
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
  if (!sections.length) {
    container.innerHTML = `<p class="list-empty">Sin coincidencias. Cambia fase, tema o termino.</p>`;
    return;
  }
  const terms = queryTerms();
  container.innerHTML = sections
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

function filterCommands(limit = 80) {
  const terms = normalizeQuery(state.query).split(" ").filter(Boolean);
  const scored = [];
  for (const entry of state.commandIndex) {
    const hay = normalizeQuery(entry.command);
    let score = terms.length ? 0 : 1;
    let ok = true;
    for (const term of terms) {
      if (hay.includes(term)) score += 2;
      else {
        ok = false;
        break;
      }
    }
    if (ok && score > 0) scored.push({ entry, score });
  }
  return scored.slice(0, limit).map((item) => item.entry);
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
      const help = explainCommand(entry.command);
      const riskMark = risk
        ? `<span class="risk-badge risk-${risk.level}" title="${escapeHtml(risk.reason)}">${risk.level === "danger" ? "⚠" : "📡"}</span>`
        : "";
      const infoMark = help.length
        ? `<span class="cmd-info" tabindex="0" title="${escapeHtml(help.map((h) => `${h.token} — ${h.desc}`).join("\n"))}">i</span>`
        : "";
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

function commandsHtml(section) {
  const rawCommands = section.commands.slice(0, 8);
  if (!rawCommands.length) return "";
  const commands = rawCommands.map((command) => adaptCommand(command, state.room));
  const helper = state.room.ip
    ? `Adaptados a <b>${escapeHtml(state.room.ip)}</b>.`
    : "Fija la IP de la room arriba para autocompletar <b>$IP</b> / <b>$URL</b>.";
  const allCommands = escapeHtml(commands.join("\n"));
  const terms = queryTerms();
  return `<section class="command-shelf" aria-label="Comandos de esta seccion">
    <div class="command-shelf-head">
      <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
      <h3>comandos · ${rawCommands.length}/${section.commands.length}</h3>
      <button type="button" class="copy-all" data-copy="${allCommands}" title="Copiar todos">${COPY_ICON}<span class="copy-label">copiar todo</span></button>
    </div>
    <p class="command-hint">${helper}</p>
    <div class="command-grid">${rawCommands.map((command) => commandCard(command, { edit: true, terms })).join("")}</div>
  </section>`;
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
    <section class="detail-body">${commandsHtml(section)}${section.blocks
      .map((block, index) => blockHtml(block, { slug: section.slug, index }))
      .join("")}</section>
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
  renderDetail(active);
  renderRoomConfig();
  renderNotes();
  renderRoomBadge();
  renderRevshell();
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

function bindKeyboard() {
  const search = document.querySelector("[data-search]");
  document.addEventListener("keydown", (event) => {
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
        render();
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

async function init() {
  const response = await fetch("./data/content.json");
  state.data = await response.json();
  try {
    const revResponse = await fetch("./data/revshells.json");
    const revData = await revResponse.json();
    REV_TEMPLATES = Array.isArray(revData.templates) ? revData.templates : [];
  } catch {
    REV_TEMPLATES = [];
  }
  state.activeSlug = state.data.sections[0]?.slug || "";
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
    render();
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
  window.addEventListener("popstate", () => {
    applyHashToState();
    render();
  });
  render();
  if ("serviceWorker" in navigator) {
    const registerSw = () => navigator.serviceWorker.register("./sw.js").catch(() => {});
    if (document.readyState === "complete") registerSw();
    else window.addEventListener("load", registerSw, { once: true });
  }
}

if (typeof document !== "undefined") {
  init().catch((error) => {
    document.body.innerHTML = `<main class="fatal"><h1>No se pudo cargar la base THM</h1><pre>${escapeHtml(error.message)}</pre></main>`;
  });
}
