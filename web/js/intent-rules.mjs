/** Pure, deterministic intent detection for practical security-search queries. */
export function normalizeQuery(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\p{L}\p{N}:._/-]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const RULES = [
  { intent: "smb", phase: "recon", terms: ["smb", "445", "smbclient", "smbmap", "enum4linux", "netexec", "nxc"], reason: "SMB/445 detectado" },
  { intent: "credentials", phase: "access", terms: ["user:pass", "usuario:contrasena", "credenciales", "password", "passwd", "credential"], reason: "posible credencial encontrada" },
  { intent: "linux-shell", phase: "post-exploitation", terms: ["shell linux", "www-data", "reverse shell", "revshell", "shell"], reason: "shell Linux detectada" },
  { intent: "sudo-privesc", phase: "privesc", terms: ["nopasswd", "sudo -l", "sudo", "vim", "gtfobins"], reason: "entrada sudo/privesc detectada" },
  { intent: "web-forbidden", phase: "web", terms: ["web 403", "403", "forbidden", "access denied"], reason: "respuesta web prohibida/denegada" },
  { intent: "hash", phase: "access", terms: ["hash ntlm", "ntlm", "hash", "hashcat", "john"], reason: "hash NTLM/cracking detectado" },
  { intent: "windows-privesc", phase: "privesc", terms: ["seimpersonateprivilege", "seimpersonate", "potato", "windows privesc"], reason: "privilegio Windows explotable detectado" },
  { intent: "jwt", phase: "web", terms: ["jwt", "json web token", "jku", "hs256"], reason: "token JWT detectado" },
  { intent: "graphql", phase: "web", terms: ["graphql", "introspection", "mutation"], reason: "API GraphQL detectada" },
];

export const INTENT_RULES = Object.freeze(RULES.map((rule) => Object.freeze({ ...rule, terms: Object.freeze([...rule.terms]) })));

export function matchIntent(value) {
  const query = normalizeQuery(value);
  if (!query) return { intent: null, phase: null, confidence: 0, signals: [], reason: null, query };
  const matches = RULES.map((rule) => {
    const signals = rule.terms.filter((term) => query.includes(term));
    return { rule, signals };
  }).filter(({ signals }) => signals.length);
  matches.sort((a, b) => b.signals.length - a.signals.length || RULES.indexOf(a.rule) - RULES.indexOf(b.rule));
  if (!matches.length) return { intent: null, phase: null, confidence: 0, signals: [], reason: null, query };
  const { rule, signals } = matches[0];
  return { intent: rule.intent, phase: rule.phase, confidence: Math.min(1, 0.55 + signals.length * 0.15), signals, reason: rule.reason, query };
}

export const detectIntent = matchIntent;
