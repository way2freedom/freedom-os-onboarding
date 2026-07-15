from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from freedom_os_manager.registry import CapabilityRegistry


class RegistryTests(unittest.TestCase):
    def test_registry_load_empty_and_upsert(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / ".freedom-os" / "registry" / "capabilities.json"
            registry = CapabilityRegistry.load(path)

            registry.upsert({"name": "demo", "type": "pure-skill", "custom": {"keep": True}})
            registry.save()

            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["version"], 1)
            self.assertEqual(loaded["capabilities"]["demo"]["type"], "pure-skill")
            self.assertEqual(loaded["capabilities"]["demo"]["custom"], {"keep": True})

    def test_registry_loads_empty_file_as_new_registry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capabilities.json"
            path.write_text("", encoding="utf-8")

            registry = CapabilityRegistry.load(path)

            self.assertEqual(registry.capabilities, {})

    def test_registry_upsert_preserves_unknown_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capabilities.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "updated_at": "old",
                        "capabilities": {"demo": {"name": "demo", "unknown": "preserve", "paths": {"skill": "old"}}},
                    }
                ),
                encoding="utf-8",
            )

            registry = CapabilityRegistry.load(path)
            registry.upsert({"name": "demo", "status": "discovered", "paths": {"service": "services/demo"}})

            record = registry.get("demo")
            self.assertEqual(record["unknown"], "preserve")
            self.assertEqual(record["paths"]["skill"], "old")
            self.assertEqual(record["paths"]["service"], "services/demo")


if __name__ == "__main__":
    unittest.main()
