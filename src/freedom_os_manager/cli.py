from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .adapters import agents, hermes
from .doctor import run_doctor
from .installed import DEFAULT_LOCAL_SKILL_ROOT, compare_installed_registry, discover_installed_skills
from .models import now_iso
from .registry import DEFAULT_REGISTRY_PATH, CapabilityRegistry
from .scanner import discover_capabilities


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="freedom-os")
    parser.add_argument("--repo-root", default=".", help="Repository root to scan; defaults to current directory.")
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY_PATH), help="Capability registry JSON path.")
    subparsers = parser.add_subparsers(dest="resource", required=True)
    for resource in ("capabilities", "cap"):
        capabilities = subparsers.add_parser(resource)
        command = capabilities.add_subparsers(dest="command", required=True)
        command.add_parser("scan")
        sync_installed = command.add_parser("sync-installed")
        sync_installed.add_argument("--local-skill-root", default=str(DEFAULT_LOCAL_SKILL_ROOT), help="Local installed skill root.")
        check_installed = command.add_parser("check-installed")
        check_installed.add_argument("--local-skill-root", default=str(DEFAULT_LOCAL_SKILL_ROOT), help="Local installed skill root.")
        check_installed.add_argument("--fix", action="store_true", help="Replace registry installed list with the local installed skill snapshot.")
        command.add_parser("list")
        status = command.add_parser("status")
        status.add_argument("name")
        doctor = command.add_parser("doctor")
        doctor.add_argument("name")
        install = command.add_parser("install")
        install.add_argument("name")
        install.add_argument("--dry-run", action="store_true", help="Print the install command without changing agent config.")
        install.add_argument("--agent", choices=("codex", "hermes"), action="append", help="Target agent. Defaults to detected agents.")
        uninstall = command.add_parser("uninstall")
        uninstall.add_argument("name")
        uninstall.add_argument("--execute", action="store_true", help="Run the agent skill removal command. Default is preview only.")
        uninstall.add_argument("--agent", choices=("codex", "hermes"), action="append", help="Target agent. Defaults to detected agents.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    registry = CapabilityRegistry.load(Path(args.registry))

    if args.command == "scan":
        return cmd_scan(registry, repo_root)
    if args.command == "sync-installed":
        return cmd_sync_installed(registry, repo_root, Path(args.local_skill_root))
    if args.command == "check-installed":
        return cmd_check_installed(registry, repo_root, Path(args.local_skill_root), fix=args.fix)
    if args.command == "list":
        return cmd_list(registry)
    if args.command == "status":
        return cmd_status(registry, args.name)
    if args.command == "doctor":
        return cmd_doctor(registry, repo_root, args.name)
    if args.command == "install":
        return cmd_install(registry, repo_root, args.name, dry_run=args.dry_run, requested_agents=args.agent)
    if args.command == "uninstall":
        return cmd_uninstall(registry, args.name, execute=args.execute, requested_agents=args.agent)
    raise AssertionError(args.command)


def cmd_scan(registry: CapabilityRegistry, repo_root: Path) -> int:
    records = discover_capabilities(repo_root)
    for record in records:
        registry.upsert(record)
    registry.save()
    print(f"Scanned {repo_root}")
    print(f"Discovered {len(records)} capabilities")
    for record in records:
        print(f"- {record['name']}: {record['type']}")
    return 0


def cmd_sync_installed(registry: CapabilityRegistry, repo_root: Path, local_skill_root: Path) -> int:
    discovered = discover_capabilities(repo_root) if repo_root.exists() else []
    records = discover_installed_skills(local_skill_root, discovered)
    registry.data["capabilities"] = {}
    for record in records:
        registry.upsert(record)
    registry.save()
    print(f"Synced installed skills from {local_skill_root}")
    print(f"Installed capabilities saved: {len(records)}")
    for record in records:
        print(f"- {record['name']}: {record['type']}")
    return 0


def cmd_check_installed(registry: CapabilityRegistry, repo_root: Path, local_skill_root: Path, *, fix: bool) -> int:
    discovered = discover_capabilities(repo_root) if repo_root.exists() else []
    known_mcp_names = {record["name"] for record in discovered} | set(registry.capabilities)
    diff = compare_installed_registry(local_skill_root, registry.capabilities, known_mcp_names)
    print(f"Compared installed skills in {local_skill_root}")
    print(f"matching={len(diff['matching'])}")
    print_names("missing_in_registry", diff["missing_in_registry"])
    print_names("stale_in_registry", diff["stale_in_registry"])
    print_names("drifted_installs", diff["drifted_installs"])
    has_diff = bool(diff["missing_in_registry"] or diff["stale_in_registry"] or diff["drifted_installs"])
    if fix:
        cmd_sync_installed(registry, repo_root, local_skill_root)
        return 0
    return 1 if has_diff else 0


def print_names(label: str, names: list[str]) -> None:
    print(f"{label}={len(names)}")
    for name in names:
        print(f"- {name}")


def cmd_list(registry: CapabilityRegistry) -> int:
    rows = sorted(registry.capabilities.values(), key=lambda item: item["name"])
    if not rows:
        print("No capabilities registered. Run: freedom-os capabilities scan")
        return 0
    print(f"{'NAME':24} {'TYPE':16} {'STATUS':12} PATHS")
    for record in rows:
        paths = record.get("paths", {})
        visible_paths = ", ".join(f"{key}={value}" for key, value in paths.items() if value and key in {"skill", "service", "project"})
        print(f"{record['name'][:24]:24} {record.get('type', 'unknown')[:16]:16} {record.get('status', 'unknown')[:12]:12} {visible_paths}")
    return 0


def cmd_status(registry: CapabilityRegistry, name: str) -> int:
    record = registry.get(name)
    if record is None:
        print(f"Capability not found in registry: {name}", file=sys.stderr)
        print("Run: freedom-os capabilities scan", file=sys.stderr)
        return 2
    print_status(record)
    return 0


def cmd_doctor(registry: CapabilityRegistry, repo_root: Path, name: str) -> int:
    record = ensure_scanned(registry, repo_root, name)
    result = run_doctor(record, repo_root)
    registry.upsert(record)
    registry.save()
    for check_name, passed, detail in result.checks:
        marker = "ok" if passed else "fail"
        print(f"{marker:4} {check_name}: {detail}")
    print(f"doctor_status={record['runtime']['last_doctor_status']}")
    return 0 if result.ok else 1


def cmd_install(registry: CapabilityRegistry, repo_root: Path, name: str, *, dry_run: bool, requested_agents: list[str] | None) -> int:
    record = ensure_scanned(registry, repo_root, name)
    skill_path = record.get("paths", {}).get("skill")
    if not skill_path:
        record["status"] = "partial"
        registry.upsert(record)
        registry.save()
        print(f"Capability has no builtin skill layer: {name}", file=sys.stderr)
        return 1

    absolute_skill_path = repo_root / skill_path
    target_agents = agents.normalize_agents(requested_agents)
    preview_agents = target_agents or ["codex", "hermes"]
    command = agents.format_install_command(absolute_skill_path, preview_agents)
    if dry_run:
        print(command)
        print("dry_run=true")
        return 0

    if not target_agents:
        record["status"] = "partial"
        registry.upsert(record)
        registry.save()
        print("No supported agents detected; no agent install was performed", file=sys.stderr)
        print(command, file=sys.stderr)
        return 1

    if not agents.npx_available():
        record["status"] = "broken"
        registry.upsert(record)
        registry.save()
        print("npx command not found; no agent install was performed", file=sys.stderr)
        print(command, file=sys.stderr)
        return 1

    result = agents.install_skill(absolute_skill_path, target_agents)
    for agent in target_agents:
        record.setdefault("agents", {}).setdefault(agent, {})["installed"] = result.returncode == 0
    record["installed_at"] = record.get("installed_at") or now_iso()
    record["status"] = "installed" if result.returncode == 0 else "broken"
    registry.upsert(record)
    registry.save()
    print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)
    print(f"install_exit_code={result.returncode}")
    return result.returncode


def cmd_uninstall(registry: CapabilityRegistry, name: str, *, execute: bool, requested_agents: list[str] | None) -> int:
    record = registry.get(name)
    if record is None:
        print(f"Capability not found in registry: {name}", file=sys.stderr)
        return 2
    target_agents = agents.normalize_agents(requested_agents)
    preview_agents = target_agents or ["codex", "hermes"]
    command = agents.format_uninstall_command(name, preview_agents)

    if execute:
        if not target_agents:
            print("No supported agents detected; no agent uninstall was performed", file=sys.stderr)
            print(command, file=sys.stderr)
            return 1
        if not agents.npx_available():
            print("npx command not found; no agent uninstall was performed", file=sys.stderr)
            print(command, file=sys.stderr)
            return 1
        result = agents.uninstall_skill(name, target_agents)
        print(result.stdout.strip())
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        print(f"uninstall_exit_code={result.returncode}")
        if result.returncode != 0:
            record["status"] = "broken"
            registry.upsert(record)
            registry.save()
            return result.returncode
        agents_to_mark = target_agents
    else:
        print(command)
        print("preview=true")
        print("Pass --execute to remove the agent skill registration.")
        agents_to_mark = []

    if execute:
        record["status"] = "uninstalled"
        for agent in agents_to_mark:
            record.setdefault("agents", {}).setdefault(agent, {})["installed"] = False
    else:
        record["status"] = "disabled"
    registry.upsert(record)
    registry.save()
    print(f"Marked {name} as {record['status']} in registry")
    print("No source files, runtime data, credentials, or user exports were deleted")
    return 0


def ensure_scanned(registry: CapabilityRegistry, repo_root: Path, name: str) -> dict[str, Any]:
    record = registry.get(name)
    if record is not None:
        return record
    for discovered in discover_capabilities(repo_root):
        registry.upsert(discovered)
    record = registry.get(name)
    if record is None:
        raise SystemExit(f"Capability not found in repository or registry: {name}")
    return record


def print_status(record: dict[str, Any]) -> None:
    paths = record.get("paths", {})
    agents = record.get("agents", {})
    runtime = record.get("runtime", {})
    mcp = record.get("mcp", {})
    print(f"name: {record['name']}")
    print(f"type: {record.get('type', 'unknown')}")
    print(f"status: {record.get('status', 'unknown')}")
    print("paths:")
    print(f"  skill: {paths.get('skill') or '-'}")
    print(f"  service: {paths.get('service') or '-'}")
    print(f"  project: {paths.get('project') or '-'}")
    print("agents:")
    print(f"  hermes.skill_installed: {agents.get('hermes', {}).get('installed', False)}")
    print(f"  codex.skill_installed: {agents.get('codex', {}).get('installed', False)}")
    print("runtime:")
    print(f"  prepared: {runtime.get('prepared', False)}")
    print(f"  last_doctor_status: {runtime.get('last_doctor_status', 'unknown')}")
    print(f"  last_checked_at: {runtime.get('last_checked_at') or '-'}")
    print("mcp:")
    print(f"  registered: {mcp.get('registered', False)}")
    print(f"  server_name: {mcp.get('server_name') or '-'}")


if __name__ == "__main__":
    raise SystemExit(main())
