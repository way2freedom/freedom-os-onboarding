#!/usr/bin/env bash
set -euo pipefail

flags=()
if command -v codex >/dev/null 2>&1; then
  flags+=(-a codex)
fi
if command -v hermes >/dev/null 2>&1; then
  flags+=(-a hermes-agent)
fi

if [ ${#flags[@]} -eq 0 ]; then
  echo "No supported agent CLI found. Install or expose codex and/or hermes on PATH." >&2
  exit 1
fi

printf '%q ' "${flags[@]}"
printf '\n'
