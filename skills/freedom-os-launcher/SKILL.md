---
name: freedom-os-launcher
description: "Use first for Freedom OS launch/bootstrap work: prepare the local environment, clone or update way2freedom/freedom-os, and hand off to the main repository."
version: 0.2.2
type: pure-skill
agents:
  - codex
  - hermes-agent
capabilities:
  - onboarding
  - git-setup
  - github-auth
  - repository-bootstrap
---

# Freedom OS Launcher

Use this skill first when a user asks to set up a new Freedom OS workspace, prepare the local machine for Freedom OS work, or clone/update the `way2freedom/freedom-os` main repository.

This skill is intentionally narrow. It is a launcher, not the place for ongoing capability installation, MCP registration, or project runtime orchestration.

默认使用中文引导；如果用户使用英文，再切换英文。

## Core model

This launcher only prepares the local environment and hands the user off to the main repository.

It may:

- detect Codex and Hermes availability
- check Git, GitHub auth, Node, Corepack, and pnpm
- help configure Git identity when missing
- clone or update `~/Code/github.com/way2freedom/freedom-os`
- tell the user what to do next inside the main repository

It does not own downstream capability installation, runtime setup, or MCP registration as a primary responsibility.

## Standard local path

Use this default team path unless the user asks otherwise:

```text
~/Code/github.com/way2freedom/freedom-os
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

You may use this script from the launcher repo:

```bash
./scripts/detect-agents.sh
```

## Bootstrap flow

When the user asks to prepare a Freedom OS workspace:

1. Check local agents.
2. Check/install Git.
3. Check Git identity and ask before setting missing name/email.
4. Check GitHub access. Prefer `gh auth status`; otherwise use SSH test.
5. Clone or update the main repository:

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
if [ ! -d freedom-os/.git ]; then
  git clone git@github.com:way2freedom/freedom-os.git
fi
cd freedom-os
git pull --ff-only
```

6. Hand the user off to the `way2freedom/freedom-os` repository for capability-specific work.

## When to stop

Stop after the environment is ready and the main repository is cloned or updated.

Do not continue into arbitrary capability installation, MCP registration, or project runtime setup unless the main repository explicitly asks for that work.

## Update and contribution flow

When the user asks to update, modify, commit, or push launcher code, keep changes scoped to this bootstrap repository.
