import assert from "node:assert/strict";
import { matchIntent, normalizeQuery } from "./intent-rules.mjs";

assert.equal(normalizeQuery("  SeImpersonatePrivilege  "), "seimpersonateprivilege");
for (const [query, intent] of [["tengo smb 445", "smb"], ["encontre user:pass", "credentials"], ["sudo -l NOPASSWD vim", "sudo-privesc"], ["web 403", "web-forbidden"], ["hash ntlm", "hash"], ["JWT session", "jwt"]]) {
  assert.equal(matchIntent(query).intent, intent, query);
}
