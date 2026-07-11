import assert from "node:assert/strict";
import { createMarkdownReport, insertNoteTemplate, redactSecrets } from "./notes-report.mjs";

assert.equal(redactSecrets({ password: "secret", notes: "ok" }).password, "[REDACTED]");
assert.doesNotMatch(createMarkdownReport({ name: "R", pass: "secret", notes: "ok" }), /secret/);
assert.match(insertNoteTemplate("", "comando", { comando: "id", resultado: "uid=0", timestamp: false }), /```bash/);
console.log("notes-report ok");
