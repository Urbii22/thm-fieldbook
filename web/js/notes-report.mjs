const SECRET_KEYS = /pass(word)?|secret|token|api[_-]?key|private[_-]?key|hash/i;

export function redactSecrets(value, { replacement = "[REDACTED]" } = {}) {
  if (Array.isArray(value)) return value.map((item) => redactSecrets(item, { replacement }));
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, SECRET_KEYS.test(key) ? replacement : redactSecrets(item, { replacement })]));
}

export const NOTE_TEMPLATES = Object.freeze({
  hallazgo: "## Hallazgo\n- Host/servicio: {{host}}\n- Evidencia: {{resultado}}\n",
  credencial: "## Credencial\n- Usuario: {{usuario}}\n- Tipo: {{tipo}}\n- Valor: {{resultado}}\n",
  hostname: "## Hostname/dominio\n- Valor: {{resultado}}\n",
  flag: "## Flag\n- Host: {{host}}\n- Valor: {{resultado}}\n",
  comando: "## Comando\n```bash\n{{comando}}\n```\nResultado:\n{{resultado}}\n",
  hipotesis: "## Hipótesis\n{{resultado}}\n",
  siguiente: "## Siguiente paso\n{{resultado}}\n",
  root_cause: "## Root cause\n{{resultado}}\n",
});

export function insertNoteTemplate(notes = "", type = "hallazgo", fields = {}) {
  const template = NOTE_TEMPLATES[type] || NOTE_TEMPLATES.hallazgo;
  const timestamp = fields.timestamp === false ? "" : (fields.timestamp || new Date().toISOString());
  const rendered = template.replace(/{{(\w+)}}/g, (_, key) => String(fields[key] ?? "")).replace(/^\s+|\s+$/g, "");
  const prefix = timestamp ? `<!-- ${timestamp} -->\n` : "";
  const base = String(notes || "").replace(/\s+$/, "");
  return base ? `${base}\n\n${prefix}${rendered}\n` : `${prefix}${rendered}\n`;
}

export function createMarkdownReport(room, { redact = true, title } = {}) {
  const source = redact ? redactSecrets(room) : room || {};
  const name = title || source.name || "Room";
  const lines = [`# ${name}`, "", `- Target: ${source.targetIp || ""}`, `- Attacker: ${source.attackerIp || ""}`, `- Domain: ${source.domain || ""}`, "", "## Notes", "", source.notes || ""];
  return lines.join("\n").replace(/\n{3,}/g, "\n\n").trimEnd() + "\n";
}

export function createExportBundle(room, options = {}) {
  const safe = options.redact === false ? room : redactSecrets(room);
  return { txt: String(room?.notes || ""), md: createMarkdownReport(room, options), json: JSON.stringify(safe, null, 2) };
}
