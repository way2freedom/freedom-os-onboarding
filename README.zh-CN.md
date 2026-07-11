# Freedom OS 新人引导

这是 way2freedom 团队公开的 bootstrap Agent Skill。新人先安装它，再让 Codex 或 Hermes 帮忙完成本地 Freedom OS 环境安装。

默认假设：新人已经安装并登录 Codex。若本机也安装了 Hermes Agent，本技能会兼容 Hermes，并尽量把团队技能/MCP 同时安装到两个 Agent。

## 第一步：安装引导技能

Codex 默认：

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-manager -a codex
```

Codex + Hermes：

```bash
npx skills add way2freedom/freedom-os-manager --skill freedom-os-manager -a codex -a hermes-agent
```

安装后，打开 Codex，说：

```text
使用 freedom-os-manager 帮我安装 todo-dashboard。
自动检测我本机有哪些 Agent。如果缺少 Git 或 GitHub 权限，请一步步引导我配置。
```

## 能力三层模型

Freedom OS 中一个能力可能由三层组成：

```text
skills/<name>      最薄 Agent Skill：说明、入口、使用规则
services/<name>    MCP/服务连接层：注册说明、配置示例
projects/<name>    项目源码和运行时：依赖、构建、测试、启动
```

安装时不能把三者混为一谈：

```text
安装 Skill 只代表 Agent 知道这个能力。
安装 Project 才代表源码依赖和构建完成。
注册 MCP 才代表 Codex/Hermes 可以调用工具。
```

也有一类项目只是独立代码仓库，例如 `alphahelper`。这类项目不需要强行拆成 skill / MCP / project 三层。onboarding 只需要：

```text
检查 Git/GitHub 权限
clone 独立 repo 到标准目录
提示用户在 Codex 中打开该文件夹
后续指导如何更新、修改、验证、提交和推送
```

例如：

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
git clone git@github.com:way2freedom/alphahelper.git
cd alphahelper
codex
```

除非该 repo 自己的 `README.md` / `AGENTS.md` / `service.json` 明确要求，否则不要自动安装 skill、注册 MCP 或执行项目 setup。

## 通用安装方式

如果这个 onboarding 仓库已经 clone 到本地，可以运行：

```bash
./skills/freedom-os-manager/scripts/install-capability.sh todo-dashboard
```

它会：

> 本仓库把技能包放在 `skills/freedom-os-manager/` 目录下，确保通过 `npx skills` 从 GitHub 安装时会连同 `references/` 和 `scripts/` 一起安装。

1. clone 或更新 `way2freedom/freedom-os`。
2. 自动检测 `codex` / `hermes`。
3. 如果存在 `skills/<name>`，安装 thin skill 到可用 Agent。
4. 如果存在 `projects/<name>`，执行 `corepack enable`、`pnpm install`、`pnpm setup`、`pnpm check`、`pnpm build`、`pnpm test`、`pnpm run doctor`。
5. 如果存在 MCP 注册脚本，Codex 可用时执行 `codex mcp add`，Hermes 可用时打印 preview 命令。

## 更新与提交代码

当需要更新团队仓库：

```bash
cd ~/Code/github.com/way2freedom/freedom-os
git fetch origin
git checkout v3
git pull --ff-only
```

当需要修改后提交代码：

1. 先检查状态：`git status --short`。
2. 只改本次任务相关文件。
3. 跑对应验证命令。
4. 查看 diff：`git diff`。
5. 用户明确要求提交时再执行：

```bash
git add <changed-files>
git commit -m "type: concise subject"
git push origin <branch>
```

详细规则见：`skills/freedom-os-manager/references/contribution-workflow.md`。

## 安全规则

- 不要把 token、私钥、密码、Cookie 粘贴到聊天里。
- 不要把 `.env`、密钥或本地个人配置提交到 Git。
- 需要 sudo、改 GitHub 权限、覆盖配置、提交或推送前，必须让用户确认。
- MCP 注册优先 preview；确认目标 Agent 和 profile 后再写入。
