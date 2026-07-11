# Troubleshooting

## `git: command not found`

macOS:

```bash
xcode-select --install
```

Or if Homebrew exists:

```bash
brew install git
```

Windows: install Git for Windows from https://git-scm.com/download/win.

Linux: use the system package manager, asking before `sudo`.

## `Permission denied (publickey)`

SSH is not configured. Use `references/github-access.md`.

## `pnpm: command not found`

Run:

```bash
corepack enable
corepack prepare pnpm@9.15.0 --activate
pnpm --version
```

## `codex mcp add` fails

Check Codex is installed and logged in:

```bash
codex --version
codex mcp list
```

If `codex` is missing but `npx @openai/codex` works, ask the user whether to install Codex globally.

## `todo-dashboard` service does not start

From `projects/todo-dashboard`:

```bash
pnpm install
pnpm build
pnpm run doctor
pnpm start
```

If port 8083 is occupied, stop the existing process or ask the user to choose a different port if supported.
