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
