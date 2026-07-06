import assert from "node:assert/strict";
import { adaptCommand, buildRoomContext, filterSections, getTopCommands, normalizeQuery } from "./app.mjs";

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
