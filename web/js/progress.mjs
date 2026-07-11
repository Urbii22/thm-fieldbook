const RULES = [
  { key: "recon", terms: /\b(nmap|scan|recon|puertos?|enumerat)/i, label: "Marcar reconocimiento/puertos" },
  { key: "credential", terms: /\b(credencial|password|passwd|usuario|hash|login)/i, label: "Marcar credenciales" },
  { key: "shell", terms: /\b(shell|reverse shell|revshell|pty|tty)/i, label: "Marcar shell conseguida" },
  { key: "root", terms: /\b(flag|root|pwned|user\.txt|root\.txt)/i, label: "Marcar flag/root" },
];

export function suggestProgress(event = {}) {
  const text = typeof event === "string" ? event : [event.command, event.text, event.result, event.type].filter(Boolean).join(" ");
  return RULES.filter((rule) => rule.terms.test(text)).map(({ key, label }) => ({ key, label, confirmRequired: true }));
}

export const getProgressSuggestions = suggestProgress;

export function applyProgressSuggestion(progress = {}, suggestion, { confirmed = false } = {}) {
  if (!confirmed) return { progress: { ...progress }, applied: false, requiresConfirmation: true };
  const key = typeof suggestion === "string" ? suggestion : suggestion?.key;
  if (!key || !RULES.some((rule) => rule.key === key)) return { progress: { ...progress }, applied: false, requiresConfirmation: false };
  return { progress: { ...progress, [key]: true }, applied: true, requiresConfirmation: false };
}

export function confirmProgress(progress, suggestion) {
  return applyProgressSuggestion(progress, suggestion, { confirmed: true }).progress;
}
