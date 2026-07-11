import assert from "node:assert/strict";
import { createRoomStore, validateImport } from "./room-store.mjs";

const data = new Map([[
  "thm-room",
  JSON.stringify({ ip: "10.0.0.1", notes: "keep", checks: { 0: true }, progress: { recon: true } }),
]]);
const storage = { getItem: (k) => data.get(k) ?? null, setItem: (k, v) => data.set(k, v), removeItem: (k) => data.delete(k) };
const store = createRoomStore({ storage });
const migrated = store.migrate();
assert.equal(migrated.targetIp, "10.0.0.1");
assert.equal(migrated.checks[0], true);
assert.equal(migrated.progress.recon, true);
assert.ok(data.has("thm-room"));
assert.throws(() => validateImport('{"version":99,"rooms":[]}'));
console.log("room-store ok");
