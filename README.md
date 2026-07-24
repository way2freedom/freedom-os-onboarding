# Freedom OS Launcher

中文文档见：[README.zh-CN.md](README.zh-CN.md)。

Freedom OS Launcher is a small bootstrap repository. It only does two things:

1. prepare the local environment
2. clone or update the `way2freedom/freedom-os` main repository

It is not the place for package lifecycle work. Capability installation, installed-state inspection, MCP registration, and project runtime setup belong to Package OS and the owning project in the main `way2freedom/freedom-os` repository.

## Quick start

Install the launcher skill from GitHub:

```bash
npx skills add way2freedom/freedom-os-launcher --skill freedom-os-launcher -a codex
```

If both Codex and Hermes Agent are installed, target both:

```bash
npx skills add way2freedom/freedom-os-launcher --skill freedom-os-launcher -a codex -a hermes-agent
```

Then ask Codex:

```text
Use the Freedom OS Launcher to prepare my environment and clone the way2freedom/freedom-os repository.
Detect my available agents automatically. If Git or GitHub access is missing, guide me step by step.
```

## What it covers

- local Git, GitHub, Node, Corepack, and pnpm checks
- Git identity and GitHub auth setup when needed
- clone or update of `~/Code/github.com/way2freedom/freedom-os`
- handoff to the main repository for actual Freedom OS workflows

## What it does not cover

- package resolution, planning, installation, status, or drift inspection
- Skill or MCP installation and registration
- project build, test, or runtime setup beyond the bootstrap handoff

## Repository layout

```text
README.md                   English launcher guide
README.zh-CN.md             Chinese launcher guide
skills/freedom-os-launcher/ Launcher skill package
```
