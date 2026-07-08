import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  adaptCommand,
  buildRoomContext,
  filterCommandEntries,
  filterSections,
  getTopCommands,
  normalizeQuery,
  shouldRenderCodeBlock,
} from "./app.mjs";

const sections = [
  {
    title: "Web y APIs",
    summary: "IDOR, JWT y uploads",
    tags: ["web"],
    phase: "enumeration",
    commands: ["ffuf -u http://$IP/FUZZ", "curl -i http://$IP"],
    searchText: "Web y APIs IDOR JWT uploads ffuf curl",
  },
  {
    title: "Windows privesc",
    summary: "Servicios y registry",
    tags: ["windows"],
    phase: "privesc",
    commands: ["whoami /priv"],
    searchText: "Windows privesc servicios registry whoami priv",
  },
];

assert.equal(normalizeQuery("  Web   APIs  "), "web apis");
assert.equal(normalizeQuery("víctima máquina acción"), "victima maquina accion");

assert.deepEqual(
  filterSections(sections, { query: "jwt", tag: "all", phase: "all" }).map((section) => section.title),
  ["Web y APIs"],
);

assert.deepEqual(
  filterSections(sections, { query: "", tag: "windows", phase: "all" }).map((section) => section.title),
  ["Windows privesc"],
);

assert.deepEqual(
  filterSections(sections, { query: "", tag: "all", phase: "privesc" }).map((section) => section.title),
  ["Windows privesc"],
);

assert.deepEqual(getTopCommands(sections, 2), ["ffuf -u http://$IP/FUZZ", "curl -i http://$IP"]);

const commandIndex = sections.flatMap((section) => section.commands.map((command) => ({ command, section })));

assert.deepEqual(
  filterCommandEntries(commandIndex, "ffuf").map((entry) => entry.command),
  ["ffuf -u http://$IP/FUZZ"],
);

assert.deepEqual(
  filterCommandEntries(commandIndex, "curl ip").map((entry) => entry.command),
  ["curl -i http://$IP"],
);

assert.deepEqual(
  filterCommandEntries(
    [
      { command: "mkdir -p nmap web loot", section: sections[0] },
      { command: "nmap -sC -sV $IP", section: sections[0] },
    ],
    "nmap",
  ).map((entry) => entry.command),
  ["nmap -sC -sV $IP", "mkdir -p nmap web loot"],
);

assert.deepEqual(buildRoomContext(" 10.10.145.23 "), {
  ip: "10.10.145.23",
  url: "http://10.10.145.23",
});

assert.equal(adaptCommand("nmap -sC -sV $IP", { ip: "10.10.145.23", url: "http://10.10.145.23" }), "nmap -sC -sV 10.10.145.23");

assert.equal(
  adaptCommand("export IP=10.10.10.10 && curl -i $URL/", { ip: "10.10.145.23", url: "http://10.10.145.23" }),
  "export IP=10.10.145.23 && curl -i http://10.10.145.23/",
);

assert.equal(
  adaptCommand("export URL=http://target.local", { ip: "10.10.145.23", url: "http://10.10.145.23" }),
  "export URL=http://10.10.145.23",
);

assert.equal(
  adaptCommand('ffuf -u "$URL/" -H "Host: FUZZ.target.local"', { ip: "10.10.145.23", url: "http://10.10.145.23" }),
  'ffuf -u "http://10.10.145.23/" -H "Host: FUZZ.target.local"',
);

assert.equal(adaptCommand("echo ATTACKER_IP", { ip: "10.10.145.23", url: "http://10.10.145.23" }), "echo ATTACKER_IP");

assert.equal(
  shouldRenderCodeBlock(["curl -i $URL/", "whatweb -a 3 $URL"], { commands: ["curl -i $URL/", "whatweb -a 3 $URL"] }),
  false,
);

assert.equal(
  shouldRenderCodeBlock(["curl -i $URL/", "ffuf -u $URL/FUZZ"], { commands: ["curl -i $URL/"] }),
  true,
);

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const js = readFileSync(new URL("./app.mjs", import.meta.url), "utf8");
const sw = readFileSync(new URL("./sw.js", import.meta.url), "utf8");
const content = JSON.parse(readFileSync(new URL("./data/content.json", import.meta.url), "utf8"));
const contentCommandIndex = content.sections.flatMap((section) => section.commands.map((command) => ({ command, section })));

for (const query of ["jwt_tool", "certutil", "ligolo", "gobuster", "wfuzz"]) {
  assert.ok(
    filterCommandEntries(contentCommandIndex, query).length > 0,
    `Expected searchable command results for ${query}`,
  );
}

assert.equal(content.stats.totalGuides, content.guides.length);
assert.ok(content.guides.length >= 8);
for (const guide of content.guides) {
  assert.ok(guide.id);
  assert.ok(guide.title);
  assert.ok(guide.summary);
  assert.ok(guide.steps.length >= 3);
}

assert.equal(content.stats.totalConcepts, content.concepts.length);
assert.equal(content.stats.totalPaths, content.paths.length);
assert.ok(content.concepts.length >= 1);
const conceptIds = new Set(content.concepts.map((concept) => concept.id));
for (const concept of content.concepts) {
  assert.ok(concept.id);
  assert.ok(concept.title);
  assert.ok(concept.summary);
  assert.ok(concept.que);
  assert.ok(concept.section);
}
for (const path of content.paths) {
  assert.ok(path.id);
  assert.ok(path.title);
  assert.ok(Array.isArray(path.concepts) && path.concepts.length);
  for (const id of path.concepts) {
    assert.ok(conceptIds.has(id), `ruta ${path.id} referencia concepto inexistente: ${id}`);
  }
}

for (const asset of [html, js, sw]) {
  assert.match(asset, /20260708-rutas/);
}

assert.match(js, /registration\.update\(\)/);
assert.match(js, /controllerchange/);
assert.match(sw, /SKIP_WAITING/);

assert.match(html, /<h1\b[^>]*>/);
assert.doesNotMatch(`${html}\n${js}`, /Ã|Â|â[^\s<>"']*/);
