import assert from "node:assert/strict";
import { createMarkdownReport, insertNoteTemplate, redactNoteSecrets, redactSecrets } from "./notes-report.mjs";

assert.equal(redactSecrets({ password: "secret", notes: "ok" }).password, "[REDACTED]");
assert.doesNotMatch(createMarkdownReport({ name: "R", pass: "dont-export-this", notes: "ok" }), /dont-export-this/);
assert.match(insertNoteTemplate("", "comando", { comando: "id", resultado: "uid=0", timestamp: false }), /```bash/);
const finding = insertNoteTemplate("", "hallazgo", { host: "10.10.10.10:443", resultado: "403 esperado, 200 observado", timestamp: false });
assert.match(finding, /\[F-01\]/);
assert.match(finding, /Impacto/);
assert.match(finding, /Mitigacion/);
assert.match(finding, /Causa raiz/);
assert.match(finding, /Retest/);
assert.equal(redactNoteSecrets("- Valor: supersecret\nAuthorization: Bearer abc.def"), "- Valor: [REDACTED]\nAuthorization: Bearer [REDACTED]");
const report = createMarkdownReport({
  name: "PT1 lab",
  targetIp: "10.10.10.10",
  domain: "lab.local",
  ports: "80,443",
  notes: "### [F-01] IDOR\n- Valor: secret-token",
  createdAt: "2026-07-13T10:00:00Z",
  updatedAt: "2026-07-13T12:00:00Z",
});
for (const heading of ["Resumen ejecutivo", "Alcance y Rules of Engagement", "Cadena de ataque", "Resumen de hallazgos", "Limpieza y estado final", "Recomendaciones priorizadas", "QA antes de entregar"]) {
  assert.match(report, new RegExp(heading));
}
assert.match(report, /10\.10\.10\.10/);
assert.match(report, /lab\.local/);
assert.doesNotMatch(report, /secret-token/);
console.log("notes-report ok");
