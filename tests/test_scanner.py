from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from freedom_os_manager.scanner import discover_capabilities


def write(path: Path, content: str = "# readme\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ScannerTests(unittest.TestCase):
    def test_discover_capabilities_and_infer_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write(root / "skills" / "twitter-feed" / "SKILL.md")
            write(root / "skills" / "todo-dashboard" / "SKILL.md")
            write(root / "services" / "todo-dashboard" / "README.md")
            write(root / "projects" / "todo-dashboard" / "README.md")
            write(root / "services" / "monitor-center" / "README.md")
            write(root / "projects" / "alphahelper" / "README.md")

            records = {record["name"]: record for record in discover_capabilities(root)}

            self.assertEqual(records["twitter-feed"]["type"], "pure-skill")
            self.assertEqual(records["todo-dashboard"]["type"], "hybrid-service")
            self.assertEqual(records["monitor-center"]["type"], "mcp-service")
            self.assertEqual(records["alphahelper"]["type"], "standalone-repo")
            self.assertEqual(records["todo-dashboard"]["paths"]["skill"], "skills/todo-dashboard")
            self.assertEqual(records["todo-dashboard"]["paths"]["service"], "services/todo-dashboard")
            self.assertEqual(records["todo-dashboard"]["paths"]["project"], "projects/todo-dashboard")


if __name__ == "__main__":
    unittest.main()
