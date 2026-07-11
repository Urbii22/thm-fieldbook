import assert from "node:assert/strict";
import { dedupeResults, rankResults } from "./search-ranking.mjs";

assert.equal(dedupeResults([{ id: "x" }, { id: "x" }]).length, 1);
const ranked = rankResults([
  { id: "generic", title: "Pivoting", text: "445 tunnel" },
  { id: "smb", title: "SMB", service: "SMB", port: 445 },
], { query: "445", port: 445, intent: "smb" });
assert.equal(ranked[0].id, "smb");
