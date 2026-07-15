# Freedom OS Manager

中文文档见：[README.zh-CN.md](README.zh-CN.md)。

A public bootstrap Agent Skill for new way2freedom team members.

This repository is intentionally small and public. New members install this skill first, then ask Codex or Hermes to set up their local Freedom OS workspace.

## Quick start

Default path for new members who already have Codex installed and logged in:

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-manager -a codex
```

If both Codex and Hermes Agent are installed, install to both:

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-manager -a codex -a hermes-agent
```

After installing, open Codex and say:

```text
Use the freedom-os-manager skill to install todo-dashboard.
Detect my available agents automatically. If Git or GitHub access is missing, guide me step by step.
```

## Generic capability model

Freedom OS capabilities can have three layers:

```text
skills/<name>      thin Agent Skill instructions
services/<name>    MCP/service registration docs and examples
projects/<name>    source code, build, tests, runtime
```

Some projects are intentionally just standalone repositories, such as `alphahelper`. Do not force those into the three-layer capability model. For a simple standalone repo, onboarding only needs to:

1. Check Git and GitHub access.
2. Clone the repo into the standard workspace.
3. Tell the user to open that folder in Codex.
4. Guide future update, edit, verify, commit, and push workflow from inside that repo.

Example:

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
git clone git@github.com:way2freedom/alphahelper.git
cd alphahelper
codex
```

Unless the standalone repo's own `README.md`, `AGENTS.md`, or service manifest says otherwise, do not install a thin skill, register MCP, run project setup/build, or copy it into `way2freedom/freedom-os/projects`.

This manager skill can guide all three:

```bash
./skills/freedom-os-manager/scripts/install-capability.sh todo-dashboard
```

The script:

1. Clones or updates `way2freedom/freedom-os`.
2. Installs `skills/<name>` to detected agents.
3. Prepares `projects/<name>` when present.
4. Registers MCP for Codex when available.
5. Prints Hermes MCP registration preview when Hermes exists.

## What this skill does

It guides an agent through:

1. Detecting local agents: Codex and/or Hermes Agent.
2. Checking Git, Node, Corepack, and pnpm.
3. Configuring Git identity if missing.
4. Setting up GitHub access with `gh`, SSH, or HTTPS credentials.
5. Cloning `way2freedom/freedom-os` into `~/Code/github.com/way2freedom/freedom-os`.
6. Installing requested thin skills into available agents.
7. Preparing project runtime, for example `projects/todo-dashboard`.
8. Registering MCP servers for Codex and/or Hermes.
9. Updating the team repository safely.
10. Committing and pushing changes only after explicit user request and verification.

## Capability Registry MVP

This repository also contains a small local CLI runtime for the Freedom OS Capability Registry. It is intentionally separate from `way2freedom/freedom-os`; source lives in this repository under `src/freedom_os_manager/`.

The registry stores local machine state in:

```text
.freedom-os/registry/capabilities.json
```

That path is ignored by Git. It records discovered capabilities, install state, layered status, and last doctor results without storing secrets.

Run from this repository:

```bash
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities scan
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities sync-installed --repo-root /Users/winston/Code/github.com/way2freedom/freedom-os
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities check-installed
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities list
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities status freedom-os-manager
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities doctor freedom-os-manager
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities install freedom-os-manager --dry-run
PYTHONPATH=src python3 -m freedom_os_manager.cli capabilities uninstall freedom-os-manager
```

Short alias:

```bash
PYTHONPATH=src python3 -m freedom_os_manager.cli cap list
```

MVP behavior:

- `scan` discovers `skills/*/SKILL.md`, `services/*/README.md`, and `projects/*/README.md`.
- `sync-installed` saves a local installed-capability snapshot from `~/.agents/skills`, using the repository scan only to enrich known types and paths. Repository capabilities that are not installed locally are omitted.
- `check-installed` compares `~/.agents/skills` with the registry and exits nonzero when they differ. Add `--fix` to replace the registry with the local installed snapshot.
- Type inference distinguishes `pure-skill`, `mcp-service`, `hybrid-service`, and `standalone-repo`.
- `status` separates Agent skill install state, runtime readiness, and MCP registration.
- `doctor` performs read-only local checks and writes only the registry's last check result.
- `install` supports built-in skills for detected Codex and Hermes agents; use `--dry-run` to preview without changing agent config.
- `uninstall` defaults to preview plus a `disabled` registry mark. Pass `--execute` to remove agent skill registration through `npx skills remove`; source files, runtime data, credentials, and exports are never deleted.

Run tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Repository layout

```text
README.md                         English manager guide
README.zh-CN.md                   Chinese manager guide
pyproject.toml                    Python CLI package metadata
src/freedom_os_manager/           Capability Registry CLI/runtime
tests/                            Registry, scanner, and CLI tests
skills/freedom-os-manager/
  SKILL.md                        bootstrap skill entrypoint
  references/
    capability-install.md         generic skill/service/project installation flow
    contribution-workflow.md      update, modify, verify, commit, push workflow
    todo-dashboard.md             todo-dashboard install flow
    github-access.md              GitHub auth guide
    troubleshooting.md            common setup issues
  scripts/
    detect-agents.sh              prints npx-skills agent flags
    install-team-skill.sh         installs a skill to detected agents
    install-capability.sh         generic skill/project/MCP installer
    bootstrap-todo-dashboard.sh   compatibility wrapper for todo-dashboard
```

The skill lives under `skills/freedom-os-manager/` instead of the repository root so `npx skills` installs the complete skill package, including `references/` and `scripts/`, when installing from GitHub.

## Safety

- Scripts do not ask for or store tokens.
- GitHub credentials are handled by `gh`, SSH, or Git credential helpers.
- MCP registration is explicit and uses local CLI commands.
- Project runtime setup happens only after the team repository is cloned locally.
- Commits/pushes require explicit user instruction.
