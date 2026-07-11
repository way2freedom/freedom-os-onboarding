# 更新、修改和提交代码规范

当用户要求更新团队仓库、修改能力、提交代码或推送远程时，按本流程执行。这个流程也适用于 `alphahelper` 这类简单独立 repo：先让用户在 Codex 中打开该 repo 文件夹，再在该 repo 内执行更新、验证、提交和推送。

## 1. 更新仓库

### 团队 skills 仓库

```bash
cd ~/Code/github.com/way2freedom/skills
git status --short
git fetch origin
git checkout v3
git pull --ff-only
```

### 简单独立 repo

例如 `alphahelper`：

```bash
cd ~/Code/github.com/way2freedom/alphahelper
git status --short
git pull --ff-only
```

如果本地还没有 clone：

```bash
mkdir -p ~/Code/github.com/way2freedom
cd ~/Code/github.com/way2freedom
git clone git@github.com:way2freedom/alphahelper.git
cd alphahelper
codex
```

如果工作区已有未提交改动，先告诉用户，不要直接覆盖。

## 2. 修改前确认边界

明确本次要改哪一层：

```text
skills/<name>      只改 Agent 使用说明
services/<name>    只改 MCP 注册说明/示例
projects/<name>    改源码、构建、测试、运行脚本
```

不要把完整项目源码复制进 `skills/` 或 `services/`。

## 3. 修改后验证

根据改动范围运行对应检查：

### 文档/skill-only

```bash
git diff --check -- skills/<name> services/<name>
```

如有脚本：

```bash
bash -n scripts/*.sh
```

### project 改动

```bash
cd projects/<name>
pnpm check
pnpm build
pnpm test
pnpm run doctor
```

如涉及 MCP：

```bash
pnpm mcp:install --agent all --mode prod
```

如涉及服务启动：

```bash
pnpm start
curl http://127.0.0.1:<port>/healthz
```

验证后停止临时启动的服务。

## 4. 提交前检查

```bash
git status --short
git diff --check
git diff --stat
git diff
```

确认没有：

- `.env`
- token / secret / password / cookie
- 私钥
- 个人浏览器 profile
- 本地绝对路径误写进通用文档
- node_modules / dist / data / backups

如果更新了英文用户文档，例如 `README.md`，必须同步更新中文文档，例如 `README.zh-CN.md`。如果某段内容不适合逐字翻译，也要在中文文档中同步同等语义和使用步骤。

## 5. 提交

只有用户明确要求提交时才执行：

```bash
git add <changed-files>
git commit -m "type: concise subject"
```

推荐类型：

```text
feat: 新能力或新功能
fix: 修复问题
docs: 文档
chore: 结构、配置、维护
refactor: 不改变行为的重构
```

## 6. 推送

只有用户明确要求推送时才执行：

```bash
git push origin <branch>
```

推送后报告：

```text
branch
commit SHA
remote URL or PR URL if available
remaining local changes, if any
```
