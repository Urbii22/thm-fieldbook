import { normalizeQuery } from "./intent-rules.mjs";

const IP_RE = /\b(?:\d{1,3}\.){3}\d{1,3}\b/g;
const PLACEHOLDER_RE = /\$(?:IP|URL|PORT|USER|PASS)|<[^>]+>/gi;

export function resultText(result) {
  return normalizeQuery([result.title, result.summary, result.text, result.description, result.command, result.service, result.slug].filter(Boolean).join(" "));
}

export function scoreResult(result, context = {}) {
  const query = normalizeQuery(context.query);
  const terms = query.split(" ").filter(Boolean);
  const hay = resultText(result);
  let score = Number(result.score) || 0;
  for (const term of terms) {
    if (String(result.port ?? "") === term) score += 100;
    else if (normalizeQuery(result.service).includes(term)) score += 35;
    else if (normalizeQuery(result.title).includes(term)) score += 25;
    else if (hay.includes(term)) score += 8;
  }
  if (context.intent && result.intent === context.intent) score += 45;
  if (context.phase && result.phase === context.phase) score += 8;
  if (context.port != null && String(result.port) === String(context.port)) score += 90;
  if (IP_RE.test(String(result.command || result.text || ""))) score -= 12;
  IP_RE.lastIndex = 0;
  if (terms.length && terms.every((term) => PLACEHOLDER_RE.test(term))) score -= 8;
  PLACEHOLDER_RE.lastIndex = 0;
  return score;
}

export function dedupeResults(results) {
  const seen = new Set();
  return results.filter((result) => {
    const key = result.id ?? `${result.type || ""}|${normalizeQuery(result.title || result.command || result.text || "")}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export function rankResults(results, context = {}) {
  return dedupeResults(results.map((result, index) => ({ ...result, score: scoreResult(result, context), _index: index })))
    .sort((a, b) => b.score - a.score || (a._index - b._index))
    .map(({ _index, ...result }) => result);
}
