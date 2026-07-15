from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import CapabilityPaths, empty_record


def discover_capabilities(repo_root: Path) -> list[dict[str, Any]]:
    repo_root = repo_root.resolve()
    by_name: dict[str, CapabilityPaths] = {}

    for skill_md in sorted((repo_root / "skills").glob("*/SKILL.md")):
        name = skill_md.parent.name
        paths = by_name.get(name, CapabilityPaths(name=name))
        by_name[name] = CapabilityPaths(name=name, skill=skill_md.parent, service=paths.service, project=paths.project)

    for service_readme in sorted((repo_root / "services").glob("*/README.md")):
        name = service_readme.parent.name
        paths = by_name.get(name, CapabilityPaths(name=name))
        by_name[name] = CapabilityPaths(name=name, skill=paths.skill, service=service_readme.parent, project=paths.project)

    for project_readme in sorted((repo_root / "projects").glob("*/README.md")):
        name = project_readme.parent.name
        paths = by_name.get(name, CapabilityPaths(name=name))
        by_name[name] = CapabilityPaths(name=name, skill=paths.skill, service=paths.service, project=project_readme.parent)

    return [record_from_paths(paths, repo_root) for paths in sorted(by_name.values(), key=lambda item: item.name)]


def record_from_paths(paths: CapabilityPaths, repo_root: Path) -> dict[str, Any]:
    record = empty_record(paths.name)
    record["type"] = paths.inferred_type()
    record["source_type"] = "builtin"
    record["source"] = repo_root.name
    record["status"] = "discovered"
    record["paths"] = {
        "skill": relative(paths.skill, repo_root),
        "service": relative(paths.service, repo_root),
        "project": relative(paths.project, repo_root),
        "external_repo": None,
        "install_dir": str(repo_root),
    }
    if paths.skill:
        record["agents"]["hermes"]["skill_name"] = paths.name
        record["agents"]["codex"]["skill_name"] = paths.name
    if paths.service:
        record["mcp"]["server_name"] = paths.name
    return record


def relative(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
