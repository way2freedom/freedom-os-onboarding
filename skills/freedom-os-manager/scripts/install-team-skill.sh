#!/usr/bin/env bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <skill-dir-or-source>" >&2
  echo "Example: $0 ./skills/todo-dashboard" >&2
  exit 2
fi

skill_source=$1
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC2207
agent_flags=($($script_dir/detect-agents.sh))

npx skills add "$skill_source" "${agent_flags[@]}"
