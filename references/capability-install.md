# 通用能力安装：Skill / MCP / Project

适用于团队仓库 `way2freedom/skills` 中任意能力 `<name>`。

## 目录含义

```text
skills/<name>      Agent Skill，最薄说明入口
services/<name>    MCP/服务注册说明和配置示例
projects/<name>    项目源码、依赖、构建、测试和运行时
```

不是每个能力都有三层：

- 纯技能：通常只有 `skills/<name>`。
- 纯 MCP：可能有 `services/<name>`，也可能有独立源码。
- 完整项目：通常有 `projects/<name>`。
- hybrid 能力：三层都有，但 skill/service 保持薄，project 是唯一源码真相。
- 简单独立 repo：不在 `way2freedom/skills` 仓库内，不需要安装 skill/MCP/project，只 clone 到标准目录并提示在 Codex 中打开。

## 简单独立 repo 项目

适用于 `alphahelper` 这类“只是一个单独代码仓库”的项目。

目标不是安装 Freedom OS capability，而是准备一个本地 checkout：

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
git clone git@github.com:way2freedom/<repo>.git
cd <repo>
codex
```

如果仓库已经存在：

```bash
cd ~/Code/github.com/way2freedom/<repo>
git status --short
git pull --ff-only
codex
```

后续只需要在 Codex 中引导：

```text
如何更新：git pull --ff-only
如何修改：先读 README.md / AGENTS.md，再改相关文件
如何验证：运行该 repo 自己的测试/检查命令
如何提交：git status、git diff、git add、git commit
如何推送：git push origin <branch>
```

除非该 repo 自己声明需要，否则不要执行以下动作：

```text
npx skills add
MCP 注册
pnpm setup / build / doctor
复制源码到 way2freedom/skills/projects
```

## 1. clone 或更新团队仓库

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

## 2. 自动检测 Agent

```bash
command -v codex >/dev/null && echo codex=present || echo codex=missing
command -v hermes >/dev/null && echo hermes=present || echo hermes=missing
```

如果两个都存在，两个都安装；只有一个就只安装一个。

## 3. 安装 Skill 层

如果存在：

```text
skills/<name>/SKILL.md
```

安装到检测到的 Agent：

```bash
# Codex only
npx skills add ./skills/<name> -a codex

# Hermes only
npx skills add ./skills/<name> -a hermes-agent

# Both
npx skills add ./skills/<name> -a codex -a hermes-agent
```

也可以从 onboarding 仓库运行：

```bash
./scripts/install-team-skill.sh ./skills/<name>
```

## 4. 安装 Project 层

如果存在：

```text
projects/<name>/package.json
```

通常执行：

```bash
cd projects/<name>
corepack enable
pnpm install
pnpm setup || true
pnpm check
pnpm build
pnpm test
pnpm run doctor || true
```

如果某个命令不存在，先读 `projects/<name>/README.md`、`AGENTS.md`、`service.json`，不要乱猜。

## 5. 注册 MCP 层

优先使用项目自己的注册脚本：

```bash
pnpm mcp:install --agent all --mode prod
```

如果 Codex 存在，且项目 manifest 指向 `pnpm --dir <project> mcp:start`，可注册：

```bash
codex mcp add <name> -- pnpm --dir "$PWD" mcp:start
codex mcp list
```

如果 Hermes 存在，优先 preview：

```bash
pnpm mcp:install --agent hermes --mode prod --profile default
```

再让用户确认目标 profile 后执行打印出的命令。

## 6. 验证

至少报告：

```text
Skill installed: yes/no and target agents
Project prepared: command results
MCP registered: yes/no and target agents
Service running: health check result, if applicable
```

不要用“应该可以”代替真实命令输出。
