#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$script_dir/install-capability.sh" todo-dashboard "${FREEDOM_OS_REPO:-$HOME/Code/github.com/way2freedom/freedom-os}"
