from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import empty_record, now_iso


DEFAULT_LOCAL_SKILL_ROOT = Path.home() / ".agents" / "skills"


def discover_installed_skills(
    skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT,
    discovered_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_name = {record["name"]: record for record in discovered_records or []}
    records: list[dict[str, Any]] = []
    for skill_md in sorted(skill_root.glob("*/SKILL.md")):
        name = skill_md.parent.name
        discovered = by_name.get(name)
        base = discovered or empty_record(name)
        record = merge_installed_skill(base, name, skill_md.parent, discovered=discovered is not None)
        records.append(record)
    return records


def installed_names(skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT) -> set[str]:
    return {skill_md.parent.name for skill_md in skill_root.glob("*/SKILL.md")}


def registry_installed_names(capabilities: dict[str, dict[str, Any]]) -> set[str]:
    return {
        name
        for name, record in capabilities.items()
        if record.get("status") in {"installed", "ready", "partial", "broken"}
        and any(agent.get("installed") for agent in record.get("agents", {}).values() if isinstance(agent, dict))
    }


def compare_installed_registry(skill_root: Path, capabilities: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    local = installed_names(skill_root)
    registry = registry_installed_names(capabilities)
    return {
        "missing_in_registry": sorted(local - registry),
        "stale_in_registry": sorted(registry - local),
        "matching": sorted(local & registry),
    }


def merge_installed_skill(base: dict[str, Any], name: str, skill_dir: Path, *, discovered: bool) -> dict[str, Any]:
    record = dict(base)
    paths = dict(record.get("paths", {}))
    if not paths.get("skill"):
        paths["skill"] = str(skill_dir)
    paths.setdefault("service", None)
    paths.setdefault("project", None)
    paths.setdefault("external_repo", None)
    paths.setdefault("install_dir", str(skill_dir.parent))

    agents = dict(record.get("agents", {}))
    for agent in ("codex", "hermes"):
        agent_state = dict(agents.get(agent, {}))
        agent_state["installed"] = True
        agent_state["skill_name"] = agent_state.get("skill_name") or name
        agents[agent] = agent_state

    timestamp = now_iso()
    record_type = record.get("type")
    record.update(
        {
            "name": name,
            "type": record_type if record_type and record_type != "unknown" else "pure-skill",
            "source_type": record.get("source_type") if discovered else "local",
            "source": record.get("source") if discovered else "local-agent-skills",
            "installed_at": record.get("installed_at") or timestamp,
            "updated_at": timestamp,
            "status": "installed",
            "paths": paths,
            "agents": agents,
        }
    )
    notes = list(record.get("notes", []))
    if "synced_from_local_skill_root" not in notes:
        notes.append("synced_from_local_skill_root")
    record["notes"] = notes
    return record
