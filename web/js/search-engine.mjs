import { matchIntent, normalizeQuery } from "./intent-rules.mjs";
import { rankResults } from "./search-ranking.mjs";

export { matchIntent, normalizeQuery, rankResults };

export const PORT_SERVICES = Object.freeze({ 21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 88: "Kerberos", 139: "NetBIOS", 1433: "MSSQL", 3306: "MySQL", 389: "LDAP", 443: "HTTPS", 445: "SMB", 5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP" });

export function parsePortQuery(value) {
  const query = normalizeQuery(value);
  const match = query.match(/^(?:(?:port|puerto)\s*)?(\d{1,5})(?:\/(?:tcp|udp))?$/);
  if (!match) return null;
  const port = Number(match[1]);
  if (port < 1 || port > 65535) return null;
  return { port, service: PORT_SERVICES[port] || null, known: Boolean(PORT_SERVICES[port]) };
}

export function search(query, corpus = [], options = {}) {
  const normalized = normalizeQuery(query);
  const intent = matchIntent(normalized);
  const port = parsePortQuery(normalized) || normalized.match(/\b(?:port|puerto)?\s*(\d{1,5})\b/)?.[1] && parsePortQuery(normalized.match(/\b\d{1,5}\b/)[0]);
  const context = { query: normalized, intent: intent.intent, phase: intent.phase, port: port?.port };
  const results = Array.isArray(corpus) ? corpus : [];
  const matched = results.filter((result) => {
    if (!normalized) return true;
    const hay = normalizeQuery([result.title, result.summary, result.text, result.description, result.command, result.service, result.slug].filter(Boolean).join(" "));
    return normalized.split(" ").filter(Boolean).some((term) => hay.includes(term)) || (intent.intent && result.intent === intent.intent) || (port && String(result.port) === String(port.port));
  });
  return { query: normalized, intent, port, results: rankResults(matched, context) };
}

export const searchResults = search;
