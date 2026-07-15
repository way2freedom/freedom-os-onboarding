from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
from typing import Any

from .models import empty_record, now_iso


DEFAULT_LOCAL_SKILL_ROOT = Path.home() / ".agents" / "skills"


def discover_installed_skills(
    skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT,
    discovered_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    by_name = {record["name"]: record for record in discovered_records or []}
    records: dict[str, dict[str, Any]] = {}
    for skill_md in sorted(skill_root.glob("*/SKILL.md")):
        name = skill_md.parent.name
        discovered = by_name.get(name)
        base = discovered or empty_record(name)
        record = merge_installed_skill(base, name, skill_md.parent, discovered=discovered is not None)
        records[name] = record
    for name in sorted(installed_mcp_names()):
        discovered = by_name.get(name)
        if discovered is None:
            continue
        base = records.get(name, discovered)
        records[name] = merge_installed_mcp(base, name)
    return [records[name] for name in sorted(records)]


def installed_names(skill_root: Path = DEFAULT_LOCAL_SKILL_ROOT, known_mcp_names: set[str] | None = None) -> set[str]:
    local_skills = {skill_md.parent.name for skill_md in skill_root.glob("*/SKILL.md")}
    mcp_names = installed_mcp_names()
    if known_mcp_names is not None:
        mcp_names &= known_mcp_names
    return local_skills | mcp_names


def registry_installed_names(capabilities: dict[str, dict[str, Any]]) -> set[str]:
    return {
        name
        for name, record in capabilities.items()
        if record.get("status") in {"installed", "ready", "partial", "broken"}
        and (
            any(agent.get("installed") for agent in record.get("agents", {}).values() if isinstance(agent, dict))
            or record.get("mcp", {}).get("registered")
        )
    }


def compare_installed_registry(
    skill_root: Path,
    capabilities: dict[str, dict[str, Any]],
    known_mcp_names: set[str] | None = None,
) -> dict[str, list[str]]:
    local = installed_names(skill_root, known_mcp_names)
    registry = registry_installed_names(capabilities)
    return {
        "missing_in_registry": sorted(local - registry),
        "stale_in_registry": sorted(registry - local),
        "matching": sorted(local & registry),
        "drifted_installs": drifted_installs(skill_root, capabilities),
    }


def drifted_installs(skill_root: Path, capabilities: dict[str, dict[str, Any]]) -> list[str]:
    drifted: list[str] = []
    for name, record in sorted(capabilities.items()):
        source_skill = source_skill_file(record)
        installed_skill = skill_root / name / "SKILL.md"
        if source_skill is None or not installed_skill.exists():
            continue
        if file_sha256(source_skill) != file_sha256(installed_skill):
            drifted.append(name)
    return drifted


def source_skill_file(record: dict[str, Any]) -> Path | None:
    paths = record.get("paths", {})
    skill = paths.get("skill")
    install_dir = paths.get("install_dir")
    if not skill:
        return None
    skill_path = Path(skill)
    if not skill_path.is_absolute():
        if not install_dir:
            return None
        skill_path = Path(install_dir) / skill_path
    candidate = skill_path / "SKILL.md"
    return candidate if candidate.exists() else None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_mcp_names() -> set[str]:
    names: set[str] = set()
    names.update(mcp_names_from_command(["codex", "mcp", "list"]))
    names.update(mcp_names_from_command(["hermes", "mcp", "list"]))
    return names


def mcp_names_from_command(command: list[str]) -> set[str]:
    if shutil.which(command[0]) is None:
        return set()
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=10)
    if result.returncode != 0:
        return set()
    names: set[str] = set()
    for line in result.stdout.splitlines():
        parts = line.strip().split()
        if not parts:
            continue
        name = parts[0]
        if name in {"Name", "MCP", "─"} or name.startswith("─"):
            continue
        if name.startswith(("WARNING:", "✓")):
            continue
        names.add(name)
    return names


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


def merge_installed_mcp(base: dict[str, Any], name: str) -> dict[str, Any]:
    record = dict(base)
    mcp = dict(record.get("mcp", {}))
    mcp["registered"] = True
    mcp["server_name"] = mcp.get("server_name") or name
    timestamp = now_iso()
    record.update(
        {
            "name": name,
            "installed_at": record.get("installed_at") or timestamp,
            "updated_at": timestamp,
            "status": "installed",
            "mcp": mcp,
        }
    )
    notes = list(record.get("notes", []))
    if "synced_from_mcp_registry" not in notes:
        notes.append("synced_from_mcp_registry")
    record["notes"] = notes
    return record
