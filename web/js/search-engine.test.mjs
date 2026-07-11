import assert from "node:assert/strict";
import { parsePortQuery, search } from "./search-engine.mjs";

assert.deepEqual(parsePortQuery("port 445/tcp"), { port: 445, service: "SMB", known: true });
assert.equal(parsePortQuery("70000"), null);
const corpus = [
  { id: "pivot", title: "Pivoting 445", text: "tunnel" },
  { id: "smb", title: "SMB enumeration", service: "SMB", port: 445, intent: "smb" },
];
const result = search("445", corpus);
assert.equal(result.port.service, "SMB");
assert.equal(result.results[0].id, "smb");
