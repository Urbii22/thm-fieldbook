const SECRET_KEYS = /pass(word)?|secret|token|api[_-]?key|private[_-]?key|hash/i;
const SECRET_NOTE_LINE = /^(\s*(?:[-*]\s*)?(?:valor|password|pass|passwd|secret|token|api[_-]?key|private[_-]?key|hash)\s*:\s*).+$/gim;
const BEARER_TOKEN = /(authorization\s*:\s*bearer\s+)[^\s]+/gi;

export function redactSecrets(value, { replacement = "[REDACTED]" } = {}) {
  if (Array.isArray(value)) return value.map((item) => redactSecrets(item, { replacement }));
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, SECRET_KEYS.test(key) ? replacement : redactSecrets(item, { replacement })]));
}

export function redactNoteSecrets(value, { replacement = "[REDACTED]" } = {}) {
  return String(value || "")
    .replace(SECRET_NOTE_LINE, `$1${replacement}`)
    .replace(BEARER_TOKEN, `$1${replacement}`);
}

export const NOTE_TEMPLATES = Object.freeze({
  hallazgo: [
    "### [F-01] Titulo del hallazgo",
    "- Severidad: Pendiente (CVSS v4.0)",
    "- Activo/servicio: {{host}}",
    "- Estado: Confirmado / Pendiente de validar",
    "",
    "#### Resumen",
    "Describe brevemente la condicion vulnerable.",
    "",
    "#### Causa raiz",
    "Explica que control falta o esta mal configurado.",
    "",
    "#### Evidencia",
    "{{resultado}}",
    "",
    "#### Reproduccion",
    "1. Precondicion.",
    "2. Accion minima.",
    "3. Resultado observado.",
    "",
    "#### Impacto",
    "Explica que puede conseguir un atacante y sobre que activos o datos.",
    "",
    "#### Mitigacion",
    "Indica una correccion concreta y priorizada.",
    "",
    "#### Retest",
    "Describe la prueba que demostrara que la correccion funciona.",
  ].join("\n"),
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
  const notes = redact ? redactNoteSecrets(source.notes) : String(source.notes || "");
  const created = String(source.createdAt || "").slice(0, 10);
  const updated = String(source.updatedAt || "").slice(0, 10);
  const cell = (value) => String(value || "Pendiente").replace(/\|/g, "\\|").replace(/\r?\n/g, " ");
  const lines = [
    `# Informe de pentest - ${name}`,
    "",
    "> Documento de trabajo. Sustituye los textos pendientes y revisa que no contenga secretos antes de entregarlo.",
    "",
    "## 1. Control del documento",
    "",
    "| Campo | Valor |",
    "| --- | --- |",
    `| Proyecto | ${cell(name)} |`,
    `| Fecha de inicio | ${cell(created)} |`,
    `| Ultima actualizacion | ${cell(updated)} |`,
    "| Autor | Pendiente |",
    "| Clasificacion | Confidencial |",
    "",
    "## 2. Resumen ejecutivo",
    "",
    "Resume en lenguaje no tecnico el objetivo, el nivel de riesgo general, la cadena de ataque mas importante y las acciones prioritarias.",
    "",
    "## 3. Alcance y Rules of Engagement",
    "",
    "| Campo | Valor |",
    "| --- | --- |",
    `| Objetivo principal | ${cell(source.targetIp)} |`,
    `| Dominio | ${cell(source.domain)} |`,
    `| Puertos/servicios observados | ${cell(source.ports)} |`,
    "| Activos excluidos | Pendiente |",
    "| Tecnicas restringidas | Pendiente |",
    "| Criterio de parada/contacto | Pendiente |",
    "",
    "## 4. Metodologia y limitaciones",
    "",
    "Describe reconocimiento, enumeracion, explotacion, post-explotacion y cierre. Registra limitaciones de tiempo, acceso o visibilidad que afecten a las conclusiones.",
    "",
    "## 5. Cadena de ataque",
    "",
    "1. Punto de entrada.",
    "2. Acceso inicial.",
    "3. Escalada o movimiento lateral.",
    "4. Impacto demostrado.",
    "",
    "## 6. Resumen de hallazgos",
    "",
    "| ID | Hallazgo | Severidad | CVSS v4.0 | Activo | Estado |",
    "| --- | --- | --- | --- | --- | --- |",
    "| F-01 | Pendiente | Pendiente | Pendiente | Pendiente | Confirmado |",
    "",
    "## 7. Hallazgos detallados",
    "",
    notes || "### [F-01] Titulo del hallazgo\n\nCompleta resumen, evidencia, reproduccion, impacto, causa raiz, mitigacion y retest.",
    "",
    "## 8. Evidencias y anexos",
    "",
    "Relaciona cada captura, request, output o fichero con su hallazgo. Evita incluir credenciales y datos que no sean necesarios.",
    "",
    "## 9. Limpieza y estado final",
    "",
    "Lista cuentas, claves, tareas, servicios, binarios y ficheros creados durante las pruebas, junto con su estado de retirada. No borres logs defensivos.",
    "",
    "## 10. Recomendaciones priorizadas",
    "",
    "1. Correcciones inmediatas que rompen la cadena de ataque.",
    "2. Controles a corto plazo.",
    "3. Mejoras estructurales y verificacion mediante retest.",
    "",
    "## 11. Conclusion",
    "",
    "Resume el riesgo residual, las causas raiz repetidas y el siguiente paso recomendado.",
    "",
    "## 12. QA antes de entregar",
    "",
    "- [ ] Cada afirmacion importante tiene evidencia.",
    "- [ ] Cada hallazgo incluye causa, reproduccion, impacto, mitigacion y retest.",
    "- [ ] Severidad tecnica y riesgo contextual estan justificados por separado.",
    "- [ ] No quedan passwords, tokens, hashes o claves privadas innecesarias.",
    "- [ ] Los activos pertenecen al alcance y la limpieza esta verificada.",
    "- [ ] Un tercero puede reproducir los pasos minimos.",
  ];
  return lines.join("\n").replace(/\n{3,}/g, "\n\n").trimEnd() + "\n";
}

export function createExportBundle(room, options = {}) {
  const safe = options.redact === false ? room : redactSecrets(room);
  return { txt: String(room?.notes || ""), md: createMarkdownReport(room, options), json: JSON.stringify(safe, null, 2) };
}
