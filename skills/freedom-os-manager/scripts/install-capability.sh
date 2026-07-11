#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: $0 <capability-name> [repo-root]" >&2
  echo "Example: $0 todo-dashboard" >&2
  exit 2
fi

name=$1
repo_root=${2:-${FREEDOM_OS_REPO:-$HOME/Code/github.com/way2freedom/freedom-os}}
repo_parent=$(dirname "$repo_root")
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if ! command -v git >/dev/null 2>&1; then
  echo "git is required. Install Git first, then rerun." >&2
  exit 1
fi

mkdir -p "$repo_parent"
if [ ! -d "$repo_root/.git" ]; then
  git clone git@github.com:way2freedom/freedom-os.git "$repo_root"
fi

cd "$repo_root"
git checkout v3
git pull --ff-only

if [ -f "skills/$name/SKILL.md" ]; then
  "$script_dir/install-team-skill.sh" "./skills/$name"
else
  echo "No thin skill found at skills/$name/SKILL.md; skipping skill install."
fi

if [ -f "projects/$name/package.json" ]; then
  cd "projects/$name"
  corepack enable
  pnpm install
  if pnpm run | grep -qE '^  setup$|^setup '; then pnpm setup; fi
  if pnpm run | grep -qE '^  check$|^check '; then pnpm check; fi
  if pnpm run | grep -qE '^  build$|^build '; then pnpm build; fi
  if pnpm run | grep -qE '^  test$|^test '; then pnpm test; fi
  if pnpm run | grep -qE '^  doctor$|^doctor '; then pnpm run doctor; fi

  if command -v codex >/dev/null 2>&1 && pnpm run | grep -qE '^  mcp:start$|^mcp:start '; then
    codex mcp add "$name" -- pnpm --dir "$PWD" mcp:start || {
      echo "Codex MCP registration failed. If supported, preview config with: pnpm mcp:install --agent codex --mode prod" >&2
      exit 1
    }
    codex mcp list
  fi

  if command -v hermes >/dev/null 2>&1 && pnpm run | grep -qE '^  mcp:install$|^mcp:install '; then
    echo "Hermes detected. Preview Hermes MCP registration with:"
    echo "  cd $PWD && pnpm mcp:install --agent hermes --mode prod --profile default"
  fi
else
  echo "No project found at projects/$name; skipping project runtime setup."
fi

if [ -d "$repo_root/services/$name" ]; then
  echo "Service docs available at: $repo_root/services/$name"
fi
