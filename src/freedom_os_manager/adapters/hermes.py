from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def hermes_available() -> bool:
    return shutil.which("hermes") is not None


def installed_skills() -> tuple[bool, str]:
    if not hermes_available():
        return False, "hermes command not found"
    result = subprocess.run(["hermes", "skills", "list"], capture_output=True, text=True, check=False)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def skill_installed(name: str) -> tuple[bool, str]:
    ok, output = installed_skills()
    if not ok:
        return False, output or "hermes skills list failed"
    if name in output:
        return True, "listed by hermes skills list"
    return False, "not found in hermes skills list"


def install_skill(skill_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["npx", "skills", "add", str(skill_dir), "-a", "hermes-agent"],
        capture_output=True,
        text=True,
        check=False,
    )
