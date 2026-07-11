# Plan — Fichas curadas de comandos (`commandMetadata`)

Objetivo: que **todo comando no trivial** explique en su modal "i" para qué sirve y qué esperar (objetivo / señal de éxito / error común / alternativa), no solo el fallback por herramienta. Estado inicial: **39/421 con ficha**; ~332 no triviales sin ficha.

## Cómo funciona (recordatorio técnico)

- Fuente: `tools/command_metadata.py`, lista `COMMAND_METADATA`, helper `_record(section, command, objective, tool, *, ...)`.
- El campo `command` **debe coincidir exacto** (tras normalizar espacios) con un comando de esa `section` en `content.json`, o el validador Python falla (orphan). Sacar el string exacto de `content.json`, no escribirlo de memoria.
- Enums válidos: `environment {kali,linux,windows,target,attacker,cross-platform}`, `targetOS {linux,windows,network,web,any}`, `credentialType {none,password,hash,key,token,mixed}`, `noise {silent,low,medium,high}`, `risk {safe,caution,intrusive}`.
- Campos por ficha: `objective` (h4), `expected`, `success` (señal de éxito), `preconditions[]`, `errors[]` (error común), `alternative`. Tono: didáctico, corto, "qué mirar en la salida y por qué falla".
- Tras cada lote: `python tools/export_web_content.py` → `python -m unittest discover -s tests` (0 orphans) → verificar 1 ficha en preview → commit → push. **Bump del sentinel** (index.html ×2, sw.js VERSION+CACHE, app.mjs APP_VERSION, app.test.mjs) cada lote porque cambia `content.json`.

## Reglas de alcance (no hacer las 332 a lo bruto)

1. **Dedupe de variantes.** Si hay 8 `ffuf`/`curl` casi idénticos que solo cambian wordlist/flag, hacer ficha del *representativo* y dejar el resto al fallback. No malgastar 8 fichas en lo mismo.
2. **Saltar secciones de metodología.** `notas-y-cierre` (39) y `checklist-de-atasco` (1) son texto/flujo, no comandos reales de herramienta → **sin ficha** (o solo las que sean comandos ejecutables de verdad).
3. **Prioridad por valor de aprendizaje**: primero las técnicas donde "qué hace / qué espero" es menos obvio (AD, privesc, cracking, CVE, web-avanzado). Recon/discovery al final (muchos duplicados, fallback ya sirve).
4. **Objetivo realista ~180-220 fichas** cubriendo lo conceptualmente único. No es meta llegar a 421.

## Lotes (ordenados por valor; ~15-20 fichas/lote)

| # | Lote | Sección(es) | Sin ficha | Foco |
|---|------|-------------|----------:|------|
| ✅0 | Web crípticos + cracking | web-inyecciones, web-apis, web-ficheros, hashes | — | HECHO (+16, commit 0aa3862) |
| 1 | Active Directory · enum/kerberos | active-directory | 30 | null/auth SMB-LDAP, kerbrute, AS-REP, kerberoast, bloodhound |
| 2 | Active Directory · lateral/dump | active-directory (resto) | ↑ | secretsdump, psexec/wmiexec, PtH, evil-winrm, DCSync, certipy |
| 3 | Linux privesc · enum/vectores | linux-privesc | 27 | sudo -l, SUID find, getcap, cron/pspy, PATH, writable, GTFOBins |
| 4 | Windows privesc · A | windows-privesc | 35 | whoami, servicios, unquoted path, AlwaysInstallElevated, registry |
| 5 | Windows privesc · B | windows-privesc (resto) | ↑ | tokens/potato, stored creds, DLL hijack, SeBackup, tareas |
| 6 | Cracking + loot | hashes-y-cracking, loot-y-secretos | 18+19 | modos hashcat/john, *2john, grep de secretos, config con creds |
| 7 | Credenciales / acceso | credenciales-y-acceso, acceso-inicial | 16+8 | hydra/medusa, spray, mssql/mysql, shells, estabilización TTY |
| 8 | Pivoting | pivoting | 24 | chisel, ligolo, ssh -L/-D/-R, proxychains, rutas internas |
| 9 | CVE / exploits | cve-y-exploits | 16 | searchsploit, msfvenom, PoC check, patrones de explotación |
| 10 | Web · ficheros/ejec + SQLi + WP | web-ficheros-y-ejecucion, sqli, wordpress | 13+5+5 | upload bypass, sqlmap, wpscan, php filters |
| 11 | Web discovery/APIs (dedupe) | web-discovery, web-apis-y-autorizacion | 24+8 | 1 ficha por técnica (ffuf dirs/vhost/param/api), no por wordlist |
| 12 | Recon servicios (dedupe) | recon-y-servicios | 40 | 1 por servicio (dns/ftp/snmp/nfs/smtp/ldap/mssql), no por variante |

Notas de reparto: AD (30), Linux privesc (27), Win privesc (35), Recon (40) se parten en 2 sub-lotes si superan ~20 tras dedupe. `notas-y-cierre`/`checklist` excluidos salvo comandos reales sueltos.

## Flujo por lote (repetible)

1. Sacar strings exactos de la sección: `python` sobre `content.json`, filtrar los que no están en `commandMetadata`.
2. Dedupe: agrupar variantes, elegir representativo.
3. Autoría de `_record(...)` en `command_metadata.py` (copiar string exacto).
4. `python tools/export_web_content.py`.
5. `python -m unittest discover -s tests` → **0 orphans** (si falla, corregir string).
6. `node --test web/app.test.mjs`.
7. Bump sentinel (5 sitios + CACHE).
8. Preview: abrir 1-2 fichas del lote, confirmar bloque rico + 0 errores consola.
9. `git commit` (`feat(content): fichas <tema> (N nuevas)`) + `git push`.
10. Marcar el lote como ✅ en esta tabla.

## Aceptación global

- [ ] Cada técnica de ataque distinta tiene su ficha (objetivo + señal de éxito).
- [ ] 0 orphans en el validador; tests JS+Python verdes en cada lote.
- [ ] Variantes near-dup cubiertas por fallback, no infladas a fichas.
- [ ] Metodología (notas/checklist) sin fichas artificiales.
- [ ] `commandMetadata` ~180-220 al cerrar; el resto = fallback por herramienta.

## Progreso

- ✅ Lote 0 — web crípticos + cracking (39 total).
- ✅ Lote 1+2 — Active Directory completo (enum, kerberos, lateral, dump, AD CS): 22 fichas → **61 total**. Cubre AD entero de una (no hizo falta partir en 2).
- ✅ Lote 3 — Linux privesc (SUID, sudo/GTFOBins, LD_PRELOAD, caps, cron/pspy/tar-wildcard, python hijack, /etc/passwd, NFS no_root_squash, docker/lxd, kernel): 25 fichas → **86 total**.
- ✅ Lote 4 — Windows privesc · A (systeminfo/qfe, winpeas/certutil, servicios: sc query/qc, accesschk, binPath hijack, unquoted path, schtasks, autoruns Run, AlwaysInstallElevated + msiexec): 14 fichas → **100 total**.
- ✅ Lote 5 — Windows privesc · B (software vuln, cmdkey, busqueda dir/findstr de secretos, unattend.xml, PSReadLine history, potato: PrintSpoofer/GodPotato/JuicyPotato): 9 fichas → **109 total**. windows-privesc cerrado (25 fichas).
- ✅ Lote 6 — Cracking + loot (hashid, *2john ssh/keepass/zip/office, john/hashcat, kpcli; grep/find secretos, firefox_decrypt, lazagne, exiftool/binwalk/steghide/stegseek/zsteg, bash_history): 22 fichas → **131 total**.
- ✅ Lote 7 — Credenciales / acceso (nxc smb/winrm validar+spray, mysql, sudo -l, hydra ssh/http-post, responder/ntlmrelayx, hashcat -m 5600, smbclient -L; estabilizar TTY stty/socat, transferencias wget/certutil): 16 fichas → **147 total**.
- ✅ Lote 8 — Pivoting (ss/arp enum interno, ssh -D/-R, chisel server/client, ligolo tun/proxy/agent/route, proxychains config/curl/nmap, nslookup DNS interno, /etc/hosts): 15 fichas → **162 total**.
- ✅ Lote 9 — CVE / exploits (leer/auditar PoC con sed+grep, --check, whatweb fingerprint, reproducir con curl, gcc compilar, script evidencia): 7 fichas → **169 total**. Resto de la seccion = comentarios/glue (sin ficha).
- ⬜ Lotes 10-12 pendientes. Siguiente: Lote 10 (Web ficheros/ejec + SQLi + WordPress).
