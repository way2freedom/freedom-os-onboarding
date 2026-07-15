from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import REGISTRY_VERSION, empty_record, now_iso


DEFAULT_REGISTRY_PATH = Path(".freedom-os/registry/capabilities.json")


class CapabilityRegistry:
    def __init__(self, path: Path = DEFAULT_REGISTRY_PATH) -> None:
        self.path = path
        self.data: dict[str, Any] = {
            "version": REGISTRY_VERSION,
            "updated_at": now_iso(),
            "capabilities": {},
        }

    @classmethod
    def load(cls, path: Path = DEFAULT_REGISTRY_PATH) -> "CapabilityRegistry":
        registry = cls(path)
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                content = handle.read().strip()
            if not content:
                return registry
            loaded = json.loads(content)
            if not isinstance(loaded, dict):
                raise ValueError(f"Registry must be a JSON object: {path}")
            loaded.setdefault("version", REGISTRY_VERSION)
            loaded.setdefault("updated_at", now_iso())
            loaded.setdefault("capabilities", {})
            registry.data = loaded
        return registry

    @property
    def capabilities(self) -> dict[str, dict[str, Any]]:
        return self.data.setdefault("capabilities", {})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data["updated_at"] = now_iso()
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")

    def get(self, name: str) -> dict[str, Any] | None:
        return self.capabilities.get(name)

    def require(self, name: str) -> dict[str, Any]:
        record = self.get(name)
        if record is None:
            raise KeyError(name)
        return record

    def upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        name = record["name"]
        existing = self.capabilities.get(name, empty_record(name))
        merged = merge_known(existing, record)
        merged["updated_at"] = now_iso()
        self.capabilities[name] = merged
        return merged


def merge_known(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = dict(merged[key])
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value
    return merged
