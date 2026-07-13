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
  resolveSlug,
  shouldRenderCodeBlock,
  SLUG_REDIRECTS,
  PORT_DB,
  lookupPort,
  appendToNotes,
  describeCommand,
  commandExplanationFor,
  getPracticeDensityState,
  studyPromptsFor,
} from "./app.mjs";

// ---- Bloc de notas: capturar comandos sin pisar lo escrito ----
assert.equal(appendToNotes("", "nmap -sV $IP"), "nmap -sV $IP");
assert.equal(appendToNotes("linea1", "linea2"), "linea1\nlinea2");
assert.equal(appendToNotes("linea1\n", "linea2"), "linea1\nlinea2", "no debe dejar lineas en blanco al anadir");
assert.equal(appendToNotes("previo", "   "), "previo", "texto vacio no cambia las notas");
assert.equal(appendToNotes(undefined, "x"), "x");

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
assert.equal(adaptCommand("nxc smb $IP -u $USER -H $HASH", { ip: "10.10.145.23", user: "admin", hash: "aabbcc" }), "nxc smb 10.10.145.23 -u admin -H aabbcc");
assert.equal(adaptCommand("ssh -i $KEY user@$IP", { ip: "10.10.145.23", key: "id_rsa" }), "ssh -i id_rsa user@10.10.145.23");

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

assert.deepEqual(getPracticeDensityState({ query: "", tag: "all", phase: "all", favOnly: false }, false), {
  queryActive: false,
  pristine: true,
  guided: true,
});
assert.deepEqual(getPracticeDensityState({ query: "445", tag: "all", phase: "all", favOnly: false }, false), {
  queryActive: true,
  pristine: false,
  guided: false,
});
assert.equal(getPracticeDensityState({ query: "", tag: "web", phase: "all", favOnly: false }, false).guided, false);
assert.equal(getPracticeDensityState({ view: "learn", query: "", tag: "all", phase: "all", favOnly: false }, false).guided, false);
const studyConcept = {
  title: "Kerberoasting",
  summary: "Obtiene material crackeable de cuentas de servicio.",
  que: "Solicita tickets TGS para analizarlos fuera de linea.",
  necesitas: ["Usuario de dominio", "SPN valido"],
  confirmacion: "Se obtiene un hash TGS en formato compatible.",
  pasos: ["Enumerar SPN antes de solicitar tickets."],
};
const studyPrompts = studyPromptsFor(studyConcept);
assert.equal(studyPrompts.length, 4);
assert.equal(studyPrompts[0].answer, studyConcept.que);
assert.match(studyPrompts[1].answer, /Usuario de dominio/);

const html = readFileSync(new URL("./index.html", import.meta.url), "utf8");
const js = readFileSync(new URL("./app.mjs", import.meta.url), "utf8");
const sw = readFileSync(new URL("./sw.js", import.meta.url), "utf8");
const content = JSON.parse(readFileSync(new URL("./data/content.json", import.meta.url), "utf8"));
const contentCommandIndex = content.sections.flatMap((section) => section.commands.map((command) => ({ command, section })));
assert.match(html, /data-filters-toggle aria-expanded="false"/);
assert.match(html, /data-filters-panel hidden/);
assert.match(html, /data-learn-val="study"[^>]*>Estudiar \(opcional\)/);
assert.match(js, /return `<button type="button" class="cmd-info"[^>]*data-explain=/);
assert.match(js, /el\.addEventListener\("keydown", trapDialogFocus\)/);
assert.match(html, /<details class="room-actions-more">[\s\S]*data-room-duplicate[\s\S]*data-room-delete[\s\S]*<\/details>/);
assert.match(html, /<details class="room-tools">[\s\S]*data-rev-type[\s\S]*data-rev-listener[\s\S]*<\/details>/);

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

// A retired slug must never be a real section (else it wasn't actually retired)
// and must resolve to one that IS real (else an old hash/favorite hits a hole).
for (const [oldSlug, newSlug] of Object.entries(SLUG_REDIRECTS)) {
  assert.ok(!sectionSlugs.has(oldSlug), `slug retirado ${oldSlug} sigue existiendo como seccion real`);
  assert.ok(sectionSlugs.has(newSlug), `redirect ${oldSlug} -> ${newSlug} apunta a seccion inexistente`);
  assert.equal(resolveSlug(oldSlug), newSlug);
}
assert.equal(resolveSlug("un-slug-cualquiera-no-redirigido"), "un-slug-cualquiera-no-redirigido");

// ---- Buscador de puertos (feature: teclear un puerto -> que es + como seguir) ----
// Puerto conocido devuelve servicio + comandos + seccion real.
const smb = lookupPort("445");
assert.ok(smb && smb.known && smb.svc === "SMB", "445 deberia resolver a SMB");
assert.ok(smb.cmds.length && sectionSlugs.has(resolveSlug(smb.slug)), "445 apunta a seccion inexistente");
assert.equal(smb.cmds[0], "nxc smb $IP -u '' -p '' --shares", "445 debe proponer una enumeracion de shares verificable");
assert.equal(PORT_DB["139"].cmds[0], smb.cmds[0], "139 y 445 deben compartir la comprobacion SMB prioritaria");
assert.ok(
  content.commandMetadata.some((item) => item.command === smb.cmds[0] && item.sectionSlug === smb.slug),
  "el comando SMB prioritario debe tener metadata curada",
);

const nxcParts = describeCommand(smb.cmds[0]).parts;
assert.equal(nxcParts.find((part) => part.token === "-u")?.desc, "usuario o fichero de usuarios");
assert.equal(nxcParts.find((part) => part.token === "-p")?.desc, "contrasena o fichero de contrasenas");
assert.equal(nxcParts.find((part) => part.token === "--shares")?.desc, "lista recursos compartidos y permisos");
const emptyNxcValues = nxcParts.filter((part) => part.token === "''").map((part) => part.desc);
assert.deepEqual(emptyNxcValues, [
  "usuario, cuenta vacia o fichero de usuarios",
  "contrasena vacia, valor o fichero de contrasenas",
]);
const curatedSmbExplanation = commandExplanationFor(smb.cmds[0], content);
assert.equal(curatedSmbExplanation.curated, true, "el SMB prioritario debe anunciar una ficha curada");
assert.equal(curatedSmbExplanation.metadata?.objective, "Enumerar shares con sesion nula (NetExec)");
const fallbackExplanation = commandExplanationFor("nmap -p $PORT --script ssh2-enum-algos $IP", content);
assert.equal(fallbackExplanation.curated, false, "una variante sin ficha no debe presentarse como curada");
assert.equal(fallbackExplanation.metadata, null);
assert.equal(fallbackExplanation.info.tool, "nmap");
// Formatos de entrada aceptados.
assert.equal(lookupPort("puerto 80").svc, "HTTP");
assert.equal(lookupPort("port 6379/tcp").svc, "Redis");
assert.equal(lookupPort("  53  ").svc, "DNS");
// Puerto fuera de la base -> fallback de fingerprint (la leccion del nombre de nmap).
const rare = lookupPort("5050");
assert.ok(rare && rare.known === false, "5050 deberia caer al fallback no-estandar");
assert.ok(rare.cmds.some((c) => c.includes("-sV")), "el fallback debe incluir fingerprint de version");
assert.ok(sectionSlugs.has(resolveSlug(rare.slug)), "fallback apunta a seccion inexistente");
// No-puertos devuelven null (no debe dispararse con texto normal).
for (const q of ["", "smb", "top 20", "nmap", "70000", "0"]) {
  assert.equal(lookupPort(q), null, `lookupPort(${JSON.stringify(q)}) deberia ser null`);
}
// Toda entrada de la base es consistente y enlaza a una seccion que existe.
for (const [port, entry] of Object.entries(PORT_DB)) {
  assert.ok(entry.svc && entry.note, `puerto ${port} sin svc/note`);
  assert.ok(Array.isArray(entry.cmds) && entry.cmds.length, `puerto ${port} sin comandos`);
  assert.ok(sectionSlugs.has(resolveSlug(entry.slug)), `puerto ${port} apunta a seccion inexistente: ${entry.slug}`);
}

const isValidCommand = (command) =>
  typeof command === "string"
    ? command.length > 0
    : Boolean(command && typeof command.cmd === "string" && command.cmd.length > 0);

assert.equal(content.stats.totalConcepts, content.concepts.length);
assert.equal(content.stats.totalPaths, content.paths.length);
assert.ok(content.concepts.length >= 1);
assert.equal(content.stats.totalCommandMetadata, content.commandMetadata.length);
assert.ok(content.commandMetadata.length >= 20, "debe haber metadata curada para comandos prioritarios");
for (const meta of content.commandMetadata) {
  const section = content.sections.find((item) => item.slug === meta.sectionSlug);
  assert.ok(section?.commands.includes(meta.command), `metadata huérfana: ${meta.sectionSlug}`);
}

const conceptIds = new Set();
for (const concept of content.concepts) {
  assert.ok(concept.id, "concepto sin id");
  assert.ok(!conceptIds.has(concept.id), `id de concepto duplicado: ${concept.id}`);
  conceptIds.add(concept.id);
  for (const field of ["title", "summary", "que", "porque", "cuando", "section", "phase", "confirmacion", "resultado"]) {
    assert.ok(concept[field], `concepto ${concept.id} sin ${field}`);
  }
  assert.ok(Array.isArray(concept.senales) && concept.senales.length, `concepto ${concept.id} sin senales`);
  assert.ok(Array.isArray(concept.pasos) && concept.pasos.length, `concepto ${concept.id} sin pasos`);
  // necesitas/no_aplica: mandatory minimal-template fields (PLAN_IMPLEMENTACION_CONTENIDOS.md fase 2).
  for (const field of ["necesitas", "no_aplica"]) {
    assert.ok(Array.isArray(concept[field]) && concept[field].length, `concepto ${concept.id} sin ${field}`);
    for (const item of concept[field]) {
      assert.ok(typeof item === "string" && item.length, `concepto ${concept.id} con item de ${field} invalido`);
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

// ---- Search alias guard (PLAN_IMPLEMENTACION_CONTENIDOS.md fase 8) ----
// Every alias query in the plan's table must return results, and the
// section it names must actually be reachable (present in the result set),
// not necessarily #1 — short/generic terms (e.g. plain "version") also match
// unrelated sections honestly, and the ALIASES fallback only fires when a
// term has zero score elsewhere, so it cannot out-rank a broad literal hit.
const ALIAS_QUERIES = [
  { query: "21", mustInclude: "recon-y-servicios" },
  { query: "25", mustInclude: "recon-y-servicios" },
  { query: "53", mustInclude: "recon-y-servicios" },
  { query: "88", mustInclude: "active-directory" },
  { query: "161", mustInclude: "recon-y-servicios" },
  { query: "389", mustInclude: "recon-y-servicios" },
  { query: "445", mustInclude: "recon-y-servicios" },
  { query: "2049", mustInclude: "recon-y-servicios" },
  { query: "3306", mustInclude: "recon-y-servicios" },
  { query: "5432", mustInclude: "recon-y-servicios" },
  { query: "transfer", mustInclude: "acceso-inicial" },
  { query: "tengo hash", mustInclude: "hashes-y-cracking" },
  { query: "tengo credenciales", mustInclude: "credenciales-y-acceso" },
  { query: "reutilizar credenciales", mustInclude: "credenciales-y-acceso" },
  { query: "shell muere", mustInclude: "acceso-inicial" },
  { query: "session jwt", mustInclude: "web-apis-y-autorizacion" },
  { query: "graphql", mustInclude: "web-apis-y-autorizacion" },
  { query: "todo devuelve 200", mustInclude: "web-discovery" },
  { query: "access denied", mustInclude: "credenciales-y-acceso" },
  { query: "reloj", mustInclude: "active-directory" },
  { query: "servicio interno", mustInclude: "pivoting" },
  { query: "version", mustInclude: "cve-y-exploits" },
  // Accent-insensitive equivalence: normalizeQuery strips accents, so the
  // Spanish spelling must return the identical result set as the ASCII one.
  { query: "versión", mustInclude: "cve-y-exploits" },
];

for (const { query, mustInclude } of ALIAS_QUERIES) {
  const results = filterSections(content.sections, { query, tag: "all", phase: "all" });
  assert.ok(results.length > 0, `alias query "${query}" no devuelve resultados`);
  assert.ok(
    results.some((section) => section.slug === mustInclude),
    `alias query "${query}" no incluye la seccion esperada "${mustInclude}" (obtuvo: ${results.map((s) => s.slug).join(", ")})`,
  );
}

assert.deepEqual(
  filterSections(content.sections, { query: "version", tag: "all", phase: "all" }).map((s) => s.slug),
  filterSections(content.sections, { query: "versión", tag: "all", phase: "all" }).map((s) => s.slug),
  "busqueda con y sin tilde debe devolver el mismo resultado",
);

for (const asset of [html, js, sw]) {
  assert.match(asset, /20260711-fichas-recon/);
}

assert.match(js, /registration\.update\(\)/);
assert.match(js, /controllerchange/);
assert.match(sw, /SKIP_WAITING/);

assert.match(html, /<h1\b[^>]*>/);
assert.match(html, /data-usage-guide/);
assert.match(js, /function openUsageGuide\(\)/);

// Mojibake guard across every shipped text asset (UTF-8 accidentally re-encoded
// shows up as these Latin-1 lead bytes). Keeps "vÃ­ctima / â˜…"-style breakage out.
const css = readFileSync(new URL("./styles.css", import.meta.url), "utf8");
const contentRaw = readFileSync(new URL("./data/content.json", import.meta.url), "utf8");
for (const [name, text] of [["index.html", html], ["app.mjs", js], ["sw.js", sw], ["styles.css", css], ["content.json", contentRaw]]) {
  assert.doesNotMatch(text, /Ã[\x80-\xbf]|Â[\x80-\xbf]|â€|â†|â˜|ï¿½/, `mojibake en ${name}`);
}
