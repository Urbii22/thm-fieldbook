import assert from "node:assert/strict";
import { applyProgressSuggestion, suggestProgress } from "./progress.mjs";

const suggestions = suggestProgress({ command: "nmap -sV", result: "ports" });
assert.ok(suggestions.some((s) => s.key === "recon"));
assert.equal(applyProgressSuggestion({}, suggestions[0]).applied, false);
assert.equal(applyProgressSuggestion({}, suggestions[0], { confirmed: true }).progress.recon, true);
console.log("progress ok");
