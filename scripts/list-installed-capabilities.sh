#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
freedom_os_root="${FREEDOM_OS_ROOT:-/Users/winston/Code/github.com/way2freedom/freedom-os}"

cd "$repo_root"

echo "== Registry Check =="
PYTHONPATH=src python3 -m freedom_os_manager.cli \
  --repo-root "$freedom_os_root" \
  capabilities check-installed || true
echo

echo "== Installed Capabilities By Platform =="
python3 - "$repo_root/.freedom-os/registry/capabilities.json" <<'PY'
import json
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> str:
    if shutil.which(command[0]) is None:
        return ""
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
    if result.returncode != 0:
        return ""
    return result.stdout


def parse_codex_mcp(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        if "WARNING:" in line or not line.strip() or line.lstrip().startswith("Name "):
            continue
        parts = line.split()
        if len(parts) >= 4 and parts[-2] == "enabled":
            names.add(parts[0])
    return names


def parse_hermes_skills(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        if "│" not in line or "Name" in line:
            continue
        cols = [col.strip() for col in line.split("│")[1:-1]]
        if len(cols) >= 5 and cols[2] == "local" and cols[4] == "enabled":
            names.add(cols[0])
    return names


def parse_hermes_mcp(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("MCP Servers", "Name", "─")):
            continue
        parts = stripped.split()
        if len(parts) >= 4 and parts[-1] == "enabled":
            names.add(parts[0])
    return names


def platform_status(skill: bool, mcp: bool, runtime: bool = False) -> str:
    labels = []
    if skill:
        labels.append("skill")
    if mcp:
        labels.append("mcp")
    if runtime:
        labels.append("runtime")
    return "+".join(labels) if labels else "-"


def project_path(record: dict):
    project = record.get("paths", {}).get("project")
    install_dir = record.get("paths", {}).get("install_dir")
    if not project:
        return None
    path = Path(project)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / path
    return path


def project_prepared(record: dict) -> bool:
    if not record.get("runtime", {}).get("prepared"):
        return False
    path = project_path(record)
    return bool(path and path.is_dir())


def read_description(record: dict) -> str:
    skill = record.get("paths", {}).get("skill")
    install_dir = record.get("paths", {}).get("install_dir")
    if not skill:
        path = project_path(record)
        service_json = path / "service.json" if path else None
        if service_json and service_json.exists():
            try:
                value = json.loads(service_json.read_text(encoding="utf-8")).get("description")
            except json.JSONDecodeError:
                value = None
            if value:
                return " ".join(str(value).split())
        pyproject = path / "pyproject.toml" if path else None
        if pyproject and pyproject.exists():
            value = read_pyproject_description(pyproject)
            if value:
                return " ".join(str(value).split())
        return ""
    path = Path(skill)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / skill
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return ""
    in_frontmatter = False
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if in_frontmatter and stripped.startswith("description:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            return " ".join(value.split())
    return ""


def read_pyproject_description(path: Path):
    in_project = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("["):
            break
        if in_project and stripped.startswith("description"):
            _, value = stripped.split("=", 1)
            return value.strip().strip("\"'")
    return None


def shorten(text: str, width: int = 48) -> str:
    if len(text) <= width:
        return text
    return text[: max(0, width - 1)] + "…"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_skill_file(record: dict):
    skill = record.get("paths", {}).get("skill")
    install_dir = record.get("paths", {}).get("install_dir")
    if not skill:
        return None
    path = Path(skill)
    if not path.is_absolute() and install_dir:
        path = Path(install_dir) / path
    skill_md = path / "SKILL.md"
    return skill_md if skill_md.exists() else None


def sync_status(name: str, record: dict) -> str:
    source = source_skill_file(record)
    installed = Path.home() / ".agents" / "skills" / name / "SKILL.md"
    if source is None or not installed.exists():
        return "n/a"
    return "ok" if file_hash(source) == file_hash(installed) else "drift"


registry_path = Path(sys.argv[1])
if not registry_path.exists():
    print(f"registry not found: {registry_path}")
    raise SystemExit(0)

records = json.loads(registry_path.read_text()).get("capabilities", {})
local_skills = {path.parent.name for path in (Path.home() / ".agents" / "skills").glob("*/SKILL.md")}
codex_mcp = parse_codex_mcp(run(["codex", "mcp", "list"]))
hermes_skills = parse_hermes_skills(run(["hermes", "skills", "list"]))
hermes_mcp = parse_hermes_mcp(run(["hermes", "mcp", "list"]))

normal = []
lark_names = []
for name, record in sorted(records.items()):
    if name.startswith("lark-"):
        lark_names.append(name)
        continue
    prepared = project_prepared(record)
    codex = platform_status(name in local_skills, name in codex_mcp, prepared)
    hermes = platform_status(name in hermes_skills or name in local_skills, name in hermes_mcp, prepared)
    normal.append((name, record.get("type", "unknown"), codex, hermes, sync_status(name, record), read_description(record)))

print("{:<30} {:<16} {:<16} {:<16} {:<8} {}".format("CAPABILITY", "TYPE", "CODEX", "HERMES", "SYNC", "DESCRIPTION"))
for name, type_, codex, hermes, sync, description in normal:
    print("{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(name[:30], type_[:16], codex, hermes, sync, shorten(description)))

if lark_names:
    codex_count = sum(1 for name in lark_names if name in local_skills)
    hermes_count = sum(1 for name in lark_names if name in hermes_skills or name in local_skills)
    print(
        "{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(
            f"lark-* ({len(lark_names)})",
            "pure-skill",
            f"skill x{codex_count}" if codex_count else "-",
            f"skill x{hermes_count}" if hermes_count else "-",
            "n/a",
            "Lark / Feishu local workflow skills",
        )
    )
    print("  " + ", ".join(lark_names))

extra_codex_mcp = sorted(codex_mcp - set(records))
extra_hermes_mcp = sorted(hermes_mcp - set(records))
if extra_codex_mcp or extra_hermes_mcp:
    print()
    print("== Other Registered MCP ==", flush=True)
    print("{:<30} {:<16} {:<16} {:<16} {:<8} {}".format("NAME", "TYPE", "CODEX", "HERMES", "SYNC", "DESCRIPTION"))
    for name in sorted(set(extra_codex_mcp) | set(extra_hermes_mcp)):
        print(
            "{:<30} {:<16} {:<16} {:<16} {:<8} {}".format(
                name[:30],
                "external",
                "mcp" if name in extra_codex_mcp else "-",
                "mcp" if name in extra_hermes_mcp else "-",
                "n/a",
                "external MCP",
            )
        )
PY
