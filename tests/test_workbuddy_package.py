from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from zh_expert_os.cli import build_parser


class WorkBuddyPackageTests(unittest.TestCase):
    def test_cli_exposes_workbuddy_export(self):
        args = build_parser().parse_args(["workbuddy-export-expert", "--expert", "router"])
        self.assertEqual(args.command, "workbuddy-export-expert")
        self.assertEqual(args.expert_id, "router")
        self.assertEqual(args.output_dir, "~/.workbuddy/agents")

    def test_workbuddy_artifacts_are_syntactically_valid(self):
        root = Path(__file__).resolve().parents[1]
        schema_paths = [
            root / "schemas" / "evidence-ref.schema.json",
            root / "schemas" / "expert-envelope.schema.json",
            root / "schemas" / "workbuddy-node-state.schema.json",
            root / "schemas" / "workbuddy-message-delivery.schema.json",
        ]
        for path in schema_paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["$schema"], "https://json-schema.org/draft/2020-12/schema")

        agents_dir = root / "adapters" / "workbuddy" / "agents"
        agent_files = sorted(agents_dir.glob("*.md"))
        self.assertGreaterEqual(len(agent_files), 7)
        for path in agent_files:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"))
            self.assertIn("name:", text)
            self.assertIn("description:", text)
            self.assertIn("maxTurns: 200", text)

        skill = (root / "adapters" / "workbuddy" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Agent", skill)
        self.assertIn("TaskStop", skill)

    def test_workbuddy_shell_installers_parse(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("install.sh", "uninstall.sh"):
            proc = subprocess.run(
                ["bash", "-n", str(root / "adapters" / "workbuddy" / name)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


    def test_install_and_uninstall_use_regular_files_and_preserve_edits(self):
        root = Path(__file__).resolve().parents[1]
        install = root / "adapters" / "workbuddy" / "install.sh"
        uninstall = root / "adapters" / "workbuddy" / "uninstall.sh"

        with tempfile.TemporaryDirectory() as td:
            temp_root = Path(td)
            agents_dir = temp_root / "agents"
            skills_dir = temp_root / "skills"
            env = {
                **os.environ,
                "WORKBUDDY_AGENTS_DIR": str(agents_dir),
                "WORKBUDDY_SKILLS_DIR": str(skills_dir),
            }

            for _ in range(2):
                proc = subprocess.run(
                    ["bash", str(install)],
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)

            installed_agents = sorted(agents_dir.glob("*.md"))
            self.assertGreaterEqual(len(installed_agents), 7)
            self.assertTrue(all(path.is_file() and not path.is_symlink() for path in installed_agents))

            skill_path = skills_dir / "zh-expert-os" / "SKILL.md"
            self.assertTrue(skill_path.is_file())
            self.assertFalse(skill_path.is_symlink())

            edited = agents_dir / "zeos-router.md"
            edited.write_text(edited.read_text(encoding="utf-8") + "\n# local edit\n", encoding="utf-8")

            proc = subprocess.run(
                ["bash", str(uninstall)],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(edited.exists())
            self.assertIn("local edit", edited.read_text(encoding="utf-8"))
            self.assertFalse(skill_path.exists())
            self.assertEqual([edited], sorted(agents_dir.glob("*.md")))


if __name__ == "__main__":
    unittest.main()
