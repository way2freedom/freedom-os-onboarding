from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


COMMAND_TIMEOUT_SECONDS = 30

AGENT_FLAGS = {
    "codex": "codex",
    "hermes": "hermes-agent",
}

AGENT_COMMANDS = {
    "codex": "codex",
    "hermes": "hermes",
}


def npx_available() -> bool:
    return shutil.which("npx") is not None


def available_agents() -> list[str]:
    return [agent for agent, command in AGENT_COMMANDS.items() if shutil.which(command) is not None]


def normalize_agents(agents: list[str] | None) -> list[str]:
    if agents:
        return agents
    return available_agents()


def format_agent_flags(agents: list[str]) -> list[str]:
    flags: list[str] = []
    for agent in agents:
        flags.extend(["-a", AGENT_FLAGS[agent]])
    return flags


def format_install_command(skill_dir: Path, agents: list[str]) -> str:
    return " ".join(["npx", "skills", "add", str(skill_dir), *format_agent_flags(agents)])


def install_skill(skill_dir: Path, agents: list[str]) -> subprocess.CompletedProcess[str]:
    return run_npx_skills(["add", str(skill_dir), *format_agent_flags(agents)])


def format_uninstall_command(skill_name: str, agents: list[str]) -> str:
    return " ".join(["npx", "skills", "remove", skill_name, *format_agent_flags(agents)])


def uninstall_skill(skill_name: str, agents: list[str]) -> subprocess.CompletedProcess[str]:
    return run_npx_skills(["remove", skill_name, *format_agent_flags(agents)])


def run_npx_skills(args: list[str]) -> subprocess.CompletedProcess[str]:
    command = ["npx", "skills", *args]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=f"Command timed out after {COMMAND_TIMEOUT_SECONDS}s: {' '.join(command)}",
        )
