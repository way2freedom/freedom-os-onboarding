# Freedom OS 启动器

英文文档见：[README.md](README.md)。

Freedom OS 启动器是一个很小的引导仓库，只负责两件事：

1. 先把本机环境准备好
2. 再 clone 或更新 `way2freedom/freedom-os` 主仓库

它不承担 Package OS 的生命周期职责。能力包的安装、已安装状态检查、MCP 注册和项目运行时准备，都应在主仓库的 Package OS 或对应项目中完成。

## 快速开始

从 GitHub 安装启动器 skill：

```bash
npx skills add way2freedom/freedom-os-launcher --skill freedom-os-launcher -a codex
```

如果本机同时安装了 Codex 和 Hermes Agent：

```bash
npx skills add way2freedom/freedom-os-launcher --skill freedom-os-launcher -a codex -a hermes-agent
```

安装后可以直接让 Codex 执行：

```text
使用 Freedom OS 启动器帮我准备本机环境，并 clone way2freedom/freedom-os 仓库。
自动检测我可用的 Agent。如果缺少 Git 或 GitHub 权限，请一步步引导我完成。
```

## 覆盖内容

- 本机 Git、GitHub、Node、Corepack、pnpm 检查
- Git 身份和 GitHub 认证的缺失补齐
- clone 或更新 `~/Code/github.com/way2freedom/freedom-os`
- 把用户交接到主仓库里的实际 Freedom OS 工作流

## 不覆盖的内容

- 能力包解析、计划、安装、状态或漂移检查
- Skill / MCP 的安装和注册
- 启动器交接之外的项目构建、测试或运行时准备

## 仓库结构

```text
README.md                    英文启动器说明
README.zh-CN.md              中文启动器说明
skills/freedom-os-launcher/  启动器 skill 包
```
