# Install todo-dashboard

Use this when the user asks to install `todo-dashboard` for Freedom OS.

## 1. Clone or update team repo

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

If SSH is not configured and the repo is public, HTTPS is acceptable:

```bash
git clone https://github.com/way2freedom/skills.git
```

## 2. Detect target agents

From the team repo root:

```bash
command -v codex >/dev/null && echo codex=present || echo codex=missing
command -v hermes >/dev/null && echo hermes=present || echo hermes=missing
```

Install to both if both exist; otherwise install to the one that exists.

## 3. Install thin skill

Codex only:

```bash
npx skills add ./skills/todo-dashboard -a codex
```

Hermes only:

```bash
npx skills add ./skills/todo-dashboard -a hermes-agent
```

Both:

```bash
npx skills add ./skills/todo-dashboard -a codex -a hermes-agent
```

## 4. Prepare runtime

```bash
cd ~/Code/github.com/way2freedom/skills/projects/todo-dashboard
corepack enable
pnpm install
pnpm setup
pnpm check
pnpm build
pnpm test
pnpm run doctor
```

## 5. Register Codex MCP

Prefer the Codex CLI command when Codex exists:

```bash
codex mcp add todo-dashboard -- pnpm --dir "$PWD" mcp:start
codex mcp list
```

The project also supports preview-only output:

```bash
pnpm mcp:install --agent codex --mode prod
```

## 6. Register Hermes MCP, if Hermes exists

Preview command:

```bash
pnpm mcp:install --agent hermes --mode prod --profile default
```

Then run the printed command after the user confirms the target Hermes profile.

## 7. Optional Web/API service

```bash
pnpm start
```

Verify:

```bash
curl http://127.0.0.1:8083/healthz
```

Expected shape:

```json
{"ok":true,"service":"todo-dashboard","version":"0.1.0"}
```

Stop the service when finished testing unless the user wants it to keep running.
