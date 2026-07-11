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

## Repository layout

```text
README.md                         English manager guide
README.zh-CN.md                   Chinese manager guide
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
