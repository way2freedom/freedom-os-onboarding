# Freedom OS Capability Registry 与 Manager 扩展方案

> 状态：讨论 / Codex 实施前设计稿  
> 目标：把 `freedom-os-manager` 从“Freedom OS 安装引导”扩展为轻量的本机能力生命周期管理入口。

## 1. 背景

当前 Freedom OS 已经有清晰的能力承载结构：

```text
skills/      Agent Skill 入口
services/    MCP / 外部服务 wrapper
projects/    可运行项目 / runtime truth
scripts/     初始化、检查、同步脚本
docs/        架构、路线图、标准和讨论
```

但本机实际状态仍然分散在多个位置：

- `skills-lock.json` 只记录少量仓库内 skill source/hash。
- `docs/roadmap/capabilities.md` 是团队级路线图和人工状态快照，不应承担本机真实安装状态。
- Hermes / Codex / MCP / 外部 CLI / 外部 repo 的安装状态没有统一视图。
- `Skill install`、`runtime ready`、`MCP registered` 容易被混为一谈。

因此需要一个轻量的本机 Capability Registry，由 `freedom-os-manager` 维护。

## 2. 定位

`freedom-os-manager` 的新增职责：

> Freedom OS 本地能力生命周期协调器：发现、安装、登记、查看、验证、更新、禁用和卸载内置及外部能力。

### 负责

- 扫描内置能力：`skills/`、`services/`、`projects/`。
- 记录外部能力：Hermes hub skill、Codex skill、外部 Git repo、外部 CLI、MCP server。
- 维护本机 registry。
- 调用能力自己的 setup / doctor / uninstall。
- 输出全局能力状态。
- 区分 skill 安装、runtime 准备、MCP 注册。

### 不负责

- 不接管每个能力的业务 runtime。
- 不保存真实 secret。
- 不强制把所有外部项目搬进 Freedom OS 仓库。
- 不重写 Hermes / Codex / MCP 的底层机制。
- 不把路线图文档当成本机状态数据库。

## 3. 核心产物

新增本机状态目录，默认不提交 Git：

```text
.freedom-os/registry/capabilities.json
```

如果后续需要 schema，可新增：

```text
docs/standards/capability-registry.md
```

第一版先把 schema 写在实现代码和本文档中，不急于标准化。

## 4. Registry Schema 草案

单个能力记录：

```json
{
  "name": "twitter-feed",
  "type": "hybrid-service",
  "source_type": "builtin",
  "source": "way2freedom/freedom-os",
  "version": "local-v3",
  "installed_at": "2026-07-15T00:00:00+08:00",
  "updated_at": "2026-07-15T00:00:00+08:00",
  "status": "partial",
  "paths": {
    "skill": "skills/twitter-feed",
    "service": "services/twitter-feed",
    "project": "projects/twitter-feed",
    "external_repo": null,
    "install_dir": "/Users/winston/Code/github.com/way2freedom/freedom-os"
  },
  "agents": {
    "hermes": {
      "installed": true,
      "skill_name": "twitter-feed"
    },
    "codex": {
      "installed": false,
      "skill_name": null
    }
  },
  "runtime": {
    "prepared": false,
    "doctor_command": null,
    "last_doctor_status": "unknown",
    "last_checked_at": null
  },
  "mcp": {
    "registered": false,
    "server_name": null
  },
  "notes": []
}
```

### 顶层文件结构

```json
{
  "version": 1,
  "updated_at": "2026-07-15T00:00:00+08:00",
  "capabilities": {
    "twitter-feed": {}
  }
}
```

## 5. 能力类型

| 类型 | 含义 | 默认安装方式 |
|---|---|---|
| `pure-skill` | 只有 Agent Skill、提示词、流程或轻量脚本 | 安装到 Hermes / Codex |
| `mcp-service` | MCP server 或外部 API wrapper | 注册 MCP / 检查服务配置 |
| `hybrid-service` | 同时包含 skill、service、project | 分层安装、分层验证 |
| `standalone-repo` | 外部独立代码仓库 | clone / pull / open in Codex |
| `external-cli` | 外部命令行工具 | 检测 binary / version / auth status |
| `external-skill` | Hermes hub / 第三方 Agent Skill | 记录来源和安装状态 |
| `template` | 模板目录 | 只发现，不作为安装目标 |

## 6. 状态模型

| 状态 | 含义 |
|---|---|
| `discovered` | 已扫描发现，但未安装或未登记完成 |
| `installed` | 已完成基础安装并写入 registry |
| `partial` | 部分安装，例如 skill 已装但 runtime 未准备好 |
| `ready` | doctor 通过，可用 |
| `broken` | 已安装但验证失败 |
| `disabled` | 本地禁用，不参与默认使用 |
| `uninstalled` | 已卸载或标记卸载 |
| `external` | 外部存在，但不由 Freedom OS 安装 |
| `unknown` | 无法确认 |

状态判断必须分层：

```text
skill installed != runtime ready != MCP registered
```

## 7. MVP 命令

第一版建议使用子命令：

```bash
freedom-os capabilities scan
freedom-os capabilities sync-installed
freedom-os capabilities check-installed
freedom-os capabilities list
freedom-os capabilities status <name>
freedom-os capabilities install <name>
freedom-os capabilities doctor <name>
freedom-os capabilities uninstall <name>
```

可加短别名：

```bash
freedom-os cap list
freedom-os cap status twitter-feed
```

## 8. MVP 范围

第一版只做“看得见 + 可登记 + 可验证基础状态”。

### 必做

1. 扫描当前仓库内置能力：
   - `skills/*/SKILL.md`
   - `services/*/README.md`
   - `projects/*/README.md`
2. 根据目录组合推断类型：
   - 只有 `skills/<name>` => `pure-skill`
   - `services/<name>` + 可选 `projects/<name>` => `mcp-service`
   - 同时存在 `skills/<name>`、`services/<name>`、`projects/<name>` => `hybrid-service`
3. 读取并合并已有 registry。
4. 写入 `.freedom-os/registry/capabilities.json`。
5. `sync-installed` 从本机 skill 根保存已安装能力快照；仓库里存在但未安装的能力不写入已安装列表。
6. `check-installed` 对比本机 skill 根和 registry；`--fix` 时校正 registry。
7. `list` 输出能力、类型、来源、状态、关键路径。
8. `status <name>` 输出 skill/service/project/runtime/mcp 分层状态。
9. `doctor <name>` 做只读检查，不自动修复。
10. `install <name>` 第一版支持内置 skill 安装到检测到的 Hermes / Codex Agent；`--dry-run` 只输出命令。
11. `uninstall <name>` 第一版默认只预览并标记 registry；传入 `--execute` 后才移除 Agent skill 登记，不删除用户数据。

### 暂不做

- 不做 UI。
- 不做 marketplace。
- 不做跨机器同步。
- 不做复杂依赖解析。
- 不自动删除 `.env`、数据库、导出文件。
- 不保存 secret。
- 不自动修改用户 Hermes profile，除非命令明确要求且有 preview。

## 9. 安装策略

### 内置能力安装

```text
1. 确认能力存在于仓库。
2. 推断能力类型和层次。
3. 如果存在 skills/<name>/SKILL.md，安装或提示安装 Agent skill。
4. 如果存在 projects/<name>/，读取 README 中的 setup / doctor 信息；第一版可只记录路径。
5. 如果存在 services/<name>/，读取 MCP 注册说明；第一版可只记录路径。
6. 更新 registry。
7. 输出下一步验证命令。
```

### 外部能力安装

第一版只设计接口，不强制实现。后续支持：

```bash
freedom-os capabilities add-external <name> --type repo --source git@github.com:owner/repo.git
freedom-os capabilities add-external <name> --type cli --command lark-cli
```

外部 Git repo 默认 clone 到：

```text
~/Code/github.com/<owner>/<repo>
```

## 10. 卸载策略

默认只做轻卸载。

### 轻卸载，MVP 默认

- 从 registry 标记 `uninstalled` 或 `disabled`。
- 如能安全调用 Agent skill uninstall，则执行或提示命令。
- 保留 repo、配置、数据库、导出文件。

### 完整卸载，后续

- 删除 runtime 依赖缓存，如 `.venv`、`node_modules`。
- 保留用户数据和配置。

### 危险卸载，后续且必须二次确认

- 删除 `.env`、数据库、本地导出、外部 clone。
- 必须 preview + confirm。

## 11. 与现有文件分工

| 文件 / 目录 | 角色 |
|---|---|
| `.freedom-os/registry/capabilities.json` | 本机真实安装状态，不提交 Git |
| `docs/roadmap/capabilities.md` | 团队级能力路线图和人工规划状态，提交 Git |
| `skills-lock.json` | 仓库内 skill source/hash 锁定，继续保留 |
| `skills/` / `services/` / `projects/` | 能力源结构 |

## 12. 建议实现位置

本方案应在独立仓库 `way2freedom/freedom-os-manager` 中实现，而不是在 `way2freedom/freedom-os` 的 `projects/` 下新增子项目。

Codex 需要先确认当前仓库是否已有 CLI/runtime。如果没有，建议在本仓库根目录新增最小 Python CLI：

```text
pyproject.toml
src/freedom_os_manager/
├── __init__.py
├── cli.py
├── registry.py
├── scanner.py
├── models.py
└── adapters/
    ├── __init__.py
    ├── hermes.py
    ├── codex.py
    ├── git_repo.py
    └── mcp.py
tests/
├── test_registry.py
├── test_scanner.py
└── test_cli.py
```

现有 `skills/freedom-os-manager/` 继续作为 bootstrap Agent Skill 包；CLI/runtime 源码放在仓库根级 `src/`。不要在 `freedom-os` 仓库里实现本需求。

## 13. Codex 实施计划

### Task 1：确认现状和技术路线

- 检查是否已有 `projects/freedom-os-manager` 或相关 CLI。
- 检查仓库是否已有 Python / Node 标准。
- 在 README 或 decisions 中记录技术选择。
- 不要修改其他能力项目。

验收：能说明 manager runtime 是复用已有还是新建。

### Task 2：定义 registry 模型和读写

- 实现 `CapabilityRecord`、`CapabilityRegistry`。
- 支持 load / save / upsert。
- registry 默认路径：`.freedom-os/registry/capabilities.json`。
- 自动创建父目录。

验收：单元测试覆盖空文件、新建文件、upsert、保留未知字段或至少不破坏已知字段。

### Task 3：实现仓库扫描器

扫描：

```text
skills/*/SKILL.md
services/*/README.md
projects/*/README.md
```

推断类型并生成 discovered records。

验收：在当前仓库运行 scan 至少能发现 `twitter-feed`、`collection-center`、`monitor-center`、`todo-dashboard`。

### Task 4：实现 list / status CLI

```bash
freedom-os capabilities list
freedom-os capabilities status twitter-feed
```

验收：输出包含 name、type、status、skill/service/project paths。

### Task 5：实现 doctor 只读检查

检查：

- path 是否存在。
- Hermes 是否可用。
- skill 是否可能已安装。
- project 是否存在。
- service 是否存在。

第一版不要求真实注册 MCP 检测完整，只要字段保留。

验收：doctor 不修改 repo 源文件；只更新 registry 中 last_checked/last_doctor_status 或输出检查结果。

### Task 6：实现 install MVP

第一版只支持内置 skill：

```bash
freedom-os capabilities install <name>
```

行为：

- 如果 `skills/<name>/SKILL.md` 存在，安装到检测到的 Hermes / Codex Agent 或输出明确命令。
- 如果没有检测到可支持的 Agent，或 `npx` 不可用，不报假成功，状态为 `partial` 或 `broken`，并给出原因。
- 更新 registry。

验收：用一个仓库内 skill 做 dry-run 或真实安装验证，并记录真实命令输出。

### Task 7：实现轻卸载 MVP

```bash
freedom-os capabilities uninstall <name>
```

行为：

- 默认不删除文件和用户数据。
- 默认标记 `disabled` 并输出 preview。
- 传入 `--execute` 时调用 Agent skill remove；命令失败时不得标记成功。

验收：测试确认不会删除 `skills/`、`services/`、`projects/` 下任何文件。

### Task 8：补文档和验证

- 更新 `projects/freedom-os-manager/README.md`。
- 如新增 CLI，写明 install / run / test 命令。
- 如影响根 README 快速开始，再单独更新，但不要膨胀 README。

验收命令由 Codex 根据技术栈确定，至少包括：

```bash
# 示例，按实际项目替换
python -m pytest
python3 -m freedom_os_manager.cli capabilities scan
python3 -m freedom_os_manager.cli capabilities list
python3 -m freedom_os_manager.cli capabilities status twitter-feed
```

## 14. 验收标准

完成后必须能回答：

1. 当前仓库发现了哪些能力？
2. 每个能力是 `pure-skill`、`hybrid-service` 还是其他类型？
3. 每个能力的 skill / service / project 路径在哪里？
4. 哪些能力只是发现，哪些已经安装？
5. 某个能力为什么不是 ready？
6. 卸载是否不会误删用户数据？

## 15. 风险和约束

- 不要把 `docs/roadmap/capabilities.md` 当成本机状态源。
- 不要声称安装成功，除非真实命令执行成功。
- 不要读取或打印 `.env`、token、cookie、private key。
- 不要删除本地数据库或用户导出文件。
- 不要把所有外部能力复制进本仓库。
- 不要把 manager 做成强依赖中心；能力应保持独立优先、集成增强。

## 16. 推荐给 Codex 的起始提示

```text
请在 Freedom OS 仓库中实现 freedom-os-manager 的 Capability Registry MVP。

先阅读：
- docs/capability-registry-and-manager.md
- README.md
- README.zh-CN.md
- skills/freedom-os-manager/SKILL.md

目标：新增或扩展 freedom-os-manager，使其支持 capabilities scan/list/status/doctor/install/uninstall 的 MVP。本次重点是本机 registry、仓库能力扫描、状态展示和只读验证。不要做 UI、marketplace、跨机器同步、危险卸载或 secret 管理。

要求：
1. 先确认当前仓库是否已有 runtime；有则复用，没有则在本仓库根级创建最小 CLI 项目。
2. registry 默认写入 .freedom-os/registry/capabilities.json，该目录不得提交真实状态。
3. scan 至少发现 skills/*、services/*、projects/* 并推断 pure-skill/mcp-service/hybrid-service。
4. status 必须区分 skill installed、runtime ready、MCP registered。
5. install MVP 先支持内置 skill；命令失败时不得报假成功。
6. uninstall MVP 默认轻卸载，不删除用户数据。
7. 补 README/使用说明，运行真实测试和 smoke commands，最后汇报真实输出。

实施时保持改动聚焦，不要重构其他能力项目，不要提交或读取 secrets。
```
