from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import hermes
from .models import DoctorResult, now_iso


def run_doctor(record: dict[str, Any], repo_root: Path) -> DoctorResult:
    result = DoctorResult(ok=True)
    paths = record.get("paths", {})

    skill = paths.get("skill")
    service = paths.get("service")
    project = paths.get("project")

    if skill:
        skill_path = repo_root / skill
        result.add("skill_path", skill_path.is_dir(), str(skill_path))
        result.add("skill_file", (skill_path / "SKILL.md").is_file(), str(skill_path / "SKILL.md"))
        installed, detail = hermes.skill_installed(record["name"])
        record.setdefault("agents", {}).setdefault("hermes", {})["installed"] = installed
        result.add("hermes_skill", installed, detail or "not listed")
    else:
        result.add("skill_path", True, "no skill layer")

    if service:
        service_path = repo_root / service
        result.add("service_path", service_path.is_dir(), str(service_path))
        result.add("service_readme", (service_path / "README.md").is_file(), str(service_path / "README.md"))
    else:
        result.add("service_path", True, "no service layer")

    if project:
        project_path = repo_root / project
        result.add("project_path", project_path.is_dir(), str(project_path))
        result.add("project_readme", (project_path / "README.md").is_file(), str(project_path / "README.md"))
    else:
        result.add("project_path", True, "no project layer")

    runtime = record.setdefault("runtime", {})
    runtime["last_checked_at"] = now_iso()
    runtime["last_doctor_status"] = "passed" if result.ok else "failed"
    if result.ok and record.get("status") not in {"uninstalled", "disabled"}:
        record["status"] = "ready"
    elif not result.ok and record.get("status") not in {"uninstalled", "disabled"}:
        record["status"] = "broken"
    return result
