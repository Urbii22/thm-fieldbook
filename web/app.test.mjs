import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  adaptCommand,
  buildRoomContext,
  commandOf,
  commandText,
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

// Learn commands are string | {cmd, why, out}; the renderer and search rely on
// commandOf/commandText normalizing both shapes.
assert.equal(commandOf("nmap -sV $IP"), "nmap -sV $IP");
assert.equal(commandOf({ cmd: "id", why: "quien soy", out: "uid" }), "id");
assert.equal(commandText("nmap -sV $IP"), "nmap -sV $IP");
assert.equal(commandText({ cmd: "id", why: "quien soy", out: "uid=0" }), "id quien soy uid=0");
assert.equal(commandText({ cmd: "id" }), "id");

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

// ---- Concept wiki integrity (guards against future content-authoring breaks) ----
const KNOWN_PHASES = new Set(["access", "closeout", "enumeration", "pivot", "privesc", "recon", "reference"]);
const sectionSlugs = new Set(content.sections.map((section) => section.slug));

const isValidCommand = (command) =>
  typeof command === "string"
    ? command.length > 0
    : Boolean(command && typeof command.cmd === "string" && command.cmd.length > 0);

assert.equal(content.stats.totalConcepts, content.concepts.length);
assert.equal(content.stats.totalPaths, content.paths.length);
assert.ok(content.concepts.length >= 1);

const conceptIds = new Set();
for (const concept of content.concepts) {
  assert.ok(concept.id, "concepto sin id");
  assert.ok(!conceptIds.has(concept.id), `id de concepto duplicado: ${concept.id}`);
  conceptIds.add(concept.id);
  for (const field of ["title", "summary", "que", "porque", "cuando", "section", "phase"]) {
    assert.ok(concept[field], `concepto ${concept.id} sin ${field}`);
  }
  assert.ok(Array.isArray(concept.senales) && concept.senales.length, `concepto ${concept.id} sin senales`);
  assert.ok(Array.isArray(concept.pasos) && concept.pasos.length, `concepto ${concept.id} sin pasos`);
  if (concept.necesitas !== undefined) {
    assert.ok(Array.isArray(concept.necesitas) && concept.necesitas.length, `concepto ${concept.id} con necesitas vacio`);
    for (const item of concept.necesitas) {
      assert.ok(typeof item === "string" && item.length, `concepto ${concept.id} con item de necesitas invalido`);
    }
  }
  assert.ok(KNOWN_PHASES.has(concept.phase), `concepto ${concept.id} con phase invalida: ${concept.phase}`);
  assert.ok(sectionSlugs.has(concept.section), `concepto ${concept.id} apunta a seccion inexistente: ${concept.section}`);
  for (const command of concept.commands || []) {
    assert.ok(isValidCommand(command), `concepto ${concept.id} con comando invalido`);
  }
}

// Every [[link]] in concept prose must resolve to an existing concept.
for (const concept of content.concepts) {
  const prose = [concept.summary, concept.que, concept.porque, concept.cuando, ...(concept.senales || []), ...(concept.pasos || [])].join(" ");
  for (const match of prose.matchAll(/\[\[([^\]]+)\]\]/g)) {
    const target = match[1].trim();
    assert.ok(conceptIds.has(target), `concepto ${concept.id} enlaza a [[${target}]] inexistente`);
  }
}

const pathIds = new Set();
const conceptsInPaths = new Set();
for (const path of content.paths) {
  assert.ok(path.id, "ruta sin id");
  assert.ok(!pathIds.has(path.id), `id de ruta duplicado: ${path.id}`);
  pathIds.add(path.id);
  assert.ok(path.title);
  assert.ok(Array.isArray(path.concepts) && path.concepts.length);
  for (const id of path.concepts) {
    assert.ok(conceptIds.has(id), `ruta ${path.id} referencia concepto inexistente: ${id}`);
    conceptsInPaths.add(id);
  }
}

// Every concept must belong to at least one ruta, or it is unreachable from
// the guided "Conceptos relacionados" / ruta-stepper navigation.
for (const concept of content.concepts) {
  assert.ok(conceptsInPaths.has(concept.id), `concepto huerfano (sin ruta): ${concept.id}`);
}

// Guides share the same command shape; validate it too, plus that guide.section
// points at a real practice section.
for (const guide of content.guides) {
  assert.ok(sectionSlugs.has(guide.section), `guia ${guide.id} apunta a seccion inexistente: ${guide.section}`);
  for (const step of guide.steps) {
    for (const command of step.commands || []) {
      assert.ok(isValidCommand(command), `guia ${guide.id} con comando invalido`);
    }
  }
}

for (const asset of [html, js, sw]) {
  assert.match(asset, /20260709-review-fixes/);
}

assert.match(js, /registration\.update\(\)/);
assert.match(js, /controllerchange/);
assert.match(sw, /SKIP_WAITING/);

assert.match(html, /<h1\b[^>]*>/);

// Mojibake guard across every shipped text asset (UTF-8 accidentally re-encoded
// shows up as these Latin-1 lead bytes). Keeps "vÃ­ctima / â˜…"-style breakage out.
const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const contentRaw = readFileSync(new URL("./data/content.json", import.meta.url), "utf8");
for (const [name, text] of [["index.html", html], ["app.mjs", js], ["sw.js", sw], ["styles.css", css], ["content.json", contentRaw]]) {
  assert.doesNotMatch(text, /Ã[\x80-\xbf]|Â[\x80-\xbf]|â€|â†|â˜|ï¿½/, `mojibake en ${name}`);
}
