from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REGISTRY_VERSION = 1


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def empty_record(name: str) -> dict[str, Any]:
    timestamp = now_iso()
    return {
        "name": name,
        "type": "unknown",
        "source_type": "builtin",
        "source": "local",
        "version": None,
        "installed_at": None,
        "updated_at": timestamp,
        "status": "discovered",
        "paths": {
            "skill": None,
            "service": None,
            "project": None,
            "external_repo": None,
            "install_dir": None,
        },
        "agents": {
            "hermes": {"installed": False, "skill_name": None},
            "codex": {"installed": False, "skill_name": None},
        },
        "runtime": {
            "prepared": False,
            "doctor_command": None,
            "last_doctor_status": "unknown",
            "last_checked_at": None,
        },
        "mcp": {"registered": False, "server_name": None},
        "notes": [],
    }


@dataclass(frozen=True)
class CapabilityPaths:
    name: str
    skill: Path | None = None
    service: Path | None = None
    project: Path | None = None

    def inferred_type(self) -> str:
        if self.skill and self.service and self.project:
            return "hybrid-service"
        if self.service:
            return "mcp-service"
        if self.skill:
            return "pure-skill"
        if self.project:
            return "standalone-repo"
        return "unknown"


@dataclass
class DoctorResult:
    ok: bool
    checks: list[tuple[str, bool, str]] = field(default_factory=list)

    def add(self, name: str, passed: bool, detail: str) -> None:
        self.checks.append((name, passed, detail))
        if not passed:
            self.ok = False
