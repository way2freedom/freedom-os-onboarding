---
name: freedom-os-onboarding
description: "Bootstrap a new way2freedom team member into Freedom OS from Codex or Hermes: Git/GitHub setup, repo clone, thin skill install, project runtime setup, MCP registration, update, and contribution workflow."
version: 0.2.0
type: pure-skill
agents:
  - codex
  - hermes-agent
capabilities:
  - onboarding
  - git-setup
  - github-auth
  - skill-install
  - project-install
  - mcp-registration
  - contribution-workflow
---

# Freedom OS Onboarding

Use this skill when a new team member needs to set up Freedom OS on a fresh machine, install a team capability, update the team repository, or modify and submit code.

默认使用中文引导；如果用户使用英文，再切换英文。

Default assumption: the user has Codex installed and logged in. If Hermes Agent is also installed, support it too. If both are available, install team skills and MCPs for both. If only one is available, install for that one.

## Core model

Freedom OS capabilities may have three layers:

```text
skills/<name>      thin Agent Skill instructions
services/<name>    MCP/service registration docs and examples
projects/<name>    source code, build, tests, runtime
```

Some team projects are intentionally just standalone repositories, not Freedom OS hybrid capabilities. For these simple repo projects, do not force the `skills/services/projects` model. The onboarding job is only to clone the repository into the standard workspace, tell the user how to open that folder in Codex, and then guide update/commit/push workflow from inside that repository.

Do not assume `npx skills add` makes a TypeScript project usable. Skill installation only installs instructions. Project runtime still needs dependency install, setup, build, verification, and MCP registration.

## Standard local paths

Use this default team path unless the user asks otherwise:

```text
~/Code/github.com/way2freedom/skills
```

## Detection flow

Run:

```bash
command -v codex >/dev/null && echo codex=present || echo codex=missing
command -v hermes >/dev/null && echo hermes=present || echo hermes=missing
git --version || true
node --version || true
corepack --version || true
pnpm --version || true
gh auth status || true
```

Agent mapping for `npx skills`:

```text
codex command  -> -a codex
hermes command -> -a hermes-agent
```

You may use this script from the onboarding repo:

```bash
./scripts/detect-agents.sh
```

## Generic install flow

For any capability `<name>` in the team repo:

1. Check local agents.
2. Check/install Git.
3. Check Git identity and ask before setting missing name/email.
4. Check GitHub access. Prefer `gh auth status`; otherwise use SSH test.
5. Clone or update team repo:

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
if [ ! -d skills/.git ]; then
  git clone git@github.com:way2freedom/skills.git
fi
cd skills
git checkout v3
git pull --ff-only
```

6. Install `skills/<name>` to detected agents when present.
7. Prepare `projects/<name>` runtime when present.
8. Register MCP from `projects/<name>` when available.
9. Verify with real commands and summarize exact results.

Detailed procedure: `references/capability-install.md`.

For todo-dashboard: `references/todo-dashboard.md`.

## Simple standalone repo flow

Use this for projects like `alphahelper` when the user only needs a local checkout and Codex development guidance.

1. Check Git and GitHub access.
2. Clone the standalone repo into the standard workspace:

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
git clone git@github.com:way2freedom/<repo>.git
```

3. Tell the user to open that folder in Codex:

```bash
cd ~/Code/github.com/way2freedom/<repo>
codex
```

4. For future updates:

```bash
git status --short
git pull --ff-only
```

5. For code changes, follow `references/contribution-workflow.md` in that repo context: inspect status, edit scoped files, run relevant verification, then commit/push only when the user explicitly asks.

Do not install a thin skill, register MCP, or run project setup unless the standalone repo's README/AGENTS/service manifest explicitly says that is required.

## Update and contribution flow

When the user asks to update, modify, commit, or push team code, follow:

```text
references/contribution-workflow.md
```

Key rules:

- Pull with `git pull --ff-only` before editing.
- Do not commit or push unless the user explicitly asks.
- Keep changes scoped to the task.
- Run relevant verification before claiming done.
- Never commit secrets, `.env`, tokens, cookies, personal local paths, or credentials.

## Safety boundaries

- Do not hardcode GitHub tokens, Feishu tokens, OpenAI keys, profile names, local IPs, or personal account identifiers.
- Do not ask the user to paste tokens, private keys, or passwords into chat.
- Prefer preview/dry-run for MCP registration when available.
- Ask before running commands that need sudo, install OS packages, overwrite config files, change GitHub credentials, commit, or push.
